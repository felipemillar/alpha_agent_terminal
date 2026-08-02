---
title: "Informe de Volatilidad — USDCLP (Prueba)"
tags: [trading, volatilidad, informe, usdclp, prueba, qrt-solutions]
date: 2026-08-01
author: QRT Solutions x Pepperstone Research
sources:
  - data/USDCLP_PEPPERSTONE_historico.csv
  - "[[Especificacion_Informe_Volatilidad]]"
---
# Informe de Volatilidad — USDCLP

**Instrumento:** USD/CLP (peso chileno) · **Periodo analizado:** 2003-12-01 a 2026-07-31 ·
**Sesiones:** 5.873 (~22,7 años) · **Fecha de corte:** 2026-07-31.
*Saneamiento: se descartaron 2 sesiones con cierre corrupto (error de decimal) previo al cálculo. Ver notas de calidad al final.*

---

## 0. Resumen ejecutivo

**Perfil estructural (histórico):** USDCLP es un instrumento **ruidoso y poco eficiente**, con
comportamiento próximo a una **caminata aleatoria** (sin dirección explotable de forma sostenida) y con
**colas gruesas** (movimientos extremos más frecuentes de lo normal). Reparte su historia casi en tercios
entre volatilidad baja, media y alta, y sus regímenes de volatilidad son **muy persistentes**.

**Estado de contingencia (hoy):** el activo se encuentra en un régimen de volatilidad **Bajo y en
contracción** — su volatilidad está **por debajo de lo habitual** (percentil 12 de sus últimos 120 días).
La condición es de calma pronunciada y, dada la persistencia histórica, tiende a mantenerse.

---

## 1. Magnitud de la volatilidad

**Nivel 1 — Clasificación:** Volatilidad actual **Baja**.

**Nivel 2 — Interpretación.**
*Base histórica:* en una sesión típica, USDCLP se mueve alrededor de **±1,4%** respecto al día anterior;
en periodos de estrés el rango diario llega a **±2,4%** y, en su extremo histórico, a **±4,5%**.
*Contingencia:* hoy el movimiento diario esperado es de **±1,1%**, en el **percentil 12** de sus últimas
120 sesiones — es decir, **más contenido que su norma reciente**.
**Implicancia:** los rangos diarios están comprimidos. Sobre una posición de $1.000, la oscilación diaria
habitual actual ronda los $11. Es un entorno de bajo recorrido; los objetivos intradía deben dimensionarse
en consecuencia.

<sub>Nivel técnico — NATR hoy 1,11% (percentil 12/100, ventana 120d) · NATR mediano histórico 1,41% · p90 (estrés) 2,36% · máx 4,48% · ATR(14) 10,29 · precio 930,47.</sub>

---

## 2. Régimen y dinámica temporal

**Nivel 1 — Clasificación:** Régimen **Bajo**, en **contracción**.

**Nivel 2 — Interpretación.**
*Base histórica:* USDCLP reparte su historia en **Bajo 40% / Medio 25% / Alto 35%**. Sus regímenes son
**muy persistentes**: la probabilidad de seguir al día siguiente en el mismo estado es del **92%** tanto
en Bajo como en Alto. Además, **nunca salta directo de calma a estrés**: los cambios de régimen pasan
siempre por el estado Medio. Un tramo de volatilidad baja dura, en mediana, **3 sesiones**, aunque puede
extenderse mucho más.
*Contingencia:* el activo está en régimen Bajo y con la volatilidad aún **descendiendo** (contracción).
La probabilidad de continuar en Bajo mañana es del **92%**.
**Implicancia:** la calma actual tiende a persistir; no conviene anticipar un salto de volatilidad
inmediato. Un cambio de régimen, de producirse, se anunciaría primero por una transición a estado Medio.

<sub>Nivel técnico — Cobertura: Bajo 39,8% / Medio 25,4% / Alto 34,8% · Markov P(Bajo→Bajo)=0,92, P(Alto→Alto)=0,92, P(Medio→Medio)=0,79; P(Bajo→Alto)=P(Alto→Bajo)=0,00 · Duración mediana de racha: Bajo 3d (máx 163), Medio 3d (máx 120), Alto 4d (máx 95) · Estado: ATR(5)  ATR(14).</sub>

---

## 3. Estructura del movimiento

**Nivel 1 — Clasificación:** Estructura **ruidosa / sin dirección** (baja eficiencia).

