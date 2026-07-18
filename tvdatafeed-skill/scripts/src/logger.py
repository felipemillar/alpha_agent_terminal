"""
Sistema de logging estructurado para tvdatafeed_project.

Proporciona dos handlers:
- Consola: formato legible con emojis y colores.
- Archivo: formato técnico con timestamp ISO 8601, rotación automática (5MB, 3 backups).

Uso:
    from src.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Mensaje informativo")
"""

import logging
import os
from logging.handlers import RotatingFileHandler

_MUTE_CONSOLE = False

def mute_console():
    """Silencia el output de consola para loggers existentes y futuros."""
    global _MUTE_CONSOLE
    _MUTE_CONSOLE = True
    
    # Remover de loggers ya creados
    for logger_name, logger_obj in logging.Logger.manager.loggerDict.items():
        if isinstance(logger_obj, logging.Logger):
            handlers_to_remove = [h for h in logger_obj.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler)]
            for h in handlers_to_remove:
                logger_obj.removeHandler(h)

# Directorio de logs relativo al proyecto
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "tvdatafeed.log")
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_BACKUP_COUNT = 3

# Mapeo de emojis por nivel de severidad para la consola
_EMOJI_MAP = {
    logging.DEBUG: "🔧",
    logging.INFO: "ℹ️ ",
    logging.WARNING: "⚠️ ",
    logging.ERROR: "❌",
    logging.CRITICAL: "🔥",
}


class EmojiConsoleFormatter(logging.Formatter):
    """Formatter para consola que antepone un emoji según el nivel de log."""

    def format(self, record):
        emoji = _EMOJI_MAP.get(record.levelno, "")
        original_msg = super().format(record)
        return f"{emoji} {original_msg}"


class TruncatedTokenFilter(logging.Filter):
    """
    Filtro de seguridad: detecta tokens JWT largos en los mensajes de log
    y los trunca automáticamente para evitar fugas de información.
    """

    def filter(self, record):
        msg = str(record.msg)
        # Si el mensaje contiene algo que parece un JWT (3 segmentos base64 separados por .)
        # con longitud > 100, lo truncamos
        if hasattr(record, 'args') and record.args:
            args = list(record.args)
            for i, arg in enumerate(args):
                arg_str = str(arg)
                if len(arg_str) > 100 and arg_str.count('.') >= 2:
                    args[i] = f"{arg_str[:20]}...[TRUNCADO]"
            record.args = tuple(args)
        return True


def get_logger(name: str, level: str = None) -> logging.Logger:
    """
    Crea y retorna un logger configurado con handlers de consola y archivo.

    Args:
        name: Nombre del logger (típicamente __name__).
        level: Nivel de log override. Si es None, usa la variable de entorno
               LOG_LEVEL o INFO por defecto.

    Returns:
        logging.Logger configurado.
    """
    log_level_str = level or os.environ.get("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    logger = logging.getLogger(name)

    # Evitar agregar handlers duplicados si el logger ya fue configurado
    if logger.handlers:
        return logger

    logger.setLevel(log_level)
    logger.propagate = False

    # Filtro de seguridad para truncar tokens
    token_filter = TruncatedTokenFilter()

    # --- Handler de Consola ---
    if not _MUTE_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = EmojiConsoleFormatter("%(message)s")
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(token_filter)
        logger.addHandler(console_handler)

    # --- Handler de Archivo con Rotación ---
    try:
        os.makedirs(_LOG_DIR, exist_ok=True)
        file_handler = RotatingFileHandler(
            _LOG_FILE,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)  # Archivo siempre captura todo
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(token_filter)
        logger.addHandler(file_handler)
    except OSError:
        # Si no se puede crear el directorio de logs (ej. permisos),
        # continuamos solo con consola
        logger.warning("No se pudo crear el directorio de logs. Solo se usará consola.")

    return logger
