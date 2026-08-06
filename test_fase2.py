import json
import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'src'))
import engine
import adn

def momentos_distribucion(df):
    ret = df['Close'].pct_change().dropna()
    df_ret = df.loc[ret.index].copy()
    df_ret['Return'] = ret
    
    res = {
        "asimetria": {
            "global": {"valor": round(float(ret.skew()), 4), "n": len(ret)}
        },
        "curtosis": {
            "nota": "exceso de curtosis (Fisher); el umbral de comparación es 0",
            "robustez": "baja",
            "global": {"valor": round(float(ret.kurt()), 4), "n": len(ret)}
        }
    }
    
    if "Regime" in df_ret.columns:
        res["asimetria"]["por_regimen"] = {}
        res["curtosis"]["por_regimen"] = {}
        for reg in ["BAJO", "MEDIO", "ALTO"]:
            r_reg = df_ret[df_ret["Regime"] == reg]["Return"]
            if len(r_reg) > 0:
                res["asimetria"]["por_regimen"][reg] = {"valor": round(float(r_reg.skew()), 4), "n": len(r_reg)}
                res["curtosis"]["por_regimen"][reg] = {"valor": round(float(r_reg.kurt()), 4), "n": len(r_reg)}
            else:
                res["asimetria"]["por_regimen"][reg] = {"valor": None, "n": 0}
                res["curtosis"]["por_regimen"][reg] = {"valor": None, "n": 0}
                
    return res

available = engine.get_available_assets()
asset_path = next((a['path'] for a in available if a['name'] == 'QQQ'), None)
df = engine.fetch_data(asset_path)
df, ctx = adn.preparar_serie(df)

res = momentos_distribucion(df)
print(json.dumps(res, indent=2))
