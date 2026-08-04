---
title: "Calibración inicial y mediciones de referencia"
fecha: 2026-08-02
tags: [evidencia, calibracion, volatilidad, adn]
instrumentos: [XAUUSD, USDCLP]
catalogo: docs/CATALOGO_KPIS_ADN.md
---

# Calibración inicial y mediciones de referencia

Primer registro de la capa de evidencia. Contiene los resultados de aplicar el
[Catálogo de KPIs](../CATALOGO_KPIS_ADN.md) sobre instrumentos concretos, junto con las
correcciones surgidas durante la sesión.

El catálogo es agnóstico al instrumento y define el método. Este documento registra qué se obtuvo al
aplicarlo.

---

## 1. Procedencia de los datos

Los archivos de `data/` fueron regenerados durante esta sesión mediante la skill de extracción
(esquema 1.1.0, saneamiento estricto). Solo permanecen dos instrumentos.

| Instrumento | Ticker | Sesiones brutas | Descartadas por el extractor |
| :-- | :-- | --: | --: |
| XAUUSD | `GC=F` | 6.503 | 441 precios inválidos |
| USDCLP | `USDCLP=X` | — | — |

> **Advertencia de trazabilidad.** Las mediciones sobre S&P 500, Nasdaq, Bitcoin, Tesla y Ford
> registradas en la sección 5 provienen de archivos que **ya no existen** en `data/`. Se conservan
> por su valor metodológico, pero no son reproducibles con el estado actual del repositorio.

---

## 2. Calibración por instrumento

Resultado de aplicar el procedimiento de calibración del catálogo (sección correspondiente).

### 2.1 Época efectiva por nivel de dato

| Instrumento | N1 (cierre) | N2 (máx/mín) | N3 (apertura) | Barras planas | Aperturas sintéticas |
| :-- | :-- | :-- | :-- | --: | --: |
| XAUUSD | 2000-08-31 | 2000-08-31 | 2000 | 13,42% | 1,70% |
| USDCLP | 2000-07-19 | 2000-07-19 | 2000 | 0,00% | 3,93% |

> **Reproducción.** Todas las cifras de este documento se regeneran con
> `python src/adn.py [ACTIVO]` o vía `GET /api/adn/pilar1?asset=<nombre>`. Los valores fueron
> recalculados con la implementación definitiva el 2026-08-03; una versión previa de este registro
> situaba la época N3 de USDCLP en 2007, resultado obtenido sobre un archivo de datos anterior.

### 2.2 Umbrales derivados

Calculados sobre la serie saneada completa al 2026-08-02.

| Instrumento | `t₃₃` | `t₆₆` | Muestra |
| :-- | --: | --: | --: |
| XAUUSD | 0,991% | 1,326% | 6.060 sesiones |
| USDCLP | 0,831% | 1,101% | 6.459 sesiones |

**Estabilidad de los umbrales.** Desviación frente al valor final según fracción de la serie
utilizada:

| Fracción de muestra | XAUUSD `t₃₃` / `t₆₆` | USDCLP `t₃₃` / `t₆₆` |
| :-- | :-- | :-- |
| 50% | +6,9% / +9,2% | −11,1% / −10,7% |
| 70% | −3,3% / +1,3% | −7,2% / −12,7% |
| 85% | −1,5% / −0,3% | −3,9% / −6,3% |

Los umbrales convergen pero no están fijos. Incorporar el último 15% de datos movió el umbral
superior de USDCLP un 6,3%.

### 2.3 Validación del diseño de segmentación

| Propiedad | XAUUSD | USDCLP |
| :-- | :-- | :-- |
| Celda más pequeña de la matriz 3×2 | 728 sesiones | 772 sesiones |
| Sesiones en EXPANSIÓN | 43,8% | 43,0% |
| Expansión en régimen BAJO / MEDIO / ALTO | 36,0% / 43,9% / 51,6% | 35,9% / 45,3% / 47,8% |

Ninguna celda resulta marginal. El gradiente de expansión es monótono creciente con el régimen en
ambos instrumentos: la volatilidad baja tiende a contraerse y la alta a expandirse, con dependencia
moderada.

### 2.4 Verificación de la columna de apertura

| Instrumento | Descomposición vía Parkinson (N2) | Vía apertura (N3) | Divergencia | Veredicto |
| :-- | --: | --: | --: | :-- |
| XAUUSD | 41,7% | 40,2% | 1,5 pp | N3 habilitado |
| USDCLP | 21,6% | 23,0% | 1,4 pp | N3 habilitado |

