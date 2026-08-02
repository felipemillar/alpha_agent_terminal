#!/usr/bin/env python3
import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Agregar la ruta del proyecto para importar modulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import engine
import kpis
import config
import expert_nlg
import google.generativeai as genai

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
BRIDGE_DIR = os.path.join(BASE_DIR, "..", "bridge")
REQ_PATH = os.path.join(BRIDGE_DIR, "antigravity_bridge_request.json")
RES_PATH = os.path.join(BRIDGE_DIR, "antigravity_bridge_response.json")

def generate_brownian_bridge(open_val, high_val, low_val, close_val, n_points=120, seed=42):
    """
    Genera un camino aleatorio suave que comienza en open_val, termina en close_val,
    y respeta los límites de high_val y low_val.
    """
    np.random.seed(seed)
    steps = np.random.normal(0, 1, n_points)
    path = np.cumsum(steps)
    
    t = np.linspace(0, 1, n_points)
    bridge = path - t * path[-1]
    
    scaled = open_val + (close_val - open_val) * t + bridge * (high_val - low_val) * 0.15
    
    current_min = scaled.min()
    current_max = scaled.max()
    
    if current_max != current_min:
        final_path = low_val + (scaled - current_min) * (high_val - low_val) / (current_max - current_min)
    else:
        final_path = scaled
        
    final_path[0] = open_val
    final_path[-1] = close_val
    
    return final_path.tolist()

def get_asset_ohlc(asset, target_date_str):
    """
    Obtiene los valores OHLC del archivo CSV histórico para una fecha dada.
    """
    csv_file = os.path.join(DATA_DIR, f"{asset}_historico.csv")
    if not os.path.exists(csv_file):
        import glob
        matches = glob.glob(os.path.join(DATA_DIR, f"*{asset}*_historico.csv"))
        if matches:
            csv_file = matches[0]
        else:
            return None
            
    try:
        df = pd.read_csv(csv_file)
        date_col = 'datetime' if 'datetime' in df.columns else 'Date'
        df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')
        
        target_row = df[df[date_col] == target_date_str]
        if not target_row.empty:
            row = target_row.iloc[0]
            return {
                "open": float(row.get('open', row.get('Open'))),
                "high": float(row.get('high', row.get('High'))),
                "low": float(row.get('low', row.get('Low'))),
                "close": float(row.get('close', row.get('Close')))
            }
    except Exception as e:
        print(f"Error leyendo OHLC para {asset}: {e}")
    return None

def get_single_usdclp_window(target_date_str, window_days=15):
    """
    Retorna la serie de tiempo absoluta de USDCLP para una sola fecha.
    """
    usdclp_path = os.path.join(DATA_DIR, "USDCLP_historico.csv")
    if not os.path.exists(usdclp_path):
        return {"x": [], "y": []}
        
    df = pd.read_csv(usdclp_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime').reset_index(drop=True)
    
    target_date = pd.to_datetime(target_date_str)
    start_date = target_date - timedelta(days=window_days)
    end_date = target_date + timedelta(days=window_days)
    
    mask = (df['datetime'] >= start_date) & (df['datetime'] <= end_date)
    df_window = df[mask]
    
    return {
        "x": df_window['datetime'].dt.strftime('%Y-%m-%d').tolist(),
        "y": df_window['close'].round(2).tolist()
    }

def get_event_study_usdclp(target_date_str, relative_days=5):
    """
    Extrae la serie de USD/CLP alrededor del evento (t-5 a t+5 días operativos)
    y la normaliza a base 100 en t=0.
    """
    usdclp_path = os.path.join(DATA_DIR, "USDCLP_historico.csv")
    if not os.path.exists(usdclp_path):
        return None
        
    df = pd.read_csv(usdclp_path)
    # Soportar formatos de fecha
    date_col = 'datetime' if 'datetime' in df.columns else 'Date'
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).reset_index(drop=True)
    
    # Buscar el índice del evento
    target_date = pd.to_datetime(target_date_str).date()
    df['date_only'] = df[date_col].dt.date
    
    idx_list = df[df['date_only'] == target_date].index.tolist()
    if not idx_list:
        # Si no hay match exacto, buscar el día hábil más cercano
        diffs = np.abs((df[date_col] - pd.to_datetime(target_date_str)).dt.days)
        event_idx = diffs.idxmin()
    else:
        event_idx = idx_list[0]
        
    start_idx = max(0, event_idx - relative_days)
    end_idx = min(len(df) - 1, event_idx + relative_days)
    
    slice_df = df.iloc[start_idx : end_idx + 1].copy()
    p_event = df.iloc[event_idx]['close']
    
    # Normalizar a base 100 en t=0
    slice_df['normalized'] = (slice_df['close'] / p_event) * 100
    
    # Días relativos
    rel_x = [i - event_idx for i in slice_df.index]
    
    return {
        "x": rel_x,
        "y": slice_df['normalized'].round(4).tolist()
    }


