"""
Prototipo del ADN DIRECCIONAL del instrumento (Volatility Desk).

Re-corta cada metrica por lado (largo / corto). La tesis a validar es que el
activo NO es simetrico: el peaje, la cola y el drift difieren segun el lado que
tome el trader, y esa asimetria es la parte accionable del ADN.

Uso: .venv/bin/python scratch/prototipo_adn_direccional.py [ACTIVO ...]
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import engine  # noqa: E402
import kpis  # noqa: E402

WARMUP = 120
MAX_ABS_RETURN = 0.20
UMBRAL_SINTETICO = 0.10  # sobre esto, la columna Open no es fiable


def inicio_apertura_fiable(df):
    """Primer anio desde el cual la apertura deja de ser copia del cierre previo."""
    sint = (df["Open"] == df["Close"].shift(1))
    por_anio = sint.groupby(df["Date"].dt.year).mean()
    anios = sorted(por_anio.index)
    for i, y in enumerate(anios):
        if all(por_anio[a] < UMBRAL_SINTETICO for a in anios[i:]):
            return y
    return None


def preparar(path):
    df = engine.fetch_data(path)

    # Saneamiento: epoca con rango intradia real + retornos imposibles.
    con_rango = df["High"] > df["Low"]
    if con_rango.any():
        df = df[df["Date"] >= df.loc[con_rango, "Date"].min()].copy()
    ret = df["Close"].pct_change()
    df = df[~(ret.abs() > MAX_ABS_RETURN)].reset_index(drop=True)

    anio_open = inicio_apertura_fiable(df)

    df["ATR"] = kpis.calculate_atr(df, 14)
    df["NATR"] = kpis.calculate_natr(df)
    df["Regime"], _ = kpis.classify_regimes_full(df)
    df["Ret"] = df["Close"].pct_change()
    df["ATR_prev"] = df["ATR"].shift(1)
    df["r_on"] = np.log(df["Open"] / df["Close"].shift(1))
    df["r_id"] = np.log(df["Close"] / df["Open"])
    return df.iloc[WARMUP:].reset_index(drop=True), anio_open


def bloque_sesgo(df):
    r = df["Ret"].dropna()
    alcistas = (r > 0).mean() * 100
    med_up = r[r > 0].mean() * 100
    med_dn = r[r < 0].mean() * 100
    return {
        "pct_alcistas": alcistas,
        "avg_up": med_up,
        "avg_dn": med_dn,
        "ratio_magnitud": abs(med_dn) / med_up,
        "drift_anual": ((1 + r.mean()) ** 252 - 1) * 100,
    }


def bloque_excursion(df, anio_open):
    """MAE y MFE por lado. Solo sobre el tramo con apertura fiable."""
    sub = df if anio_open is None else df[df["Date"].dt.year >= anio_open]
    sub = sub[sub["ATR_prev"] > 0]
    if len(sub) < 250:
        return None
    arriba = (sub["High"] - sub["Open"]) / sub["ATR_prev"]   # favorable largo / adverso corto
    abajo = (sub["Open"] - sub["Low"]) / sub["ATR_prev"]     # adverso largo / favorable corto
    return {
        "n": len(sub),
        "desde": int(sub["Date"].dt.year.min()),
        "largo_peaje": abajo.median(), "largo_peaje_p80": abajo.quantile(0.80),
        "largo_premio": arriba.median(),
        "corto_peaje": arriba.median(), "corto_peaje_p80": arriba.quantile(0.80),
        "corto_premio": abajo.median(),
        "ratio_peaje": arriba.median() / abajo.median() if abajo.median() else float("nan"),
    }


def bloque_colas(df):
    r = df["Ret"].dropna()
    var_izq, var_der = r.quantile(0.05), r.quantile(0.95)
    es_izq = r[r <= var_izq].mean() * 100
    es_der = r[r >= var_der].mean() * 100
    return {
        "es_izq": es_izq, "es_der": es_der,
        "asimetria": abs(es_izq) / es_der,
        "peor": r.min() * 100, "mejor": r.max() * 100,
    }


def bloque_sesion(df, anio_open):
    sub = df if anio_open is None else df[df["Date"].dt.year >= anio_open]
    on, idd = sub["r_on"].dropna(), sub["r_id"].dropna()
    if len(on) < 250:
        return None
    return {
        "on_acum": (np.exp(on.sum()) - 1) * 100,
        "id_acum": (np.exp(idd.sum()) - 1) * 100,
        "on_share_var": on.var() / (on.var() + idd.var()) * 100,
        "desde": int(sub["Date"].dt.year.min()),
    }


def bloque_por_regimen(df):
    out = {}
    for reg in ["BAJO", "MEDIO", "ALTO"]:
        s = df[df["Regime"] == reg]["Ret"].dropna()
        if len(s) < 100:
            continue
        out[reg] = {
            "n": len(s),
            "drift_dia": s.mean() * 100,
            "pct_alcistas": (s > 0).mean() * 100,
            "es_izq": s[s <= s.quantile(0.05)].mean() * 100,
            "es_der": s[s >= s.quantile(0.95)].mean() * 100,
        }
    return out


def informe(nombre, path):
    df, anio_open = preparar(path)
    print("\n" + "=" * 82)
    print(f"ADN DIRECCIONAL — {nombre}   ({str(df['Date'].min())[:10]} -> {str(df['Date'].max())[:10]}, {len(df)} sesiones)")
    if anio_open:
        print(f"   apertura fiable desde {anio_open}")
    print("=" * 82)

    s = bloque_sesgo(df)
    print(f"\nA. SESGO BASE   dias alcistas {s['pct_alcistas']:.1f}%  |  subida media {s['avg_up']:+.2f}%  "
          f"bajada media {s['avg_dn']:+.2f}%  (caida {s['ratio_magnitud']:.2f}x la subida)")
    print(f"                drift anualizado {s['drift_anual']:+.1f}%")

    e = bloque_excursion(df, anio_open)
    if e:
        print(f"\nB. EXCURSION POR LADO   (n={e['n']}, desde {e['desde']}, multiplos de ATR)")
        print(f"   LARGO   peaje {e['largo_peaje']:.2f} (p80 {e['largo_peaje_p80']:.2f})   premio {e['largo_premio']:.2f}")
        print(f"   CORTO   peaje {e['corto_peaje']:.2f} (p80 {e['corto_peaje_p80']:.2f})   premio {e['corto_premio']:.2f}")
        print(f"   -> el peaje del corto es {e['ratio_peaje']:.2f}x el del largo")

    c = bloque_colas(df)
    print(f"\nC. COLAS POR LADO   cola izquierda (mata largos) {c['es_izq']:+.2f}%  |  "
          f"cola derecha (mata cortos) {c['es_der']:+.2f}%")
    print(f"   -> la cola bajista pesa {c['asimetria']:.2f}x la alcista   (peor {c['peor']:+.2f}% / mejor {c['mejor']:+.2f}%)")

    ss = bloque_sesion(df, anio_open)
    if ss:
        print(f"\nD. DONDE SE GANA   (desde {ss['desde']})  overnight {ss['on_acum']:+.0f}% acumulado  |  "
              f"intradia {ss['id_acum']:+.0f}% acumulado")
        print(f"                   riesgo overnight: {ss['on_share_var']:.1f}% de la varianza")

    print("\nE. DIRECCION POR REGIMEN")
    print("   regimen   n     drift/dia   %alcistas   cola izq   cola der")
    for reg, v in bloque_por_regimen(df).items():
        print(f"   {reg:<8} {v['n']:5d}   {v['drift_dia']:+7.3f}%    {v['pct_alcistas']:5.1f}%    "
              f"{v['es_izq']:+7.2f}%   {v['es_der']:+7.2f}%")


if __name__ == "__main__":
    activos = sys.argv[1:] or ["XAUUSD", "USDCLP_PEPPERSTONE", "NASDAQ", "SP500", "BTCUSD"]
    disponibles = {a["name"]: a["path"] for a in engine.get_available_assets()}
    for nombre in activos:
        if nombre in disponibles:
            informe(nombre, disponibles[nombre])
        else:
            print(f"\n{nombre}: no encontrado en data/")
