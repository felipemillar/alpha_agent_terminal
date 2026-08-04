---
title: "Catálogo de KPIs para la Caracterización del Instrumento (ADN)"
tags: [trading, volatilidad, kpis, catalogo, adn, qrt-solutions]
date: 2026-08-02
author: QRT Solutions x Pepperstone Research
alcance: Volatility Desk (pestaña 1). El Opening Gaps Desk queda fuera de este catálogo.
naturaleza: Especificación agnóstica al instrumento. Las mediciones concretas residen en docs/evidence/.
sources:
  - src/kpis.py
  - src/engine.py
  - src/server.py
  - frontend/dashboard_volatilidad.html
---

# Catálogo de KPIs para la Caracterización del Instrumento (ADN)

Registro canónico de los indicadores que sostienen la primera etapa del análisis: la
**caracterización descriptiva de la historia de un instrumento**.

Este documento es **agnóstico al instrumento**. Define qué se mide, cómo se calcula, qué aporta a la
caracterización y bajo qué condiciones es publicable. No contiene valores medidos: los resultados
sobre instrumentos concretos residen en [`docs/evidence/`](evidence/).

Documentos relacionados: el [Manual de KPIs](research/Manual_KPIs_Dashboard_Volatilidad.md) mantiene
la explicación narrativa; la [Especificación del Informe](research/Especificacion_Informe_Volatilidad.md)
define cómo se redactan los resultados.

---

## Convenciones

### Clasificación funcional

Solo la primera categoría pertenece a este catálogo. Las restantes se registran en el anexo de cada
pilar.

| Categoría | Definición |
| :-- | :-- |
| **ADN** | Propiedad persistente del instrumento, derivada de su historia completa. |
| Contingencia | Estado del día. Pertenece al informe de sesión, no a la ficha estructural. |
| Herramienta | Fórmula o regla operativa que **consume** indicadores en lugar de producirlos. |
| Visualización | Forma de representar datos. Pertenece al inventario del dashboard. |

### Estado de implementación

| Estado | Significado |
| :-- | :-- |
| **ACTIVO** | Calculado y **expuesto por la API**. El informe puede afirmarlo. |
| **LATENTE** | Existe código, no está conectado a ningún endpoint. El informe **no** puede afirmarlo. |
| **DOCUMENTADO** | Especificado en el corpus teórico, sin implementación. El informe **no** puede afirmarlo. |
| **PROPUESTO** | Definido y validado metodológicamente, pendiente de implementación. |

> El criterio de ACTIVO es la **exposición por API**, no la existencia de un panel. El agente
> redactor consume el backend, no la interfaz. La presencia de panel en el dashboard se registra
> por separado en la columna correspondiente y no condiciona lo que el informe puede afirmar.

> **Regla de anti-alucinación interna.** El agente redactor solo puede afirmar indicadores en estado
> ACTIVO. Los indicadores LATENTE y DOCUMENTADO están descritos con fórmula completa en este
> repositorio, lo que los vuelve especialmente fáciles de afirmar sin respaldo.

### Nivel de dato exigido

Cada instrumento tiene una **fecha efectiva distinta por nivel**. Se determina en la calibración.

| Nivel | Columnas necesarias | Falla característica |
| :-- | :-- | :-- |
| **N1** | Cierre | Prácticamente ninguna. |
| **N2** | Máximo y mínimo | Barras planas (`High == Low`) degeneran el True Range y sesgan los estimadores de rango. |
| **N3** | Apertura real | Aperturas sintéticas (`Open == Cierre previo`) o con ruido de medición invalidan el cálculo. |

### Tipo de umbral

| Código | Significado |
| :-- | :-- |
| **U** | Universal. Constante metodológica, idéntica para todo instrumento. |
| **D** | Derivado. Se calcula desde la propia historia del instrumento y debe publicarse con su fecha y muestra. |
| **—** | El indicador no requiere umbral. |

### Robustez del estimador

