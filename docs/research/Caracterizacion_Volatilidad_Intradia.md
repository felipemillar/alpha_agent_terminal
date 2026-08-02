---
title: Caracterización Cuantitativa y Volatilidad Intradía del Activo (ADN del Instrumento)
tags: [trading, cuantitativo, volatilidad, atr, zscore, pepperstone, obsidian]
date: 2026-07-21
author: QRT Solutions x Pepperstone Research
sources:
  - file:///Users/fmillar/Proyectos_Desarrollo/pepperstone/atr_research_notebooklm.md
  - file:///Users/fmillar/Proyectos_Desarrollo/pepperstone/directrices_investigacion.md
---

# Caracterización Cuantitativa y Volatilidad Intradía del Activo (ADN del Instrumento)

## 1. Introducción y Propósito
El objetivo de este documento es establecer el **Marco de Caracterización y Perfilamiento Cuantitativo (Asset Factsheet / ADN del Instrumento)**. Este análisis no busca generar señales mecánicas inmediatas de entrada/salida, sino **caracterizar empíricamente el comportamiento microestructural y de varianza** de un activo antes de diseñar cualquier estrategia.

---

## 2. Matriz de Fuentes y Trazabilidad de Conceptos

| Sección / Métrica | Fuente Primaria en Repositorio | Autor / Referencia Académica |
| :--- | :--- | :--- |
| **Filtros Z-Score ($Z < 2.5$) y Fat Tails** | [[atr_research_notebooklm#3. Z-Score (Desviación Estándar y Distribución de Gauss)]] | Richard Weissman (*Mechanical Trading Systems*) |
| **Filtros de Regímenes de Volatilidad ($<0.35\sigma$)** | [[atr_research_notebooklm#2. Cálculo de Regímenes de Volatilidad y Filtros Operativos (No-Trade)]] | Perry Kaufman (*Trading Systems and Methods*) |
| **ATR True Range con Gaps** | [[atr_research_notebooklm#1. Average True Range (ATR): Marco Teórico y Matemático]] | J. Welles Wilder Jr. (1978) |
| **Efficiency Ratio (KAMA ER)** | Literatura Cuantitativa | Perry Kaufman |
| **Exponente de Hurst ($H$) & Volatility Clustering** | Econometría de Mercados Financieros | Benoît Mandelbrot (1963) |
| **Partición Intradía vs. Overnight** | Microestructura de Mercado | Kakushadze (2014) / Glasserman et al. (2025) |

---

## 3. Las 5 Dimensiones del ADN del Activo

### 3.1. Dimensión de Varianza y Partición de Volatilidad (Vol Partitioning)
1. **Volatilidad Intradía vs. Overnight ($\sigma_{intraday}$ vs $\sigma_{overnight}$):**
   $$\sigma_{overnight} = \text{std}\left(\ln\left(\frac{\text{Open}_t}{\text{Close}_{t-1}}\right)\right), \quad \sigma_{intraday} = \text{std}\left(\ln\left(\frac{\text{Close}_t}{\text{Open}_t}\right)\right)$$
2. **Ratio de Régimen de Volatilidad (VRR):**
   $$\text{VRR} = \frac{\text{ATR}_{14}}{\text{ATR}_{50}}$$
   - $\text{VRR} < 0.85$: Compresión de volatilidad (acumulación).
   - $\text{VRR} > 1.25$: Expansión / Régimen de estrés.
3. **Estimadores Extremos de Volatilidad (Parkinson):**
   $$\sigma_{Parkinson}^2 = \frac{1}{4 \ln 2} \ln\left(\frac{\text{High}_t}{\text{Low}_t}\right)^2$$

### 3.2. Dimensión de Morfología de Distribución y Riesgo de Cola
- **Sesgo (Skewness):** Asimetría de retornos. Equities sufren sesgo negativo; commodities presentan sesgo positivo en crisis.
- **Curtosis ($Kurt > 3$):** Cuantificación de colas gruesas (*Fat Tails*) para evitar quiebres de stops por eventos improbables bajo la campana de Gauss.
- **Z-Score Normalizado ($Z = \frac{X - \mu}{\sigma}$):** Filtro no-trade si $Z > 2.5$.

### 3.3. Dimensión de Ruido y Eficiencia Estructural
- **Kaufman Efficiency Ratio (ER):**
  $$\text{ER}_n = \frac{|\text{Precio}_t - \text{Precio}_{t-n}|}{\sum_{i=0}^{n-1} |\text{Precio}_{t-i} - \text{Precio}_{t-i-1}|}$$
- **Ratio Cuerpo-Rango (Body-to-Range):**
  $$\text{BRR} = \frac{|\text{Close} - \text{Open}|}{\text{High} - \text{Low}}$$

### 3.4. Dimensión de Memoria y Autocorrelación
- **Exponente de Hurst ($H$):**
  - $H > 0.5$: Activo tendencial (persistencia).
  - $H < 0.5$: Activo de reversión a la media (antipersistencia).
- **Autocorrelación de Volatilidad ($|R_t|$):** Verificación de clusterización de volatilidad a rezagos 1, 5 y 20.

### 3.5. Dimensión de Estacionalidad Intradía y Calendario
- **Curva de Volatilidad Intradía (U-Shape por Hora):** Distribución porcentual del ATR consumido por sesión (Londres, NY, Asia).
- **Día de la Semana:** Análisis diferencial de volatilidad Lunes vs. Viernes.

---

## 4. Próximos Pasos de Implementación (Python ETL)
1. Extracción de datos OHLC intradía (15m y 1h) para el universo Pepperstone (EURUSD, US100, GOLD).
2. Generación del reporte comparativo **Asset Factsheet** en Streamlit / Plotly.
