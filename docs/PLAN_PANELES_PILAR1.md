---
title: "Plan de implementación — Paneles del Pilar 1 en el dashboard"
tags: [plan, frontend, dashboard, adn, pilar1]
date: 2026-08-03
estado: propuesto
depende_de: docs/CATALOGO_KPIS_ADN.md, src/adn.py
---

# Plan de implementación — Paneles del Pilar 1

Los ocho indicadores del Pilar 1 están calculados y expuestos en `GET /api/adn/pilar1?asset=<nombre>`.
Solo P1.01 tiene representación en el dashboard. Este plan cubre los siete restantes.

**Alcance:** frontend exclusivamente, más dos extensiones menores del backend identificadas en la
fase 0. No modifica la metodología ni el catálogo.

---

## 1. Decisión de arquitectura previa

> **Los paneles del ADN quedan exentos de la barra de filtros globales.**

El dashboard filtra por régimen y estado mediante `aplicarFiltroGlobal7x3()`
([línea 2396](../frontend/dashboard_volatilidad.html)). Los indicadores del Pilar 1 describen la
**historia incondicional completa** del instrumento: aplicarles ese filtro sería conceptualmente
incorrecto y, en el caso de P1.05, directamente circular — la tabla de contingencia mide la relación
entre régimen y estado, de modo que filtrar por ellos vaciaría el propio objeto de medición.

Consecuencias operativas:

1. Los contenedores de estos paneles **no se registran** en el listener de la barra global.
2. Cada panel lleva una marca visible de *lectura estructural — no afectada por los filtros*, para
   que el usuario no interprete que el filtro está roto.
3. Se ubican en una sección propia, separada de los paneles de contingencia.

Esta separación es la misma que la especificación del informe ya declara entre base histórica y
contingencia. El dashboard todavía no la refleja.

---

## 2. Ubicación y estructura

**Sección nueva al final de `#desk-volatilidad`** ([línea 1062](../frontend/dashboard_volatilidad.html)),
titulada *Caracterización Estructural del Instrumento*, colapsable y cerrada por defecto.

Justificación del emplazamiento: los indicadores estructurales cambian con lenta cadencia y no
compiten con la lectura diaria. Colocarlos al final respeta el orden historia → estado actual que la
especificación del informe ya define.

**Consolidación: siete indicadores en cinco paneles.**

| Panel | Indicadores | Título propuesto |
| :-- | :-- | :-- |
| A | P1.02 | Estructura temporal del régimen |
| B | P1.03 + P1.08 | Dirección de la volatilidad |
| C | P1.04 | Persistencia del estado direccional |
| D | P1.05 | Validación de la segmentación |
| E | P1.06 + P1.07 | Partición del riesgo diario |

P1.03 y P1.08 miden la misma dimensión en horizontes distinto (corto y medio); presentarlos juntos
evita que el lector los confunda con métricas independientes. P1.06 es el insumo de P1.07 y carece de
lectura autónoma.

Disposición: paneles A y D en `.dashboard-grid` (dos columnas), B y C en una segunda fila, E a ancho
completo por contener una fila de KPI.

---

## 3. Fase 0 — Extensiones de backend requeridas

Dos indicadores necesitan más resolución de la que hoy devuelve el endpoint.

**0.1 · `adn.persistencia_estado` debe devolver la distribución completa de duraciones**, no solo
mediana, percentil 80 y máxima. El panel C es un histograma y hoy solo hay cuatro estadísticos.
Devolver los conteos por duración agrupados en tramos.

> Este mismo componente sirve a **P4.04 (histograma de persistencia de regímenes)**, que ya figura en
> el catálogo y en `brainstorming_canvas.md`. Conviene construirlo parametrizado por serie de
> etiquetas desde el inicio y usarlo dos veces, en lugar de escribir dos histogramas.

**0.2 · `adn.razon_direccion` debe devolver los tramos del histograma** además de los percentiles. El
panel B representa la distribución con una referencia en 1,00 y los percentiles no bastan.

Ambos cambios son aditivos sobre `src/adn.py` y no alteran las claves existentes.

---

## 4. Especificación por panel

Se aplica la heurística de forma: el trabajo que debe hacer el lector determina el tipo de gráfico, y
el color se decide al final.

### Panel A — Estructura temporal del régimen (P1.02)

- **Trabajo del lector:** ver cómo se reparte el tiempo entre regímenes a lo largo de las décadas.
  Es parte-a-todo con eje temporal.
