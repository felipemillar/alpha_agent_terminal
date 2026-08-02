---
title: "Guía de Utilidad: Mapa de Síntesis 2D (Constelación Hurst H × Kaufman ER)"
tags: [trading, volatilidad, hurst, kaufman, efficiency-ratio, base-rates, adn-activo, qrt-solutions]
date: 2026-07-28
author: QRT Solutions x Pepperstone Research
sources:
  - src/kpis.py#calculate_hurst_kaufman_scatter
  - frontend/dashboard_volatilidad.html#MAPA_SINTESIS_2D
  - "[[Resumen_Perfilamiento_Volatilidad_ADN_Activo]]"
  - "[[Caracterizacion_Volatilidad_Intradia]]"
---

# Guía de Utilidad: Mapa de Síntesis 2D (Constelación Hurst H × Kaufman ER)

> **Cómo usar esta guía.** Es el manual de lectura del panel *MAPA DE SÍNTESIS 2D* del dashboard.
> No enseña *cuándo* comprar o vender un día concreto; enseña a **caracterizar el instrumento** —
> a leer su historia como una huella de comportamiento— para decidir **qué familia de estrategia
> tiene sentido siquiera intentar** sobre ese activo. Es la capa de diagnóstico previa a cualquier
> estrategia, en línea con el marco "ADN del Activo".

---

## 1. Propósito y encuadre

**Qué NO es la matriz.** No es un generador de señales de entrada/salida. Ningún cuadrante dice
"compra aquí". El día actual dentro de la nube es solo *un* punto entre miles y no debe leerse como
gatillo operativo.

**Qué SÍ es.** Es la **huella de comportamiento estocástico** del instrumento a lo largo de toda su
historia (~3,600 días). Cada día se resume en dos coordenadas —cuánta **memoria** tiene su precio
(Hurst) y cuán **eficiente/limpio** fue su movimiento (Kaufman ER)— y se ubica como un punto en un
plano. La nube resultante responde una sola pregunta, la más importante antes de operar:

> **¿En qué tipo de comportamiento pasa este instrumento la mayor parte de su tiempo?**

La respuesta determina si tiene sentido aplicar seguimiento de tendencia, reversión a la media, o si
el activo es estructuralmente ruidoso y exige filtros severos (o simplemente no operarlo con esa
lógica). Esto es coherente con el propósito del *Asset Factsheet / ADN del Activo*: **estudiar la
naturaleza del activo antes de desplegar una estrategia**, no generar señales inmediatas
([[Resumen_Perfilamiento_Volatilidad_ADN_Activo]]).

---

## 2. Anatomía de la matriz: qué mide cada eje

La matriz es un plano bivariado. Cada eje captura una propiedad ortogonal del comportamiento del precio.

### Eje horizontal (X) — Exponente de Hurst H · *"¿tiene memoria?"*

El exponente de Hurst mide la **autocorrelación / memoria** de la serie de retornos:

| H | Interpretación | Naturaleza |
| :--- | :--- | :--- |
| **H < 0.50** | Antipersistencia | El movimiento tiende a **revertir** (lo que sube, corrige). Terreno de *mean-reversion*. |
| **H ≈ 0.50** | Random walk | Sin memoria explotable. Movimiento tipo caminata aleatoria. |
| **H > 0.50** | Persistencia | El movimiento tiende a **continuar** (inercia/momentum). Terreno de *trend-following*. |

En el panel, H se calcula sobre una ventana móvil con **horizonte de memoria seleccionable: 5D / 14D /
30D** (`calculate_hurst_kaufman_scatter`, invocado por horizonte en `engine.py`). El horizonte define
*a qué escala temporal* se mide la memoria (ver §4.4).

### Eje vertical (Y) — Kaufman Efficiency Ratio (ER) · *"¿el movimiento fue limpio?"*

El *Efficiency Ratio* de Perry Kaufman mide **cuánta señal direccional hubo por unidad de ruido**:

$$\text{ER}_n = \frac{|\,P_t - P_{t-n}\,|}{\sum_{i} |\,P_{t-i} - P_{t-i-1}\,|} = \frac{\text{Desplazamiento neto}}{\text{Distancia total recorrida}}$$

