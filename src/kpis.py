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

def classify_regimes_full(df, lookback=120):
    """
    Clasifica el régimen de volatilidad de cada fila del DataFrame completo de forma móvil.
    Retorna dos pd.Series: (regimes, colors)
    """
    df = df.copy()
    if 'NATR' not in df.columns:
        # Importación local para evitar dependencia circular si se requiere
        import kpis
        df['NATR'] = kpis.calculate_natr(df)
        
    regimes = []
    colors = []
    
    natr_values = df['NATR'].values
    
    for i in range(len(df)):
        if i < lookback:
            regimes.append("MEDIO")
            colors.append("#28A745")
            continue
            
        lookback_slice = natr_values[i-lookback:i+1]
        current_natr = natr_values[i]
        
        # Calcular percentil ranking móvil de forma vectorizada súper rápida
        percentile = (np.count_nonzero(lookback_slice < current_natr) / len(lookback_slice)) * 100
        
        if percentile <= 33.33:
            regimes.append("BAJO")
            colors.append("#FFC107")
        elif percentile <= 66.66:
            regimes.append("MEDIO")
            colors.append("#28A745")
        else:
            regimes.append("ALTO")
            colors.append("#DC3545")
            
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

