import pandas as pd
import glob
import os

def check_data_quality():
    files = glob.glob('data/*_historico.csv')
    print(f"Archivos encontrados para revisión: {len(files)}\n")
    
    for file in files:
        asset_name = os.path.basename(file)
        print(f"=== Revisión de: {asset_name} ===")
        
        try:
            df = pd.read_csv(file)
            
            # 1. Registros
            print(f"- Registros totales: {len(df)}")
            print(f"- Rango de fechas: {df['datetime'].min()} a {df['datetime'].max()}")
            
            # 2. Valores Nulos
            nulls = df.isnull().sum()
            total_nulls = nulls.sum()
            print(f"- Valores Nulos (NaN): {total_nulls}")
            if total_nulls > 0:
                print(f"  Detalle nulos:\n{nulls[nulls > 0]}")
                
            # 3. Precios en 0 o negativos (anomalías)
            price_cols = ['open', 'high', 'low', 'close']
            zeros = (df[price_cols] <= 0).sum().sum()
            print(f"- Precios <= 0 (Anomalías): {zeros}")
            if zeros > 0:
                print(f"  Advertencia: Existen precios en cero o negativos.")
            
            # 4. Gaps (Saltos de tiempo)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime')
            date_diff = df['datetime'].diff().dt.days
            max_gap = date_diff.max()
            print(f"- Salto máximo entre fechas: {max_gap} días")
            if max_gap > 10:
                print(f"  Advertencia: Se detectó un salto temporal grande ({max_gap} días).")
                
            # 5. Duplicados
            dups = df.duplicated(subset=['datetime']).sum()
            print(f"- Fechas duplicadas: {dups}")
            
        except Exception as e:
            print(f"Error procesando {asset_name}: {type(e).__name__} (detalles omitidos por seguridad)")
            
        print("-" * 50)

if __name__ == "__main__":
    check_data_quality()