- **ER → 1.0**: el precio fue casi en línea recta de A a B. **Dirección limpia**, poca fricción.
- **ER → 0.0**: el precio recorrió mucho camino para ir a casi ningún lado. **Ruido errático**, whipsaw.

El ER es, por diseño, un **filtro no-trade**: cuando ER colapsa, el ATR ajustado (`ATR/ER`) se dispara,
señalando ruido no comerciable ([[Caracterizacion_Volatilidad_Intradia]] §3.3).

### Ortogonalidad (por qué dos ejes y no uno)

Los ejes miden cosas distintas: **memoria ≠ limpieza**. Un activo puede tener fuerte tendencia (H alta)
pero sucia (ER baja) —tendencia entre sacudidas—, o revertir de forma tan limpia como tiende. Cruzar
ambas dimensiones es lo que hace útil la matriz: separa "hacia dónde va la memoria" de "qué tan
operable es el trayecto".

---

## 3. Los cuatro cuadrantes

El plano se parte en cuatro con dos cortes **binarios**: **H = 0.50** (vertical) y **ER = 0.45**
(horizontal). Estos umbrales son la fuente de verdad del código
(`calculate_hurst_kaufman_scatter`, `src/kpis.py`).

```
                      ER ALTA (≥ 0.45) — DIRECCIÓN LIMPIA
                                    ▲
        Q-II                        │                        Q-I
   REVERSIÓN PULCRA                 │              TENDENCIA LIMPIA
   fade / rango                     │              trend-following
   H < 0.50 · ER ≥ 0.45             │              H ≥ 0.50 · ER ≥ 0.45
                                    │
   REVERSIÓN ◄─────────────────────┼─────────────────────► PERSISTENCIA
   (H baja)                        │                        (H alta)
                                    │
        Q-III                       │                        Q-IV
   ERRÁTICO / RUIDO                 │              TENDENCIA RUIDOSA
   zona no-trade                    │              fricción / stops anchos
   H < 0.50 · ER < 0.45             │              H ≥ 0.50 · ER < 0.45
                                    ▼
                      ER BAJA (< 0.45) — ERRÁTICO
```

| Cuadrante | Condición | Nombre (código) | Color | Qué significa para trading |
| :--- | :--- | :--- | :--- | :--- |
| **Q-I** (arriba-der.) | H ≥ 0.50 · ER ≥ 0.45 | TENDENCIA LIMPIA & PERSISTENTE | `#0284c7` azul | Avance direccional firme con bajo ruido. **Terreno del seguimiento de tendencia.** Rupturas y momentum funcionan; los stops respiran. |
| **Q-II** (arriba-izq.) | H < 0.50 · ER ≥ 0.45 | REVERSIÓN A LA MEDIA PULCRA | `#0f766e` teal | Oscilación limpia entre niveles. **Terreno del fade / rango.** Comprar soportes, vender resistencias, mean-reversion con buen ratio. |
| **Q-III** (abajo-izq.) | H < 0.50 · ER < 0.45 | ERRÁTICO & RUIDO EXTREMO | `#475569` slate | Movimiento caótico con alta fricción. **Zona no-trade.** Whipsaw: ni tendencia ni reversión limpia. Exige filtros severos o abstenerse. |
| **Q-IV** (abajo-der.) | H ≥ 0.50 · ER < 0.45 | TENDENCIA RUIDOSA CON FRICCIÓN | `#b45309` ámbar | Hay inercia, pero sucia. **Tendencia golpeada por ruido.** Se puede seguir el sesgo, pero exige stops anchos y presupuesto de slippage; entradas finas fallan. |

**Regla mnemónica:** las columnas responden *"¿hacia dónde?"* (izquierda = revierte, derecha =
continúa); las filas responden *"¿operable?"* (arriba = limpio, abajo = ruidoso).

---

## 4. La lectura central — Distribución por cuadrante (base rates)

Esta es la utilidad principal de la matriz y el eje de esta guía. Un solo punto no dice nada; **la nube
completa lo dice todo**.

### 4.1. El concepto: la distribución es la personalidad del activo

La pregunta operativa no es *"¿en qué cuadrante está hoy?"* sino:

> **¿Qué fracción de su historia pasa el instrumento en cada cuadrante?**

