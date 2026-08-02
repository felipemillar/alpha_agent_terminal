import pandas as pd

try:
    df = pd.read_csv('data/NASDAQ_historico.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    print("=== Estadísticas Descriptivas del Nasdaq (^IXIC) ===")
    print(df[['open', 'high', 'low', 'close', 'volume']].describe().round(2))
    
    print("\n=== Análisis de Saltos Temporales (Gaps) ===")
    df = df.sort_values('datetime')
    df['dias_desde_anterior'] = df['datetime'].diff().dt.days
    
    print("Top 5 mayores saltos temporales (Fines de semana largos / Feriados históricos):")
    print(df.nlargest(5, 'dias_desde_anterior')[['datetime', 'dias_desde_anterior']])
    
    # Check for extreme daily returns (potential bad data spikes)
    df['daily_return'] = df['close'].pct_change() * 100
    print("\n=== Top 3 Mayores Caídas Diarias (%) ===")
    print(df.nsmallest(3, 'daily_return')[['datetime', 'close', 'daily_return']])
    
    print("\n=== Top 3 Mayores Subidas Diarias (%) ===")
    print(df.nlargest(3, 'daily_return')[['datetime', 'close', 'daily_return']])

except Exception as e:
    print(f"Error: {type(e).__name__} (detalles omitidos por seguridad)")
