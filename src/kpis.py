import numpy as np
import pandas as pd

def calculate_atr(df, period=14):
    """
    Calcula el Average True Range (ATR) clásico usando suavizado de Wilder.
    Requiere que el DataFrame tenga las columnas 'High', 'Low' y 'Close'.
    """
    df = df.copy()
    df['Prev_Close'] = df['Close'].shift(1)
    df['TR1'] = df['High'] - df['Low']
    df['TR2'] = abs(df['High'] - df['Prev_Close'])
    df['TR3'] = abs(df['Low'] - df['Prev_Close'])
    df['TR'] = df[['TR1', 'TR2', 'TR3']].max(axis=1)
    df['ATR'] = df['TR'].ewm(alpha=1/period, adjust=False).mean()
    return df['ATR']

def calculate_natr(df, period=14):
    """
    Calcula el Normalized Average True Range (NATR) expresado en porcentaje.
    NATR = (ATR(period) / Close) * 100
    """
    atr = calculate_atr(df, period)
    return (atr / df['Close']) * 100

def calculate_returns(df):
    """
    Calcula el retorno diario en porcentaje de base simple.
    """
    prev_close = df['Close'].shift(1)
    return ((df['Close'] - prev_close) / prev_close) * 100

def calculate_volatility_zscore(natr_series, lookback=120):
    """
    Calcula el Z-Score del NATR sobre una ventana móvil.
    Mide a cuántas desviaciones estándar se encuentra la volatilidad actual de su media.
    Útil para detectar compresión extrema (< -1.5) o expansión extrema (> 1.5).
    """
    rolling_mean = natr_series.rolling(window=lookback).mean()
    rolling_std = natr_series.rolling(window=lookback).std()
    return (natr_series - rolling_mean) / rolling_std

def calculate_parkinson_volatility(df, window=20):
    """
    Calcula la Volatilidad de Parkinson, que utiliza los precios Máximo y Mínimo.
    Es un estimador de volatilidad más eficiente que la desviación estándar de cierres simples.
    Retorna la volatilidad histórica anualizada (asumiendo 252 días de trading).
    """
    log_hl = np.log(df['High'] / df['Low'])
    variance = (1 / (4 * np.log(2))) * (log_hl ** 2)
    rolling_var = variance.rolling(window=window).mean()
    return np.sqrt(rolling_var * 252) * 100

def calculate_kaufman_efficiency_ratio(df, window=10):
    """
    Calcula el Efficiency Ratio (ER) de Kaufman.
    Compara el movimiento neto del precio con la suma de los movimientos diarios absolutos.
    ER = |Cierre(t) - Cierre(t-n)| / Suma(|Cierre(i) - Cierre(i-1)|) para i de t-n a t.
    Valores cercanos a 1 indican una tendencia limpia y sin ruido (eficiente).
    Valores cercanos a 0 indican un rango plano con mucho ruido.
    """
    df = df.copy()
    df['Prev_Close'] = df['Close'].shift(1)
    df['Abs_Diff'] = abs(df['Close'] - df['Prev_Close'])
    
    net_change = abs(df['Close'] - df['Close'].shift(window))
    sum_changes = df['Abs_Diff'].rolling(window=window).sum()
    
    # Evitar división por cero
    return np.where(sum_changes > 0, net_change / sum_changes, 0)