Ese reparto porcentual —el **base rate** de cada cuadrante— es la personalidad estructural del activo.
En el panel se lee como **densidad de puntos**: el cuadrante donde se apiña la nube es donde el
instrumento "vive". Un activo no es "tendencial" porque hoy esté en Q-I; es tendencial si **pasa la
mayoría de su historia** en Q-I / Q-IV (columna derecha, H alta).

### 4.2. De la distribución a la decisión de estrategia

El base rate es la **tasa base de éxito estructural** de cada familia de estrategia sobre ese activo.
La lógica de decisión:

- **Peso en la columna derecha (Q-I + Q-IV, H ≥ 0.50)** → el activo tiene memoria tendencial →
  el *trend-following* tiene soporte histórico. Cuánto de ese peso está en Q-I (limpio) vs. Q-IV
  (ruidoso) dice si la tendencia es operable con stops ajustados o si exige holgura.
- **Peso en la columna izquierda (Q-II + Q-III, H < 0.50)** → el activo revierte → la *mean-reversion*
  tiene soporte. Cuánto está en Q-II (pulcro) vs. Q-III (ruido) dice si el fade es limpio o una trampa.
- **Peso en la fila inferior (Q-III + Q-IV, ER < 0.45)** → mucho ruido estructural →
  cualquier estrategia necesita **filtros de eficiencia** y gestión de riesgo más ancha.
- **Q-III dominante** → el activo es, la mayor parte del tiempo, **no comerciable** con lógica
  direccional simple. Es el hallazgo más valioso: evita desplegar sistemas que la historia no respalda.

**Principio rector:** *elige la familia de estrategia cuyo cuadrante concentre la mayor densidad
histórica; descarta las que la historia no soporta.*

### 4.3. Arquetipos y la frase de factsheet

Traduce la distribución a una afirmación objetiva y accionable. Ejemplos de lectura (los porcentajes
son ilustrativos):

| Arquetipo | Firma de distribución | Frase de factsheet (lectura objetiva) |
| :--- | :--- | :--- |
| **Tendencial limpio** | Q-I dominante (p. ej. > 40% Q-I) | "El activo pasa la mayoría de su historia en tendencia limpia; el seguimiento de tendencia tiene la tasa base más alta. Priorizar rupturas/momentum." |
| **Reversivo de rango** | Q-II dominante | "Predomina la reversión pulcra; el fade contra extremos de rango es la lógica con mayor soporte histórico. El trend-following opera contra el activo." |
| **Ruidoso-dominante** | Q-III mayoritario (p. ej. > 55%) | "Más de la mitad de la historia es ruido errático (no-trade). Cualquier estrategia direccional exige filtros de eficiencia fuertes; base rate bajo — considerar no operarlo con esta lógica." |
| **Tendencial sucio** | Q-I + Q-IV altos, Q-IV pesado | "Hay memoria tendencial, pero mayormente ruidosa. Se puede seguir el sesgo con stops anchos y presupuesto de slippage; entradas de precisión fallarán." |
| **Sin carácter** | Reparto ~uniforme entre 4 cuadrantes | "El activo no tiene un modo dominante; su comportamiento es inestable. Ninguna familia tiene edge estructural claro — el timing/régimen manda (ver §7)." |

La frase de factsheet es el producto final que buscamos: **una afirmación objetiva, anclada en la
historia, que selecciona (o descarta) una familia de estrategia** — no una predicción.

### 4.4. Efecto del horizonte de memoria (5D / 14D / 30D)

La distribución **cambia con el horizonte** porque el Hurst se recalcula a esa escala:

- **5D** — comportamiento táctico/de corto plazo. Más sensible; la nube suele dispersarse hacia
  reversión/ruido (a escala corta casi todo parece menos tendencial).
- **30D** — comportamiento estructural/de fondo. Más estable; revela la tendencia de fondo del activo.
- **Uso recomendado:** lee **30D para caracterizar** el activo (¿quién es?) y compara con **5D** para
  ver si su carácter táctico contradice el de fondo (útil para elegir el horizonte de tu estrategia).

Si un activo es Q-I en 30D pero Q-III en 5D, la lectura es: *"tendencial de fondo, pero ruidoso intradía
— operable en swing, traicionero en scalping"*. Esa comparación entre horizontes es, en sí misma, una
conclusión de trading.

