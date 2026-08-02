import yfinance as yf
import pandas as pd
from typing import Optional
from src.logger import get_logger

logger = get_logger(__name__)

class YahooFinanceAdapter:
    def __init__(self):
        # Map common intervals to yfinance valid intervals
        self.interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "1h", 
            "1d": "1d",
            "1wk": "1wk",
            "1mo": "1mo"
        }

    def get_historical_data(self, symbol: str, interval: str = "1d", bars: int = 100) -> Optional[pd.DataFrame]:
        yf_interval = self.interval_map.get(interval, interval)
        logger.info(f"Downloading {bars} bars for {symbol} at interval {yf_interval}...")
        
        try:
            if "m" in yf_interval or "h" in yf_interval:
                period = "60d" 
            else:
                period = "max"
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=yf_interval)
            
            if df.empty:
                logger.warning(f"No data returned for {symbol} at interval {yf_interval}.")
                return None
            
            df.index.name = "datetime"
            df.reset_index(inplace=True)
            
            cols_to_keep = ["datetime", "Open", "High", "Low", "Close", "Volume"]
            existing_cols = [c for c in cols_to_keep if c in df.columns]
            df = df[existing_cols]
            
            df.sort_values("datetime", inplace=True)
            df = df.tail(bars).reset_index(drop=True)
            
            logger.info(f"Successfully downloaded {len(df)} bars.")
            return df
            
        except Exception as e:
            logger.error(f"Error downloading data for {symbol}: {type(e).__name__} (detalles omitidos por seguridad)")
            return None
