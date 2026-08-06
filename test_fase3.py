import json
import os
import sys
import numpy as np

sys.path.append(os.path.join(os.getcwd(), 'src'))
import engine
import adn

def _retornos_por_horizonte(df, h):
    ret = (df['Close'].shift(-h) / df['Close']) - 1
    df_h = df[['Regime', 'State']].copy()
    df_h['Return'] = ret
    return df_h.dropna(subset=['Return'])

def _celda_cola(retornos, lado, h, piso, percentil):
    n = len(retornos)
    if n == 0:
        return {"publicable": False, "motivo": "0 observaciones", "n": 0, "n_cola": 0, "n_efectivo": 0}
        
    if lado == "largo":
        var = np.percentile(retornos, percentil)
        cola = retornos[retornos <= var]
        es = cola.mean()
        err_std = cola.std() / np.sqrt(len(cola) / h) if len(cola) > 1 else 0
    else:
        var = np.percentile(retornos, 100 - percentil)
        cola = retornos[retornos >= var]
        var = -var
        es = -cola.mean()
        err_std = cola.std() / np.sqrt(len(cola) / h) if len(cola) > 1 else 0
        
    n_cola = len(cola)
    n_efectivo = n_cola // h
    
    if n_efectivo < piso:
        return {
            "publicable": False,
            "motivo": f"muestra efectiva insuficiente: {n_efectivo} observaciones, minimo {piso}",
            "n_cola": n_cola,
            "n_efectivo": n_efectivo
        }
        
    razon = es / var if var != 0 else float('inf')
    
    return {
        "var_pct": round(float(var * 100), 2),
        "es_pct": round(float(es * 100), 2),
        "razon_es_var": round(float(razon), 2),
        "n": n,
        "n_cola": n_cola,
        "n_efectivo": n_efectivo,
        "error_estandar": round(float(err_std * 100), 2),
        "publicable": True
    }

def riesgo_cola(df, horizontes=(1,2,3,5), percentil=5, piso_efectivo=20):
    res = {
        "percentil": percentil,
        "horizontes": list(horizontes),
        "piso_efectivo": piso_efectivo,
        "global": {},
        "por_regimen": {},
        "por_regimen_estado": {}
    }
    
    for h in horizontes:
        df_h = _retornos_por_horizonte(df, h)
        str_h = str(h)
        
        if str_h not in res["global"]: res["global"][str_h] = {}
        res["global"][str_h] = {
            "largo": _celda_cola(df_h['Return'], "largo", h, piso_efectivo, percentil),
            "corto": _celda_cola(df_h['Return'], "corto", h, piso_efectivo, percentil)
        }
        
        if "Regime" in df_h.columns and "State" in df_h.columns:
            for reg in ("BAJO", "MEDIO", "ALTO"):
                if reg not in res["por_regimen"]: res["por_regimen"][reg] = {}
                res["por_regimen"][reg][str_h] = {
                    "largo": _celda_cola(df_h[df_h['Regime'] == reg]['Return'], "largo", h, piso_efectivo, percentil),
                    "corto": _celda_cola(df_h[df_h['Regime'] == reg]['Return'], "corto", h, piso_efectivo, percentil)
                }
                
                for state in ("EXPANSIÓN", "CONTRACCIÓN"):
                    key_rs = f"{reg}|{state}"
                    if key_rs not in res["por_regimen_estado"]: res["por_regimen_estado"][key_rs] = {}
                    
                    df_rs = df_h[(df_h['Regime'] == reg) & (df_h['State'] == state)]
                    res["por_regimen_estado"][key_rs][str_h] = {
                        "largo": _celda_cola(df_rs['Return'], "largo", h, piso_efectivo, percentil),
                        "corto": _celda_cola(df_rs['Return'], "corto", h, piso_efectivo, percentil)
                    }
                    
    return res

available = engine.get_available_assets()
asset_path = next((a['path'] for a in available if a['name'] == 'BTCUSD'), None)
df = engine.fetch_data(asset_path)
df, ctx = adn.preparar_serie(df)

res = riesgo_cola(df)
print("BTCUSD H=5 ALTO|EXPANSIÓN Largo:", res["por_regimen_estado"]["ALTO|EXPANSIÓN"]["5"]["largo"])
print("BTCUSD H=5 ALTO Largo:", res["por_regimen"]["ALTO"]["5"]["largo"])
print("BTCUSD H=1 ALTO Largo:", res["por_regimen"]["ALTO"]["1"]["largo"])
