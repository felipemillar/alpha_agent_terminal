import pandas as pd
import numpy as np

def compute_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

try:
    df = pd.read_csv('data/NASDAQ_historico.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime')
    
    # 1. Math: ATR and Percentiles (252 days rolling)
    df['atr'] = compute_atr(df, 14)
    # Using normalized ATR (ATR%) to compare apples to apples over 50 years
    df['atr_pct'] = (df['atr'] / df['close']) * 100
    
    df['p33'] = df['atr_pct'].rolling(252).quantile(0.33)
    df['p66'] = df['atr_pct'].rolling(252).quantile(0.66)
    
    df = df.dropna().copy()
    
    # 2. Regimes Classification
    conditions = [
        (df['atr_pct'] < df['p33']),
        (df['atr_pct'] > df['p66'])
    ]
    choices = ['LOW', 'HIGH']
    df['regime'] = np.select(conditions, choices, default='MID')
    
    # 3. Streaks calculation
    # A new streak starts when the regime changes
    df['regime_shift'] = (df['regime'] != df['regime'].shift(1))
    df['streak_id'] = df['regime_shift'].cumsum()
    
    # Calculate daily returns
    df['daily_ret'] = df['close'].pct_change()
    
    # Group by streak
    streaks = df.groupby(['streak_id', 'regime']).agg(
        start_date=('datetime', 'first'),
        end_date=('datetime', 'last'),
        duration=('datetime', 'count'),
        cum_ret=('daily_ret', lambda x: (np.prod(1 + x) - 1) * 100)
    ).reset_index()
    
    # Drop ongoing final streak for clean data
    streaks = streaks.iloc[:-1]
    
    print("=== NASADQ REGIME PERSISTENCE KPIs ===")
    for regime in ['LOW', 'MID', 'HIGH']:
        r_df = streaks[streaks['regime'] == regime]
        n_obs = len(r_df)
        med_d = r_df['duration'].median()
        max_d = r_df['duration'].max()
        hit_ratio = (r_df['cum_ret'] > 0).mean() * 100
        print(f"[{regime}] N_OBS: {n_obs} | MEDIAN(D): {med_d:.0f} | MAX(D): {max_d} | HIT_RATIO: {hit_ratio:.1f}%")

except Exception as e:
    print(f"Error: {e}")