| Código | Significado |
| :-- | :-- |
| **A** | Alta. Estimador estable; converge con muestras moderadas. |
| **M** | Media. Sensible a decisiones de saneamiento o a la ventana elegida. Requiere declarar el criterio. |
| **B** | Baja. Estimador de varianza elevada o sesgo conocido. Debe subordinarse a nivel 3 y nunca encabezar un veredicto. |

---

## Pilar 1 — Magnitud y estructura de la volatilidad

*Responde: cuánta volatilidad tiene el instrumento, cómo se distribuye y hacia dónde se mueve.*

### 1.1 Espacio de estado de dos dimensiones

La caracterización se apoya en dos dimensiones ortogonales: el **nivel** de la volatilidad y su
**dirección de cambio**. Son a la volatilidad lo que la posición y la velocidad son a un móvil, y su
cruce genera la segmentación que estructura el resto del sistema.

| Dimensión | Variable continua | Clasificación | Umbral |
| :-- | :-- | :-- | :-- |
| **Nivel** | NATR(14) = `ATR(14) / Close × 100` | Régimen BAJO / MEDIO / ALTO | Terciles empíricos incondicionales `t₃₃`, `t₆₆` — **derivado** |
| **Dirección** | Razón `ATR(5) / ATR(14)` | Estado EXPANSIÓN / CONTRACCIÓN | 1,00, cambio de signo — **universal** |

**Denominación técnica.** El régimen es una *clasificación no paramétrica por terciles empíricos
incondicionales del NATR sobre la serie histórica completa*. El estado es un *indicador de dirección
de la volatilidad por razón de dos escalas temporales del ATR*.

#### Fundamento metodológico

1. **No paramétrica.** No asume forma de la distribución. A diferencia de GARCH o de un modelo de
   cambio de régimen de Markov, no requiere especificar un modelo ni estimar parámetros, lo que
   resulta apropiado ante distribuciones con colas gruesas.
2. **Reparto de masa uniforme.** Los terciles asignan por construcción un tercio de la muestra a cada
   régimen, maximizando la potencia estadística de cada celda. Una clasificación por desviaciones
   típicas dejaría el régimen extremo con muestra insuficiente.
3. **Umbrales absolutos.** Al calcularse sobre la serie completa, un régimen ALTO de hace veinte años
   y uno actual designan el mismo nivel de volatilidad. Esto hace comparables épocas distintas, que
   es el requisito de una lectura estructural.
4. **Dimensiones complementarias.** El nivel no determina la dirección. La dependencia entre ambos
   ejes debe verificarse en la calibración y ser moderada; si un eje predijera al otro, la
   segmentación cruzada perdería sentido.

#### Propiedad esperada del umbral de dirección

El umbral de 1,00 no coincide con la mediana de la razón `ATR(5)/ATR(14)`, que tiende a situarse por
debajo de la unidad. En consecuencia, menos de la mitad de las sesiones se clasifican en expansión.
Esto no constituye un defecto del corte: refleja la asimetría estructural de la volatilidad, que se
expande en episodios breves y se contrae en períodos prolongados. El umbral conserva su
justificación por corresponder al cambio de signo de la derivada.

#### Limitaciones que deben declararse en cada ficha

1. **Los umbrales son revisables.** Dependen de la muestra disponible y se recalculan al extender la
   serie. La ficha publica `t₃₃` y `t₆₆` con su fecha de cálculo y tamaño de muestra, y advierte que
   la clasificación de sesiones pasadas puede modificarse en revisiones posteriores.
2. **Las etiquetas históricas incorporan información posterior.** El régimen de una sesión antigua
   depende de datos futuros respecto de ella. Es legítimo en una lectura descriptiva de la historia y
   constituiría contaminación si se empleara como señal en una prueba retrospectiva.
3. **Supone estacionariedad distribucional, que no se cumple.** Se mitiga declarando el período de
   referencia y publicando el reparto de régimen por época (P1.02).
4. **El reparto global por régimen es 33/33/33 por construcción** y por tanto no es informativo. La
   información reside en su distribución temporal.

### 1.2 Variables base

Insumos del pilar. No son indicadores reportables.

