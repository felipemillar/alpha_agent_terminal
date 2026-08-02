import pandas as pd
import numpy as np
import os
import glob
import json
import config

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

def get_available_assets():
    """
    Lista todos los archivos CSV descargados por la skill de TradingView.
    Retorna una lista de diccionarios con el nombre a mostrar y la ruta.
    """
    csv_files = glob.glob(os.path.join(DATA_DIR, "*_historico.csv"))
    assets = []
    for file_path in csv_files:
        basename = os.path.basename(file_path)
        name = basename.replace("_historico.csv", "")
        assets.append({"name": name, "path": file_path})
    return sorted(assets, key=lambda x: x["name"])

def fetch_data(file_path: str) -> pd.DataFrame:
    """
    Lee los datos históricos desde el CSV local.
    """
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            raise ValueError(f"El archivo CSV {file_path} está vacío.")
        
        # Mapear columnas a formato estándar
        df = df.rename(columns={
            "datetime": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        })
        
        # Convertir a datetime y ordenar cronológicamente
        df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
        df = df.sort_values('Date').reset_index(drop=True)
        
        return df
    except Exception as e:
        raise RuntimeError(f"Error leyendo el archivo {file_path}: {str(e)}")

import kpis

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calcula el ATR delegando a la biblioteca de KPIs.
    """
    df = df.copy()
    df['ATR'] = kpis.calculate_atr(df, period)
    return df

def calculate_natr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el NATR delegando a la biblioteca de KPIs.
    """
    df = df.copy()
    df['NATR'] = kpis.calculate_natr(df)
    return df

def analyze_volatility(df: pd.DataFrame) -> dict:
    """
    Analiza la volatilidad actual en contexto histórico.
    Usa un lookback estricto de 6 meses (120 días operativos).
    """
    if 'NATR' not in df.columns:
        raise ValueError("El DataFrame debe contener la columna 'NATR'")
        
    valid_data = df.dropna(subset=['NATR'])
    
    lookback_period = 120
    if len(valid_data) > lookback_period:
        valid_data = valid_data.tail(lookback_period).copy()
    
    if len(valid_data) < 20:
        raise ValueError("No hay suficientes datos históricos (mínimo 20 días) para el percentil.")
        
    current_natr = valid_data['NATR'].iloc[-1]
    current_price = valid_data['Close'].iloc[-1]
    current_atr = valid_data['ATR'].iloc[-1]
    last_date = valid_data['Date'].iloc[-1]
    
    # Calcular expansión / contracción sobre el dataframe original para tener suficiente lookback
    exp_contra_series = kpis.calculate_expansion_contraction(df)
    current_exp_contra = exp_contra_series.iloc[-1]
    
    percentile_rank = (np.count_nonzero(valid_data['NATR'] < current_natr) / len(valid_data['NATR'])) * 100
    
    if percentile_rank <= 33.33:
        regime = "BAJO"
        color = "PLATA"
        hex_color = "#a4b7c1"
        alert = "Alerta de Asfixia / Mercado Plano"
        action = "Operar con 50% de riesgo. Priorizar reversión a la media. No esperar grandes recorridos."
    elif percentile_rank <= 66.66:
        regime = "MEDIO"
        color = "ACERO"
        hex_color = "#4a6984"
        alert = "Entorno Óptimo"
        action = "Estructura limpia. Ejecutar sistema tendencial estándar con riesgo normal."
    else:
        regime = "ALTO"
        color = "CRIMSON"
        hex_color = "#883030"
        alert = "Alerta de Ruido Extremo (Fat Tails)"
        action = "KILL SWITCH ACTIVADO. Prohibición total de operar hoy."

    # Calcular Exponente de Hurst H(t) segmentado por Regímenes de Volatilidad
    hurst_info = kpis.calculate_hurst_by_regime(df)

    # Calcular Eficiencia Estructural de Kaufman ER y Noise Factor
    kaufman_info = kpis.calculate_kaufman_metrics(df)

    # Calcular Z-Score de Retornos y Regla de Weissman (Serie Histórica Completa)
    zscore_info = kpis.calculate_zscore_metrics(df, window=None)


    # Calcular Plano Cartesiano 2D Hurst vs. Kaufman (Constelación Histórica Completa) para múltiples horizontes
    scatter2d_info_5d = kpis.calculate_hurst_kaufman_scatter(df, trajectory_days=None, window_days=5)
    scatter2d_info_14d = kpis.calculate_hurst_kaufman_scatter(df, trajectory_days=None, window_days=14)
    scatter2d_info_30d = kpis.calculate_hurst_kaufman_scatter(df, trajectory_days=None, window_days=30)
    
    scatter2d_info = {
        "5d": scatter2d_info_5d,
        "14d": scatter2d_info_14d,
        "30d": scatter2d_info_30d
    }



    return {
        "current_price": round(float(current_price), 2),
        "current_atr": round(float(current_atr), 4),
        "current_natr": round(float(current_natr), 4),
        "percentile": round(float(percentile_rank), 1),
        "regime": regime,
        "color": color,
        "hex_color": hex_color,
        "alert": alert,
        "action": action,
        "volatility_state": current_exp_contra,
        "hurst": hurst_info,
        "kaufman": kaufman_info,
        "zscore": zscore_info,
        "scatter_2d": scatter2d_info,
        "lookback_days": len(valid_data),
        "last_date": last_date.strftime("%Y-%m-%d")
    }






