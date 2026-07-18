"""
Extracción de cookies de sesión de TradingView desde navegadores locales.

Soporta Chrome, Safari y Firefox. Detecta automáticamente si el entorno
es de producción (contenedor/cloud) y omite la extracción para evitar
errores en entornos headless.
"""

import os

from src.logger import get_logger

logger = get_logger(__name__)


def _is_headless_environment() -> bool:
    """
    Detecta si estamos en un entorno sin navegadores (contenedor Docker, CI/CD, cloud).

    Returns:
        True si se detecta un entorno headless donde no tiene sentido
        buscar cookies de navegador.
    """
    # Variable explícita de entorno
    env = os.environ.get("ENV", "dev").lower()
    if env in ("prod", "production", "staging", "ci"):
        logger.debug("Entorno detectado: %s. Omitiendo extracción de cookies.", env)
        return True

    # Detección de contenedor Docker
    if os.path.exists("/.dockerenv"):
        logger.debug("Archivo /.dockerenv detectado. Entorno containerizado.")
        return True

    # Detección de Kubernetes
    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        logger.debug("Variable KUBERNETES_SERVICE_HOST detectada.")
        return True

    return False


def get_sessionid_from_browser() -> str | None:
    """
    Intenta extraer la cookie 'sessionid' de TradingView desde los navegadores
    instalados en el sistema local.

    Orden de búsqueda: Chrome → Safari → Firefox.

    Returns:
        El valor de la cookie sessionid, o None si no se encuentra.
    """
    # Guardia de entorno: no intentar en producción/contenedores
    if _is_headless_environment():
        logger.info("Entorno headless detectado. Omitiendo extracción de cookies del navegador.")
        return None

    try:
        import browser_cookie3
    except ImportError:
        logger.warning("La librería browser-cookie3 no está instalada. "
                       "Instalar con: pip install browser-cookie3")
        return None

    browsers = [
        ("Chrome", browser_cookie3.chrome),
        ("Safari", browser_cookie3.safari),
        ("Firefox", browser_cookie3.firefox),
    ]

    logger.info("Buscando sesión activa de TradingView en navegadores locales...")

    for name, get_cookies in browsers:
        try:
            cj = get_cookies(domain_name="tradingview.com")
            for cookie in cj:
                if "tradingview.com" in cookie.domain and cookie.name == "sessionid":
                    value = cookie.value
                    if value and _validate_sessionid(value):
                        logger.info("sessionid extraído con éxito desde %s.", name)
                        return value
        except Exception as err:
            err_type = type(err).__name__
            logger.debug(
                "No se pudo extraer sessionid de %s: %s (detalles omitidos por seguridad)",
                name, err_type,
            )

    logger.warning("No se encontró ninguna sesión activa de TradingView en los navegadores.")
    return None


def _validate_sessionid(sessionid: str) -> bool:
    """
    Validación básica de seguridad del sessionid antes de enviarlo por HTTP.
    Previene inyección de caracteres maliciosos en headers.

    Args:
        sessionid: El valor crudo extraído de la cookie.

    Returns:
        True si el formato es válido (alfanumérico).
    """
    if not sessionid or len(sessionid) < 10:
        logger.warning("sessionid demasiado corto o vacío.")
        return False

    # TradingView sessionids son alfanuméricos (letras + dígitos)
    if not all(c.isalnum() for c in sessionid):
        logger.warning("sessionid contiene caracteres no alfanuméricos. Rechazado por seguridad.")
        return False

    return True
