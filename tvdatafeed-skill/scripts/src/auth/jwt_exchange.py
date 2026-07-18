"""
Canje de sessionid de TradingView por JWT auth_token vía scraping de /chart/.

Incluye:
- Reintentos con backoff exponencial (3 intentos: 1s → 2s → 4s).
- Múltiples patrones regex para resistir cambios en el HTML.
- Validación estructural del JWT antes de aceptarlo.
"""

import re
import time

import requests

from src.logger import get_logger

logger = get_logger(__name__)

# Configuración de reintentos
_MAX_RETRIES = 3
_BASE_BACKOFF_SECONDS = 1.0
_REQUEST_TIMEOUT = 15

# User-Agent realista para evitar bloqueos
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Patrones regex ordenados por probabilidad de éxito (más común primero)
_JWT_PATTERNS = [
    # Patrón principal: clave auth_token en JSON embebido
    r'"auth_token"\s*:\s*"([^"]+)"',
    # Variante: con comillas simples o sin espacios
    r"'auth_token'\s*:\s*'([^']+)'",
    # Variante: asignación directa en JavaScript
    r'authToken\s*[=:]\s*"([^"]+)"',
]


def exchange_sessionid_for_jwt(sessionid: str) -> str | None:
    """
    Canjea un sessionid de TradingView por el JWT auth_token real
    requerido por los WebSockets.

    Realiza una petición HTTP a /chart/ con la cookie de sesión y extrae
    el token del HTML de respuesta.

    Args:
        sessionid: Cookie sessionid válida de TradingView.

    Returns:
        El JWT auth_token, o None si no se pudo obtener.
    """
    if not sessionid:
        logger.error("Se intentó canjear un sessionid vacío.")
        return None

    cookies = {"sessionid": sessionid}
    headers = {"User-Agent": _USER_AGENT}

    last_error = None

    for attempt in range(1, _MAX_RETRIES + 1):
        logger.info(
            "Canjeando sessionid por JWT (intento %d/%d)...",
            attempt, _MAX_RETRIES,
        )

        try:
            response = requests.get(
                "https://www.tradingview.com/chart/",
                cookies=cookies,
                headers=headers,
                timeout=_REQUEST_TIMEOUT,
            )

            if response.status_code == 200:
                jwt = _extract_jwt_from_html(response.text)
                if jwt:
                    logger.info("JWT auth_token obtenido y validado con éxito.")
                    return jwt
                else:
                    logger.warning(
                        "Respuesta HTTP 200 pero no se encontró auth_token en el HTML."
                    )
            elif response.status_code == 403:
                logger.error(
                    "HTTP 403 Forbidden. La sesión puede haber expirado o TradingView "
                    "está bloqueando la petición."
                )
                return None  # No reintentar en 403
            else:
                logger.warning(
                    "HTTP %d al consultar /chart/. Reintentando...",
                    response.status_code,
                )

        except requests.exceptions.Timeout:
            logger.warning("Timeout en intento %d/%d.", attempt, _MAX_RETRIES)
            last_error = "Timeout"
        except requests.exceptions.ConnectionError:
            logger.warning("Error de conexión en intento %d/%d.", attempt, _MAX_RETRIES)
            last_error = "ConnectionError"
        except Exception as err:
            err_type = type(err).__name__
            logger.error(
                "Error inesperado en canje de token: %s (detalles omitidos por seguridad)",
                err_type,
            )
            last_error = err_type

        # Backoff exponencial antes del siguiente intento
        if attempt < _MAX_RETRIES:
            wait = _BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
            logger.debug("Esperando %.1f segundos antes del siguiente intento...", wait)
            time.sleep(wait)

    logger.error(
        "Agotados los %d intentos de canje de token. Último error: %s",
        _MAX_RETRIES, last_error,
    )
    return None


def _extract_jwt_from_html(html: str) -> str | None:
    """
    Intenta extraer el JWT auth_token del HTML usando múltiples patrones regex.

    Args:
        html: Contenido HTML de la página /chart/.

    Returns:
        El JWT si se encuentra y es válido, None en caso contrario.
    """
    for i, pattern in enumerate(_JWT_PATTERNS):
        match = re.search(pattern, html)
        if match:
            candidate = match.group(1)
            if _validate_jwt_structure(candidate):
                if i > 0:
                    logger.debug(
                        "JWT encontrado con patrón alternativo #%d.", i + 1
                    )
                return candidate
            else:
                logger.warning(
                    "Se encontró un candidato con patrón #%d pero falló la validación "
                    "estructural.",
                    i + 1,
                )

    return None


def _validate_jwt_structure(token: str) -> bool:
    """
    Validación estructural básica de un JWT.
    Un JWT válido tiene 3 segmentos separados por '.' y longitud mínima razonable.

    Args:
        token: Cadena candidata a JWT.

    Returns:
        True si el token tiene estructura de JWT válida.
    """
    if not token or len(token) < 100:
        return False

    parts = token.split(".")
    if len(parts) != 3:
        return False

    # Cada segmento debe ser no vacío
    if any(len(part) == 0 for part in parts):
        return False

    return True
