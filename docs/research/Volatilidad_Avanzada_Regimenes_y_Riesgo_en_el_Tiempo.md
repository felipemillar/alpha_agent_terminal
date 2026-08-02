---
title: Modelos Avanzados de Volatilidad Diaria: Regímenes de Markov, GARCH, EVT y Riesgo en el Tiempo
tags: [trading, cuantitativo, markov-regimes, garch, evt, hurst, carmona, kaufman, grimes, obsidian]
date: 2026-07-21
author: QRT Solutions x Pepperstone Research
sources:
  - file:///Users/fmillar/Proyectos_Desarrollo/Transcripcion_pdf_docx_to_MD/Libros_Markdown_Planos/Springer%20Texts%20in%20Statistics)%20Rene%CC%81%20Carmona%20(auth.)%20-%20Statistical%20Analysis%20of%20Financial%20Data%20in%20R-Springer-Verlag%20New%20York%20(2014).md
  - file:///Users/fmillar/Proyectos_Desarrollo/Transcripcion_pdf_docx_to_MD/Libros_Markdown_Planos/The%20art%20and%20science%20of%20technical%20analysis%20_%20market%20structure,%20price%20action,%20and%20trading%20strategies-J.%20Wiley%20%20%26%20%20Sons%20%20(2012).md
  - file:///Users/fmillar/Proyectos_Desarrollo/Transcripcion_pdf_docx_to_MD/Libros_Markdown_Planos/7-Trading%20Systems%20and%20Methods%20Technical%20Analysis%20%26%20Strategies.md
---

# Modelos Avanzados de Volatilidad Diaria: Regímenes de Markov, GARCH, EVT y Riesgo en el Tiempo

## 1. Introducción: De la Volatilidad Estática al "Riesgo en el Tiempo"

Llevar el estudio del **$\text{ATR}_{Daily}$** a un nivel poco ortodoxo y cuantitativamente avanzado exige abandonar la visión del ATR como un promedio estático. El riesgo a largo plazo no se define por "cuánto se movió el precio ayer", sino por la **Estructura Estocástica del Riesgo en el Tiempo**, determinada por las probabilidades de transición entre **Regímenes de Volatilidad**.

---

## 2. Matriz de Fuentes Avanzadas en tu Vault de Obsidian

| Modelo Avanzado | Archivo Fuente en tu Vault de Obsidian | Referencia Académica |
| :--- | :--- | :--- |
| **Markov Regime Switching (HMM)** | [[Springer Texts in Statistics) Rene Carmona...#L11976]] | C.J. Kim & C.R. Nelson (1999) / Carmona (2014) |
| **Volatilidad Condicional GARCH / FIGARCH** | [[Springer Texts in Statistics) Rene Carmona...#L11328]] | Robert Engle (1982) / Bollerslev (1986) |
| **Teoría de Valores Extremos (EVT / GEV)** | [[Springer Texts in Statistics) Rene Carmona...#L2099]] | Teorema de Pickands-Balkema-de Haan |
| **Volatility Clustering & Ineficiencia** | [[The art and science of technical analysis...#L5568]] | Adam Grimes (2012) / Mandelbrot |
| **Optimal Position Sizing & Regime Distortion** | [[The art and science of technical analysis...#L3115]] | Ralph Vince / Adam Grimes |
| **Kaufman Noise-Adjusted ATR** | [[7-Trading Systems and Methods...#L29178]] | Perry Kaufman |

---

## 3. Los 5 Modelos Avanzados de Riesgo en el Tiempo

### 3.1. Modelo HMM de Cambio de Régimen de Volatilidad (Markov Regime-Switching)
El activo no evoluciona en una curva uniforme, sino que habita en **Estados Discretos No Observables ($S_t$)**:
- **Estado 0 (Baja Volatilidad / Tendencia Estable):** $\mu > 0, \, \sigma_{Daily} \ll \overline{\text{ATR}}$.
- **Estado 1 (Alta Volatilidad / Ruido y Caos):** $\mu < 0, \, \sigma_{Daily} \gg \overline{\text{ATR}}$.
- **Estado 2 (Compresión Pre-Explosión / Squeeze):** $\sigma_{Daily} \to \text{mínimos}$.

$$\text{Riesgo en el Tiempo} = P(S_{t+1} = 1 \mid S_t = 0, \mathcal{F}_t)$$
* **Insight:** El riesgo de largo plazo no es el ATR actual, sino la **probabilidad de transición** de que el activo cambie de régimen mañana.

### 3.2. Descomposición GARCH: Varianza Transitoria vs. Persistente
$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$
- **Spike Transitorio ($\alpha$ alto, $\beta$ bajo):** Un choque de noticias (CPI/NFP) genera una expansión de ATR que se disipa rápidamente.
- **Cambio Estructural ($\alpha + \beta \to 1$):** El ATR expandido presenta "histeresis"; la volatilidad elevada persistirá durante semanas (Volatility Clustering).

### 3.3. Teoría de Valores Extremos (EVT) y Value-at-Risk Dinámico ($\text{VaR}_{EVT}$)
Sustituyendo la campana de Gauss por la distribución Generalizada de Pareto para modelar las colas gruesas:
$$\text{VaR}_{t, 99\%} = \text{Precio}_t \times \left( \mu_{Daily} + q_{\gamma} \cdot \sigma_{EVT}(\text{ATR}_{Daily}) \right)$$
Permite estimar la pérdida máxima real a 30 o 90 días adaptada al régimen de varianza actual.

### 3.4. Exponente de Hurst Dinámico $H(t)$ (Regímenes de Memoria)
$$\text{Rescaled Range } (R/S)_n = c \cdot n^{H}$$
- **$H(t) > 0.6$ + Expansión de ATR:** Tendencia macro desbocada (Momentum).
- **$H(t) < 0.4$ + Expansión de ATR:** Violenta reversión a la media / Destrucción de stops.

### 3.5. ATR Ajustado por Ruido (Kaufman Noise-Adjusted ATR)
$$\text{Adjusted ATR}_{Daily} = \frac{\text{ATR}_t(14)}{\text{ER}_t}$$
Donde $\text{ER}_t$ es el Efficiency Ratio de Kaufman. Si $\text{ER}_t \to 0$, el ATR ajustado se dispara, alertando que la volatilidad actual es puro ruido no comerciable.

---

## 4. Síntesis para la Conferencia Pepperstone

Al presentar esta metodología, demostramos que evaluar la volatilidad diaria no es mirar un indicador estático, sino cuantificar **la matriz de transición de riesgo del activo en el tiempo**.
