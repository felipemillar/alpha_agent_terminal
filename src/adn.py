"""
Capa de caracterización del instrumento (ADN) — Pilar 1.

Implementa los indicadores P1.02 a P1.08 del catálogo y el procedimiento de
calibración por instrumento descrito en docs/CATALOGO_KPIS_ADN.md.

Separación de responsabilidades:
    kpis.py -> fórmulas de cálculo (ATR, NATR, régimen, estado)
    adn.py  -> caracterización estructural y reglas de publicación

Toda función devuelve el tamaño de muestra junto al resultado, de modo que las
reglas de publicación del catálogo puedan aplicarse aguas arriba.

Uso directo:
    python src/adn.py [ACTIVO]
"""

import numpy as np
import pandas as pd

import kpis

# ─── Parámetros de calibración ───────────────────────────────────────
RETORNO_IMPOSIBLE = 0.20        # descarta filas con error de decimal
APERTURA_SINTETICA_MAX = 0.10   # sobre esto la columna Open no es fiable
CORR_MINIMA_APERTURA = -0.20    # bajo esto hay ruido de medicion en Open
DIVERGENCIA_MAX_PP = 8.0        # divergencia admitida entre metodos N2 y N3
MIN_SESIONES_CELDA = 100        # celda minima de una matriz segmentada
BLOQUE_EPOCA_ANIOS = 5


# ═════════════════════════════════════════════════════════════════════
# Paso 1 — Saneamiento
# ═════════════════════════════════════════════════════════════════════

def sanear(df):
    """
    Descarta retornos imposibles y recorta la epoca inicial sin rango intradia.
    No elimina barras planas intermedias: hacerlo rompe la adyacencia entre
    sesiones y contamina todo calculo que use el cierre previo.
    """
    n_bruto = len(df)
    df = df.copy()

    con_rango = df["High"] > df["Low"]
    inicio_n2 = df.loc[con_rango, "Date"].min() if con_rango.any() else None
    if inicio_n2 is not None:
        df = df[df["Date"] >= inicio_n2]

    ret = df["Close"].pct_change()
    imposibles = int((ret.abs() > RETORNO_IMPOSIBLE).sum())
    df = df[~(ret.abs() > RETORNO_IMPOSIBLE)].reset_index(drop=True)

    return df, {
        "n_bruto": n_bruto,
        "n_saneado": len(df),
        "retornos_imposibles": imposibles,
    }


# ═════════════════════════════════════════════════════════════════════
# Paso 2 — Epoca efectiva por nivel de dato
# ═════════════════════════════════════════════════════════════════════

def epocas_efectivas(df):
    """
    Determina las tres fechas de inicio del instrumento (N1, N2, N3).

    N3 es el primer anio desde el cual la proporcion de aperturas sinteticas se
    mantiene bajo el umbral en TODOS los anios posteriores.
    """
    con_rango = df["High"] > df["Low"]
    sinteticas = df["Open"] == df["Close"].shift(1)
    por_anio = sinteticas.groupby(df["Date"].dt.year).mean()
    anios = sorted(por_anio.index)

    anio_n3 = None
    for i, y in enumerate(anios):
        if all(por_anio[a] < APERTURA_SINTETICA_MAX for a in anios[i:]):
            anio_n3 = int(y)
            break

    return {
        "n1_desde": str(df["Date"].min())[:10],
        "n2_desde": str(df.loc[con_rango, "Date"].min())[:10] if con_rango.any() else None,
        "n3_desde": anio_n3,
        "barras_planas_pct": round(float((~con_rango).mean()) * 100, 2),
        "aperturas_sinteticas_pct": round(float(sinteticas.mean()) * 100, 2),
    }


# ═════════════════════════════════════════════════════════════════════
# P1.06 — Volatilidad de Parkinson
# ═════════════════════════════════════════════════════════════════════

