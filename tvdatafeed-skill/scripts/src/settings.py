"""
Configuración centralizada del proyecto tvdatafeed_project.

Este módulo es PURAMENTE DECLARATIVO: no ejecuta lógica de red ni efectos
secundarios al ser importado. Toda la autenticación se activa explícitamente
llamando a resolve_auth_token().

Variables de entorno soportadas (.env):
    TV_USERNAME     - Credenciales de TradingView (raramente funciona por CAPTCHA)
    TV_PASSWORD     - Contraseña de TradingView
    TV_AUTH_TOKEN   - Token manual (sessionid o JWT directo)
    ENV             - Entorno: dev (default), prod, staging, ci
    LOG_LEVEL       - Nivel de logging: DEBUG, INFO (default), WARNING, ERROR
    CACHE_TTL_HOURS - TTL del cache de JWT en horas (default: 6)
"""

import os

from dotenv import load_dotenv

# Cargar variables desde .env (sin efectos secundarios de red)
load_dotenv()

# --- Constantes de configuración ---
TV_USERNAME: str = os.getenv("TV_USERNAME", "")
TV_PASSWORD: str = os.getenv("TV_PASSWORD", "")
ENV: str = os.getenv("ENV", "dev")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
CACHE_TTL_HOURS: float = float(os.getenv("CACHE_TTL_HOURS", "6"))
DEFAULT_REQUEST_TIMEOUT: int = 15

# Token raw del .env (puede ser sessionid o JWT)
_RAW_TOKEN: str = os.getenv("TV_AUTH_TOKEN", "")
_PLACEHOLDER = "ESTE_ES_TU_TOKEN"


def resolve_auth_token() -> str | None:
    """
    Resuelve el JWT auth_token siguiendo una cadena de prioridad:

    1. Cache local (si existe y no ha expirado).
    2. Variable .env TV_AUTH_TOKEN (si es un JWT completo, len > 500).
    3. Variable .env TV_AUTH_TOKEN (si es un sessionid, canjearlo por JWT).
    4. Extracción automática de cookies del navegador → canje por JWT.
    5. Fallback: token expirado del cache (último recurso).

    Returns:
        El JWT auth_token válido, o None si no se pudo obtener.
    """
    # Import diferido para evitar dependencias circulares y side-effects al importar
    from src.logger import get_logger
    from src.auth.token_cache import TokenCache
    from src.auth.browser_cookies import get_sessionid_from_browser
    from src.auth.jwt_exchange import exchange_sessionid_for_jwt

    logger = get_logger(__name__)
    cache = TokenCache(ttl_hours=CACHE_TTL_HOURS)

    # Paso 1: Intentar cache
    cached_token = cache.get()
    if cached_token:
        os.environ["TV_AUTH_TOKEN"] = cached_token
        return cached_token

    jwt = None
    sessionid = None

    # Paso 2/3: Verificar valor del .env
    if _RAW_TOKEN and _RAW_TOKEN != _PLACEHOLDER:
        if len(_RAW_TOKEN) > 500:
            # Ya es un JWT completo pegado directamente
            logger.info("Usando JWT auth_token configurado manualmente en .env.")
            jwt = _RAW_TOKEN
        else:
            # Es un sessionid que necesita ser canjeado
            logger.info("Usando sessionid configurado manualmente en .env.")
            sessionid = _RAW_TOKEN

    # Paso 4: Extracción automática del navegador
    if not jwt and not sessionid:
        sessionid = get_sessionid_from_browser()

    # Canjear sessionid por JWT si lo tenemos
    if sessionid and not jwt:
        jwt = exchange_sessionid_for_jwt(sessionid)

    # Paso 5: Fallback a cache expirado
    if not jwt:
        logger.warning("Todas las fuentes de autenticación fallaron. Intentando cache fallback...")
        jwt = cache.get_fallback()

    # Resultado final
    if jwt:
        os.environ["TV_AUTH_TOKEN"] = jwt
        cache.save(jwt)
        return jwt

    logger.error(
        "No se pudo obtener un token de autenticación. "
        "Inicia sesión en tu navegador o configura TV_AUTH_TOKEN en .env."
    )
    return None
