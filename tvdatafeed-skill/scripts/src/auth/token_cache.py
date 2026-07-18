"""
Caché local de JWT auth_token con TTL configurable.

Almacena el último token válido en un archivo JSON local para:
1. Evitar peticiones HTTP redundantes si el token sigue vigente.
2. Servir como fallback si la petición a /chart/ falla temporalmente.

El archivo de cache se crea con permisos 0600 (solo propietario).
"""

import json
import os
import stat
import time

from src.logger import get_logger

logger = get_logger(__name__)

# Ruta por defecto del cache (relativa al proyecto)
_DEFAULT_CACHE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".token_cache.json",
)


class TokenCache:
    """
    Gestiona el almacenamiento y recuperación de tokens JWT con TTL.

    Attributes:
        cache_path: Ruta al archivo JSON de cache.
        ttl_hours: Tiempo de vida del token en horas.
    """

    def __init__(self, cache_path: str = None, ttl_hours: float = None):
        """
        Args:
            cache_path: Ruta al archivo de cache. Por defecto: .token_cache.json
            ttl_hours: TTL en horas. Por defecto: variable CACHE_TTL_HOURS o 6.
        """
        self.cache_path = cache_path or _DEFAULT_CACHE_PATH
        self.ttl_hours = ttl_hours or float(os.environ.get("CACHE_TTL_HOURS", "6"))
        self._ttl_seconds = self.ttl_hours * 3600

    def get(self) -> str | None:
        """
        Recupera un token del cache si existe y no ha expirado.

        Returns:
            El JWT almacenado, o None si el cache está vacío, corrupto o expirado.
        """
        if not os.path.exists(self.cache_path):
            logger.debug("Archivo de cache no encontrado: %s", self.cache_path)
            return None

        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            stored_token = data.get("token", "")
            stored_time = data.get("timestamp", 0)
            elapsed = time.time() - stored_time

            if elapsed > self._ttl_seconds:
                logger.info(
                    "Token en cache expirado (%.1f horas de antigüedad, TTL: %.1f horas).",
                    elapsed / 3600,
                    self.ttl_hours,
                )
                return None

            if not stored_token or len(stored_token) < 100:
                logger.warning("Token en cache tiene formato inválido. Descartado.")
                return None

            remaining = (self._ttl_seconds - elapsed) / 60
            logger.info(
                "Token recuperado del cache (válido por %.0f minutos más).",
                remaining,
            )
            return stored_token

        except (json.JSONDecodeError, KeyError, TypeError):
            logger.warning("Archivo de cache corrupto. Se regenerará.")
            return None
        except Exception as err:
            err_type = type(err).__name__
            logger.error(
                "Error leyendo cache: %s (detalles omitidos por seguridad)", err_type
            )
            return None

    def save(self, token: str) -> bool:
        """
        Almacena un token JWT en el cache con timestamp actual.

        Args:
            token: El JWT a almacenar.

        Returns:
            True si se guardó correctamente, False en caso de error.
        """
        if not token or len(token) < 100:
            logger.warning("Se intentó cachear un token inválido. Operación rechazada.")
            return False

        data = {
            "token": token,
            "timestamp": time.time(),
            "token_preview": f"{token[:20]}...",
        }

        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            # Establecer permisos restrictivos (solo propietario lee/escribe)
            try:
                os.chmod(self.cache_path, stat.S_IRUSR | stat.S_IWUSR)  # 0600
            except OSError:
                logger.debug("No se pudieron establecer permisos 0600 en el cache.")

            logger.debug("Token almacenado en cache: %s", self.cache_path)
            return True

        except Exception as err:
            err_type = type(err).__name__
            logger.error(
                "Error escribiendo cache: %s (detalles omitidos por seguridad)", err_type
            )
            return False

    def invalidate(self) -> None:
        """Elimina el archivo de cache si existe."""
        if os.path.exists(self.cache_path):
            try:
                os.remove(self.cache_path)
                logger.debug("Cache invalidado: %s", self.cache_path)
            except OSError:
                logger.warning("No se pudo eliminar el archivo de cache.")

    def get_fallback(self) -> str | None:
        """
        Recupera un token del cache IGNORANDO el TTL.
        Usar solo como último recurso cuando todas las demás fuentes fallan.

        Returns:
            El token almacenado (aunque esté expirado), o None si no existe.
        """
        if not os.path.exists(self.cache_path):
            return None

        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            token = data.get("token", "")
            if token and len(token) >= 100:
                elapsed_hours = (time.time() - data.get("timestamp", 0)) / 3600
                logger.warning(
                    "Usando token de cache como FALLBACK (%.1f horas de antigüedad). "
                    "Puede no funcionar.",
                    elapsed_hours,
                )
                return token
        except Exception:
            pass

        return None
