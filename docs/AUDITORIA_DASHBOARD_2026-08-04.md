---
title: "Auditoría del dashboard — inventario completo de indicadores"
tags: [auditoria, dashboard, kpis, adn]
date: 2026-08-04
alcance: frontend/dashboard_volatilidad.html (6.143 líneas), ambos escritorios
metodo: inspección del archivo y trazado de cada elemento a su función de renderizado y fuente de datos
---

# Auditoría del dashboard — inventario completo

Auditoría del archivo real, no de la documentación. Cada elemento visible se trazó hasta su función
de renderizado y desde ahí hasta su fuente de datos. Los valores se verificaron ejecutando el motor.

---

## 1. Cambio de estado desde la auditoría anterior

El **Pilar 2 se implementó por completo** siguiendo el plan de siete fases. Verificado en ejecución:

| Componente | Situación |
| :-- | :-- |
| `preparar_serie`, `momentos_distribucion`, `_retornos_por_horizonte`, `_celda_cola`, `riesgo_cola`, `caracterizar_pilar2` | Presentes en `src/adn.py` (665 líneas) |
| `GET /api/adn/pilar2` | Operativo |
| `generate_analysis.py` | Llama a `caracterizar_pilar2` e inyecta el resultado en `stats['pilar2']` |
| `expert_nlg.py` | Consume el Pilar 2 con vía de repliegue, y usa el umbral corregido `kurt > 0` |
| Panel en el dashboard | `renderPilar2Widget` con selector de horizonte |

Salida verificada sobre QQQ, régimen ALTO, horizonte 1, posición larga: umbral −4,04%, pérdida
esperada −5,50%, 112 observaciones en cola, publicable.

---

## 2. Inventario — Escritorio 1 · Volatility Desk

### 2.1 Cabecera

| Elemento | Fuente | Catálogo |
| :-- | :-- | :-- |
| Selector de activo, semáforo, botón de informe | `/api/assets` | — |
| Barra de filtros globales: régimen × estado | local | Aplica el eje de P1.04 |
| Cierre, ATR(14), NATR(%), estado de volatilidad | `/api/volatility` | Variables base y P1.05 |

### 2.2 Sección estructural — ADN Pilar 1 (colapsable, renderizado diferido)

| Panel | Función | Catálogo | Fuente |
| :-- | :-- | :-- | :-- |
| Estructura temporal del régimen | `renderizarPanelA_P102` | P1.02 | `/api/adn/pilar1` |
| Partición del riesgo diario | `renderizarPanelE_P106_107` | P1.06 + P1.07 | ídem |
| Dirección de la volatilidad | `renderizarPanelB_P103_108` | P1.03 + P1.08 | ídem |
| Persistencia direccional | `renderizarPanelC_P104` | P1.04 | ídem |
| Validación de la segmentación | `renderizarPanelD_P105` | P1.05 | ídem |

La partición incluye una fila de cuatro cifras: sigma total (N1), sigma intradía por Parkinson,
riesgo fuera de sesión por vía N2 y por vía N3.

### 2.3 Riesgo de cola — ADN Pilar 2

| Panel | Función | Catálogo | Fuente |
| :-- | :-- | :-- | :-- |
| Riesgo posición larga (caídas) y posición corta (alzas), con selector de horizonte | `renderPilar2Widget`, `cambiarHorizontePilar2` | P2.03 + P2.04 | `/api/adn/pilar2` |

### 2.4 Paneles analíticos

| Panel | Función | Catálogo | Fuente |
| :-- | :-- | :-- | :-- |
| Persistencia del régimen | `renderizarScatterRachas` | P4.01 + P4.02 | `/api/streaks`, `/api/markov` |
| Línea de tiempo de volatilidad | `renderizarGraficoATR` | Visualización (anexo P1) | `/api/volatility` |
| Histograma de distribución de volatilidad | `renderizarHistogramaVolatilidad` | P1.01 | `/api/volatility` |
| Dispersión de retornos diarios | `renderizarGraficoDispersion` | Visualización (anexo P2) | `/api/volatility` |
| Matriz de memoria Hurst 7×3 | `renderHurstHeatmap` | P5.04 + P5.05 | `/api/volatility` |
| Matriz de eficiencia Kaufman 7×3 | `renderKaufmanHeatmap` | P5.01 + P5.02 + P5.03 | ídem |
| Z-Score y campana empírica | `renderZScoreChart`, `animateZScoreFrame` | Contingencia + P2.01 + P2.02 | ídem |
| Mapa de síntesis 2D Hurst × Kaufman | `renderHurstKaufmanScatter2D`, `drawScatter2DStep` | P5.06 | ídem |

---

## 3. Inventario — Escritorio 2 · Opening Gaps Desk

| Elemento | Catálogo | Fuente |
| :-- | :-- | :-- |
| Strip de KPIs: total de gaps, probabilidad de cierre mismo día, tamaño medio en ATR, gaps cerrados, profundidad media de cierre, deriva neta, razón de continuación intradía | **sin ficha** | `/api/gaps` |
| Dispersión: tamaño de gap contra volatilidad | **sin ficha** | `/api/gaps` |
| Matriz SDFP: régimen × estado × día de la semana | **sin ficha** | `/api/gaps` |
| Tasa de cierre: régimen × día | **sin ficha** | `/api/gaps` |
| Tasa de cierre: tamaño de gap × día | **sin ficha** | `/api/gaps` |
| Superficie de probabilidad 3D, con panel lateral de zonas y corte transversal | **sin ficha** | `/api/gaps/analyze_surface` |
| Análisis inferencial de celda: prueba Z y remuestreo bootstrap | **sin ficha** | `/api/gaps/analyze_cell` |
| Objetivos de reversión: cierre completo, mitad del hueco, tres cuartos | **sin ficha** | `/api/gaps` |