- **Forma:** barra apilada **horizontal**, un renglón por bloque de cinco años, tres segmentos que
  suman 100%. Horizontal porque las etiquetas de bloque son largas.
- **Color:** los regímenes son una escala **ordenada** (BAJO < MEDIO < ALTO), no categorías nominales.
  Formalmente corresponde una rampa ordinal de un solo tono. **Sin embargo**, el dashboard ya usa
  amarillo/verde/rojo para régimen en todos los paneles, definidos en `classify_regimes_full`.
  *Recomendación:* conservar esa paleta por coherencia con el resto de la interfaz, y registrar la
  alternativa (rampa Viridis de tres pasos) como decisión pendiente. Cambiarla aquí y no en el resto
  produciría dos lenguajes cromáticos para la misma variable.
- **Detalles:** separación de 2 px entre segmentos apilados; etiqueta directa dentro del segmento solo
  cuando quepa con holgura, en caso contrario al margen; el NATR medio del bloque como anotación al
  final de cada renglón.
- **Lectura acompañante:** una línea de texto con el contraste de percentiles (historia completa
  frente a últimos cinco años), que es la conclusión operativa del panel.

### Panel B — Dirección de la volatilidad (P1.03 + P1.08)

- **Trabajo del lector:** ver dónde cae la razón actual dentro de su distribución histórica y de qué
  lado del umbral está. Es posición respecto de una línea base.
- **Forma:** histograma de la razón `ATR(5)/ATR(14)` con línea de referencia vertical en 1,00.
- **Color:** trabajo **divergente** — dos tonos opuestos, cálido y frío, con el umbral como punto
  neutro. Contracción de un lado, expansión del otro. No una rampa de magnitud.
- **P1.08 (VRR)** se representa debajo como **medidor horizontal**: una pista con las dos zonas de
  umbral (0,85 y 1,25) y una marca en el valor actual. Un solo valor contra un límite no justifica un
  gráfico; el medidor es la forma correcta.
- **Detalles:** anotar la mediana sobre el histograma, dado que la propiedad relevante es que se sitúa
  bajo 1,00. Indicar el porcentaje de sesiones en expansión como cifra, no como segundo gráfico.

### Panel C — Persistencia del estado direccional (P1.04)

- **Trabajo del lector:** comparar dos distribuciones de duración.
- **Forma:** histograma doble de duración de rachas, expansión y contracción. Dos series.
- **Color:** categórico de dos tonos, coherente con los asignados en el panel B a cada estado.
- **Detalles:** eje horizontal en tramos de duración, vertical en número de rachas. Marcar la mediana
  de cada serie con una línea directa etiquetada; la cola larga se lee del propio histograma. Con dos
  series, leyenda obligatoria.
- **Requiere la extensión 0.1.**

### Panel D — Validación de la segmentación (P1.05)

- **Trabajo del lector:** comprobar que las celdas del cruce están pobladas y observar el gradiente.
- **Forma:** mapa de calor de 3×2 (régimen × estado).
- **Color:** **secuencial de un solo tono** — Viridis, coherente con los tres mapas de calor
  existentes. Es magnitud, no identidad.
- **Detalles:** con solo seis celdas, **etiquetar todas** con porcentaje y número de sesiones; la
  prohibición de rotular cada punto aplica a gráficos densos, no a una rejilla de seis. Reutilizar el
  tratamiento de **borde punteado para celdas bajo el mínimo** ya empleado en la matriz SDFP del Gaps
  Desk: es un patrón establecido del proyecto y debe mantenerse consistente.
- **Lectura acompañante:** el veredicto binario que ya devuelve el endpoint (`celdas_validas`), en
  texto, porque es la conclusión del panel.

### Panel E — Partición del riesgo diario (P1.06 + P1.07)

- **Trabajo del lector:** saber qué fracción del riesgo ocurre fuera de la sesión. Son cifras de
  titular, no una serie.
- **Forma:** fila de KPI con cuatro cifras — sigma total, sigma intradía por Parkinson, fracción fuera
  de sesión por método N2, y la misma por método N3 — acompañada de **una barra apilada horizontal de
  dos segmentos** que representa la partición. Dos segmentos es un uso legítimo de barra apilada;
  un gráfico circular de dos porciones no lo sería.