def get_streak_metrics(df, regime_col='Regime', target_regime='BAJO'):
    """
    Analiza y retorna un listado detallado de todas las rachas consecutivas 
    de un régimen de volatilidad específico dentro del DataFrame histórico.
    Calcula además el máximo downswing y upswing en el periodo de cada racha.
    """
    streaks = []
    current_streak = 0
    start_idx = None
    
    # Asegurarse de que esté ordenado y con índice limpio
    df_sorted = df.sort_values('Date').reset_index(drop=True)
    
    for idx, row in df_sorted.iterrows():
        if row[regime_col] == target_regime:
            if current_streak == 0:
                start_idx = idx
            current_streak += 1
        else:
            if current_streak > 0:
                end_idx = idx - 1
                start_date = df_sorted.loc[start_idx, 'Date']
                end_date = df_sorted.loc[end_idx, 'Date']
                start_close = df_sorted.loc[start_idx, 'Close']
                end_close = df_sorted.loc[end_idx, 'Close']
                pct_change = ((end_close - start_close) / start_close) * 100
                
                # Extraer sub-dataframe de la racha para upswing/downswing
                df_streak = df_sorted.loc[start_idx:end_idx]
                max_high = df_streak['High'].max()
                min_low = df_streak['Low'].min()
                
                upswing = ((max_high - start_close) / start_close) * 100
                downswing = ((min_low - start_close) / start_close) * 100
                
                streaks.append({
                    "duration": current_streak,
                    "start_date": start_date if isinstance(start_date, str) else start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date if isinstance(end_date, str) else end_date.strftime("%Y-%m-%d"),
                    "start_price": float(start_close),
                    "end_price": float(end_close),
                    "change": float(pct_change),
                    "upswing": float(upswing),
                    "downswing": float(downswing)
                })
                current_streak = 0
                start_idx = None
                
    # Procesar última si quedó abierta al final
    if current_streak > 0:
        end_idx = len(df_sorted) - 1
        start_date = df_sorted.loc[start_idx, 'Date']
        end_date = df_sorted.loc[end_idx, 'Date']
        start_close = df_sorted.loc[start_idx, 'Close']
        end_close = df_sorted.loc[end_idx, 'Close']
        pct_change = ((end_close - start_close) / start_close) * 100
        
        # Extraer sub-dataframe de la racha
        df_streak = df_sorted.loc[start_idx:end_idx]
        max_high = df_streak['High'].max()
        min_low = df_streak['Low'].min()
        
        upswing = ((max_high - start_close) / start_close) * 100
        downswing = ((min_low - start_close) / start_close) * 100
        
        streaks.append({
            "duration": current_streak,
            "start_date": start_date if isinstance(start_date, str) else start_date.strftime("%Y-%m-%d"),
            "end_date": end_date if isinstance(end_date, str) else end_date.strftime("%Y-%m-%d"),
            "start_price": float(start_close),
            "end_price": float(end_close),
            "change": float(pct_change),
            "upswing": float(upswing),
            "downswing": float(downswing)
        })
        
    return pd.DataFrame(streaks)

def calculate_expansion_contraction(df):
    """
    Calcula el estado de volatilidad basado en el cruce de ATR de 5 y 14 periodos.
    Retorna una Serie con valores 'EXPANSIÓN' (ATR 5 > ATR 14) o 'CONTRACCIÓN' (ATR 5 <= ATR 14).
    """
    df = df.copy()
    atr5 = calculate_atr(df, period=5)
    atr14 = calculate_atr(df, period=14)
    # np.where maneja la comparación por elemento de forma vectorizada en Pandas/Numpy
    status = np.where(atr5 > atr14, "EXPANSIÓN", "CONTRACCIÓN")
    return pd.Series(status, index=df.index)

def classify_regimes_full(df):
    """
    Clasifica el régimen de volatilidad de cada fila del DataFrame usando el percentil global
    de toda la historia disponible del activo.
    Retorna dos pd.Series: (regimes, colors)
    """
    df = df.copy()
    if 'NATR' not in df.columns:
        # Importación local para evitar dependencia circular si se requiere
        import kpis
        df['NATR'] = kpis.calculate_natr(df)
        
    # Calcular percentil global
    percentiles = df['NATR'].rank(pct=True) * 100
    
    # Asignar regímenes usando np.select
    conditions = [
        percentiles <= 33.33,
        percentiles <= 66.66,
        percentiles > 66.66
    ]
    
    regime_choices = ["BAJO", "MEDIO", "ALTO"]
    color_choices = ["#FFC107", "#28A745", "#DC3545"]
    
    regimes = np.select(conditions, regime_choices, default="MEDIO")
    colors = np.select(conditions, color_choices, default="#28A745")
    
    # Rellenar NaNs iniciales de NATR con MEDIO
    na_mask = df['NATR'].isna()
    if na_mask.any():
        regimes[na_mask] = "MEDIO"
        colors[na_mask] = "#28A745"
            
    return pd.Series(regimes, index=df.index), pd.Series(colors, index=df.index)