| Variable | Definición | Uso |
| :-- | :-- | :-- |
| True Range | `max(H−L, \|H−C₋₁\|, \|L−C₋₁\|)` | Absorbe el salto de apertura por diseño (Wilder, 1978) |
| ATR(14), ATR(5) | Media suavizada de Wilder del True Range | Escalas larga y corta de la dimensión dirección |
| NATR(14) | `ATR(14) / Close × 100` | Magnitud relativa comparable entre instrumentos |

> El **ATR en unidades de precio** no forma parte del ADN: no es comparable entre instrumentos y su
> valor cambia con el nivel de precio a lo largo de las décadas. Es una unidad operativa para stops y
> objetivos, y pertenece a la capa de aplicación.

### 1.3 Indicadores

Implementados en [`src/adn.py`](../src/adn.py) y expuestos en `GET /api/adn/pilar1?asset=<nombre>`.

| ID | Indicador | Definición operativa | Aporte al ADN | Umbral | Rob. | Estado | Panel | Nivel |
| :-- | :-- | :-- | :-- | :-: | :-: | :-- | :-: | :-: |
| P1.01 | Distribución del NATR y umbrales de régimen | Distribución empírica completa del NATR(14); `t₃₃` y `t₆₆` como sus dos cortes, con prueba de estabilidad sobre fracciones crecientes de la serie | Identidad de magnitud del instrumento. La distribución es el ADN; el valor de un día es contingencia. | D | A | ACTIVO | sí | N2 |
| P1.02 | Reparto de régimen por época | Proporción de sesiones en cada régimen por bloque temporal fijo, más NATR medio del bloque | Cuantifica la no estacionariedad y delimita el período de referencia válido. | D | A | ACTIVO | sí | N2 |
| P1.03 | Distribución de la razón de dirección | Percentiles de `ATR(5)/ATR(14)` sobre la historia completa | Aporta la resolución que la etiqueta binaria pierde: dos valores muy distintos comparten etiqueta. | U | A | ACTIVO | sí | N2 |
| P1.04 | Persistencia del estado direccional | Distribución de duración de las rachas de expansión y de contracción | Establece cuánto dura una fase direccional de la volatilidad una vez iniciada. | — | A | ACTIVO | sí | N2 |
| P1.05 | Dependencia entre nivel y dirección | Tabla de contingencia régimen × estado, con verificación de celda mínima | Verifica que la segmentación cruzada tiene contenido y que sus celdas están pobladas. Valida el propio diseño. | — | A | ACTIVO | sí | N2 |
| P1.06 | Volatilidad de Parkinson | `(1/4·ln2)·[ln(H/L)]²` promediada, excluyendo barras planas del promedio sin eliminarlas de la serie | Componente **intradía** de la varianza, estimado sin usar la apertura. Cinco veces más eficiente que la desviación de cierres. | — | M | ACTIVO | sí | N2 |
| P1.07 | Descomposición fuera de sesión / intradía | Varianza total menos varianza de Parkinson (N2); alternativamente partición entre `ln(O/C₋₁)` y `ln(C/O)` (N3), sujeta a tres verificaciones | Fracción del riesgo que se materializa cuando la posición no puede gestionarse. Determina si la defensa es el stop o el tamaño. | — | M | ACTIVO | sí | N2 / N3 |
| P1.08 | Razón de régimen a horizonte medio | `ATR(14) / ATR(50)`, con cortes en 0,85 y 1,25 | Misma dimensión de dirección que P1.03 en horizonte más largo. Complementario, no sustituto. | U | A | ACTIVO | sí | N2 |

**Puerta de publicación de P1.07.** El método N3 solo se publica si supera tres verificaciones
automáticas: proporción de aperturas sintéticas bajo umbral, correlación entre ambas mitades del día
no marcadamente negativa, y convergencia con el método N2 dentro del margen admitido. Si alguna
falla, el endpoint devuelve `disponible: false` con el motivo, en lugar de una cifra.

**Notas de robustez.** P1.06 subestima sistemáticamente por asumir cotización continua, y las barras
planas deben excluirse de su promedio sin eliminarlas de la serie. P1.07 exige contrastar ambos
métodos: una divergencia material entre la vía N2 y la vía N3 señala un problema en la columna de
apertura.