def run_pipeline(file_path: str, asset_name: str) -> dict:
    """
    Ejecuta el pipeline completo, calcula el estado y escribe el estado_dashboard.json
    para la sincronización con Antigravity en tiempo real.
    """
    df = fetch_data(file_path)
    df = calculate_atr(df)
    df = calculate_natr(df)
    result = analyze_volatility(df)
    result['ticker'] = asset_name
    
    # Escribir estado_dashboard.json para la sincronización con Antigravity
    estado_path = config.ESTADO_DASHBOARD_PATH
    estado = {
        "activo": asset_name,
        "ultimo_calculo": {
            "fecha": result["last_date"],
            "precio_cierre": result["current_price"],
            "atr_actual": result["current_atr"],
            "natr_actual": result["current_natr"],
            "regimen_volatilidad": result["regime"],
            "estado_volatilidad": result["volatility_state"]
        },
        "alerta": result["alert"],
        "mandato_qrt": result["action"]
    }
    
    try:
        with open(estado_path, "w") as f:
            json.dump(estado, f, indent=2)
    except Exception as e:
        print(f"Error escribiendo estado_dashboard.json: {str(e)}")
        
    return result

def analyze_gaps(df: pd.DataFrame) -> dict:
    """
    Analiza estadísticamente los gaps de apertura históricos en el dataframe.
    """
    df = df.copy()
    
    # Asegurarnos de tener ATR y NATR
    if 'ATR' not in df.columns:
        df['ATR'] = calculate_atr(df)['ATR']
    if 'NATR' not in df.columns:
        df['NATR'] = calculate_natr(df)['NATR']
        
    # Clasificar antes de dropna para preservar lookback de 120 días
    regime_series, _ = kpis.classify_regimes_full(df)
    state_series = kpis.calculate_expansion_contraction(df)
    
    df['Regime'] = regime_series
    df['State'] = state_series
    
    df = df.dropna(subset=['ATR', 'NATR', 'Regime', 'State']).reset_index(drop=True)
    
    points = []
    total_gaps = 0
    filled_gaps = 0
    
    # Estructura para agrupar por día de la semana
    day_stats = {
        0: {"total": 0, "filled": 0, "name": "Lunes"},
        1: {"total": 0, "filled": 0, "name": "Martes"},
        2: {"total": 0, "filled": 0, "name": "Miércoles"},
        3: {"total": 0, "filled": 0, "name": "Jueves"},
        4: {"total": 0, "filled": 0, "name": "Viernes"},
        5: {"total": 0, "filled": 0, "name": "Sábado"},
        6: {"total": 0, "filled": 0, "name": "Domingo"}
    }
    
    for i in range(1, len(df)):
        close_prev = df['Close'].iloc[i-1]
        open_curr = df['Open'].iloc[i]
        high_curr = df['High'].iloc[i]
        low_curr = df['Low'].iloc[i]
        close_curr = df['Close'].iloc[i]
        date_curr = df['Date'].iloc[i]
        natr_curr = df['NATR'].iloc[i]
        atr_curr = df['ATR'].iloc[i]
        regime_curr = df['Regime'].iloc[i]
        state_curr = df['State'].iloc[i]
        
        gap_size = open_curr - close_prev
        gap_pct = (gap_size / close_prev) * 100
        gap_atr = gap_size / atr_curr if atr_curr > 0 else 0
        
        # Ignorar mini gaps que son ruido (umbral absoluto de 0.05 ATR)
        if abs(gap_atr) < 0.05:
            continue
            
        # Determinar si se llenó en el día t
        filled = False
        if gap_size > 0:  # Gap Up
            if low_curr <= close_prev:
                filled = True
        elif gap_size < 0:  # Gap Down
            if high_curr >= close_prev:
                filled = True
                
        # --- KPI 1: Fill Depth (Profundidad de Retracement del Gap) ---
        # Gap UP:  (Open - Low) / gap_size   → cuánto retrocedió hacia el cierre anterior
        # Gap DOWN: (High - Open) / |gap_size| → cuánto subió hacia el cierre anterior
        if gap_size > 0:
            fill_depth = (open_curr - low_curr) / gap_size
        else:
            fill_depth = (high_curr - open_curr) / abs(gap_size)
        
        # --- KPI 2: Net Post-Gap Drift (Close-to-Close / ATR) ---
        net_drift = (close_curr - close_prev) / atr_curr if atr_curr > 0 else 0
        
        # --- KPI 3: Intraday Continuation Ratio (Cuerpo / Gap) ---
        icr = (close_curr - open_curr) / gap_size
                
        total_gaps += 1
        if filled:
            filled_gaps += 1
            
        day_of_week = date_curr.dayofweek
        if day_of_week in day_stats:
            day_stats[day_of_week]["total"] += 1
            if filled:
                day_stats[day_of_week]["filled"] += 1
                
        points.append({
            "date": date_curr.strftime("%Y-%m-%d"),
            "gap_size_pct": round(float(gap_pct), 3),
            "gap_size_atr": round(float(gap_atr), 3),
            "natr": round(float(natr_curr), 3),
            "filled": bool(filled),
            "direction": "UP" if gap_size > 0 else "DOWN",
            "regime": regime_curr,
            "state": state_curr,
            "fill_depth": round(float(fill_depth), 3),
            "net_drift": round(float(net_drift), 3),
            "icr": round(float(icr), 3)
        })
        
    fill_rate = (filled_gaps / total_gaps * 100) if total_gaps > 0 else 0
    avg_gap_atr = np.mean([abs(p["gap_size_atr"]) for p in points]) if points else 0
    avg_fill_depth = np.mean([p["fill_depth"] for p in points]) if points else 0
    avg_net_drift = np.mean([p["net_drift"] for p in points]) if points else 0
    avg_icr = np.mean([p["icr"] for p in points]) if points else 0
    
    # Formatear estadísticas por día de la semana
    weekly_stats = {}
    for dow, info in day_stats.items():
        if info["total"] > 0:
            weekly_stats[info["name"]] = round(info["filled"] / info["total"] * 100, 1)
        else:
            weekly_stats[info["name"]] = 0.0
            
    return {
        "summary": {
            "total_gaps": total_gaps,
            "filled_gaps": filled_gaps,
            "fill_rate": round(fill_rate, 1),
            "avg_gap_atr": round(float(avg_gap_atr), 3),
            "avg_fill_depth": round(float(avg_fill_depth), 3),
            "avg_net_drift": round(float(avg_net_drift), 3),
            "avg_icr": round(float(avg_icr), 3)
        },
        "weekly_fill_rates": weekly_stats,
        "points": points
    }
