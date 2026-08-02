import argparse
import sys
import json
import requests
from pydantic import BaseModel
from typing import List, Optional
from src.logger import get_logger

logger = get_logger(__name__)

class SymbolResult(BaseModel):
    symbol: str
    description: str
    exchange: str
    type: str

class SearchResponse(BaseModel):
    results: List[SymbolResult]
    error: Optional[str] = None

def search_yahoo_finance(query: str) -> List[SymbolResult]:
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for quote in data.get("quotes", []):
            if "symbol" in quote:
                results.append(SymbolResult(
                    symbol=quote.get("symbol", ""),
                    description=quote.get("longname", quote.get("shortname", "N/A")),
                    exchange=quote.get("exchDisp", quote.get("exchange", "Unknown")),
                    type=quote.get("quoteType", "Unknown")
                ))
        return results
    except Exception as e:
        logger.error(f"Error fetching data from Yahoo Finance: {type(e).__name__} (detalles omitidos por seguridad)")
        raise

def main():
    parser = argparse.ArgumentParser(description="Search symbols on Yahoo Finance")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol or keyword to search")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    try:
        results = search_yahoo_finance(args.symbol)
        
        if args.json:
            response = SearchResponse(results=results)
            print(response.model_dump_json(indent=2))
        else:
            if not results:
                print("No results found.")
            for r in results:
                print(f"[{r.exchange}] {r.symbol} - {r.description} ({r.type})")
                
    except Exception as e:
        if args.json:
            response = SearchResponse(results=[], error=str(e))
            print(response.model_dump_json(indent=2))
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