- **Color:** dos tonos de una misma rampa, dado que ambos segmentos son partes del mismo total.
- **Comportamiento crítico:** cuando el endpoint devuelve `n3.disponible: false`, la celda del método
  N3 **muestra el texto del motivo**, no una cifra ni un cero. Es la regla de publicación del catálogo
  hecha visible, y el único panel donde el estado de no disponibilidad es información valiosa.
- **Detalles:** la divergencia entre ambos métodos se muestra como cifra secundaria; es el indicador
  de confianza de la medición.

---

## 5. Integración en el código

| Punto | Ubicación actual | Cambio |
| :-- | :-- | :-- |
| Contenedores HTML | fin de `#desk-volatilidad`, tras la línea ~1410 | Una sección colapsable con los cinco paneles |
| Estilos | bloque `<style>` existente | Reutilizar `.dashboard-grid`, `.grid-panel`, `.kpi-strip`. Sin clases nuevas salvo la marca de "lectura estructural" |
| Obtención de datos | `cargarDatosActivo()`, línea 2776 | Una petición adicional a `/api/adn/pilar1`, en paralelo con las existentes |
| Renderizado | — | Cinco funciones nuevas siguiendo la convención `renderizar*` / `render*` ya presente |
| Filtros globales | `aplicarFiltroGlobal7x3()`, línea 2396 | **Ningún cambio.** Los paneles no se registran deliberadamente |

**Renderizado diferido.** El dashboard ya instancia dieciséis gráficos de Plotly. Los cinco nuevos
deben dibujarse al desplegar la sección, no durante la carga inicial, para no penalizar el tiempo de
apertura. La petición al endpoint sí puede lanzarse en paralelo desde el inicio.

**Caché.** El endpoint recalcula la caracterización completa en cada llamada. Los resultados son
estructurales y solo cambian cuando se extiende la serie: conviene cachear en el servidor por activo,
invalidando con la fecha de modificación del CSV.

---

## 6. Secuencia propuesta

| Fase | Contenido | Verificable por |
| :-- | :-- | :-- |
| **0** | Extensiones 0.1 y 0.2 en `src/adn.py`; caché por activo en el endpoint | Respuesta del endpoint contiene los tramos de histograma |
| **1** | Sección colapsable, marca de lectura estructural, petición y cableado de datos | La sección abre y muestra las cifras en crudo |
| **2** | Paneles D y E — los de mayor valor por unidad de esfuerzo: un mapa de calor de seis celdas y una fila de KPI, ambos sobre patrones existentes | Coinciden con la salida de `python src/adn.py` |
| **3** | Paneles A y B — barra apilada y histograma divergente con medidor | Ídem |
| **4** | Panel C — histograma doble; construir el componente parametrizado para reutilizarlo en P4.04 | Ídem |
| **5** | Actualizar la columna *Panel* del catálogo a 8 de 8 | Tabla de resumen del catálogo |

Las fases 2 a 4 son independientes entre sí y pueden abordarse en cualquier orden.

---

## 7. Riesgos

| Riesgo | Mitigación |
| :-- | :-- |
| `dashboard_volatilidad.html` tiene 5.407 líneas con Javascript embebido, y otra sesión puede editarlo en paralelo — ya ocurrió con `kpis.py` durante el desarrollo del Pilar 1 | Implementar en un bloque contiguo al final del escritorio, minimizando la superficie de conflicto. Verificar el estado del archivo antes de editar |
| Duplicación del lenguaje cromático de régimen si el panel A adopta una rampa distinta a la del resto | Decidir la paleta **antes** de la fase 3, y aplicarla al dashboard completo o a ninguna parte |
| El usuario interpreta que los filtros globales están averiados al no afectar a estos paneles | La marca de "lectura estructural" es requisito de la fase 1, no un adorno posterior |
| Coste de carga con veintiún gráficos de Plotly | Renderizado diferido al desplegar la sección |

---

## 8. Criterio de finalización

1. Los cinco paneles reproducen exactamente la salida de `python src/adn.py` para ambos instrumentos.
2. El panel E muestra el motivo textual cuando el método N3 no supera su puerta de publicación,
   verificable forzando el fallo con un instrumento de apertura sintética.
3. Ningún panel de la sección responde a la barra de filtros globales.
4. Todo panel dispone de su equivalente en tabla, conforme a las reglas de accesibilidad.
5. La columna *Panel* del catálogo queda en 8 de 8 para el Pilar 1.