def calculate_markov_matrix(regime_series):
    """
    Calcula la Matriz de Transición de Markov de Primer Orden y estadísticas asociadas.
    """
    states = ["BAJO", "MEDIO", "ALTO"]
    state_to_idx = {state: i for i, state in enumerate(states)}
    
    # Inicializar conteos
    counts = np.zeros((3, 3), dtype=int)
    
    # Limpiar nulos
    series_list = regime_series.dropna().tolist()
    
    # Contar transiciones
    for i in range(len(series_list) - 1):
        from_state = series_list[i]
        to_state = series_list[i+1]
        if from_state in state_to_idx and to_state in state_to_idx:
            idx_from = state_to_idx[from_state]
            idx_to = state_to_idx[to_state]
            counts[idx_from, idx_to] += 1
            
    # Calcular matriz de probabilidades
    matrix = np.zeros((3, 3))
    for i in range(3):
        row_sum = counts[i].sum()
        if row_sum > 0:
            matrix[i] = counts[i] / row_sum
            
    persistence = {states[i]: float(matrix[i, i]) for i in range(3)}
    
    # Calcular coverage
    total_valid = len(series_list)
    coverage = {}
    if total_valid > 0:
        counts_dict = pd.Series(series_list).value_counts(normalize=True).to_dict()
        for state in states:
            coverage[state] = float(counts_dict.get(state, 0.0))
    else:
        coverage = {state: 0.0 for state in states}
        
    return {
        "states": states,
        "matrix": matrix.tolist(),
        "counts": counts.tolist(),
        "persistence": persistence,
        "coverage": coverage
    }

