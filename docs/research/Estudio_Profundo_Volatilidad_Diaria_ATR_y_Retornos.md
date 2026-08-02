---
title: Marco Teórico y Cuantitativo de la Volatilidad Diaria (ATR Daily) y Distribución de Retornos
tags: [trading, cuantitativo, atr-daily, volatilidad-diaria, z-score, pepperstone, obsidian, carter, kaufman, weissman]
date: 2026-07-21
author: QRT Solutions x Pepperstone Research
sources:
  - file:///Users/fmillar/Proyectos_Desarrollo/Transcripcion_pdf_docx_to_MD/Libros_Markdown_Planos/John%20F%20Carter%20-%20Mastering%20the%20Trade,%20Third%20Edition_%20Proven%20Techniques%20for%20Profiting%20from%20Intraday%20and%20Swing%20Trading%20Setups-McGraw-Hill%20Education%20(2018).md
  - file:///Users/fmillar/Proyectos_Desarrollo/Transcripcion_pdf_docx_to_MD/Libros_Markdown_Planos/New%20York%20Institute%20of%20Finance)%20John%20J.%20Murphy%20-%20Technical%20Analysis%20of%20the%20Financial%20Markets_%20A%20Comprehensive%20Guide%20to%20Trading%20Methods%20and%20Applications%20(New%20York%20Institute%20of%20Finance)-New%20York%20Institu.md
  - file:///Users/fmillar/Proyectos_Desarrollo/Transcripcion_pdf_docx_to_MD/Libros_Markdown_Planos/15-Richard%20L.%20Weissman%20-%20Mechanical%20Trading%20Systems.md
  - file:///Users/fmillar/Proyectos_Desarrollo/Transcripcion_pdf_docx_to_MD/Libros_Markdown_Planos/7-Trading%20Systems%20and%20Methods%20Technical%20Analysis%20%26%20Strategies.md
  - file:///Users/fmillar/Proyectos_Desarrollo/Transcripcion_pdf_docx_to_MD/Libros_Markdown_Planos/10-Building_Winning_Trading_Systems.md
  - file:///Users/fmillar/Proyectos_Desarrollo/pepperstone/atr_research_notebooklm.md
---

# Marco Teórico y Cuantitativo de la Volatilidad Diaria (ATR Daily) y Distribución de Retornos

## 1. Introducción y Tesis Central

El análisis de la **Volatilidad Diaria** mediante el **Average True Range Diario ($\text{ATR}_{Daily}$)** y la **Distribución de Retornos Diarios ($R_t$)** constituye el pilar primario para comprender el comportamiento estructural y el régimen de riesgo de un activo a **largo plazo**.

A diferencia de la volatilidad intradiaria (que cuantifica el ruido microestructural de la sesión), el $\text{ATR}_{Daily}$ absorbe las brechas de apertura (gaps overnight) y permite proyectar la capacidad de expansión del precio en horizontes multidiarios, semanas y meses.

---

## 2. Matriz de Fuentes y Trazabilidad en tu Vault de Obsidian

