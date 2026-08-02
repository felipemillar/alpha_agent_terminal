import argparse
import sys
import os
import re
from pydantic import BaseModel  # type: ignore
from typing import Optional
from src.logger import get_logger  # type: ignore
from src.adapter import YahooFinanceAdapter  # type: ignore

logger = get_logger(__name__)

class ExtractorResponse(BaseModel):
    status: str
    csv_path: Optional[str] = None
    rows_extracted: int = 0
    error: Optional[str] = None
    error_type: Optional[str] = None

def main():
    parser = argparse.ArgumentParser(description="Extract historical data from Yahoo Finance")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol to extract (e.g. AAPL)")
    parser.add_argument("--interval", type=str, default="1d", help="Interval (e.g. 1m, 5m, 1h, 1d)")
    parser.add_argument("--bars", type=int, default=100, help="Number of bars to extract")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--output-dir", type=str, default="data", help="Output directory for CSVs")
    
    args = parser.parse_args()
    
    # Validation against basic injection
    if not re.match(r"^[A-Za-z0-9\.\-=^]+$", args.symbol):
        err_msg = "Invalid symbol format."
        if args.json:
            print(ExtractorResponse(status="error", error=err_msg, error_type="INVALID_INPUT").model_dump_json(indent=2))
        else:
            logger.error(err_msg)
        sys.exit(1)

    try:
        adapter = YahooFinanceAdapter()
        df = adapter.get_historical_data(symbol=args.symbol, interval=args.interval, bars=args.bars)
        
        if df is None or df.empty:
            err_msg = "No data available or invalid symbol/interval combination."
            if args.json:
                print(ExtractorResponse(status="error", error=err_msg, error_type="NO_DATA").model_dump_json(indent=2))
            else:
                logger.error(err_msg)
            sys.exit(1)
            
        # Ensure data directory exists
        data_dir = args.output_dir
        os.makedirs(data_dir, exist_ok=True)
        
        csv_filename = f"{args.symbol}_YF_historico.csv"
        csv_path = os.path.join(data_dir, csv_filename)
        
        df.to_csv(csv_path, index=False)
        
        if args.json:
            print(ExtractorResponse(status="success", csv_path=csv_path, rows_extracted=len(df)).model_dump_json(indent=2))
        else:
            logger.info(f"Data saved to {csv_path}")
            
    except Exception as e:
        err_type = type(e).__name__
        err_msg = f"Unexpected error: {err_type} (detalles omitidos por seguridad)"
        logger.error(err_msg)
        if args.json:
            print(ExtractorResponse(status="error", error=err_msg, error_type="UNKNOWN_ERROR").model_dump_json(indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