---

## 4. Capa agéntica

| Elemento | Fuente |
| :-- | :-- |
| Generación de informe experto y modal de resultados | `/api/agent/analyze`, `/api/agent/read_bridge` |
| Sondeo de progreso del agente | `startAgentPolling` |
| Gráficos inyectados por el agente (curva 5m, ventana USDCLP) | Bridge en disco |

**Endpoints consumidos por el dashboard: once.** `/assets`, `/volatility`, `/streaks`, `/markov`,
`/gaps`, `/gaps/analyze_cell`, `/gaps/analyze_surface`, `/agent/analyze`, `/agent/read_bridge`,
`/adn/pilar1`, `/adn/pilar2`.

---

## 5. Cobertura del catálogo

| Ámbito | Elementos en el dashboard | Con ficha en el catálogo |
| :-- | --: | --: |
| Escritorio 1 · Volatility Desk | 18 | 18 |
| Escritorio 2 · Opening Gaps Desk | 8 bloques | **0** |
| Capa agéntica | 3 | — |

En sentido inverso, de los 30 indicadores del catálogo:

| Pilar | Con panel | Total |
| :-- | --: | --: |
| 1 · Magnitud | 6 | 8 |
| 2 · Distribución | 3 | 6 |
| 3 · Geometría | 0 | 4 |
| 4 · Dinámica | 2 | 5 |
| 5 · Textura | 6 | 7 |

---

## 6. Hallazgos

### 6.1 · El Opening Gaps Desk está íntegramente fuera del catálogo — severidad alta

Ocho bloques funcionales, incluida una superficie de probabilidad por regresión de núcleo y un
motor de inferencia con remuestreo bootstrap, sin ficha, sin robustez declarada, sin nivel de dato
exigido y sin regla de publicación.

Es aproximadamente la mitad del producto operando sin el gobierno documental que se estableció para
la otra mitad. En particular, la superficie 3D **alimenta al agente redactor** a través de
`/api/gaps/analyze_surface`, de modo que el informe puede afirmar contenido que ninguna regla
respalda.

### 6.2 · Discrepancia de umbral entre el dashboard y el informe — severidad media

Ambas implementaciones calculan correctamente exceso de curtosis, pero clasifican con umbrales
distintos:

| Superficie | Umbral | Ubicación |
| :-- | :-- | :-- |
| Informe | `kurt > 0` | `expert_nlg.py` (corregido en el Pilar 2) |
| Dashboard | `kurt > 0.8` | `dashboard_volatilidad.html`, línea 2239 |

Un instrumento con exceso de curtosis entre 0 y 0,8 se declara de colas normales en pantalla y de
colas gruesas en el informe. Afecta hoy a tres celdas medidas: QQQ en régimen MEDIO (0,68), AAPL en
MEDIO (0,73) y USDCLP en MEDIO (0,51).

### 6.3 · Deriva documental en las tarjetas de cabecera — severidad media

El Manual de KPIs documenta cinco tarjetas: ATR, NATR, percentil de volatilidad, sesgo de
volatilidad y memoria de Hurst. El dashboard tiene cuatro: cierre, ATR, NATR y estado. **El
percentil de volatilidad y la memoria de Hurst ya no existen como tarjetas.** El manual describe una
interfaz que no corresponde a la actual.

### 6.4 · Identificador engañoso persistente — severidad baja

El contenedor `grafico-autocorr` aloja el histograma de distribución de volatilidad. No hay
autocorrelación en el dashboard: **P2.05 sigue sin implementar**. El riesgo es que un implementador
futuro concluya que ya existe.

### 6.5 · Doble implementación de asimetría y curtosis — severidad baja

`adn.py` es la fuente autorizada; `calculateSkewness` y `calculateKurtosis` permanecen en
JavaScript alimentando el panel Z-Score. Es la causa directa del hallazgo 6.2.

### 6.6 · La razón entre pérdida esperada y umbral es global, no condicional

La evidencia registra una razón estable en torno a 1,5. Ese valor corresponde al nivel **global**.
Condicionado al régimen desciende: QQQ en régimen ALTO a horizonte 1 arroja 5,50 / 4,04 = **1,36**.
La evidencia debe precisar el nivel de condicionamiento al que se refiere la constante.

---

## 7. Recomendaciones, por orden de prioridad

1. **Incorporar el Opening Gaps Desk al catálogo.** Es el vacío mayor y afecta a lo que el agente
   puede afirmar. Requiere una sesión de caracterización equivalente a la del Pilar 1: qué mide cada
   KPI, su robustez, su nivel de dato y su regla de publicación.
2. **Unificar el umbral de curtosis en 0,8 o en 0**, y aplicarlo a ambas superficies. Mi
   recomendación es 0, que es el valor teórico de la distribución normal; 0,8 es una convención sin
   fundamento declarado.
3. **Actualizar el Manual de KPIs** para que refleje las cuatro tarjetas actuales, y el catálogo para
   que la columna *Panel* refleje el estado real.
4. **Renombrar `grafico-autocorr`** a `grafico-histograma-natr`, liberando el nombre para P2.05.
5. **Precisar en la evidencia** que la razón entre pérdida esperada y umbral de 1,5 es una propiedad
   del nivel global.
