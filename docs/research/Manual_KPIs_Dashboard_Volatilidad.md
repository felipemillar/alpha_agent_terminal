---
title: "Manual de KPIs del Dashboard — Entendimiento de la Volatilidad de un Activo"
tags: [trading, volatilidad, kpis, dashboard, atr, hurst, kaufman, gaps, qrt-solutions]
date: 2026-08-01
author: QRT Solutions x Pepperstone Research
sources:
  - src/kpis.py
  - src/engine.py
  - frontend/dashboard_volatilidad.html
---

# Manual de KPIs del Dashboard — Entendimiento de la Volatilidad de un Activo

> Referencia de cada KPI de *Alpha Agent Terminal*. Para cada indicador: **qué mide** y, sobre todo,
> **qué te dice sobre la volatilidad y el comportamiento del activo**. El dashboard tiene dos escritorios:
> **Volatility Desk** (perfil estocástico del activo) y **Opening Gaps Desk** (microestructura de apertura).

---

## 0. Mapa mental: las 5 preguntas que responde el dashboard

Ningún KPI se lee solo. Cada panel responde una de estas cinco preguntas sobre la volatilidad del activo:

| # | Pregunta sobre la volatilidad | Paneles que la responden |
| :-- | :--- | :--- |
| 1 | **¿Cuánta hay?** (magnitud) | ATR, NATR, Percentil, Histograma de volatilidad |
| 2 | **¿Cómo evoluciona en el tiempo?** (régimen y dinámica) | Régimen BAJO/MEDIO/ALTO, Expansión/Contracción, Timeline, Rachas, Markov |
| 3 | **¿Qué textura tiene el movimiento?** (memoria y ruido) | Hurst 7×3, Kaufman ER 7×3, Mapa de Síntesis 2D |
| 4 | **¿Cómo se distribuyen los retornos?** (forma y colas) | Z-Score / Weissman, Skewness & Kurtosis, Return Dispersion |
| 5 | **¿Cómo se comporta en la apertura?** (gaps) | Los 7 KPIs de gaps, SDFP Matrix, Fill Rates, Superficie 3D |

**Filtros globales transversales:** toda la lectura se puede condicionar por **Régimen** (BAJO/MEDIO/ALTO)
× **Estado** (EXPANSIÓN/CONTRACCIÓN). Es la palanca clave: no preguntas *"¿cómo se comporta el activo?"*
sino *"¿cómo se comporta **cuando la volatilidad está alta y expandiéndose**?"*.

---

## DESK 1 — VOLATILITY DESK

### Cabecera: semáforo + 4 tarjetas KPI

**1. Precio de Cierre.**
*Qué mide:* el último precio registrado del activo.
*Lectura de volatilidad:* contexto base sobre el valor actual del instrumento antes de analizar su variación.

**2. ATR(14) — Average True Range.**
*Qué mide:* el rango diario promedio (incluye gaps), suavizado de Wilder, en unidades de precio.
*Lectura de volatilidad:* magnitud **absoluta** del movimiento diario esperado. Es la unidad base para
stops y objetivos ("el activo se mueve ±X por día"). No es comparable entre activos por sí solo.

**3. NATR(%) — ATR Normalizado.**
*Qué mide:* `ATR / Close × 100`.
*Lectura de volatilidad:* magnitud **relativa y comparable** entre activos. Un NATR de 2% dice que el
activo se mueve el doble (en %) que uno de 1%, sea EURUSD u ORO. Es la métrica para comparar universos.

**4. Estado de Volatilidad (Expansión / Contracción).**
*Qué mide:* cruce `ATR(5) vs ATR(14)`. Expansión si el corto supera al largo.
*Lectura de volatilidad:* la **dirección de la volatilidad** (no del precio): ¿se está acelerando o
comprimiendo? Compresión suele preceder rupturas; expansión indica régimen de estrés en curso.

**Semáforo QRT.** Sintetiza régimen + estado en un veredicto legible con mandato operativo (qué favorece
/ qué evitar). Es el "titular" que resume las cinco tarjetas.

---

### 6. Régimen de volatilidad — BAJO / MEDIO / ALTO
*Qué mide:* clasificación por percentil móvil (120d) del NATR: ≤33% = **BAJO**, ≤66% = **MEDIO**,
resto = **ALTO** (`classify_regimes_full`).
*Lectura de volatilidad:* el **estado macro** en que vive el activo hoy. Es la columna que segmenta casi
todos los demás paneles (las matrices 7×3, los gaps, las rachas). Convierte cada métrica en algo
*condicional al régimen*.

---

### 7. Mapa de Síntesis 2D (Constelación Hurst × Kaufman)
*Qué mide:* cada día histórico como punto en el plano **memoria (Hurst) × eficiencia (Kaufman ER)**,
clasificado en 4 cuadrantes (`calculate_hurst_kaufman_scatter`). Horizonte de memoria 5D/14D/30D.
*Lectura de volatilidad:* la **huella de comportamiento** del activo. Dónde se concentra la nube revela
si la volatilidad del activo se manifiesta como tendencia limpia (Q-I), reversión pulcra (Q-II), ruido
errático (Q-III) o tendencia sucia (Q-IV). *(Detalle completo en [[Guia_Utilidad_Mapa_Sintesis_2D_Hurst_Kaufman]].)*