def varianza_parkinson(df, excluir_planas=True):
    """
    Varianza diaria intradia por el estimador de Parkinson: (1/4ln2)·ln(H/L)².

    Usa exclusivamente maximo y minimo, por lo que ignora el salto entre
    sesiones. Las barras planas aportan cero y sesgan el promedio a la baja:
    se excluyen del promedio sin eliminarlas de la serie.
    """
    log_hl = np.log(df["High"] / df["Low"])
    var = (1 / (4 * np.log(2))) * log_hl ** 2
    if excluir_planas:
        var = var[log_hl > 0]
    return {
        "varianza_diaria": float(var.mean()),
        "sigma_diaria_pct": round(float(np.sqrt(var.mean())) * 100, 4),
        "n": int(var.notna().sum()),
    }


# ═════════════════════════════════════════════════════════════════════
# P1.07 — Descomposicion fuera de sesion / intradia
# ═════════════════════════════════════════════════════════════════════

def descomposicion_sesion(df, epocas):
    """
    Fraccion de la varianza diaria que ocurre fuera de la sesion.

    Metodo N2 (Parkinson): 1 - var_intradia / var_total. No usa la apertura.
    Metodo N3 (apertura):  var_overnight / (var_overnight + var_intradia).

    El metodo N3 solo se publica si supera tres verificaciones: proporcion de
    aperturas sinteticas bajo umbral, correlacion entre ambas mitades del dia
    no marcadamente negativa (senal de ruido de medicion) y convergencia con
    el metodo N2.
    """
    var_cc = float(np.log(df["Close"] / df["Close"].shift(1)).dropna().var())
    var_intra = varianza_parkinson(df)["varianza_diaria"]
    share_n2 = 1 - var_intra / var_cc if var_cc > 0 else np.nan

    resultado = {
        "sigma_total_pct": round(float(np.sqrt(var_cc)) * 100, 4) if var_cc > 0 else np.nan,
        "share_n2_pct": round(share_n2 * 100, 1),
        "metodo_n2": "varianza total menos varianza de Parkinson",
        "n": int(len(df)),
    }

    anio_n3 = epocas.get("n3_desde")
    if anio_n3 is None:
        resultado["n3"] = {"disponible": False, "motivo": "sin epoca con apertura fiable"}
        return resultado

    sub = df[df["Date"].dt.year >= anio_n3]
    on = np.log(sub["Open"] / sub["Close"].shift(1)).dropna()
    idd = np.log(sub["Close"] / sub["Open"]).dropna()
    idx = on.index.intersection(idd.index)
    on, idd = on.loc[idx], idd.loc[idx]

    if len(on) < 250:
        resultado["n3"] = {"disponible": False, "motivo": "muestra insuficiente tras la epoca N3"}
        return resultado

    share_n3 = float(on.var() / (on.var() + idd.var()))
    corr = float(on.corr(idd))
    sint = float((sub["Open"] == sub["Close"].shift(1)).mean())
    divergencia = abs(share_n3 - share_n2) * 100

    fallos = []
    if sint > APERTURA_SINTETICA_MAX:
        fallos.append(f"aperturas sinteticas {sint*100:.1f}%")
    if corr < CORR_MINIMA_APERTURA:
        fallos.append(f"correlacion entre mitades {corr:+.2f}")
    if divergencia > DIVERGENCIA_MAX_PP:
        fallos.append(f"divergencia con N2 de {divergencia:.1f} pp")

    resultado["n3"] = {
        "disponible": len(fallos) == 0,
        "share_pct": round(share_n3 * 100, 1),
        "correlacion_mitades": round(corr, 3),
        "aperturas_sinteticas_pct": round(sint * 100, 2),
        "divergencia_pp": round(divergencia, 1),
        "desde": anio_n3,
        "n": int(len(on)),
    }
    if fallos:
        resultado["n3"]["motivo"] = "; ".join(fallos)
    return resultado


# ═════════════════════════════════════════════════════════════════════
# P1.01 — Distribucion del NATR y umbrales de regimen
# ═════════════════════════════════════════════════════════════════════