**Nivel 2 — Interpretación.**
*Base histórica:* la memoria del activo es próxima a una caminata aleatoria, con un leve sesgo a la
reversión (Hurst 0,46): sus movimientos **no tienden a extenderse** de forma sostenida. Su eficiencia es
**muy baja** (ER 0,16): el precio recorre mucho para avanzar poco — es un instrumento **de zigzag, no de
tendencia limpia**.
*Contingencia:* condicionado al régimen actual (Bajo, contracción), el comportamiento es aún más
indefinido: memoria en caminata aleatoria pura (Hurst 0,51) y eficiencia todavía menor (ER 0,14).
**Contraste e implicancia:** la lectura actual **confirma la norma** — en calma, USDCLP es esencialmente
ruido sin dirección aprovechable. No hay soporte histórico para estrategias de seguimiento de tendencia en
esta condición; las aproximaciones de rango/reversión son más coherentes con su naturaleza.

<sub>Nivel técnico — Hurst serie completa 0,46; condicional Bajo-Contracción 0,51 · Kaufman ER(10) global 0,16 (factor de ruido 63), condicional 0,14 (factor 73). El scatter 2D de ventana 30d clasifica hoy en Cuadrante IV, pero su Hurst de ventana corta (0,86) está sesgado al alza por muestra pequeña; prima el Hurst de serie completa.</sub>

---

## 4. Distribución de retornos y riesgo de cola

**Nivel 1 — Clasificación:** Retorno de hoy **dentro de la norma**; colas históricas **gruesas**.

**Nivel 2 — Interpretación.**
*Base histórica:* los retornos diarios se distribuyen con **leve asimetría negativa** (las caídas tienden
a ser algo más bruscas que las subidas) y con **colas gruesas**: los movimientos extremos ocurren mucho
más de lo que predice una distribución normal. En promedio, unas **15 sesiones al año** superan las ±2
desviaciones estándar.
*Contingencia:* el retorno de la última sesión fue **−0,47%**, equivalente a **−0,44 desviaciones** — un
movimiento **normal**, sin señal de choque estadístico.
**Implicancia:** aunque hoy no hay anomalía, el activo es propenso a **sustos extremos periódicos**; el
dimensionamiento no debe calibrarse solo con la volatilidad promedio. La leve asimetría sugiere vigilar en
particular los movimientos a la baja del peso (alzas bruscas de USDCLP).

<sub>Nivel técnico — Retorno último −0,47% · Z = −0,44 (dentro de ±1σ) · media diaria ≈ 0,0% · desviación diaria 1,11% · asimetría −0,23 · curtosis (exceso) 7,04 · eventos |Z|2: 340 en 22,7 años ≈ 15/año.</sub>

---

## 5. Trayectoria reciente

**Nivel 2 — Interpretación.** En las últimas ~12 sesiones, USDCLP se ha mantenido predominantemente en
régimen **Bajo y en contracción**, con un repunte transitorio a **Medio / expansión** a mediados de julio
(en torno al 17-07) que se reabsorbió rápidamente. La trayectoria describe un activo que **regresó a la
calma** tras un breve episodio de mayor movimiento.
**Implicancia:** el estado actual no es un punto aislado sino la continuación de una fase de baja
volatilidad ya establecida; refuerza la lectura de persistencia del bloque 2.

---

## 6. Síntesis operativa

**Estructural (aplica siempre a USDCLP):**

- Instrumento **ruidoso y de baja eficiencia**; no es un vehículo de tendencia limpia.
- **Colas gruesas** con leve sesgo negativo: eventos extremos periódicos → gestión de riesgo prudente y
  tamaño de posición conservador, sin calibrar solo por la volatilidad media.
- Regímenes **muy persistentes** y de transición gradual (siempre vía estado Medio).

**Coyuntural (aplica ahora, mientras persista el régimen Bajo):**

- Volatilidad **comprimida** (percentil 12) y descendente; rangos diarios reducidos.
- **Sin estructura direccional** aprovechable; condición coherente con su norma (no atípica).
- Alta probabilidad de continuidad de la calma (92%); una expansión se anticiparía por una transición a
  régimen Medio.

---

## Notas de calidad de datos y metodología

1. **Datos corruptos en la fuente.** El CSV que alimenta el dashboard contiene 2 sesiones con cierre
   erróneo (2014-04-10 Close=5,46 y 2016-12-22 Close=5,00; errores de decimal). Sin saneamiento, distorsionan
   gravemente std (12,4%→1,1%), curtosis (1.449→7,0) y NATR máximo (302%→4,5%). **Recomendación:** corregir
   la fuente, ya que el dashboard en vivo presenta hoy estas estadísticas distorsionadas para USDCLP.
2. **Sesgo del Hurst de ventana corta.** Ver nota metodológica en [[Especificacion_Informe_Volatilidad]] §9.
3. Cálculos reproducidos con las funciones de `src/kpis.py` sobre la serie saneada.