---

### 8. Diagnóstico de Memoria — Hurst H 7×3
*Qué mide:* exponente de Hurst por **7 filas (régimen-estado) × 3 columnas (global / alcista / bajista)**
(`calculate_hurst_by_regime`). Bandas: >0.55 persistente · 0.45–0.55 random walk · <0.45 reversión.
*Lectura de volatilidad:* si la volatilidad **se autoperpetúa** (tendencia) o **se autocorrige**
(reversión), y —clave— **cómo cambia por régimen y por dirección**. Que las subidas sean persistentes
(alcista >0.55) pero las bajadas reviertan (<0.45) es un hallazgo directo sobre cómo operar cada lado.

---

### 9. Diagnóstico de Eficiencia — Kaufman ER 7×3 + Noise Factor
*Qué mide:* Efficiency Ratio de Kaufman (`|ΔP neto| / Σ|pasos|`) por ventana **10/20/50d**, segmentado
7×3 (`calculate_kaufman_metrics`). Bandas: >0.60 direccional · 0.30–0.60 moderado · <0.30 errático.
**Noise Factor = ATR / ER.**
*Lectura de volatilidad:* cuán **limpio o ruidoso** es el movimiento. El Noise Factor es especialmente
útil: cuando ER colapsa, el ATR "ajustado por ruido" se dispara, señalando volatilidad **no comerciable**
(mucho recorrido, poco avance). Es el filtro no-trade por excelencia.

---

### 10. Evaluación Estocástica de Retornos — Z-Score & Regla de Weissman
*Qué mide:* Z-Score del retorno del día vs. la media/σ de la serie histórica (`calculate_zscore_metrics`),
sobre una campana de Gauss empírica. Umbral Weissman |Z| > 2.
*Lectura de volatilidad:* detecta **choques estadísticos** — días cuyo movimiento excede lo normal.
|Z| > 2 marca sobre-extensión (agotamiento potencial) y sirve de **filtro no-trade** para no fadear
quiebres explosivos. Cuantifica cuándo "hoy" es un evento anómalo.

---

### 11. Forma Estocástica — Skewness & Kurtosis
*Qué mide:* asimetría (skew) y colas (kurtosis) de la distribución de retornos (calculado en frontend
sobre la muestra).
*Lectura de volatilidad:* la **forma del riesgo**. Skew negativo = caídas más bruscas que las subidas
(típico en equities). Kurtosis > 3 = **colas gruesas** (fat tails): los eventos extremos son mucho más
frecuentes que lo que predice la campana normal → los stops "improbables" saltan más de lo esperado.

---

### 12. Volatility Timeline (C1)
*Qué mide:* evolución temporal del ATR/NATR con coloreado por régimen.
*Lectura de volatilidad:* la **historia visual** de la volatilidad — cuándo hubo crisis, compresiones y
cómo se encadenan. Da el contexto de largo plazo a la foto de hoy.

### 13. Return Dispersion (C2)
*Qué mide:* dispersión del retorno diario frente al NATR.
*Lectura de volatilidad:* relación entre **nivel de volatilidad y tamaño de los retornos** — verifica
que más NATR efectivamente implica días más grandes, y expone outliers.

### 14. Volatility Distribution Histogram (C3)
*Qué mide:* distribución del NATR histórico + curva acumulada (CDF) y percentil de hoy.
*Lectura de volatilidad:* el **rango típico** de volatilidad del activo y dónde cae el día actual dentro
de esa distribución. Responde "¿este nivel de volatilidad es raro o habitual para este activo?".

### 15. Regime Persistence (C4) — Rachas + Markov
*Qué mide:* **rachas** de cada régimen (`get_streak_metrics`): N observaciones, duración mediana y máxima,
hit-ratio (% de días positivos), más up/down-swing. Complementado por la **Matriz de Markov 3×3**
(`calculate_markov_matrix`, vía `/api/markov`): probabilidad de transición entre BAJO/MEDIO/ALTO y
persistencia (diagonal).
*Lectura de volatilidad:* el **riesgo en el tiempo**. Cuánto **dura** típicamente un régimen (rachas) y
qué probabilidad hay de **saltar** a otro (Markov). Responde "si hoy estoy en ALTO, ¿cuántos días suele
durar y con qué probabilidad pasa a MEDIO mañana?".

---

## DESK 2 — OPENING GAPS DESK

Analiza el hueco entre el cierre previo y la apertura (`engine.analyze_gaps`). Se ignoran micro-gaps
< 0.05 ATR. Un gap se considera "llenado" (fill) si el precio vuelve a tocar el cierre anterior el mismo día.

### Strip de 7 KPIs

**16. Total Gaps** — número de gaps significativos en la historia. *Tamaño de la muestra* para todo lo demás.