def umbrales_regimen(df):
    """
    Terciles empiricos incondicionales del NATR, con su prueba de estabilidad.

    Los umbrales son derivados: dependen de la muestra y deben publicarse con
    fecha y tamano. La estabilidad se estima recalculandolos sobre fracciones
    crecientes de la serie.
    """
    natr = df["NATR"].dropna()
    t33, t66 = float(natr.quantile(1 / 3)), float(natr.quantile(2 / 3))

    estabilidad = []
    for frac in (0.50, 0.70, 0.85):
        s = natr.iloc[: int(len(natr) * frac)]
        a, b = float(s.quantile(1 / 3)), float(s.quantile(2 / 3))
        estabilidad.append({
            "fraccion": frac,
            "desv_t33_pct": round((a / t33 - 1) * 100, 1),
            "desv_t66_pct": round((b / t66 - 1) * 100, 1),
        })

    q = natr.quantile([0.05, 0.25, 0.50, 0.75, 0.95])
    return {
        "t33": round(t33, 4),
        "t66": round(t66, 4),
        "distribucion": {f"p{int(k*100)}": round(float(v), 4) for k, v in q.items()},
        "media": round(float(natr.mean()), 4),
        "estabilidad": estabilidad,
        "n": int(len(natr)),
    }


# ═════════════════════════════════════════════════════════════════════
# P1.02 — Reparto de regimen por epoca
# ═════════════════════════════════════════════════════════════════════

