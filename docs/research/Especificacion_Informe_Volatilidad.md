---
title: "Especificación — Informe de Volatilidad del Activo (Volatility Desk)"
tags: [trading, volatilidad, informe, especificacion, minorista, qrt-solutions]
date: 2026-08-01
author: QRT Solutions x Pepperstone Research
sources:
  - src/kpis.py
  - src/engine.py
  - "[[Manual_KPIs_Dashboard_Volatilidad]]"
  - "[[Guia_Utilidad_Mapa_Sintesis_2D_Hurst_Kaufman]]"
---

# Especificación — Informe de Volatilidad del Activo (Volatility Desk)

## 1. Propósito y alcance

Definir la estructura y la lógica de redacción de un **informe de volatilidad** generado a partir del
Volatility Desk (primera pestaña del dashboard). El informe está dirigido a **traders minoristas de
cualquier nivel**: debe ser comprensible sin formación econométrica, manteniendo un registro **técnico y
profesional**. Su objetivo es entregar dos interpretaciones complementarias del activo:

- **Interpretación histórica (estructural):** la identidad del activo sobre su historia completa.
- **Interpretación de contingencia (coyuntural):** su estado actual, condicionado al régimen vigente.

El valor interpretativo surge del **contraste** entre ambas: determinar si la condición de hoy es *típica
o atípica* para el activo.

## 2. Principio de divulgación por tres niveles

Cada bloque se presenta en tres niveles; cada lector desciende hasta donde le sea útil.

| Nivel | Contenido | Destinatario |
| :-- | :-- | :-- |
| 1 · Clasificación | Etiqueta (Bajo/Medio/Alto u homólogo) + veredicto de una línea | Todos |
| 2 · Interpretación | Explicación en lenguaje llano + implicancia operativa | Intermedio |
| 3 · Métrica | Valor, ventana de cálculo y definición del indicador | Avanzado (subordinado) |

El contenido técnico no se elimina: se subordina. En los niveles 1–2 no aparecen términos como "Hurst".

## 3. Los dos planos de lectura

| Plano | Definición | Cálculo | Cadencia |
| :-- | :-- | :-- | :-- |
| **Base histórica** | Norma estructural del activo | Serie completa, **incondicional** (columna global de las matrices 7×3, momentos de toda la muestra, cobertura de regímenes) | Lenta |
| **Contingencia** | Estado actual vs. esa norma | Valor actual/reciente + su percentil histórico + la **fila del régimen vigente** de las matrices 7×3 | Por sesión |

Regla técnica: la contingencia **no es solo el valor de hoy**, sino la lectura condicionada al régimen
actual — *"cuando el activo estuvo como hoy, así se comportó históricamente"*. Base = columna global;
contingencia = fila del régimen vigente.

## 4. Estructura del informe (7 bloques)

Orden: historia → estado actual → dinámica esperada.

| # | Bloque | Base histórica | Contingencia | Indicadores (nivel 3) |
| :-- | :-- | :-- | :-- | :-- |
| 0 | **Resumen ejecutivo** | Qué es el activo | Cómo está hoy | Régimen + síntesis |
| 1 | **Magnitud de volatilidad** | Rango diario típico y de estrés | NATR de hoy y su percentil | ATR(14), NATR |
| 2 | **Régimen y dinámica** | Reparto y duración de regímenes | Régimen actual, antigüedad, transición | Percentil, rachas, Markov, Exp/Con |
| 3 | **Estructura del movimiento** | Carácter predominante | Estructura reciente, condicional al régimen | Hurst, Kaufman ER, Síntesis 2D |
| 4 | **Distribución y colas** | Asimetría, curtosis, frecuencia de extremos | Retorno reciente en σ | Z-Score, skew, curtosis |
| 5 | **Trayectoria reciente** | — | Evolución de las últimas N sesiones | Serie régimen/estado |
| 6 | **Síntesis operativa** | Lo que aplica siempre | Lo que aplica ahora | Consolidado |

## 5. Tabla de traducción (indicador → enunciado)

| Indicador | Enunciado en lenguaje llano |
| :-- | :-- |
| NATR elevado / bajo | "presenta rangos diarios amplios / estrechos en términos porcentuales" |
| Régimen Alto / Bajo | "la volatilidad actual supera / no alcanza a la de la mayoría de sus sesiones recientes" |
| Racha larga | "los episodios de este régimen tienden a prolongarse varias sesiones" |
| Markov diagonal alta | "el régimen es persistente: rara vez cambia de un día a otro" |
| Hurst > 0.55 | "persistencia: los movimientos tienden a extenderse en la misma dirección" |
| Hurst ≈ 0.50 | "comportamiento próximo a una caminata aleatoria, sin dirección explotable" |
| Hurst < 0.45 | "reversión: los movimientos tienden a corregirse hacia su promedio" |
| Kaufman ER bajo | "baja eficiencia: el precio avanza poco respecto al recorrido total (ruido)" |
| Curtosis (exceso) > 0 | "colas gruesas: los movimientos extremos ocurren más que en una distribución normal" |
| Asimetría negativa | "las caídas tienden a ser de mayor magnitud que las subidas" |

## 6. Plantilla de mensaje por bloque

> "Históricamente, **{base estructural}**. Actualmente, **{valor de hoy}** ({posición relativa a su norma});
> condicionado al régimen vigente, **{lectura de la fila del régimen actual}**. Esto configura una condición
> **{típica / atípica}**. **Implicancia:** {consecuencia operativa}."

El juicio de contraste (**típica / atípica**) se determina por la distancia entre el valor actual y la
base (percentil, o cuadrante actual vs. cuadrante dominante).

## 7. Reglas de redacción

- Registro impersonal y profesional; sin emojis ni signos de exclamación.
- Cada término técnico se define una única vez, en su primera aparición.
- Toda cifra acompañada de unidad y ventana de cálculo.
- Una sola idea por bloque; cada bloque cierra con **Implicancia**.

## 8. Requisitos de datos y calidad (obligatorio)

- **Saneamiento previo:** eliminar filas con precio de cierre corrupto antes de calcular. En el dataset de
  USDCLP se detectaron 2 filas con error de decimal (Close = 5.46 y 5.00) que inflan std, curtosis y NATR
  máximo por varios órdenes de magnitud. Filtro recomendado: descartar retornos diarios con `|Δ| > 20%` o
  precios fuera del rango histórico plausible del activo.
- **Ventana de calentamiento:** el régimen requiere 120 sesiones previas; excluirlas de las estadísticas.

## 9. Nota metodológica

El exponente de Hurst por **rango reescalado (R/S) en ventanas cortas (30d)** presenta un **sesgo al alza**
en muestras pequeñas, que tiende a clasificar la mayoría de las sesiones como persistentes. Para la lectura
**estructural** (bloque 3) debe primar el **Hurst de serie completa**; la constelación 2D de ventana corta
se usa como apoyo visual, no como base del veredicto estructural.

---
Ver aplicación real en [[Informe_Prueba_USDCLP]].