### 1.4 Anexo del pilar

| Entrada | Categoría | Destino |
| :-- | :-- | :-- |
| NATR del día y su percentil | Contingencia | Informe de sesión |
| Etiquetas de régimen y estado vigentes | Contingencia | Informe de sesión |
| Serie temporal de volatilidad coloreada por régimen | Visualización | Inventario del dashboard |
| ATR en unidades de precio | Herramienta | Capa de aplicación |
| Período de referencia | Declaración de validez | Encabezado de la ficha |

---

## Pilar 2 — Distribución de retornos y riesgo de cola

*Responde: qué forma tiene el riesgo del instrumento y qué ocurre en sus extremos.*

### 2.1 Indicadores

| ID | Indicador | Definición operativa | Aporte al ADN | Umbral | Rob. | Estado | Nivel |
| :-- | :-- | :-- | :-- | :-: | :-: | :-- | :-: |
| P2.01 | Asimetría de la distribución | Tercer momento estandarizado de los retornos diarios | Indica si las caídas superan en magnitud a las subidas. Primer indicio direccional del ADN. | U | M | ACTIVO | N1 |
| P2.02 | Curtosis | Cuarto momento estandarizado | Frecuencia de eventos extremos frente a la normal. Explica la activación de stops considerados improbables. | U | **B** | ACTIVO | N1 |
| P2.03 | Umbral de pérdida extrema | Percentil 5 de los retornos diarios, condicionado a régimen y a lado de la posición | Define a partir de qué pérdida una sesión es extrema para este instrumento. | U | A | ACTIVO | N1 |
| P2.04 | Pérdida esperada en escenario extremo | Media del 5% de retornos más adversos, condicionada a régimen y a lado | Traduce la curtosis a una cifra de pérdida. Es el valor que el dimensionamiento debe soportar. | U | A | ACTIVO | N1 |
| P2.05 | Autocorrelación del retorno absoluto | Autocorrelación de `\|Rt\|` a rezagos 1, 5 y 20 | **Verifica el supuesto que sostiene todo el marco de regímenes**: que la volatilidad se agrupa. Sin este indicador, la existencia de regímenes es una premisa no comprobada. | — | A | DOCUMENTADO | N1 |
| P2.06 | Valor en riesgo por teoría de valores extremos | Ajuste de una distribución de Pareto generalizada sobre la cola | Refinamiento paramétrico de P2.04 para cuantiles muy altos. Segunda etapa. | U | B | DOCUMENTADO | N1 |

**Notas de robustez.** La curtosis está dominada por las pocas observaciones más extremas de la
muestra y su estimador tiene varianza elevada: debe subordinarse a nivel 3 y ceder el titular a
P2.04, que expresa el mismo fenómeno de forma estable. P2.06 exige cuidado: con muestras del orden de
algunos miles de sesiones, los cuantiles al 99% y superiores resultan inestables.

### 2.2 Anexo del pilar

| Entrada | Categoría | Destino |
| :-- | :-- | :-- |
| Z-Score del retorno del día | Contingencia | Informe de sesión |
| Campana empírica doble (régimen contra global) | Visualización | Inventario del dashboard |
| Dispersión de retorno contra NATR | Visualización | Control de calidad |
| Regla de Weissman (\|Z\| > 2) | Herramienta | Capa de aplicación |

---

## Pilar 3 — Geometría de la posición

*Responde: qué le cuesta al operador tomar cada lado del instrumento.*

> Pilar sin indicadores ACTIVO. Es el único que convierte la caracterización en una decisión de
> tamaño, y hoy existe solo como especificación.

### 3.1 Indicadores