| Concepto Cuantitativo | Archivo Fuente en tu Vault de Obsidian | Referencia Académica / Autor |
| :--- | :--- | :--- |
| **Definición del True Range y Gaps** | [[7-Trading Systems and Methods Technical Analysis & Strategies#L28341]] | J. Welles Wilder Jr. (1978) |
| **TTM Squeeze y Expansión de ATR** | [[John F Carter - Mastering the Trade, Third Edition...#L3605]] | John F. Carter (*Mastering the Trade*) |
| **Regla del Stop de 2x ATR Daily** | [[John F Carter - Mastering the Trade, Third Edition...#L3643]] | John F. Carter |
| **Normalización de Mercado (Sizing por ATR)** | [[10-Building_Winning_Trading_Systems#L3992]] | Design & Testing of Trading Systems |
| **Filtros No-Trade por Z-Score ($Z > 2.5$)** | [[15-Richard L. Weissman - Mechanical Trading Systems#L58-L88]] | Richard Weissman |
| **Canales Keltner y STARC Bands** | [[New York Institute of Finance) John J. Murphy...#L5609]] | John J. Murphy / Chester Keltner |
| **Estacionalidad del Rango por Día** | [[10-Building_Winning_Trading_Systems#L5253]] | Análisis de Varianza por Día de la Semana |

---

## 3. Pilar I: El ATR Diario ($\text{ATR}_{Daily}$) como Barómetro Macro de Largo Plazo

### 3.1. Formulación del True Range ($TR$) Incorporando Gaps
El Rango Verdadero de la sesión diaria $t$ se define como:
$$TR_t = \max\left( \text{High}_t - \text{Low}_t, \, |\text{High}_t - \text{Close}_{t-1}|, \, |\text{Low}_t - \text{Close}_{t-1}| \right)$$
El $\text{ATR}_{Daily}(n)$ suaviza estos valores en un período estándar de $n = 14$ o $n = 20$ días:
$$\text{ATR}_t(n) = \frac{1}{n} \sum_{i=0}^{n-1} TR_{t-i}$$

### 3.2. Normalización Cross-Asset: % ATR (NATR)
Para comparar la volatilidad de largo plazo entre activos con precios nominales distintos (ej. EURUSD a $1.08, Apple a $220, S&P 500 a $5,500), se normaliza el $\text{ATR}$ en porcentaje del precio:
$$\text{NATR}_t = \frac{\text{ATR}_t(14)}{\text{Close}_t} \times 100$$
* **Aplicación a largo plazo:** Permite determinar qué activo es estructuralmente más volátil independientemente de su valor por punto o pip.

### 3.3. Regímenes de Volatilidad: Compresión (Squeeze) vs. Expansión (Carter & Kaufman)
Según John Carter (*Mastering the Trade*, L3605), los mercados alternan entre estados de baja y alta volatilidad diaria:
- **Compresión (Squeeze):** Las Bandas de Bollinger (basadas en desviación estándar $2\sigma$) se contraen e ingresan dentro de los Canales de Keltner (basados en $1.5 \times \text{ATR}_{Daily}$). El $\text{ATR}$ cae a mínimos de 50 o 100 días.
- **Expansión (Breakout):** La ruptura de la compresión expande violentamente el $\text{ATR}_{Daily}$. Las metas de proyección a largo plazo se miden en múltiplos del ATR: $+1 \text{ ATR}$, $+2 \text{ ATR}$ y $+3 \text{ ATR}$.

### 3.4. Normalización de Riesgo en Capital (Position Sizing por ATR)
Según *Building Winning Trading Systems* (L3992), para normalizar el riesgo de largo plazo entre dos instrumentos en un portafolio:
$$\text{Posición (Contratos/Lotes)} = \frac{\text{Riesgo Máximo en USD}}{\text{Multiplicador de Contrato} \times k \times \text{ATR}_{Daily}}$$
Donde $k$ es el factor de ajuste de stop (típicamente $k = 2.0$, siguiendo la regla de Carter).

---

## 4. Pilar II: Distribución de Retornos Diarios ($R_t$) y Riesgo de Cola

### 4.1. Retorno Logarítmico Diario
$$R_t = \ln\left(\frac{\text{Close}_t}{\text{Close}_{t-1}}\right)$$

### 4.2. Momentos Estadísticos de la Distribución Diaria
1. **Media ($\mu$):** Retorno esperado diario.
2. **Varianza ($\sigma^2$):** Volatilidad diaria estándar.
3. **Sesgo (Skewness):** 
   - $Skew < 0$ (Asimetría negativa): Típico de índices accionarios (caídas rápidas, subidas lentas).
   - $Skew > 0$ (Asimetría positiva): Típico de commodities o criptoactivos.
4. **Curtosis ($Kurt > 3$ - Fat Tails):** 
   Frecuencia de retornos extremos a largo plazo. Evidencia que la distribución real de precios posee colas más anchas que la distribución Gaussiana teórica (Weissman, L80).

### 4.3. Z-Score de Retornos Diarios y Filtros Operativos No-Trade
$$Z_t = \frac{R_t - \mu_{20}}{\sigma_{20}}$$
- **Regla de Weissman:** Si $|Z_t| > 2.5$, el retorno diario representa un movimiento extremo de $>2.5$ desviaciones estándar. Se activa una regla de **No-Trade** para evitar operar en contra de tendencias explosivas sostenidas.

---

## 5. Pilar III: Estacionalidad Diaria y Autocorrelación (Mandelbrot)

### 5.1. Ratio de Rango por Día de la Semana
Medir qué día de la semana presenta mayor expansión del rango diario:
$$\text{RatioWeekday}_d = \frac{TR_d}{\text{ATR}_{30}(\text{Viernes Anterior})}$$
Permite identificar si los Lunes o Jueves tienen sesgos estacionales de mayor o menor volatilidad a largo plazo.

### 5.2. Clusterización de Volatilidad (Volatility Clustering)
Propiedad postulada por Benoît Mandelbrot: Días de alto $\text{ATR}_{Daily}$ tienden a ser seguidos por días de alto $\text{ATR}_{Daily}$. La autocorrelación de $|R_t|$ a rezagos de 1 a 20 días confirma la persistencia del régimen de volatilidad a largo plazo.

---

## 6. Conclusión y Aplicación en el Ciclo Pepperstone

Esta metodología permite construir una **Ficha de Caracterización de Largo Plazo (Asset Profile Factsheet)** para presentar a la audiencia de Pepperstone, demostrando cómo estudiar el "ADN" de cualquier activo (EURUSD, SPX, GOLD, BTC) utilizando exclusivamente datos diarios de OHLC.

---
*Documento generado y sincronizado automáticamente en tu Vault de Obsidian.*
