# Canvas: Cálculo de Persistencia de Regímenes

## 1. Visión & Enfoque Confirmado
- **Objetivo:** Calcular matemáticamente la persistencia (duración y retorno acumulado) de los regímenes de mercado utilizando la data histórica estandarizada para nutrir los KPIs: `N_OBS`, `MEDIAN(D)`, `MAX(D)` y `HIT_RATIO`.
- **Enfoque Seleccionado:** Régimen por Volatilidad (Percentiles del ATR). Los regímenes se clasificarán como Baja, Media o Alta volatilidad.

## 2. Componentes / Pilares Clave
- **Definición de Régimen:** Cálculo de percentiles 33 (LOW) y 66 (HIGH) de la Volatilidad Relativa (ATR 14 días / Cierre) en ventana móvil de 252 días.
- **Lógica de Persistencia Pura:** Rastreo de la duración estricta (en días) de cada racha (`streak_id`). Se aísla la variable temporal del precio.
- **Mapeo de KPIs:** Extracción del conteo total (`N_OBS`), la racha normal/mediana (`MEDIAN(D)`) y la racha máxima histórica (`MAX(D)`).
- **Modelo Visual:** Distribución de Frecuencias (Histograma de barras), donde el eje X representa "Días de Duración" agrupados en rangos o conteo unitario, y el eje Y representa la "Cantidad de Rachas" que tuvieron esa duración.

## 3. Estado de Madurez
- **Progreso:** 100% | **Puntos Pendientes:** Ninguno. La idea central de "Persistencia Pura" vía Histograma está completamente definida para ser implementada en el Dashboard.