**17. SDFP (Same-Day Fill Probability)** — % de gaps que se llenaron el mismo día.
*Lectura:* la **tendencia del activo a "cerrar el hueco"**. SDFP alto → los gaps son ruido que revierte
(favorece fade del gap); SDFP bajo → los gaps tienen convicción y continúan.

**18. Avg Gap Size (ATR)** — tamaño medio del gap en unidades de ATR.
*Lectura:* cuán grandes son los saltos de apertura **relativos a la volatilidad diaria** del activo.

**19. Filled Gaps** — cantidad absoluta de gaps llenados (numerador del SDFP).

**20. Avg Fill Depth** — retracement promedio hacia el cierre previo (`(Open−Low)/gap` en gap up).
*Lectura:* aunque un gap no se llene del todo, ¿**cuánto** suele retroceder? Mide la presión de reversión
parcial en la apertura.

**21. Avg Net Drift** — movimiento neto cierre-a-cierre tras el gap, en ATR (`(Close−Close_prev)/ATR`).
*Lectura:* al final del día, ¿el gap **se sostuvo o se revirtió**? Positivo = el activo mantiene la
dirección del gap; negativo = lo devuelve. Es el saldo direccional del día de gap.

**22. ICR (Intraday Capture / Continuation Ratio)** — cuerpo relativo al gap (`(Close−Open)/gap`).
*Lectura:* durante la sesión, ¿el precio **continuó** en la dirección del gap o lo **rellenó**? Separa el
comportamiento intradía del salto de apertura.

### 23. Gap Size vs Volatility Scatter
*Qué mide:* cada gap ubicado por tamaño (ATR) vs. NATR del día; color = llenado/abierto.
*Lectura:* relación entre **tamaño del gap, régimen de volatilidad y probabilidad de llenado**. Revela si
los gaps grandes en alta volatilidad se comportan distinto a los pequeños en calma.

### 24. SDFP Matrix (Regime × State × Weekday)
*Qué mide:* probabilidad de llenado segmentada por régimen, estado y día de la semana (bordes punteados = n<5).
*Lectura:* el **contexto** donde los gaps se llenan más/menos. Condiciona la lectura del SDFP global a
la situación concreta (p. ej. "los gaps de lunes en régimen ALTO casi nunca se llenan").

### 25. Fill Rate: Regime × Weekday  ·  26. Fill Rate: Gap Size × Weekday
*Qué miden:* tasas de llenado cruzando día de la semana con régimen (25) y con tamaño del gap (26).
*Lectura:* aíslan los efectos de **calendario** y **magnitud** sobre el comportamiento de los gaps.

### 27. 3D Probability Surface (Gaps × NATR × SDFP)
*Qué mide:* superficie continua de probabilidad de llenado en función de tamaño de gap × NATR, vía
regresión de kernel gaussiano; incluye interpretación agéntica (panel lateral con zonas calientes/frías).
*Lectura:* la **vista suavizada y completa** de cómo interactúan tamaño de gap y volatilidad sobre la
probabilidad de cierre — corrige las celdas discretas de muestra baja de los heatmaps.

### 28. Calculadora Pre-Market (herramienta aplicada)
*Qué hace:* dado un gap de apertura observado hoy, ubica su tamaño/contexto contra la estadística histórica
para estimar su probabilidad de llenado. Convierte todo el desk en una lectura operativa del día.

---

## Cómo se usan juntos: flujo de comprensión

Léelo de arriba hacia abajo, de lo macro a lo micro:

1. **Magnitud** (ATR/NATR/percentil): ¿cuánto se mueve y si hoy es caro/barato.
2. **Régimen y dinámica** (régimen, expansión, timeline, rachas, Markov): en qué estado vive, cuánto dura,
   hacia dónde transita.
3. **Textura** (Hurst, Kaufman, Síntesis 2D): si esa volatilidad es tendencia limpia o ruido — y por qué lado.
4. **Forma/colas** (Z-Score, Skew/Kurtosis): cómo se distribuyen los retornos y cuán peligrosas son las colas.
5. **Microestructura** (Gaps desk): cómo se comporta específicamente en la apertura.

**Regla de oro:** activa siempre los **filtros globales de régimen/estado** antes de concluir. El mismo
activo tiene *varias personalidades* según el régimen; el poder del dashboard está en leer cada KPI
*condicionado* al estado de volatilidad, no en promedio.

---

### Referencias de implementación
- Cálculo de KPIs: `src/kpis.py` · Ensamblado y gaps: `src/engine.py` · Endpoints: `src/server.py`
  (`/api/volatility`, `/api/streaks`, `/api/markov`, `/api/gaps`, `/api/gaps/analyze_surface`).
- Render y paneles: `frontend/dashboard_volatilidad.html`.
- Marco conceptual: [[Resumen_Perfilamiento_Volatilidad_ADN_Activo]], [[Caracterizacion_Volatilidad_Intradia]],
  [[Guia_Utilidad_Mapa_Sintesis_2D_Hurst_Kaufman]].