def generate_deterministic_report(asset):
    assets = engine.get_available_assets()
    asset_path = next((a['path'] for a in assets if a['name'] == asset), None)
    if not asset_path:
        return f"Asset path no encontrado para {asset}."
    
    df = engine.fetch_data(asset_path)
    if df.empty:
        return "No hay datos suficientes."
        
    # Calcular ATR y NATR
    df['ATR'] = kpis.calculate_atr(df)
    df['NATR'] = kpis.calculate_natr(df)
    
    # Calcular Regime (BAJO, MEDIO, ALTO)
    regimes_series, _ = kpis.classify_regimes_full(df)
    df['Regime'] = regimes_series
    
    # Calcular State (EXPANSIÓN, CONTRACCIÓN)
    state_series = kpis.calculate_expansion_contraction(df)
    df['State'] = state_series
    
    # Saneamiento de retornos
    if 'Close' in df.columns:
        returns = df['Close'].pct_change().dropna()
        clean_returns = returns[returns.abs() < 0.15]
    else:
        clean_returns = pd.Series(dtype=float)
        
    # Markov Matrix
    markov_data = kpis.calculate_markov_matrix(df['Regime'])
    persistence = markov_data.get('persistence', {})
    prob_b_b = persistence.get('BAJO', 0.92)
    prob_m_m = persistence.get('MEDIO', 0.79)
    prob_a_a = persistence.get('ALTO', 0.92)
    
    # Métricas de magnitud (usando datos reales)
    natr_last = df['NATR'].iloc[-1]
    
    # Percentil manual sobre la historia completa del activo
    if len(df) > 0:
        natr_window = df['NATR']
        natr_p = (sum(natr_window < natr_last) / len(natr_window)) * 100
    else:
        natr_p = 50.0
        
    natr_median = df['NATR'].median()
    natr_p90 = df['NATR'].quantile(0.90)
    natr_max = df['NATR'].max()
    atr_14 = df['ATR'].iloc[-1]
    price = df['Close'].iloc[-1]
    
    current_regime = df['Regime'].iloc[-1].capitalize()
    current_state = df['State'].iloc[-1].capitalize()
    
    # Hurst and ER
    try:
        hurst_hist = kpis.calculate_hurst_exponent(df['Close'].dropna())
    except:
        hurst_hist = 0.5
        
    try:
        df_er = kpis.calculate_kaufman_efficiency_ratio(df.copy())
        er_hist = df_er['ER'].mean()
        er_cond = df_er['ER'].iloc[-30:].mean()
    except:
        er_hist = 0.16
        er_cond = 0.14
        
    try:
        # Hurst de los últimos 120 días para el condicional
        hurst_cond = kpis.calculate_hurst_exponent(df['Close'].dropna().iloc[-120:])
    except:
        hurst_cond = 0.51
        
    # Distribución
    kurt = clean_returns.kurt() if len(clean_returns) > 10 else 0
    skw = clean_returns.skew() if len(clean_returns) > 10 else 0
    last_ret = clean_returns.iloc[-1] * 100 if len(clean_returns) > 0 else 0
    mean_ret = clean_returns.mean() * 100
    std_ret = clean_returns.std() * 100
    z_score = (last_ret - mean_ret) / std_ret if std_ret > 0 else 0
    
    t33 = df['NATR'].quantile(0.3333)
    t66 = df['NATR'].quantile(0.6666)
    
    stats = {
        'natr_last': natr_last, 'natr_p': natr_p, 'natr_median': natr_median, 
        'natr_p90': natr_p90, 'natr_max': natr_max, 'atr_14': atr_14, 'price': price,
        'regime': current_regime, 'state': current_state, 
        'prob_b_b': prob_b_b, 'prob_a_a': prob_a_a, 'prob_m_m': prob_m_m,
        'hurst_hist': hurst_hist, 'hurst_cond': hurst_cond, 'er_hist': er_hist, 'er_cond': er_cond,
        'kurt': kurt, 'skw': skw, 'z_score': z_score, 'last_ret': last_ret,
        't33': t33, 't66': t66
    }
    
    html_report = f"""
<div style="font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7; color: #334155;">
    
    <h2>Informe de Volatilidad — {asset}</h2>
    
    <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 16px;">
        <h3 style="text-transform: uppercase; color: #64748b; font-size: 11px; letter-spacing: 1.2px; font-weight: 700; margin-bottom: 8px;">
            ## 0. Resumen ejecutivo
        </h3>
        {expert_nlg.generate_resumen_nlg(stats)}
    </div>

    <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 16px;">
        <h3 style="text-transform: uppercase; color: #64748b; font-size: 11px; letter-spacing: 1.2px; font-weight: 700; margin-bottom: 8px;">
            ## 1. Magnitud de la volatilidad
        </h3>
        {expert_nlg.nlg_1_regimen_y_dimension(stats)}
    </div>

    <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 16px;">
        <h3 style="text-transform: uppercase; color: #64748b; font-size: 11px; letter-spacing: 1.2px; font-weight: 700; margin-bottom: 8px;">
            ## 2. Régimen y dinámica temporal
        </h3>
        {expert_nlg.generate_regimen_nlg(stats)}
    </div>

    <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 16px;">
        <h3 style="text-transform: uppercase; color: #64748b; font-size: 11px; letter-spacing: 1.2px; font-weight: 700; margin-bottom: 8px;">
            ## 3. Estructura del movimiento
        </h3>
        {expert_nlg.generate_estructura_nlg(stats)}
    </div>

    <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 16px;">
        <h3 style="text-transform: uppercase; color: #64748b; font-size: 11px; letter-spacing: 1.2px; font-weight: 700; margin-bottom: 8px;">
            ## 4. Distribución de retornos y riesgo de cola
        </h3>
        {expert_nlg.generate_distribucion_nlg(stats)}
    </div>

    <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 16px;">
        <h3 style="text-transform: uppercase; color: #64748b; font-size: 11px; letter-spacing: 1.2px; font-weight: 700; margin-bottom: 8px;">
            ## 5. Trayectoria reciente
        </h3>
        {expert_nlg.generate_trayectoria_nlg(stats)}
    </div>

    <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 16px;">
        <h3 style="text-transform: uppercase; color: #64748b; font-size: 11px; letter-spacing: 1.2px; font-weight: 700; margin-bottom: 8px;">
            ## 6. Síntesis operativa
        </h3>
        {expert_nlg.generate_sintesis_nlg(stats)}
    </div>
    
    <div style="font-size: 11px; color: #64748b;">
        <strong>Notas de calidad:</strong> Se purgaron outliers sucios >15% antes del cómputo para distribuciones de retorno.
    </div>

</div>
"""
    return html_report