| ID | Indicador | Definición operativa | Aporte al ADN | Umbral | Rob. | Estado | Nivel |
| :-- | :-- | :-- | :-- | :-: | :-: | :-- | :-: |
| P3.01 | Excursión desde la apertura | Dos mediciones independientes en múltiplos del ATR previo: recorrido al alza `(H−O)/ATR₋₁` y a la baja `(O−L)/ATR₋₁`. Mediana y percentil 80, condicionadas al régimen. | Geometría de la sesión. Convierte la distancia del stop en una elección de probabilidad en lugar de una convención. Las cuatro celdas por lado derivan de estas dos mediciones. | — | A | PROPUESTO | N3 |
| P3.02 | Relación recorrido a favor / en contra | Cociente de las dos mediciones de P3.01, calculado para cada lado | **Titular del pilar.** Cuantifica si el instrumento favorece estructuralmente la compra o la venta. Un valor distinto de 1,00 indica asimetría direccional. | U | A | PROPUESTO | N3 |
| P3.03 | Prima direccional por régimen | Rendimiento medio diario por régimen, acompañado de su error estándar y estadístico t | Establece en qué régimen se remunera asumir dirección. Se publica *no medible* cuando no supera significancia. | U | M | PROPUESTO | N1 |
| P3.04 | Ratio cuerpo-rango | `\|Close − Open\| / (High − Low)` | Indica si la sesión resuelve direccionalmente o revierte dentro del día. Complementa P3.01. | — | A | DOCUMENTADO | N3 |

**Notas de robustez.** P3.03 rara vez alcanza significancia fuera de instrumentos con deriva marcada;
la ausencia de prima medible es en sí misma una afirmación válida del ADN y debe reportarse como tal.
Tres de los cuatro indicadores son de nivel N3, por lo que este pilar es el más expuesto a la calidad
de la columna de apertura.

### 3.2 Anexo del pilar

| Entrada | Categoría | Destino |
| :-- | :-- | :-- |
| Dimensionamiento por ATR | Herramienta | Capa de aplicación. El factor de ajuste debe provenir de P3.01, no de una convención de libro. |

---

## Pilar 4 — Dinámica de regímenes y riesgo en el tiempo

*Responde: cuánto duran los estados del instrumento y con qué probabilidad cambian.*

### 4.1 Indicadores

| ID | Indicador | Definición operativa | Aporte al ADN | Umbral | Rob. | Estado | Nivel |
| :-- | :-- | :-- | :-- | :-: | :-: | :-- | :-: |
| P4.01 | Distribución de duración de rachas | Número de episodios y distribución completa de su duración, por régimen | Cuánto persiste un estado una vez instalado. La distribución completa reemplaza al par mediana-máxima. | — | M | ACTIVO (parcial) | N2 |
| P4.02 | Matriz de transición de Markov | Probabilidades de transición de primer orden entre regímenes | Riesgo en el tiempo: probabilidad de cambio de estado en la sesión siguiente. | — | M | ACTIVO | N2 |
| P4.03 | Tiempo de normalización | Sesiones desde la entrada al decil superior **móvil** del NATR hasta el retorno a su mediana **móvil** | Horizonte de planificación tras un episodio extremo. Único indicador que conserva referencia móvil por diseño. | U | A | PROPUESTO | N2 |
| P4.04 | Descomposición de varianza condicional | Estimación GARCH: componente transitorio contra persistente | Distingue el choque puntual del cambio estructural de volatilidad. Segunda etapa. | — | M | DOCUMENTADO | N1 |
| P4.05 | Cambio de régimen por estados latentes | Modelo oculto de Markov sobre la serie de volatilidad | Alternativa probabilística a la clasificación por terciles. Segunda etapa. | — | M | DOCUMENTADO | N1 |

**Notas de robustez.** La **racha máxima** de P4.01 es sensible a la definición de régimen: con
umbrales absolutos un instrumento puede permanecer en un régimen durante períodos muy prolongados,
mientras que con referencia móvil eso resulta imposible por construcción. Debe reportarse la
distribución, no el máximo aislado. P4.02 requiere reevaluación bajo umbrales absolutos: la diagonal
de persistencia se infla y el indicador pierde poder informativo.

> **Advertencia arquitectónica.** P4.05 no es aditivo. Adoptar un modelo de estados latentes
> **sustituiría** la clasificación por terciles y obligaría a reconstruir toda la segmentación
> cruzada. Es una decisión de arquitectura, no una incorporación incremental.