def reparto_por_epoca(df, bloque=BLOQUE_EPOCA_ANIOS):
    """
    Proporcion de sesiones en cada regimen por bloque temporal, y NATR medio.

    El reparto global es 33/33/33 por construccion: la informacion sobre la no
    estacionariedad reside en su distribucion temporal.
    """
    t = df.dropna(subset=["NATR", "Regime"]).copy()
    t["bloque"] = (t["Date"].dt.year // bloque) * bloque

    filas = []
    for b, g in t.groupby("bloque"):
        if len(g) < MIN_SESIONES_CELDA:
            continue
        rep = g["Regime"].value_counts(normalize=True) * 100
        filas.append({
            "bloque": f"{int(b)}-{int(b)+bloque-1}",
            "n": int(len(g)),
            "natr_medio": round(float(g["NATR"].mean()), 4),
            "bajo_pct": round(float(rep.get("BAJO", 0)), 1),
            "medio_pct": round(float(rep.get("MEDIO", 0)), 1),
            "alto_pct": round(float(rep.get("ALTO", 0)), 1),
        })

    natr_hoy = float(t["NATR"].iloc[-1])
    ult = t[t["Date"] >= t["Date"].max() - pd.DateOffset(years=5)]["NATR"]
    return {
        "bloques": filas,
        "percentil_historia_completa": round(float((t["NATR"] < natr_hoy).mean()) * 100, 1),
        "percentil_ultimos_5a": round(float((ult < natr_hoy).mean()) * 100, 1),
    }


# ═════════════════════════════════════════════════════════════════════
# P1.03 — Distribucion de la razon de direccion
# ═════════════════════════════════════════════════════════════════════

def razon_direccion(df):
    """
    Distribucion de ATR(5)/ATR(14), la variable continua tras la etiqueta
    EXPANSION / CONTRACCION. El umbral universal es 1,00.
    """
    ratio = (kpis.calculate_atr(df, 5) / kpis.calculate_atr(df, 14)).dropna()
    q = ratio.quantile([0.05, 0.25, 0.50, 0.75, 0.95])
    counts, edges = np.histogram(ratio, bins=50)
    return {
        "distribucion": {f"p{int(k*100)}": round(float(v), 4) for k, v in q.items()},
        "histograma": {
            "counts": [int(c) for c in counts],
            "edges": [round(float(e), 4) for e in edges]
        },
        "mediana": round(float(ratio.median()), 4),
        "expansion_pct": round(float((ratio > 1).mean()) * 100, 1),
        "umbral": 1.0,
        "n": int(len(ratio)),
    }


# ═════════════════════════════════════════════════════════════════════
# P1.04 — Persistencia del estado direccional
# ═════════════════════════════════════════════════════════════════════

def persistencia_estado(df):
    """Distribucion de duracion de las rachas de expansion y de contraccion."""
    estado = df["State"].dropna()
    grupos = (estado != estado.shift()).cumsum()
    rachas = estado.groupby(grupos).agg(["first", "size"])

    salida = {}
    for st in estado.unique():
        s = rachas[rachas["first"] == st]["size"]
        if len(s) == 0:
            continue
        
        m = int(s.max())
        bins_arg = 50 if m > 50 else range(1, m + 2)
        counts, edges = np.histogram(s, bins=bins_arg)
        
        salida[str(st)] = {
            "rachas": int(len(s)),
            "mediana": round(float(s.median()), 1),
            "p80": round(float(s.quantile(0.80)), 1),
            "maxima": int(s.max()),
            "histograma": {
                "counts": [int(c) for c in counts],
                "edges": [round(float(e), 1) for e in edges]
            }
        }
    return salida


# ═════════════════════════════════════════════════════════════════════
# P1.05 — Dependencia entre nivel y direccion
# ═════════════════════════════════════════════════════════════════════

def dependencia_ejes(df):
    """
    Tabla de contingencia regimen x estado. Valida el diseno de la
    segmentacion cruzada: ninguna celda debe quedar bajo el minimo, y la
    dependencia entre ejes debe ser moderada.
    """
    sub = df.dropna(subset=["Regime", "State"])
    conteo = pd.crosstab(sub["Regime"], sub["State"])
    pct = pd.crosstab(sub["Regime"], sub["State"], normalize="index") * 100

    filas = []
    for reg in ("BAJO", "MEDIO", "ALTO"):
        if reg not in pct.index:
            continue
        fila = {"regimen": reg, "n": int(conteo.loc[reg].sum())}
        for col in pct.columns:
            fila[str(col)] = round(float(pct.loc[reg, col]), 1)
        filas.append(fila)

    minima = int(conteo.values.min()) if conteo.size else 0
    return {
        "reparto": filas,
        "celda_minima": minima,
        "celdas_validas": bool(minima >= MIN_SESIONES_CELDA),
        "minimo_exigido": MIN_SESIONES_CELDA,
    }


# ═════════════════════════════════════════════════════════════════════
# P1.08 — Razon de regimen a horizonte medio (VRR)
# ═════════════════════════════════════════════════════════════════════

def vrr(df, compresion=0.85, expansion=1.25):
    """Razon ATR(14)/ATR(50). Misma dimension que P1.03 en horizonte largo."""
    r = (kpis.calculate_atr(df, 14) / kpis.calculate_atr(df, 50)).dropna()
    return {
        "mediana": round(float(r.median()), 4),
        "actual": round(float(r.iloc[-1]), 4),
        "compresion_pct": round(float((r < compresion).mean()) * 100, 1),
        "expansion_pct": round(float((r > expansion).mean()) * 100, 1),
        "umbrales": {"compresion": compresion, "expansion": expansion},
        "n": int(len(r)),
    }


# ═════════════════════════════════════════════════════════════════════
# P2.01 y P2.02 — Momentos de la distribución
# ═════════════════════════════════════════════════════════════════════

def momentos_distribucion(df):
    """
    P2.01 - Asimetría y P2.02 - Curtosis.
    """
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
        for reg in ("BAJO", "MEDIO", "ALTO"):
            r_reg = df_ret[df_ret["Regime"] == reg]["Return"]
            if len(r_reg) > 0:
                res["asimetria"]["por_regimen"][reg] = {"valor": round(float(r_reg.skew()), 4), "n": len(r_reg)}
                res["curtosis"]["por_regimen"][reg] = {"valor": round(float(r_reg.kurt()), 4), "n": len(r_reg)}
            else:
                res["asimetria"]["por_regimen"][reg] = {"valor": None, "n": 0}
                res["curtosis"]["por_regimen"][reg] = {"valor": None, "n": 0}
                
    return res


# ═════════════════════════════════════════════════════════════════════
# P2.03 y P2.04 — Riesgo de cola accionable por lado
# ═════════════════════════════════════════════════════════════════════

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
    """
    P2.03 - Umbral de pérdida extrema (VaR) y P2.04 - Pérdida esperada (ES).
    """
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


# ═════════════════════════════════════════════════════════════════════
# Orquestador


# ═════════════════════════════════════════════════════════════════════

def preparar_serie(df):
    """
    Absorbe el preámbulo de calibración compartida.
    Sanea la serie, determina épocas y calcula las métricas base (NATR, Regime, State).
    Devuelve (df_calibrado, contexto) donde contexto agrupa periodo, saneamiento y epocas.
    Conserva la guarda de muestra mínima de 400 sesiones.
    """
    df, diag = sanear(df)
    if len(df) < 400:
        return None, {"error": "muestra insuficiente tras el saneamiento", "n": len(df)}
        
    epocas = epocas_efectivas(df)
    
    df["NATR"] = kpis.calculate_natr(df)
    df["Regime"], _ = kpis.classify_regimes_full(df)
    df["State"] = kpis.calculate_expansion_contraction(df)
    
    contexto = {
        "periodo": {"desde": str(df["Date"].min())[:10], "hasta": str(df["Date"].max())[:10]},
        "saneamiento": diag,
        "epocas_efectivas": epocas
    }
    return df, contexto

def caracterizar_pilar2(df):
    """
    Ejecuta el procedimiento de calibracion para el Pilar 2 del
    ADN del instrumento. Devuelve momentos de la distribucion y riesgo de cola.
    """
    df_cal, contexto = preparar_serie(df)
    if df_cal is None:
        return contexto

    momentos = momentos_distribucion(df_cal)
    
    return {
        "periodo": contexto["periodo"],
        "saneamiento": contexto["saneamiento"],
        "P2_01_asimetria": momentos["asimetria"],
        "P2_02_curtosis": momentos["curtosis"],
        "P2_03_04_riesgo_cola": riesgo_cola(df_cal),
    }

def caracterizar_pilar1(df):
    """
    Ejecuta el procedimiento de calibracion completo y devuelve el Pilar 1 del
    ADN del instrumento. Recibe el DataFrame crudo de engine.fetch_data().
    """
    df, contexto = preparar_serie(df)
    if df is None:
        return contexto

    return {
        "periodo": contexto["periodo"],
        "saneamiento": contexto["saneamiento"],
        "epocas_efectivas": contexto["epocas_efectivas"],
        "P1_01_umbrales_regimen": umbrales_regimen(df),
        "P1_02_reparto_por_epoca": reparto_por_epoca(df),
        "P1_03_razon_direccion": razon_direccion(df),
        "P1_04_persistencia_estado": persistencia_estado(df),
        "P1_05_dependencia_ejes": dependencia_ejes(df),
        "P1_06_parkinson": varianza_parkinson(df),
        "P1_07_descomposicion_sesion": descomposicion_sesion(df, contexto["epocas_efectivas"]),
        "P1_08_vrr": vrr(df),
    }


# ═════════════════════════════════════════════════════════════════════
# Salida legible
# ═════════════════════════════════════════════════════════════════════

def imprimir(nombre, a):
    if "error" in a:
        print(f"\n{nombre}: {a['error']} (n={a['n']})")
        return

    print("\n" + "=" * 78)
    print(f"ADN — PILAR 1 · {nombre}   {a['periodo']['desde']} a {a['periodo']['hasta']}")
    print("=" * 78)

    e, s = a["epocas_efectivas"], a["saneamiento"]
    print(f"\nCALIBRACION   {s['n_bruto']} sesiones brutas -> {s['n_saneado']} saneadas "
          f"({s['retornos_imposibles']} retornos imposibles)")
    print(f"              epocas: N1 {e['n1_desde']} · N2 {e['n2_desde']} · N3 {e['n3_desde']}")
    print(f"              barras planas {e['barras_planas_pct']}% · aperturas sinteticas {e['aperturas_sinteticas_pct']}%")

    u = a["P1_01_umbrales_regimen"]
    print(f"\nP1.01  UMBRALES DE REGIMEN (derivados, n={u['n']})")
    print(f"       t33 = {u['t33']}%   t66 = {u['t66']}%   NATR medio {u['media']}%")
    print(f"       distribucion NATR  " + " · ".join(f"{k} {v}%" for k, v in u["distribucion"].items()))
    print("       estabilidad  " + " · ".join(
        f"{int(x['fraccion']*100)}%: {x['desv_t33_pct']:+.1f}/{x['desv_t66_pct']:+.1f}%" for x in u["estabilidad"]))

    r = a["P1_02_reparto_por_epoca"]
    print(f"\nP1.02  REPARTO DE REGIMEN POR EPOCA")
    print("       bloque        n    NATR    BAJO   MEDIO    ALTO")
    for b in r["bloques"]:
        print(f"       {b['bloque']}  {b['n']:5d}  {b['natr_medio']:5.2f}%  {b['bajo_pct']:5.1f}%  "
              f"{b['medio_pct']:5.1f}%  {b['alto_pct']:5.1f}%")
    print(f"       percentil actual: {r['percentil_historia_completa']} sobre historia completa "
          f"vs {r['percentil_ultimos_5a']} sobre 5 anios")

    d = a["P1_03_razon_direccion"]
    print(f"\nP1.03  RAZON DE DIRECCION ATR(5)/ATR(14)   (umbral {d['umbral']})")
    print("       " + " · ".join(f"{k} {v}" for k, v in d["distribucion"].items()))
    print(f"       mediana {d['mediana']}   sesiones en expansion {d['expansion_pct']}%")

    print(f"\nP1.04  PERSISTENCIA DEL ESTADO DIRECCIONAL")
    for st, v in a["P1_04_persistencia_estado"].items():
        print(f"       {st:<12} {v['rachas']:4d} rachas · mediana {v['mediana']:.0f} · "
              f"p80 {v['p80']:.0f} · maxima {v['maxima']}")

    dep = a["P1_05_dependencia_ejes"]
    print(f"\nP1.05  DEPENDENCIA ENTRE NIVEL Y DIRECCION")
    for f in dep["reparto"]:
        extra = " · ".join(f"{k} {v}%" for k, v in f.items() if k not in ("regimen", "n"))
        print(f"       {f['regimen']:<7} n={f['n']:5d}   {extra}")
    print(f"       celda minima {dep['celda_minima']} sesiones -> "
          f"{'valida' if dep['celdas_validas'] else 'INSUFICIENTE'}")

    p = a["P1_06_parkinson"]
    dc = a["P1_07_descomposicion_sesion"]
    print(f"\nP1.06  PARKINSON   sigma intradia {p['sigma_diaria_pct']}%/dia (n={p['n']})")
    print(f"\nP1.07  DESCOMPOSICION FUERA DE SESION")
    print(f"       via N2 (Parkinson): {dc['share_n2_pct']}%")
    n3 = dc.get("n3", {})
    if n3.get("disponible"):
        print(f"       via N3 (apertura):  {n3['share_pct']}%  desde {n3['desde']} "
              f"(divergencia {n3['divergencia_pp']} pp · corr {n3['correlacion_mitades']:+.2f})")
    else:
        print(f"       via N3 (apertura):  NO DISPONIBLE — {n3.get('motivo', 'sin datos')}")

    v = a["P1_08_vrr"]
    print(f"\nP1.08  VRR ATR(14)/ATR(50)   mediana {v['mediana']} · actual {v['actual']} · "
          f"compresion {v['compresion_pct']}% · expansion {v['expansion_pct']}%")


if __name__ == "__main__":
    import sys

    import engine

    disponibles = {x["name"]: x["path"] for x in engine.get_available_assets()}
    objetivo = sys.argv[1:] or sorted(disponibles)
    for nombre in objetivo:
        if nombre not in disponibles:
            print(f"\n{nombre}: no encontrado en data/")
            continue
        imprimir(nombre, caracterizar_pilar1(engine.fetch_data(disponibles[nombre])))
        
        # P2 CLI
        p2 = caracterizar_pilar2(engine.fetch_data(disponibles[nombre]))
        if "error" in p2:
            print(f"PILAR 2 NO DISPONIBLE: {p2['error']}")
        else:
            print(f"\nPILAR 2: RIESGO DE COLA")
            print(f"P2.01 Asimetria global: {p2['P2_01_asimetria']['global']['valor']}")
            print(f"P2.02 Curtosis global:  {p2['P2_02_curtosis']['global']['valor']}")
            for reg in p2['P2_03_04_riesgo_cola']['por_regimen'].keys():
                largo_es = p2['P2_03_04_riesgo_cola']['por_regimen'][reg]['1']['largo'].get('es_pct')
                corto_es = p2['P2_03_04_riesgo_cola']['por_regimen'][reg]['1']['corto'].get('es_pct')
                print(f"      Regimen {reg:<5} ES Largo: {largo_es}% | ES Corto: {corto_es}%")

