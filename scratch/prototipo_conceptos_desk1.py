"""
Prototipo de los 5 conceptos nuevos del Volatility Desk (pestana 1).

No modifica src/. Solo valida que los conceptos produzcan numeros informativos
sobre los datos reales antes de integrarlos en src/kpis.py.

Uso: .venv/bin/python scratch/prototipo_conceptos_desk1.py [ACTIVO ...]
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import engine  # noqa: E402
import kpis  # noqa: E402

WARMUP = 120          # sesiones que exige la clasificacion de regimen
MAX_ABS_RETURN = 0.20  # filtro de decimal corrupto (spec seccion 8)


def sanear(df):
    """Aplica los requisitos de calidad y devuelve (df_limpio, diagnostico)."""
    n_bruto = len(df)

    # Epoca efectiva: primera barra con rango intradia real (High > Low).
    con_rango = df["High"] > df["Low"]
    inicio_efectivo = df.loc[con_rango, "Date"].min() if con_rango.any() else None
    df = df[df["Date"] >= inicio_efectivo].copy() if inicio_efectivo is not None else df.copy()

    # Filtro de retornos imposibles (decimales corruptos).
    ret = df["Close"].pct_change()
    corruptas = int((ret.abs() > MAX_ABS_RETURN).sum())
    df = df[~(ret.abs() > MAX_ABS_RETURN)].copy().reset_index(drop=True)

    return df, {
        "n_bruto": n_bruto,
        "n_limpio": len(df),
        "inicio_efectivo": inicio_efectivo,
        "barras_descartadas": n_bruto - len(df),
        "filas_corruptas": corruptas,
    }


def preparar(df):
    """Anade ATR, NATR, regimen y estado usando el motor existente."""
    df["ATR"] = kpis.calculate_atr(df, 14)
    df["NATR"] = kpis.calculate_natr(df)
    df["Regime"], _ = kpis.classify_regimes_full(df)
    df["State"] = kpis.calculate_expansion_contraction(df)
    df["Ret"] = df["Close"].pct_change()
    # ATR previo: evita mirar el futuro al normalizar la sesion en curso.
    df["ATR_prev"] = df["ATR"].shift(1)
    return df.iloc[WARMUP:].copy().reset_index(drop=True)


# --- Concepto 1: excursion adversa tipica -----------------------------------
def excursion_adversa(df):
    ok = df["ATR_prev"] > 0
    largo = ((df["Open"] - df["Low"]) / df["ATR_prev"])[ok]
    corto = ((df["High"] - df["Open"]) / df["ATR_prev"])[ok]
    out = {
        "mae_largo_mediana": largo.median(),
        "mae_largo_p80": largo.quantile(0.80),
        "mae_corto_mediana": corto.median(),
        "mae_corto_p80": corto.quantile(0.80),
        "n": int(ok.sum()),
        "por_regimen": {},
    }
    for reg in ["BAJO", "MEDIO", "ALTO"]:
        m = ok & (df["Regime"] == reg)
        if m.sum() < 30:
            continue
        serie = ((df["Open"] - df["Low"]) / df["ATR_prev"])[m]
        out["por_regimen"][reg] = (serie.median(), serie.quantile(0.80), int(m.sum()))
    return out


# --- Concepto 2: descomposicion overnight vs intradia ------------------------
def descomposicion_riesgo(df):
    r_on = np.log(df["Open"] / df["Close"].shift(1)).dropna()
    r_id = np.log(df["Close"] / df["Open"]).dropna()
    idx = r_on.index.intersection(r_id.index)
    r_on, r_id = r_on.loc[idx], r_id.loc[idx]
    r_total = r_on + r_id

    var_on, var_id, var_tot = r_on.var(), r_id.var(), r_total.var()
    aperturas_sinteticas = float((df["Open"] == df["Close"].shift(1)).mean())
    return {
        "share_overnight": var_on / (var_on + var_id),
        "sigma_on_pct": r_on.std() * 100,
        "sigma_id_pct": r_id.std() * 100,
        "sigma_total_pct": r_total.std() * 100,
        "covarianza_share": (var_tot - var_on - var_id) / var_tot,
        "aperturas_sinteticas": aperturas_sinteticas,
    }


# --- Concepto 3: vida media del shock ---------------------------------------
def vida_media_shock(df, lookback=120):
    """
    Sesiones desde que el NATR entra en su decil superior MOVIL hasta que vuelve
    a su mediana MOVIL. El umbral debe ser local: con un umbral global sobre una
    serie no estacionaria, epocas enteras quedan por encima y la duracion medida
    deja de ser un shock (ver concepto 5).
    """
    tmp = df.dropna(subset=["NATR"]).reset_index(drop=True)
    p90 = tmp["NATR"].rolling(lookback).quantile(0.90)
    med = tmp["NATR"].rolling(lookback).quantile(0.50)
    v, u, m = tmp["NATR"].values, p90.values, med.values

    duraciones, picos, i = [], [], lookback + 1
    while i < len(v):
        if not (np.isnan(u[i]) or np.isnan(u[i - 1])) and v[i] > u[i] and v[i - 1] <= u[i - 1]:
            j, pico = i, v[i]
            while j < len(v) and (np.isnan(m[j]) or v[j] > m[j]):
                pico = max(pico, v[j])
                j += 1
            if j < len(v):
                duraciones.append(j - i)
                picos.append(pico)
            i = j
        i += 1
    if len(duraciones) < 3:
        return None
    d = pd.Series(duraciones)
    return {
        "episodios": len(d),
        "mediana": d.median(),
        "p80": d.quantile(0.80),
        "max": d.max(),
        "umbral_natr": float(np.nanmean(u)),
        "natr_mediano": float(np.nanmean(m)),
        "pico_medio": float(np.mean(picos)),
    }


# --- Concepto 4: la cola en dinero (VaR / expected shortfall) ---------------
def cola_en_dinero(df, regimen=None):
    sub = df if regimen is None else df[df["Regime"] == regimen]
    r = sub["Ret"].dropna()
    if len(r) < 100:
        return None
    var5 = r.quantile(0.05)
    cola = r[r <= var5]
    peor_idx = r.idxmin()
    return {
        "n": len(r),
        "var5_pct": var5 * 100,
        "es5_pct": cola.mean() * 100,
        "peor_pct": r.min() * 100,
        "peor_fecha": str(df.loc[peor_idx, "Date"])[:10],
        "ratio_es_var": cola.mean() / var5,
    }


# --- Concepto 5: epoca de referencia ----------------------------------------
def epoca_referencia(df):
    tmp = df.dropna(subset=["NATR"]).copy()
    tmp["bloque"] = (tmp["Date"].dt.year // 5) * 5
    g = tmp.groupby("bloque")["NATR"].agg(["mean", "std", "count"])
    g = g[g["count"] >= 100]

    natr_hoy = tmp["NATR"].iloc[-1]
    pct_total = (tmp["NATR"] < natr_hoy).mean() * 100
    ult5 = tmp[tmp["Date"] >= tmp["Date"].max() - pd.DateOffset(years=5)]["NATR"]
    pct_5y = (ult5 < natr_hoy).mean() * 100
    return {"bloques": g, "natr_hoy": natr_hoy, "pct_total": pct_total, "pct_5y": pct_5y}


def informe(nombre, path):
    df = engine.fetch_data(path)
    df, diag = sanear(df)
    if len(df) < WARMUP + 300:
        print(f"\n{nombre}: muestra insuficiente tras el saneamiento ({len(df)}).")
        return
    df = preparar(df)

    print("\n" + "=" * 78)
    print(f"{nombre}   |   {str(df['Date'].min())[:10]} -> {str(df['Date'].max())[:10]}   ({len(df)} sesiones utiles)")
    print("=" * 78)
    print(f"  Saneamiento: {diag['n_bruto']} brutas -> {diag['n_limpio']} tras epoca efectiva "
          f"({str(diag['inicio_efectivo'])[:10]}); {diag['filas_corruptas']} filas con |ret| > 20%")

    e = excursion_adversa(df)
    print("\n[1] EXCURSION ADVERSA TIPICA (multiplos de ATR previo)")
    print(f"  Largo  mediana {e['mae_largo_mediana']:.2f} ATR | p80 {e['mae_largo_p80']:.2f} ATR")
    print(f"  Corto  mediana {e['mae_corto_mediana']:.2f} ATR | p80 {e['mae_corto_p80']:.2f} ATR")
    for reg, (med, p80, n) in e["por_regimen"].items():
        print(f"    regimen {reg:<6} mediana {med:.2f} | p80 {p80:.2f}  (n={n})")

    d = descomposicion_riesgo(df)
    print("\n[2] DESCOMPOSICION DEL RIESGO")
    print(f"  Overnight {d['share_overnight']*100:.1f}% de la varianza | sigma_on {d['sigma_on_pct']:.2f}% "
          f"vs sigma_intradia {d['sigma_id_pct']:.2f}%")
    print(f"  Aperturas identicas al cierre previo: {d['aperturas_sinteticas']*100:.1f}%")

    s = vida_media_shock(df)
    print("\n[3] VIDA MEDIA DEL SHOCK DE VOLATILIDAD")
    if s:
        print(f"  {s['episodios']} episodios sobre p90 (NATR {s['umbral_natr']:.2f}%) -> vuelta a la mediana "
              f"({s['natr_mediano']:.2f}%)")
        print(f"  Mediana {s['mediana']:.0f} sesiones | p80 {s['p80']:.0f} | maximo {s['max']:.0f}")

    print("\n[4] LA COLA EN DINERO (retorno diario)")
    for reg in [None, "ALTO", "BAJO"]:
        c = cola_en_dinero(df, reg)
        if not c:
            continue
        etiqueta = "GLOBAL" if reg is None else f"reg. {reg}"
        print(f"  {etiqueta:<10} VaR5 {c['var5_pct']:+.2f}% | ES5 {c['es5_pct']:+.2f}% "
              f"({c['ratio_es_var']:.2f}x el VaR) | peor {c['peor_pct']:+.2f}% ({c['peor_fecha']})  n={c['n']}")

    ep = epoca_referencia(df)
    print("\n[5] EPOCA DE REFERENCIA (NATR medio por quinquenio)")
    for bloque, row in ep["bloques"].iterrows():
        barra = "#" * int(round(row["mean"] / ep["bloques"]["mean"].max() * 40))
        print(f"  {int(bloque)}-{int(bloque)+4}  {row['mean']:5.2f}%  {barra}")
    print(f"  NATR actual {ep['natr_hoy']:.2f}% -> percentil {ep['pct_total']:.0f} sobre historia completa "
          f"vs percentil {ep['pct_5y']:.0f} sobre los ultimos 5 anos")


if __name__ == "__main__":
    activos = sys.argv[1:] or ["XAUUSD", "USDCLP_PEPPERSTONE", "NASDAQ", "SP500", "BTCUSD"]
    disponibles = {a["name"]: a["path"] for a in engine.get_available_assets()}
    for nombre in activos:
        if nombre not in disponibles:
            print(f"\n{nombre}: no encontrado en data/")
            continue
        informe(nombre, disponibles[nombre])