### 4.2 Anexo del pilar

| Entrada | Categoría | Destino |
| :-- | :-- | :-- |
| Régimen vigente y sesiones transcurridas en él | Contingencia | Informe de sesión |

---

## Pilar 5 — Textura del movimiento

*Responde: si la volatilidad del instrumento se traduce en avance direccional o en ruido.*

### 5.1 Indicadores

| ID | Indicador | Definición operativa | Aporte al ADN | Umbral | Rob. | Estado | Nivel |
| :-- | :-- | :-- | :-- | :-: | :-: | :-- | :-: |
| P5.01 | Efficiency Ratio de Kaufman | `\|ΔP neto\| / Σ\|pasos\|` sobre ventanas de 10, 20 y 50 sesiones. Bandas: >0,60 direccional, 0,30–0,60 moderado, <0,30 errático | Cuán limpio o ruidoso es el movimiento. Estimador más estable del pilar. | U | A | ACTIVO | N1 |
| P5.02 | Matriz de eficiencia por régimen y dirección | Efficiency Ratio segmentado por régimen-estado y por dirección del movimiento | Identifica en qué condiciones el movimiento resulta aprovechable, y si difiere entre alzas y bajas. | U | A | ACTIVO | N1 |
| P5.03 | Factor de ruido | `ATR / ER` | Señala volatilidad no comerciable: mucho recorrido con poco avance neto. | — | A | ACTIVO | N2 |
| P5.04 | Exponente de Hurst | Rango reescalado sobre la serie de precios. Bandas: >0,55 persistente, 0,45–0,55 caminata aleatoria, <0,45 reversión | Memoria de la serie. Distingue si los movimientos se extienden o se corrigen. | U | **B** | ACTIVO | N1 |
| P5.05 | Matriz de memoria por régimen y dirección | Exponente de Hurst segmentado por régimen-estado y dirección | Revela que la memoria difiere entre subidas y bajadas, hallazgo directamente operativo. | U | **B** | ACTIVO | N1 |
| P5.06 | Mapa de síntesis bidimensional | Cada sesión histórica situada en el plano memoria × eficiencia, clasificada en cuatro cuadrantes | Huella de comportamiento del instrumento: dónde se concentra su masa de probabilidad. | U | M | ACTIVO | N1 |
| P5.07 | Estacionalidad por día de la semana | Rango relativo de la sesión según jornada de la semana | Efecto de calendario sobre la volatilidad. Implementado en el Gaps Desk, ausente en este escritorio. | — | A | DOCUMENTADO | N2 |

**Notas de robustez.** El exponente de Hurst por rango reescalado presenta **sesgo al alza en
ventanas cortas**, que tiende a clasificar la mayoría de las sesiones como persistentes. Para la
lectura estructural debe primar el valor calculado sobre la serie completa; las ventanas cortas se
usan como apoyo visual, no como base de veredicto. Las matrices segmentadas de P5.02 y P5.05 dividen
la muestra en muchas celdas: **debe marcarse visualmente toda celda que no alcance el mínimo de
sesiones definido en la calibración**.

### 5.2 Fuera de alcance

| Entrada | Motivo |
| :-- | :-- |
| Curva de volatilidad intradía por hora | Requiere datos de frecuencia intradía. No calculable con OHLC diario. |

---

## Resumen del catálogo

| Pilar | ACTIVO | LATENTE | DOCUMENTADO | PROPUESTO | Total | Panel en dashboard |
| :-- | --: | --: | --: | --: | --: | --: |
| 1 · Magnitud | **8** | 0 | 0 | 0 | 8 | 6 |
| 2 · Distribución | **4** | 0 | 2 | **0** | 6 | 3 |
| 3 · Geometría | **0** | 0 | 1 | 3 | 4 | 0 |
| 4 · Dinámica | 2 | 0 | 2 | 1 | 5 | 2 |
| 5 · Textura | 6 | 0 | 1 | 0 | 7 | 6 |
| **Total** | **20** | **0** | **6** | **4** | **30** | 17 |