Ambos métodos son independientes: Parkinson usa únicamente máximo y mínimo, la vía N3 usa la
apertura. La coincidencia dentro de 1,5 puntos porcentuales valida ambas columnas.

**USDCLP por subperíodo**, para descartar inestabilidad temporal:

| Período | Aperturas sintéticas | Parkinson (N2) | Apertura (N3) | corr(fuera, intra) |
| :-- | --: | --: | --: | --: |
| 2000-2006 | 5,6% | 30,3% | 16,7% | −0,08 |
| 2007-2013 | 3,4% | 20,1% | 23,2% | −0,09 |
| 2014-2020 | 3,7% | 21,6% | 23,2% | −0,06 |
| 2021-2027 | 3,0% | 16,2% | 23,0% | −0,04 |

Estable desde 2007. La correlación entre ambas mitades del día se mantiene entre −0,04 y −0,09, sin
firma de ruido de medición.

---

## 3. Mediciones por indicador

### P1.02 · Reparto de régimen por época

**XAUUSD** — NATR medio por quinquenio: 0,92% (2000-2004) → 1,42% (2005-2009) → 1,36% (2010-2014) →
1,00% (2015-2019) → 1,17% (2020-2024) → 1,80% (2025-2029).

Reparto de régimen en el bloque 2025-2029: **1,8% BAJO · 29,5% MEDIO · 68,8% ALTO**. La época
reciente concentra la volatilidad alta del instrumento, lo que confirma la no estacionariedad y
obliga a declarar el período de referencia.

**USDCLP** — el bloque 2020-2024 concentra **91,0%** de sesiones en régimen ALTO.

### P1.03 · Distribución de la razón de dirección

`ATR(5)/ATR(14)` en XAUUSD: p5 = 0,759 · p25 = 0,889 · **mediana = 0,980** · p75 = 1,081 ·
p95 = 1,269. USDCLP: p5 = 0,827 · mediana = 0,981 · p95 = 1,215.

La mediana se sitúa por debajo de 1,00 en ambos instrumentos, lo que confirma la propiedad esperada
descrita en el catálogo.

### P1.04 · Persistencia del estado direccional

| Instrumento · Estado | Rachas | Mediana | Percentil 80 | Máxima |
| :-- | --: | --: | --: | --: |
| XAUUSD · Expansión | 518 | 3 | 8 | 34 |
| XAUUSD · Contracción | 519 | 4 | 11 | 50 |
| USDCLP · Expansión | 442 | 4 | 10 | 42 |
| USDCLP · Contracción | 442 | 4 | 14 | 60 |

El estado direccional no es ruido diario: persiste una mediana de 3 a 4 sesiones.

### P3.01 y P3.02 · Excursión desde la apertura

Múltiplos del ATR previo, mediana y percentil 80.

| Instrumento | Recorrido a la baja | Recorrido al alza | Relación en posición larga | En posición corta |
| :-- | --: | --: | --: | --: |
| XAUUSD | 0,22 (p80 0,71) | 0,23 (p80 0,72) | 1,05 | 0,96 |
| USDCLP | 0,18 (p80 0,57) | 0,30 (p80 0,82) | 1,67 | 0,60 |

XAUUSD presenta geometría simétrica. USDCLP es **direccionalmente asimétrico**: la posición corta
soporta un recorrido en contra 1,70 veces superior al de la larga.

### P3.03 · Prima direccional por régimen

Rendimiento medio diario con su estadístico t. Umbral de significancia \|t\| > 1,96.

| Instrumento | BAJO | MEDIO | ALTO |
| :-- | :-- | :-- | :-- |
| XAUUSD | +0,0595% (t = 3,64) | +0,1071% (t = 5,16) | −0,0066% (t = −0,18) |
| USDCLP | +0,0200% (t = 1,90) | +0,0016% (t = 0,11) | +0,0110% (t = 0,50) |

**XAUUSD:** prima significativa en BAJO y MEDIO; **no medible** en ALTO. La lectura correcta no es
que el rendimiento se vuelva negativo, sino que deja de existir prima medible mientras la pérdida
esperada en escenario extremo se duplica.

**USDCLP:** sin prima direccional significativa en ningún régimen. La ventaja del instrumento, de
existir, proviene de la geometría (P3.02) y no del sesgo direccional.

Ambos resultados se verificaron bajo dos criterios de saneamiento distintos y bajo las dos
definiciones de régimen (móvil y absoluta), manteniéndose estables.

### P4.03 · Tiempo de normalización

