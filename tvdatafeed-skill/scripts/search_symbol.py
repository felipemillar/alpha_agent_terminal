import argparse
import requests
import json
import sys
import re
from typing import List, Optional
from pydantic import BaseModel, Field

# Validación estricta para evitar inyecciones en el CLI
SYMBOL_REGEX = re.compile(r'^[A-Za-z0-9\-\.]+$')

class SymbolResult(BaseModel):
    exchange: Optional[str] = Field(None, description="El exchange del activo")
    symbol: str = Field(..., description="El ticker del activo")
    description: Optional[str] = Field(None, description="Nombre o descripción del activo")
    type: Optional[str] = Field(None, description="Tipo de activo (stock, crypto, etc)")

class SearchResponse(BaseModel):
    status: str = Field(..., description="'success' o 'error'")
    results: List[SymbolResult] = Field(default_factory=list, description="Resultados de la búsqueda")
    error_message: Optional[str] = Field(None, description="Mensaje de error si falló")

def search_tradingview(symbol: str, limit: int = 5, use_json: bool = False):
    if not SYMBOL_REGEX.match(symbol):
        response = SearchResponse(status="error", error_message=f"Símbolo inválido. Caracteres no permitidos detectados: {symbol}")
        if use_json:
            print(response.model_dump_json())
        else:
            print(f"❌ Error de Seguridad: Símbolo inválido '{symbol}'", file=sys.stderr)
        sys.exit(1)
        
    url = f"https://symbol-search.tradingview.com/symbol_search/v3/?text={symbol}&hl=1&lang=en&domain=production"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Origin": "https://www.tradingview.com",
        "Referer": "https://www.tradingview.com/"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        # Pedimos más símbolos internamente para asegurarnos de encontrar Pepperstone
        symbols = data.get("symbols", [])[:50]
        
        results_list = []
        for s in symbols:
            results_list.append(SymbolResult(
                exchange=s.get("exchange"),
                symbol=s.get("symbol", "").replace("<em>", "").replace("</em>", ""),
                description=s.get("description", "").replace("<em>", "").replace("</em>", ""),
                type=s.get("type")
            ))
            
        # Ordenar para priorizar Pepperstone si está en los resultados
        results_list.sort(key=lambda x: 0 if x.exchange and x.exchange.lower() == 'pepperstone' else 1)
        
        # Ahora limitamos al número solicitado por el usuario
        results_list = results_list[:limit]
            
        response = SearchResponse(status="success", results=results_list)
        
        if use_json:
            print(response.model_dump_json())
        else:
            for r in results_list:
                print(f"[{r.exchange}] {r.symbol} - {r.description} ({r.type})")
            
    except requests.exceptions.RequestException as e:
        response = SearchResponse(status="error", error_message=str(e))
        if use_json:
            print(response.model_dump_json())
        else:
            print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for a symbol in TradingView.")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol to search for (e.g. AAPL)")
    parser.add_argument("--limit", type=int, default=5, help="Max number of results to return")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON estricto")
    
    args = parser.parse_args()
    search_tradingview(args.symbol, args.limit, args.json)