El pilar 1 está completo en la capa de cálculo y API. Siete de sus ocho indicadores carecen todavía
de representación en el dashboard, lo que no restringe lo que el informe puede afirmar pero sí lo
que el usuario ve.

Distribución por robustez: 18 indicadores de robustez alta, 8 media y 4 baja. Los cuatro de robustez
baja —curtosis, valor en riesgo por valores extremos y las dos entradas basadas en el exponente de
Hurst— no pueden encabezar un veredicto.

---

## Procedimiento de calibración por instrumento

Todo instrumento incorporado al sistema atraviesa esta secuencia antes de que su ficha sea
publicable. Es lo que convierte una especificación agnóstica en una caracterización concreta.

**1. Saneamiento.** Descartar retornos diarios imposibles según el umbral definido para la clase de
activo. Registrar el número de filas eliminadas.

**2. Época efectiva por nivel de dato.** Determinar tres fechas de inicio distintas:

- **N1**: primera sesión con cierre válido.
- **N2**: primera sesión con rango intradía real, y proporción global de barras planas.
- **N3**: primer año desde el cual la proporción de aperturas sintéticas se mantiene por debajo del
  umbral admitido en todos los años posteriores.

**3. Verificación de la columna de apertura.** Para habilitar los indicadores de nivel N3, contrastar
la descomposición por apertura contra la vía de Parkinson. Una divergencia material entre ambas
señala un problema en la apertura y obliga a declarar los indicadores N3 como no disponibles.

**4. Umbrales derivados.** Calcular `t₃₃` y `t₆₆` sobre la serie saneada. Registrar valor, fecha de
cálculo y tamaño de muestra.

**5. Validación del diseño de segmentación.** Construir la tabla de contingencia régimen × estado y
verificar que ninguna celda quede por debajo del mínimo de sesiones. Verificar que la dependencia
entre ambos ejes sea moderada.

**6. Período de referencia.** Calcular el reparto de régimen por bloque temporal y contrastar el
percentil del valor actual sobre historia completa contra el de los últimos años. Si divergen de
forma material, declararlo en el encabezado de la ficha.

### Requisitos mínimos de muestra

| Ámbito | Mínimo exigido |
| :-- | :-- |
| Serie completa para publicar una ficha | Suficiente para que los umbrales derivados hayan convergido |
| Celda de una matriz segmentada | Marcar visualmente por debajo del mínimo; suprimir la afirmación si es marginal |
| Estadístico basado en un promedio | Debe superar la prueba de significancia o publicarse como *no medible* |

---

## Reglas de publicación

1. El informe solo afirma indicadores en estado **ACTIVO**.
2. Toda cifra basada en un promedio se publica con su prueba de significancia y se sustituye por
   *no medible* si no la supera.
3. Todo indicador de nivel **N3** exige la verificación previa de la apertura descrita en la
   calibración. Si falla, se declara *no disponible* en lugar de publicar una cifra.
4. Todo bloque declara el período de referencia sobre el que fue calculado.
5. Todo umbral **derivado** se publica con su valor, fecha de cálculo y tamaño de muestra.
6. Ningún indicador de **robustez baja** encabeza un veredicto; se subordina al nivel de detalle
   técnico.

---

## Deuda técnica detectada en la auditoría de implementación

| Hallazgo | Ubicación | Efecto |
| :-- | :-- | :-- |
| `calculate_returns` sin uso | `kpis.py:26` | Código muerto |
| `calculate_volatility_zscore` sin uso | `kpis.py:33` | Duplica el propósito de `calculate_zscore_metrics` |
| `calculate_parkinson_volatility` sin uso | `kpis.py:43` | Sustituida por `adn.varianza_parkinson`, que devuelve la varianza diaria en lugar de una serie móvil anualizada y excluye barras planas del promedio. La función original quedó huérfana y debe eliminarse. |
| Dos implementaciones del Efficiency Ratio | `kpis.py:54` y `kpis.py:401` | Riesgo de divergencia entre paneles que reportan el mismo indicador |