def calculate_hurst_exponent(price_series, min_window=2, max_window=None):
    """
    Calcula el Exponente de Hurst H(t) usando el método de Rango Reescalado (R/S).
    price_series: pd.Series de precios de cierre.
    Retorna un valor float entre 0.0 y 1.0 (clamped).
    """
    series_vals = price_series.dropna().values
    N = len(series_vals)
    if N < 4:
        return 0.50
    
    # Retornos logarítmicos
    returns = np.diff(np.log(series_vals))
    N_ret = len(returns)

    if max_window is None:
        max_window = max(2, N_ret // 2)
        
    if min_window > max_window:
        min_window = max(2, max_window // 2)

    # Longitud máxima del bloque típicamente es N_ret // 2
    # Para ventanas muy pequeñas (como 5d), ajustamos para permitir al menos 2 lags
    if N_ret < 8:
        max_lag = max(2, N_ret - 1)
    else:
        max_lag = max(2, N_ret // 2)

    lags = range(min_window, max_lag + 1)
    if len(lags) < 2:
        return 0.50

    rs_values = []
    valid_lags = []

    for lag in lags:
        n_chunks = N_ret // lag
        if n_chunks < 1:
            continue
        
        rs_chunk_list = []
        for i in range(n_chunks):
            chunk = returns[i * lag : (i + 1) * lag]
            mean_chunk = np.mean(chunk)
            std_chunk = np.std(chunk, ddof=1)
            if std_chunk == 0:
                continue
            
            deviations = chunk - mean_chunk
            cum_dev = np.cumsum(deviations)
            R = np.max(cum_dev) - np.min(cum_dev)
            S = std_chunk
            rs_chunk_list.append(R / S)
        
        if rs_chunk_list:
            rs_values.append(np.mean(rs_chunk_list))
            valid_lags.append(lag)

    if len(rs_values) < 2:
        return 0.50

    log_lags = np.log(valid_lags)
    log_rs = np.log(rs_values)
    
    poly = np.polyfit(log_lags, log_rs, 1)
    hurst = poly[0]
    
    # Do not clip the upper bound; finite-sample R/S can naturally yield H > 1.
    return float(max(0.0, hurst))

def classify_hurst_regime(hurst_val):
    """
    Clasifica el régimen del Exponente de Hurst sin emojis (estándar textual Slate/Bloomberg).
    """
    if hurst_val > 0.55:
        return {
            "regime": "PERSISTENTE",
            "color": "#883030", # Crimson / Dark Accent
            "label": "PERSISTENCIA / INERCIA MACRO",
            "interpretation": "El activo presenta autocorrelación positiva de largo alcance (H > 0.55). Las propiedades estocásticas favorecen modelos de inercia y tendencia."
        }
    elif hurst_val < 0.45:
        return {
            "regime": "ANTIPERSISTENTE",
            "color": "#4a6984", # Acero / Slate
            "label": "REVERSIÓN A LA MEDIA",
            "interpretation": "El activo presenta autocorrelación negativa / elasticidad (H < 0.45). Las desviaciones tienden a retornar rápidamente a su centro."
        }
    else:
        return {
            "regime": "ALEATORIO",
            "color": "#64748b", # Muted Slate
            "label": "CAMINATA ALEATORIA (RANDOM WALK)",
            "interpretation": "El activo no muestra memoria persistente (H ≈ 0.50). Su comportamiento es indistinguible de un proceso estocástico puro."
        }

def _compute_hurst_entry(series):
    valid_series = series.dropna()
    n_samples = len(valid_series)
    if n_samples >= 20:
        h_val = calculate_hurst_exponent(valid_series)
        h_info = classify_hurst_regime(h_val)
        h_info["value"] = round(float(h_val), 2)
        h_info["sample_size"] = n_samples
    else:
        h_info = {
            "regime": "INSUFICIENTE",
            "color": "#64748b",
            "label": "MUESTRA INSUFICIENTE",
            "interpretation": f"Muestra insuficiente ({n_samples} días) para un cálculo econométrico válido.",
            "value": "N/D",
            "sample_size": n_samples
        }
    return h_info

def calculate_hurst_by_regime(df):
    """
    Calcula el Exponente de Hurst H(t) y su clasificación de forma segmentada
    para la matriz jerárquica 7x3 (7 Filas de Régimen-Estado x 3 Columnas de Dirección).
    """
    df = df.copy()
    if 'Regime' not in df.columns:
        regime_series, _ = classify_regimes_full(df)
        df['Regime'] = regime_series

    if 'State' not in df.columns:
        df['State'] = calculate_expansion_contraction(df)

    # Calcular retornos diarios para filtro de dirección
    df['Prev_Close'] = df['Close'].shift(1)
    df['Return'] = np.log(df['Close'] / df['Prev_Close'])

    row_definitions = [
        ("global", df),
        ("BAJO_EXPANSION", df[(df['Regime'] == "BAJO") & (df['State'] == "EXPANSIÓN")]),
        ("BAJO_CONTRACCION", df[(df['Regime'] == "BAJO") & (df['State'] == "CONTRACCIÓN")]),
        ("MEDIO_EXPANSION", df[(df['Regime'] == "MEDIO") & (df['State'] == "EXPANSIÓN")]),
        ("MEDIO_CONTRACCION", df[(df['Regime'] == "MEDIO") & (df['State'] == "CONTRACCIÓN")]),
        ("ALTO_EXPANSION", df[(df['Regime'] == "ALTO") & (df['State'] == "EXPANSIÓN")]),
        ("ALTO_CONTRACCION", df[(df['Regime'] == "ALTO") & (df['State'] == "CONTRACCIÓN")])
    ]

    result = {}

    for r_key, r_df in row_definitions:
        result[r_key] = {
            "global": _compute_hurst_entry(r_df['Close']),
            "alcista": _compute_hurst_entry(r_df[r_df['Return'] > 0]['Close']),
            "bajista": _compute_hurst_entry(r_df[r_df['Return'] < 0]['Close'])
        }

    return result

def calculate_kaufman_er(price_series, period=10):
    """
    Calcula el Ratio de Eficiencia de Kaufman (ER) sobre una ventana de n periodos.
    ER = |P_t - P_{t-n}| / sum_{i=0}^{n-1} |P_{t-i} - P_{t-i-1}|
    Retorna float entre 0.0 y 1.0.
    """
    series_vals = price_series.dropna().values
    if len(series_vals) <= period:
        return 0.50

    # Cambio neto en los 'period' dias
    net_change = abs(series_vals[-1] - series_vals[-(period + 1)])

    # Suma de cambios absolutos diarios
    daily_changes = np.abs(np.diff(series_vals[-(period + 1):]))
    sum_changes = np.sum(daily_changes)

    if sum_changes == 0:
        return 0.0

    er = net_change / sum_changes
    return float(np.clip(er, 0.0, 1.0))

def classify_kaufman_er(er_val):
    """
    Clasifica la Eficiencia Estructural de Kaufman sin emojis.
    """
    if er_val > 0.60:
        return {
            "regime": "DIRECCIONAL",
            "color": "#883030", # Crimson / Slate Accent
            "label": "ESTRUCTURA LIMPIA / DIRECCIONAL",
            "interpretation": f"El Ratio de Eficiencia de Kaufman es elevado (ER = {er_val:.2f}). El precio se desplaza con baja fricción y pocos retrocesos. Favorece modelos de tendencia y quiebre."
        }
    elif er_val < 0.30:
        return {
            "regime": "ERRÁTICO",
            "color": "#475569", # Slate Oscuro
            "label": "ESTRUCTURA ERRÁTICA EXTREMA",
            "interpretation": f"El Ratio de Eficiencia de Kaufman es reducido (ER = {er_val:.2f}). El precio zigzaguea con alta fricción y ruido. Destruye quiebres y favorece reversión a la media."
        }
    else:
        return {
            "regime": "MODERADO",
            "color": "#64748b", # Slate Muted
            "label": "ESTRUCTURA MODERADA / RUIDOSA",
            "interpretation": f"El Ratio de Eficiencia de Kaufman se encuentra en rango intermedio (ER = {er_val:.2f}). El avance presenta ruido aleatorio estándar."
        }

def _compute_kaufman_entry(series, current_atr, period):
    valid_series = series.dropna()
    n_samples = len(valid_series)
    if n_samples > period:
        er_val = calculate_kaufman_er(valid_series, period=period)
        info = classify_kaufman_er(er_val)
        info["value"] = round(er_val, 2)
        noise_factor = round(current_atr / er_val, 2) if er_val > 0 else "N/D"
        info["noise_factor"] = noise_factor
        info["sample_size"] = n_samples
    else:
        info = {
            "regime": "INSUFICIENTE",
            "color": "#64748b",
            "label": "MUESTRA INSUFICIENTE",
            "interpretation": f"Muestra insuficiente ({n_samples} días) para un cálculo econométrico válido en ventana {period}d.",
            "value": "N/D",
            "noise_factor": "N/D",
            "sample_size": n_samples
        }
    info["period"] = period
    return info

def calculate_kaufman_metrics(df):
    """
    Calcula el Kaufman ER y Noise Factor (ATR / ER) segmentado en la Matriz Jerárquica 7x3
    (7 Filas de Régimen-Estado x 3 Columnas de Dirección) para las ventanas 10d, 20d y 50d.
    """
    df = df.copy()
    if 'ATR' not in df.columns:
        df['ATR'] = calculate_atr(df, period=14)

    if 'Regime' not in df.columns:
        regime_series, _ = classify_regimes_full(df)
        df['Regime'] = regime_series

    if 'State' not in df.columns:
        df['State'] = calculate_expansion_contraction(df)

    # Calcular retornos diarios para filtro de dirección
    df['Prev_Close'] = df['Close'].shift(1)
    df['Return'] = np.log(df['Close'] / df['Prev_Close'])

    current_atr = float(df['ATR'].dropna().iloc[-1]) if not df['ATR'].dropna().empty else 1.0

    row_definitions = [
        ("global", df),
        ("BAJO_EXPANSION", df[(df['Regime'] == "BAJO") & (df['State'] == "EXPANSIÓN")]),
        ("BAJO_CONTRACCION", df[(df['Regime'] == "BAJO") & (df['State'] == "CONTRACCIÓN")]),
        ("MEDIO_EXPANSION", df[(df['Regime'] == "MEDIO") & (df['State'] == "EXPANSIÓN")]),
        ("MEDIO_CONTRACCION", df[(df['Regime'] == "MEDIO") & (df['State'] == "CONTRACCIÓN")]),
        ("ALTO_EXPANSION", df[(df['Regime'] == "ALTO") & (df['State'] == "EXPANSIÓN")]),
        ("ALTO_CONTRACCION", df[(df['Regime'] == "ALTO") & (df['State'] == "CONTRACCIÓN")])
    ]

    result = {}
    for period in [10, 20, 50]:
        period_key = f"{period}d"
        p_dict = {}
        for r_key, r_df in row_definitions:
            p_dict[r_key] = {
                "global": _compute_kaufman_entry(r_df['Close'], current_atr, period),
                "alcista": _compute_kaufman_entry(r_df[r_df['Return'] > 0]['Close'], current_atr, period),
                "bajista": _compute_kaufman_entry(r_df[r_df['Return'] < 0]['Close'], current_atr, period)
            }
        result[period_key] = p_dict

    return result

def calculate_zscore_metrics(df, window=None):
    """
    Calcula el Z-Score de retornos diarios sobre toda la serie histórica disponible (o ventana n si se especifica).
    Retorna el Z-Score actual, retorno %, media histórica, desviación estándar histórica, clasificación econométrica,
    y datos empíricos de la curva de distribución Z (etiquetados con Régimen y Estado) para la Campana de Gauss.
    """
    df = df.copy()
    if 'Regime' not in df.columns:
        regime_series, _ = classify_regimes_full(df)
        df['Regime'] = regime_series

    if 'State' not in df.columns:
        df['State'] = calculate_expansion_contraction(df)

    df['Prev_Close'] = df['Close'].shift(1)
    df['Return'] = np.log(df['Close'] / df['Prev_Close'])

    valid_df = df.dropna(subset=['Return']).copy()
    
    if window is not None and window > 0 and len(valid_df) > window:
        recent_df = valid_df.tail(window).copy()
    else:
        recent_df = valid_df.copy()
        window = len(recent_df)

    returns_series = recent_df['Return']
    mean_ret = float(returns_series.mean())
    std_ret = float(returns_series.std(ddof=1))

    if std_ret == 0:
        std_ret = 1e-6

    last_return = float(returns_series.iloc[-1])
    last_return_pct = float((np.exp(last_return) - 1) * 100)
    z_score = float((last_return - mean_ret) / std_ret)

    # Clasificación econométrica según la Regla de Weissman
    if z_score > 2.0:
        regime = "SOBRE_EXTENSION_ALCISTA"
        label = "SOBRE-EXTENSIÓN ALCISTA (+2.0σ)"
        color = "#883030" # Crimson
        interpretation = f"El retorno del día (+{last_return_pct:.2f}%) supera en +{z_score:.2f}σ la media histórica de la serie ({window} días, Regla de Weissman). Alerta de sobre-extensión alcista y posible agotamiento."
    elif z_score > 1.0:
        regime = "IMPULSO_ALCISTA"
        label = "IMPULSO ALCISTA NORMAL (+1.0σ a +2.0σ)"
        color = "#4a6984" # Slate Blue
        interpretation = f"El retorno del día (+{last_return_pct:.2f}%) registra un Z-Score de +{z_score:.2f}σ respecto a la serie histórica. Avance firme dentro de límites estocásticos esperados."
    elif z_score >= -1.0:
        regime = "NEUTRAL"
        label = "DENTRO DE LA NORMA (±1.0σ)"
        color = "#64748b" # Slate Muted
        interpretation = f"El retorno del día ({last_return_pct:+.2f}%) tiene un Z-Score de {z_score:+.2f}σ respecto a la serie histórica. Variación habitual sin anomalías direccionales."
    elif z_score >= -2.0:
        regime = "PRESION_BAJISTA"
        label = "PRESIÓN BAJISTA NORMAL (-1.0σ a -2.0σ)"
        color = "#475569" # Slate Dark
        interpretation = f"El retorno del día ({last_return_pct:.2f}%) registra un Z-Score de {z_score:.2f}σ respecto a la serie histórica. Retroceso bajista moderado dentro de parámetros normales."
    else:
        regime = "SOBRE_EXTENSION_BAJISTA"
        label = "SOBRE-EXTENSIÓN BAJISTA (-2.0σ)"
        color = "#883030" # Crimson
        interpretation = f"El retorno del día ({last_return_pct:.2f}%) cae en {z_score:.2f}σ respecto a la media histórica ({window} días, Regla de Weissman). Alerta de sobre-venta y pánico."

    # Serie normalizada Z de la muestra para el gráfico de distribución empírica
    z_series = ((returns_series - mean_ret) / std_ret).round(3).tolist()

    z_series_detail = []
    for idx, row in recent_df.iterrows():
        z_val = round(float((row['Return'] - mean_ret) / std_ret), 3)
        ret_pct = round(float((np.exp(row['Return']) - 1) * 100), 2)
        d_str = str(row['Date'])[:10] if 'Date' in row else ""
        z_series_detail.append({
            "date": d_str,
            "z": z_val,
            "return_pct": ret_pct,
            "regime": str(row.get('Regime', 'MEDIO')),
            "state": str(row.get('State', 'EXPANSIÓN'))
        })

    return {
        "z_score": round(z_score, 2),
        "last_return_pct": round(last_return_pct, 2),
        "mean_daily_pct": round(float((np.exp(mean_ret) - 1) * 100), 4),
        "std_daily_pct": round(float(std_ret * 100), 4),
        "window_days": window,
        "regime": regime,
        "label": label,
        "color": color,
        "interpretation": interpretation,
        "z_series": z_series,
        "z_series_detail": z_series_detail
    }


def calculate_hurst_kaufman_scatter(df, trajectory_days=None, window_days=30):
    """
    Calcula el par de coordenadas (Hurst H, Kaufman ER) para todos los días históricos (o trajectory_days si se especifica)
    y clasifica cada día dentro del plano cartesiano de 4 cuadrantes.
    """
    df = df.copy()
    if 'Regime' not in df.columns:
        regime_series, _ = classify_regimes_full(df)
        df['Regime'] = regime_series

    if 'State' not in df.columns:
        df['State'] = calculate_expansion_contraction(df)

    n = len(df)
    if n < 35:
        return {
            "current_hurst": 0.50,
            "current_kaufman": 0.50,
            "quadrant_id": "III",
            "quadrant_name": "ERRÁTICO & RUIDO EXTREMO",
            "color": "#475569",
            "description": "Datos insuficientes para el cálculo estocástico 2D.",
            "trajectory": []
        }

    # Pre-calcular Kaufman ER en toda la serie (usando window_days)
    change = (df['Close'] - df['Close'].shift(window_days)).abs()
    volatility = (df['Close'] - df['Close'].shift(1)).abs().rolling(window=window_days).sum()
    er_series = (change / volatility).replace([np.inf, -np.inf], np.nan).fillna(0.5)

    if trajectory_days is not None and trajectory_days > 0 and n > trajectory_days:
        start_idx = max(window_days, n - trajectory_days)
    else:
        start_idx = window_days

    trajectory = []

    for i in range(start_idx, n):
        date_val = df.index[i]
        date_str = date_val.strftime("%Y-%m-%d") if hasattr(date_val, 'strftime') else str(date_val)
        sub_df = df.iloc[max(0, i - window_days + 1):i + 1]
        try:
            h_val = float(calculate_hurst_exponent(sub_df['Close']))
        except Exception:
            h_val = 0.50

        er_val = float(er_series.iloc[i])
        h_round = round(h_val, 3)
        er_round = round(er_val, 3)

        row_data = df.iloc[i]
        reg_val = str(row_data.get('Regime', 'MEDIO'))
        state_val = str(row_data.get('State', 'EXPANSIÓN'))

        # Clasificar cuadrante de este día específico
        if h_round >= 0.50 and er_round >= 0.45:
            q_id = "I"
            q_name = "TENDENCIA LIMPIA & PERSISTENTE"
            q_color = "#0284c7"
            q_desc = f"Día {date_str} | Hurst ({h_round:.2f}) ≥ 0.50 y ER ({er_round:.2f}) ≥ 0.45: Avance firme direccional con bajo ruido."
        elif h_round < 0.50 and er_round >= 0.45:
            q_id = "II"
            q_name = "REVERSIÓN A LA MEDIA PULCRA"
            q_color = "#0f766e"
            q_desc = f"Día {date_str} | Hurst ({h_round:.2f}) < 0.50 y ER ({er_round:.2f}) ≥ 0.45: Oscilación limpia entre niveles."
        elif h_round < 0.50 and er_round < 0.45:
            q_id = "III"
            q_name = "ERRÁTICO & RUIDO EXTREMO"
            q_color = "#475569"
            q_desc = f"Día {date_str} | Hurst ({h_round:.2f}) < 0.50 y ER ({er_round:.2f}) < 0.45: Movimiento caótico con alta fricción."
        else:
            q_id = "IV"
            q_name = "TENDENCIA RUIDOSA CON FRICCIÓN"
            q_color = "#b45309"
            q_desc = f"Día {date_str} | Hurst ({h_round:.2f}) ≥ 0.50 y ER ({er_round:.2f}) < 0.45: Inercia tendencial golpeada por ruido errático."

        trajectory.append({
            "date": date_str,
            "hurst": h_round,
            "kaufman": er_round,
            "quadrant_id": q_id,
            "quadrant_name": q_name,
            "color": q_color,
            "description": q_desc,
            "regime": reg_val,
            "state": state_val
        })

    if not trajectory:
        current_h = 0.50
        current_er = 0.50
        latest_item = {
            "quadrant_id": "III",
            "quadrant_name": "ERRÁTICO & RUIDO EXTREMO",
            "color": "#475569",
            "description": "Sin trayectoria."
        }
    else:
        latest_item = trajectory[-1]
        current_h = latest_item["hurst"]
        current_er = latest_item["kaufman"]

    return {
        "current_hurst": current_h,
        "current_kaufman": current_er,
        "quadrant_id": latest_item["quadrant_id"],
        "quadrant_name": latest_item["quadrant_name"],
        "color": latest_item["color"],
        "description": latest_item["description"],
        "trajectory": trajectory
    }