| Instrumento | Episodios | Mediana | Percentil 80 | Máximo |
| :-- | --: | --: | --: | --: |
| XAUUSD | 48 | 28 sesiones | 62 | 132 |
| USDCLP | 38 | 36 sesiones | 75 | 97 |

---

## 4. Efecto del cambio de definición de régimen

La definición pasó de percentil móvil de 120 sesiones a terciles absolutos sobre historia completa
([`kpis.py:162`](../../src/kpis.py#L162)).

**Coincidencia de etiquetas entre ambas definiciones: 49,4% (XAUUSD) y 45,5% (USDCLP).** Más de la
mitad de las sesiones cambia de régimen.

Efectos verificados:

- **Las conclusiones sustantivas se mantienen.** La prima direccional de XAUUSD sigue siendo
  significativa en BAJO y MEDIO y no medible en ALTO bajo ambas definiciones.
- **Mejora la discriminación de riesgo.** La razón entre la pérdida esperada en régimen ALTO y en
  BAJO pasa de 2,2x (móvil) a 2,6x (absoluta) en XAUUSD.
- **Se compromete la racha máxima.** La duración máxima en régimen ALTO pasa de 79 a 373 sesiones en
  XAUUSD y de 85 a 405 en USDCLP. La **mediana no cambia** (4 y 6 sesiones respectivamente).
- **La matriz de Markov requiere reevaluación**: la diagonal de persistencia se infla.

---

## 5. Mediciones sobre instrumentos ya no disponibles

Conservadas por valor metodológico. **No reproducibles** con el estado actual de `data/`.

### Relación entre pérdida esperada y su umbral

Medida sobre cinco instrumentos (XAUUSD, USDCLP, Nasdaq, S&P 500, BTCUSD), con muestras de 4.200 a
16.100 sesiones: la pérdida media del 5% de sesiones más adversas resultó **1,50 a 1,56 veces** el
umbral que la define, con notable estabilidad entre instrumentos.

### Tiempo de normalización

Mediana de **28 a 44 sesiones** en los cinco instrumentos, con percentil 80 entre 62 y 75.

### Calidad de datos del S&P 500

| Década | Barras planas | Apertura == cierre previo |
| :-- | --: | --: |
| 1930-1950 | 100% | ~3% |
| 1970 | 0,7% | 92,4% |
| 1980-2000 | 0% | 64-77% |
| 2020 | 0% | 0,1% |

El índice no dispone de apertura real hasta aproximadamente 2014. De 24.762 sesiones, 16.252 son
utilizables en nivel N2 y considerablemente menos en N3.

---

## 6. Correcciones registradas

La capa de evidencia registra también lo que fue retractado, para impedir que una afirmación
descartada regrese en una sesión posterior.

| Afirmación emitida | Estado | Motivo |
| :-- | :-- | :-- |
| "El 56,6% del riesgo de USDCLP ocurre fuera de sesión" | **Retractada** | Provenía de `USDCLP_PEPPERSTONE_historico.csv`, archivo ya inexistente. El valor sobre el dataset actual es 21-23%. |
| "La descomposición de USDCLP es un artefacto (correlación −0,50)" | **Retractada** | La correlación fue producida por un error de procesamiento: eliminar barras planas a mitad de serie rompe la adyacencia entre días y fabrica correlación negativa espuria. El valor real está entre −0,04 y −0,09. |
| "El rendimiento medio se vuelve negativo en régimen ALTO" | **Corregida** | El signo depende del criterio de saneamiento y ningún valor alcanza significancia. La afirmación correcta es que la prima direccional deja de ser medible. |
| "El recorrido en contra del S&P 500 es 0,40 ATR" | **Corregida** | Contaminada por aperturas sintéticas. Sobre el tramo con apertura real el valor es 0,33 ATR, coincidente con el Nasdaq. |
| "La descomposición fuera de sesión / intradía carece de respaldo teórico en el corpus" | **Corregida** | Está especificada en `Caracterizacion_Volatilidad_Intradia.md` §3.1, con las mismas fórmulas y citas a Kakushadze (2014) y Glasserman et al. (2025). |
| "El cruce ATR(5)/ATR(14) es redundante frente al VRR" | **Corregida** | El cruce es uno de los dos ejes de la segmentación 7×3. El VRR mide la misma dimensión en horizonte más largo; es complementario, no sustituto. |

**Lección metodológica.** Tres de las seis correcciones se detectaron únicamente porque existía una
segunda medición independiente del mismo fenómeno. La disponibilidad de un método alternativo —el
estimador de Parkinson frente a la vía de la apertura— fue lo que permitió identificar el error.
