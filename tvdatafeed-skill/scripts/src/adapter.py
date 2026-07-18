"""
TradingViewAdapter: capa de abstracción sobre tvDatafeed.

Usa el patrón Adapter (composición, no herencia) para desacoplar
la lógica de negocio de la librería subyacente. Si tvDatafeed deja
de mantenerse o cambia su API, solo se modifica esta clase.

Uso:
    from src.adapter import TradingViewAdapter
    adapter = TradingViewAdapter()
    adapter.connect()
    df = adapter.get_historical_data("AAPL", "NASDAQ", "daily", 1000)
"""

import os
import time
import io
import contextlib

import pandas as pd
from tvDatafeed import TvDatafeed, Interval

from src import settings
from src.logger import get_logger

logger = get_logger(__name__)

# Mapeo de strings amigables a valores del Enum Interval
INTERVAL_MAP: dict[str, Interval] = {
    "1s": Interval.in_1_second,
    "5s": Interval.in_5_second,
    "10s": Interval.in_10_second,
    "30s": Interval.in_30_second,
    "1m": Interval.in_1_minute,
    "3m": Interval.in_3_minute,
    "5m": Interval.in_5_minute,
    "15m": Interval.in_15_minute,
    "30m": Interval.in_30_minute,
    "45m": Interval.in_45_minute,
    "1h": Interval.in_1_hour,
    "2h": Interval.in_2_hour,
    "3h": Interval.in_3_hour,
    "4h": Interval.in_4_hour,
    "daily": Interval.in_daily,
    "1d": Interval.in_daily,
    "weekly": Interval.in_weekly,
    "1w": Interval.in_weekly,
    "monthly": Interval.in_monthly,
    "1M": Interval.in_monthly,
}


class TradingViewAdapter:
    """
    Wrapper desacoplado sobre TvDatafeed.

    Encapsula toda la interacción con la librería de terceros usando
    composición. La API pública de este adapter es estable.
    """

    def __init__(self):
        self._client: TvDatafeed | None = None
        self._connected: bool = False

    @property
    def is_connected(self) -> bool:
        """Indica si la conexión con TradingView está activa."""
        return self._connected

    def connect(self) -> bool:
        """
        Resuelve la autenticación e inicializa la conexión con TradingView.

        Returns:
            True si la conexión fue exitosa, False en caso contrario.
        """
        logger.info("Inicializando conexión con TradingView...")

        # Resolver autenticación a través de la cadena de prioridad
        token = settings.resolve_auth_token()
        if not token:
            logger.error("No se pudo resolver un token de autenticación.")
            return False

        try:
            # tvdatafeed es ruidoso y hace prints crudos. Atrapamos su stdout.
            with contextlib.redirect_stdout(io.StringIO()):
                if settings.TV_USERNAME and settings.TV_PASSWORD:
                    logger.info("Intentando login clásico con credenciales...")
                    self._client = TvDatafeed(
                        username=settings.TV_USERNAME,
                        password=settings.TV_PASSWORD,
                    )
                else:
                    logger.info("Inicializando TvDatafeed con JWT del entorno...")
                    self._client = TvDatafeed()

            self._connected = True
            logger.info("Conexión establecida con TradingView.")
            return True

        except Exception as err:
            err_type = type(err).__name__
            logger.error(
                "Error de conexión con TradingView: %s (detalles omitidos por seguridad)",
                err_type,
            )
            self._connected = False
            return False

    def get_historical_data(
        self,
        symbol: str,
        exchange: str,
        interval: str | Interval = "daily",
        n_bars: int = 1000,
    ) -> pd.DataFrame | None:
        """
        Descarga datos históricos de un símbolo.

        Args:
            symbol: Ticker del activo (ej. "AAPL").
            exchange: Exchange del activo (ej. "NASDAQ").
            interval: Temporalidad. Acepta string ("daily", "1h", "15m") o Interval enum.
            n_bars: Cantidad de barras a solicitar.

        Returns:
            DataFrame con columnas [symbol, open, high, low, close, volume]
            indexado por datetime, o None si falla.
        """
        if not self._connected or self._client is None:
            logger.error("No hay conexión activa. Llama a connect() primero.")
            return None

        # Resolver interval si es string
        if isinstance(interval, str):
            resolved = INTERVAL_MAP.get(interval.lower())
            if resolved is None:
                logger.error(
                    "Intervalo '%s' no reconocido. Opciones: %s",
                    interval,
                    ", ".join(sorted(INTERVAL_MAP.keys())),
                )
                return None
            interval = resolved

        logger.info(
            "Solicitando %d barras de %s:%s en resolución %s...",
            n_bars, exchange, symbol, interval,
        )

        try:
            # tvdatafeed es ruidoso. Atrapamos su stdout.
            with contextlib.redirect_stdout(io.StringIO()):
                data = self._client.get_hist(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    n_bars=n_bars,
                )
        except Exception as err:
            err_type = type(err).__name__
            logger.error(
                "Error al obtener datos de %s:%s: %s (detalles omitidos por seguridad)",
                exchange, symbol, err_type,
            )
            return None

        if data is None or data.empty:
            logger.warning(
                "No se recibieron datos para %s:%s. Verifica símbolo/exchange/sesión.",
                exchange, symbol,
            )
            return None

        logger.info("Se obtuvieron %d registros de %s:%s.", len(data), exchange, symbol)
        return data

    def get_historical_data_batch(
        self,
        requests_list: list[dict],
        delay_seconds: float = 1.0,
    ) -> dict[str, pd.DataFrame]:
        """
        Descarga datos históricos de múltiples símbolos secuencialmente.

        Inserta un delay configurable entre cada solicitud para evitar
        rate-limiting de TradingView.

        Args:
            requests_list: Lista de diccionarios con claves:
                - symbol (str): Ticker del activo.
                - exchange (str): Exchange del activo.
                - interval (str | Interval): Temporalidad (default: "daily").
                - n_bars (int): Cantidad de barras (default: 1000).
            delay_seconds: Pausa entre solicitudes en segundos.

        Returns:
            Diccionario {clave: DataFrame} donde clave es "EXCHANGE:SYMBOL".
            Los símbolos que fallen no se incluyen en el resultado.
        """
        results: dict[str, pd.DataFrame] = {}
        total = len(requests_list)

        logger.info("Iniciando descarga batch de %d símbolos...", total)

        for i, req in enumerate(requests_list, 1):
            symbol = req.get("symbol", "")
            exchange = req.get("exchange", "")
            interval = req.get("interval", "daily")
            n_bars = req.get("n_bars", 1000)
            key = f"{exchange}:{symbol}"

            logger.info("[%d/%d] Descargando %s...", i, total, key)

            data = self.get_historical_data(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=n_bars,
            )

            if data is not None:
                results[key] = data
            else:
                logger.warning("[%d/%d] Sin datos para %s. Continuando...", i, total, key)

            # Delay entre solicitudes (excepto en la última)
            if i < total and delay_seconds > 0:
                time.sleep(delay_seconds)

        logger.info(
            "Batch completo: %d/%d símbolos descargados con éxito.",
            len(results), total,
        )
        return results
