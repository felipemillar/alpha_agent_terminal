#!/usr/bin/env python3
"""
extractor.py — Script principal de descarga de datos históricos de TradingView.

Uso:
    # Valores por defecto: AAPL, NASDAQ, daily, 1000 barras
    python extractor.py

    # Con argumentos personalizados
    python extractor.py --symbol MSFT --exchange NASDAQ --interval 1h --bars 500

    # Descarga múltiple (batch)
    python extractor.py --symbol AAPL,MSFT,GOOGL --exchange NASDAQ --interval daily --bars 1000
"""

import argparse
import sys
import os
import re

import pandas as pd

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# Saneamiento de parámetros
SAFE_REGEX = re.compile(r'^[A-Za-z0-9\-\.]+$')

from src.adapter import TradingViewAdapter
from src.logger import get_logger, mute_console

class ExtractedFile(BaseModel):
    symbol: str = Field(..., description="Ticker del activo")
    exchange: str = Field(..., description="Exchange del activo")
    filepath: str = Field(..., description="Ruta absoluta o relativa al CSV generado")
    rows: int = Field(..., description="Cantidad de filas extraídas")
    sample_data: List[Dict[str, Any]] = Field(default_factory=list, description="Muestra de las últimas filas")

class ExtractorResponse(BaseModel):
    status: str = Field(..., description="'success' o 'error'")
    error_type: Optional[str] = Field(None, description="Código de error para integraciones (ej. AUTH_REQUIRED)")
    files: List[ExtractedFile] = Field(default_factory=list, description="Archivos generados")
    error_message: Optional[str] = Field(None, description="Mensaje de error")


logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """Parsea argumentos de línea de comandos con valores por defecto sensibles."""
    parser = argparse.ArgumentParser(
        description="Descarga datos históricos de TradingView.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Intervalos soportados:
  1s, 5s, 10s, 30s         (segundos)
  1m, 3m, 5m, 15m, 30m, 45m (minutos)
  1h, 2h, 3h, 4h           (horas)
  daily, weekly, monthly    (períodos largos)

Ejemplos:
  python extractor.py
  python extractor.py --symbol MSFT --interval 1h --bars 500
  python extractor.py --symbol AAPL,MSFT,GOOGL --exchange NASDAQ
        """,
    )
    parser.add_argument(
        "--symbol", type=str, default="AAPL",
        help="Ticker(s) del activo, separados por coma para batch (default: AAPL)",
    )
    parser.add_argument(
        "--exchange", type=str, default="NASDAQ",
        help="Exchange del activo (default: NASDAQ)",
    )
    parser.add_argument(
        "--interval", type=str, default="daily",
        help="Temporalidad de las velas (default: daily)",
    )
    parser.add_argument(
        "--bars", type=int, default=1000,
        help="Cantidad de barras a descargar (default: 1000)",
    )
    parser.add_argument(
        "--output-dir", type=str, default="data",
        help="Directorio de salida para los CSV (default: data)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Silencia logs de consola y escupe JSON estrictamente por stdout",
    )
    return parser.parse_args()


def export_to_csv(data: pd.DataFrame, symbol: str, exchange: str, output_dir: str) -> str:
    """
    Exporta un DataFrame a CSV en el directorio especificado.

    Returns:
        Ruta del archivo generado.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{symbol}_{exchange}_historico.csv"
    filepath = os.path.join(output_dir, filename)
    data.to_csv(filepath)
    logger.info("CSV guardado: %s", filepath)
    return filepath


def main():
    """Punto de entrada principal del extractor."""
    args = parse_args()
    if args.json:
        mute_console()
        
    symbols = [s.strip().upper() for s in args.symbol.split(",")]
    exchange = args.exchange.upper()

    # Validación de Seguridad
    for sym in symbols:
        if not SAFE_REGEX.match(sym):
            if args.json:
                print(ExtractorResponse(status="error", error_message=f"Error de Seguridad: Símbolo inválido '{sym}'").model_dump_json())
            else:
                logger.critical("Error de Seguridad: Símbolo inválido '%s'", sym)
            sys.exit(1)
            
    if not SAFE_REGEX.match(exchange):
        if args.json:
            print(ExtractorResponse(status="error", error_message=f"Error de Seguridad: Exchange inválido '{exchange}'").model_dump_json())
        else:
            logger.critical("Error de Seguridad: Exchange inválido '%s'", exchange)
        sys.exit(1)

    # Inicializar adapter
    adapter = TradingViewAdapter()
    if not adapter.connect():
        logger.critical("No se pudo establecer conexión. Abortando.")
        if args.json:
            print(ExtractorResponse(
                status="error",
                error_type="AUTH_REQUIRED",
                error_message="Fallo al conectar con TradingView: No se encontró sesión activa de TradingView."
            ).model_dump_json())
        sys.exit(1)

    extracted_files = []

    # Descarga: single o batch
    if len(symbols) == 1:
        symbol = symbols[0]
        data = adapter.get_historical_data(
            symbol=symbol,
            exchange=exchange,
            interval=args.interval,
            n_bars=args.bars,
        )

        if data is None:
            logger.error("No se obtuvieron datos para %s:%s.", exchange, symbol)
            if args.json:
                print(ExtractorResponse(status="error", error_message=f"No se obtuvieron datos para {symbol}").model_dump_json())
            sys.exit(1)

        if not args.json:
            logger.info("Muestra de datos (últimas 5 filas):")
            print(data.tail())
            
        filepath = export_to_csv(data, symbol, exchange, args.output_dir)
        # sample as dict
        sample_records = json.loads(data.tail().to_json(orient="records", date_format="iso")) if not data.empty else []
        
        extracted_files.append(ExtractedFile(
            symbol=symbol,
            exchange=exchange,
            filepath=filepath,
            rows=len(data),
            sample_data=sample_records
        ))

    else:
        # Batch download
        requests_list = [
            {
                "symbol": sym,
                "exchange": exchange,
                "interval": args.interval,
                "n_bars": args.bars,
            }
            for sym in symbols
        ]

        results = adapter.get_historical_data_batch(requests_list)

        if not results:
            logger.error("No se obtuvieron datos de ningún símbolo.")
            if args.json:
                print(ExtractorResponse(status="error", error_message="No se obtuvieron datos de ningún símbolo.").model_dump_json())
            sys.exit(1)

        for key, data in results.items():
            ex, sym = key.split(":")
            if not args.json:
                logger.info("Muestra de %s (últimas 3 filas):", key)
                print(data.tail(3))
                print()
            filepath = export_to_csv(data, sym, ex, args.output_dir)
            sample_records = json.loads(data.tail(3).to_json(orient="records", date_format="iso")) if not data.empty else []
            extracted_files.append(ExtractedFile(
                symbol=sym,
                exchange=ex,
                filepath=filepath,
                rows=len(data),
                sample_data=sample_records
            ))

        if not args.json:
            logger.info(
                "Batch completado: %d/%d símbolos exportados.",
                len(results), len(symbols),
            )

    if args.json:
        print(ExtractorResponse(status="success", files=extracted_files).model_dump_json())

if __name__ == "__main__":
    import json
    main()