---

## 5. Flujo de uso práctico (paso a paso)

Antes de desplegar cualquier estrategia sobre un instrumento:

1. **Carga el instrumento** y abre el MAPA DE SÍNTESIS 2D en horizonte **30D** (caracterización de fondo).
2. **Lee la densidad**: ¿dónde se apiña la nube? Identifica el cuadrante (o columna/fila) dominante.
3. **Formula la frase de factsheet** (§4.3): traduce la densidad a una afirmación objetiva sobre qué
   familia de estrategia soporta la historia.
4. **Selecciona / descarta familia**: alinea tu estrategia con el cuadrante dominante; descarta las
   familias sin soporte. Si Q-III domina → exige filtros o reconsidera el activo.
5. **Contrasta horizontes**: compara 30D vs. 5D (§4.4) para elegir la escala temporal coherente con tu
   estrategia (swing vs. intradía).
6. **Recién entonces** pasa a las herramientas de *timing* (heatmaps, superficie 3D, Z-Score, régimen)
   para el *cuándo*. La matriz 2D resuelve el *qué* y el *si*, no el *cuándo*.

---

## 6. Rigor y advertencias (para mantenerlo objetivo)

- **Corte binario vs. bandas finas.** La matriz clasifica con umbrales **binarios** (H = 0.50, ER = 0.45).
  Las tarjetas de diagnóstico del dashboard usan bandas más finas y **distintas**: Hurst
  (reversión < 0.45 · random walk 0.45–0.55 · persistencia > 0.55) y Kaufman ER (errático < 0.30 ·
  moderado 0.30–0.60 · direccional > 0.60). Es intencional: la matriz simplifica para dar una **foto de
  conjunto**, no una medición fina. Un día apenas sobre 0.50/0.45 está cerca de la frontera y no debe
  sobre-interpretarse; lo que importa es **la masa de la nube**, no los puntos limítrofes.
- **Base rate ≠ probabilidad futura.** El % histórico en un cuadrante describe el pasado empírico. Es la
  tasa base, no una garantía condicional del próximo día. Es un filtro de *plausibilidad estructural*,
  no una señal.
- **Dependencia de la muestra.** La lectura exige historia suficiente; el cálculo se degrada con
  n < 35 días. Sub-poblaciones muy filtradas (pocos puntos) dan distribuciones ruidosas — desconfía de
  porcentajes calculados sobre muestras pequeñas.
- **No es dirección de mercado.** La matriz dice *cómo* se mueve el activo (memoria/limpieza), no *hacia
  dónde* (alcista/bajista). La dirección se resuelve con otras capas del dashboard.

---

## 7. Próximas capas de lectura (fuera del foco de esta guía)

La distribución global es la base. Sobre ella se pueden construir lecturas más finas, que quedan como
extensiones futuras:

- **Shift por régimen** — cómo cambia la mezcla de cuadrantes al filtrar por régimen/estado
  (BAJO/MEDIO/ALTO × EXPANSIÓN/CONTRACCIÓN). Convierte *"el activo tiende"* en *"el activo solo tiende
  limpio en ALTO_EXPANSIÓN"*: define el **cuándo**. El panel ya permite este filtrado en tiempo real vía
  la barra global; falta cuantificar el desplazamiento del base rate.
- **Hoy vs. historia** — si el día actual está en el núcleo denso (aplican los base rates) o es un
  outlier (posible transición de régimen → base rates poco fiables), más la trayectoria reciente entre
  cuadrantes como alerta temprana de cambio de carácter.
- **Centroide y dispersión** — el (H, ER) medio como "estado de reposo" del activo y el ancho de la nube
  como estabilidad de carácter (nube apretada = playbook confiable; dispersa = camaleónico).

---

### Referencias de implementación

- Clasificación de cuadrantes y trayectoria: `src/kpis.py` → `calculate_hurst_kaufman_scatter`.
- Ensamblado por horizonte (5D/14D/30D): `src/engine.py`.
- Render del panel y ejes: `frontend/dashboard_volatilidad.html` → *MAPA DE SÍNTESIS 2D*.
- Marco conceptual: [[Resumen_Perfilamiento_Volatilidad_ADN_Activo]], [[Caracterizacion_Volatilidad_Intradia]].