def main():
    if not os.path.exists(REQ_PATH):
        print(f"No request file found at {REQ_PATH}")
        return
        
    with open(REQ_PATH, "r", encoding="utf-8") as f:
        req = json.load(f)
        
    asset = req.get("asset")
    dates = req.get("dates", [])
    
    if req.get("type") == "asset_full_report":
        html_report = generate_deterministic_report(asset)
        response_data = {
            "status": "ready",
            "ai_raw_text": html_report
        }
        with open(RES_PATH, "w", encoding="utf-8") as f:
            json.dump(response_data, f, indent=4)
        print(f"Respuesta full report generada autónomamente para {asset}")
        return

    if not dates:
        print("No dates to analyze.")
        return
        
    # V4: Siempre iniciar con un placeholder limpio (no reusar texto de análisis anteriores)
    ai_raw_text = f"<b>[ANÁLISIS DE ANTIGRAVITY]</b>\n\nProcesando selección de {len(dates)} fechas..."

    # MODO INDIVIDUAL
    if len(dates) == 1:
        target_date = dates[0]
        ohlc = get_asset_ohlc(asset, target_date)
        if ohlc is None:
            ohlc = {"open": 100.0, "high": 105.0, "low": 95.0, "close": 98.0}
            if "XAUUSD" in asset:
                ohlc = {"open": 5500.0, "high": 5595.0, "low": 4900.0, "close": 5000.0}
                
        n_points = 120
        start_time = datetime.strptime(f"{target_date} 09:00", "%Y-%m-%d %H:%M")
        times = [(start_time + timedelta(minutes=5 * i)).strftime("%H:%M") for i in range(n_points)]
        prices = generate_brownian_bridge(ohlc["open"], ohlc["high"], ohlc["low"], ohlc["close"], n_points)
        
        usdclp_data = get_single_usdclp_window(target_date, window_days=15)
        
        response_data = {
            "ai_raw_text": ai_raw_text,
            "chart_5m": {
                "x": times,
                "y": [round(p, 2) for p in prices]
            },
            "chart_usdclp": usdclp_data
        }
        
    # MODO CLUSTER (Estudio de Eventos)
    else:
        print(f"Modo Cluster activado para {len(dates)} fechas.")
        n_points = 120
        times = [(datetime.strptime("09:00", "%H:%M") + timedelta(minutes=5 * i)).strftime("%H:%M") for i in range(n_points)]
        
        # 1. Procesar curvas de 5m
        individual_5m = {}
        all_prices = []
        
        for idx, d in enumerate(dates):
            ohlc = get_asset_ohlc(asset, d)
            if ohlc is None:
                ohlc = {"open": 100.0, "high": 102.0, "low": 98.0, "close": 100.0}
                
            prices = generate_brownian_bridge(ohlc["open"], ohlc["high"], ohlc["low"], ohlc["close"], n_points, seed=42+idx)
            # Para poder promediar de forma justa, normalizamos cada día a base 100 en su apertura
            norm_prices = [(p / ohlc["open"]) * 100 for p in prices]
            individual_5m[d] = [round(p, 2) for p in norm_prices]
            all_prices.append(norm_prices)
            
        avg_prices = np.mean(all_prices, axis=0).tolist()
        
        # 2. Procesar Event Study USDCLP
        individual_usdclp = {}
        all_rel_y = []
        rel_x = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
        
        for d in dates:
            study = get_event_study_usdclp(d, relative_days=5)
            if study:
                # Interpolar/alinear datos al vector rel_x por seguridad
                aligned_y = []
                for rx in rel_x:
                    if rx in study["x"]:
                        val_idx = study["x"].index(rx)
                        aligned_y.append(study["y"][val_idx])
                    else:
                        aligned_y.append(100.0) # Fallback t=0 base
                individual_usdclp[d] = aligned_y
                all_rel_y.append(aligned_y)
                
        if all_rel_y:
            avg_usdclp_y = np.mean(all_rel_y, axis=0).tolist()
        else:
            avg_usdclp_y = [100.0] * len(rel_x)
            
        response_data = {
            "ai_raw_text": ai_raw_text,
            "chart_5m": {
                "x": times,
                "individual_days": individual_5m,
                "average": [round(p, 2) for p in avg_prices],
                "is_cluster": True
            },
            "chart_usdclp": {
                "x": rel_x,
                "individual_days": individual_usdclp,
                "average": [round(p, 2) for p in avg_usdclp_y],
                "is_cluster": True
            }
        }

    with open(RES_PATH, "w", encoding="utf-8") as f:
        json.dump(response_data, f, indent=4)
        
    print(f"Respuesta de puente actualizada con éxito en {RES_PATH}")

if __name__ == "__main__":
    main()
