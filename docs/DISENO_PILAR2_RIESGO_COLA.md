---
title: "Diseño — Pilar 2: Riesgo de cola accionable por lado"
tags: [diseno, spec, adn, pilar2, riesgo-cola, qrt-solutions]
date: 2026-08-03
estado: aprobado
implementa: P2.01, P2.02, P2.03, P2.04 del catálogo
depende_de: docs/CATALOGO_KPIS_ADN.md, src/adn.py
---

# Diseño — Pilar 2: Riesgo de cola accionable por lado

## 1. Propósito

Convertir la afirmación *"este instrumento tiene colas gruesas"* en una cifra que un operador pueda
usar para dimensionar una posición, diferenciada según tome el lado comprador o el vendedor.

El bloque de distribución del informe cierra hoy con la implicancia *"el dimensionamiento no debe
calibrarse solo con la media"*, sin indicar con qué cifra sí debe calibrarse. Este pilar la aporta.

## 2. Alcance

**Entran cuatro indicadores del catálogo:**

| ID | Indicador | Situación previa |
| :-- | :-- | :-- |
| P2.03 | Umbral de pérdida extrema | PROPUESTO |
| P2.04 | Pérdida esperada en escenario extremo | PROPUESTO |
| P2.01 | Asimetría | Calculado en JavaScript y, por separado, en `generate_analysis.py` |
| P2.02 | Curtosis | Ídem |

**Sobre la doble implementación de P2.01 y P2.02.** Existen hoy dos cálculos en Python
—`generate_analysis.py` y el frontend en JavaScript— y ambos alimentan destinos distintos. Esta
iteración elimina la duplicación **en el lado Python**: `adn.py` pasa a ser la fuente autorizada y
`generate_analysis.py` deja de calcularlos. El cálculo en JavaScript permanece, porque alimenta un
panel existente y retirarlo exige tocar el frontend, que queda fuera de alcance. Se registra como
deuda pendiente en el catálogo.

**Quedan fuera de esta iteración:** P2.05 (autocorrelación del retorno absoluto) y P2.06 (valor en
riesgo por teoría de valores extremos).

### 2.1 Defecto corregido por esta iteración

`expert_nlg.py` clasifica las colas con la regla `kurt > 3`, aplicada sobre el valor que devuelve
`pandas.Series.kurt()`. Esa función implementa la definición de Fisher y devuelve **exceso de
curtosis**, cuyo valor para una distribución normal es 0, no 3. Comparar contra 3 mezcla dos
convenciones.

Consecuencia medida sobre los cuatro instrumentos disponibles: **diez de las doce celdas de régimen
presentan exceso de curtosis entre 0 y 3**, de modo que el informe las declara actualmente *"colas
normales"* cuando corresponden a colas gruesas. El umbral correcto es 0 y esta iteración lo corrige.

## 3. Decisiones de diseño y su fundamento

| Decisión | Alternativas descartadas | Fundamento |
| :-- | :-- | :-- |
| Profundidad: régimen × lado garantizada; estado solo donde alcance la muestra | Solo global; régimen × estado completo | Con 5% de cola, las celdas de régimen dejan 72-111 observaciones y las de régimen × estado solo 24-43. La apertura completa produciría cifras inestables presentadas como firmes |
| Horizonte: 1 sesión por defecto, con selector de 2, 3 y 5 | Solo 1 sesión; incluir 20 sesiones | La cola de un día no describe el riesgo de quien mantiene la posición. Horizontes cortos mantienen el solapamiento de ventanas en un rango manejable |
| Ambos lados expresados como pérdida en signo negativo | Publicar la cola derecha en positivo | Una cola derecha de +2,76% es una pérdida de 2,76% para quien vendió. Expresarla en positivo obliga al lector a invertir el signo mentalmente |
| Calibración extraída a función compartida | Replicar el preámbulo en cada pilar | Pilar 2 exige las mismas etiquetas de régimen sobre la misma serie saneada que Pilar 1. Dos calibraciones independientes pueden divergir |
| Endpoints separados por pilar | Endpoint unificado `/api/adn` | El endpoint de Pilar 1 y el código del dashboard que lo consume son recientes; unificar ahora arriesga conflicto sin beneficio inmediato. La unificación se justifica al llegar el tercer pilar |

## 4. Arquitectura

### 4.1 Cambios en `src/adn.py`

```
preparar_serie(df)            NUEVO      saneamiento, épocas efectivas, NATR, Regime, State
                                         devuelve (df_calibrado, diagnostico)
caracterizar_pilar1(df)       REFACTOR   consume preparar_serie; sin cambio de conducta
caracterizar_pilar2(df)       NUEVO      consume preparar_serie
riesgo_cola(df, horizontes)   NUEVO      P2.03 y P2.04
momentos_distribucion(df)     NUEVO      P2.01 y P2.02
```

El refactor de `caracterizar_pilar1` no altera su salida. Es condición de aceptación que el endpoint
de Pilar 1 devuelva exactamente los mismos valores antes y después.

### 4.2 Endpoint

`GET /api/adn/pilar2?asset=<nombre>` en `src/server.py`, con el mismo tratamiento de errores que
`/api/adn/pilar1`: 400 sin parámetro, 404 si el activo no existe, 500 con traza en el registro.

### 4.3 Informe

`src/expert_nlg.py` → `generate_distribucion_nlg(stats)` consume la salida del Pilar 2.
`src/generate_analysis.py` deja de calcular `skew` y `kurt` por su cuenta y los toma de la misma
fuente.

## 5. Definición operativa

### 5.1 Retorno por horizonte

Para cada horizonte `h ∈ {1, 2, 3, 5}`:

```
R_h(t) = Close(t+h) / Close(t) − 1
```

Cada observación se agrupa por el **régimen y estado vigentes el día de entrada `t`**, no los del día
de salida. La pregunta que responde es *"si abro una posición hoy, con el régimen que observo hoy"*.

### 5.2 Umbral y pérdida esperada por lado

| Lado | Umbral de pérdida extrema (P2.03) | Pérdida esperada (P2.04) |
| :-- | :-- | :-- |
| **Larga** | Percentil 5 de `R_h` | Media de las observaciones de `R_h` iguales o inferiores al umbral |
| **Corta** | Percentil 95 de `R_h`, con signo invertido | Media de las observaciones iguales o superiores al percentil 95, con signo invertido |

Ambos lados se publican como **magnitud de pérdida en signo negativo**.

### 5.3 Condicionamiento

| Nivel | Celdas | Publicación |
| :-- | :-- | :-- |
| Global × lado | 2 | Siempre, como referencia |
| Régimen × lado | 6 | Profundidad garantizada |
| Régimen × estado × lado | 12 | Se calcula siempre; se publica solo donde supere el piso |

### 5.4 Momentos de la distribución

P2.01 y P2.02 se calculan sobre los retornos diarios simples de la serie saneada, con las funciones
`skew()` y `kurt()` de pandas — esta última devuelve exceso de curtosis, de modo que el umbral de
comparación es 0 y no 3. Se reportan a nivel global y por régimen.

## 6. Reglas de publicación

Cada celda declara su muestra y su precisión:

| Campo | Definición |
| :-- | :-- |
| `n` | Sesiones de la celda |
| `n_cola` | Observaciones en la cola del 5% |
| `n_efectivo` | `n_cola / h` — corrige el solapamiento de ventanas, que a horizonte `h` reduce la independencia de las observaciones |
| `error_estandar` | Error estándar de la pérdida esperada |
| `publicable` | Verdadero si `n_efectivo ≥ 20` |

Bajo el piso, la celda devuelve `publicable: false` con el motivo textual y **sin cifra**, igual que la
puerta de nivel N3 del Pilar 1. El informe imprime *no medible*.

**Piso de 20 observaciones efectivas.** Verificado sobre los instrumentos disponibles, produce una
degradación gradual: habilita la tabla por régimen en los horizontes 1 a 3 en todos los casos, admite
la apertura por estado solo en horizonte 1, y suprime el horizonte de 5 sesiones en BTCUSD.

Adicionalmente rige la curtosis: por su fragilidad como estimador —robustez B en el catálogo— **no
puede encabezar un veredicto**. El titular del bloque corresponde a la pérdida esperada.

## 7. Contrato de salida

```json
{
  "activo": "QQQ",
  "calculado": "2026-08-03T12:00:00",
  "periodo": { "desde": "2000-01-03", "hasta": "2026-08-03" },
  "saneamiento": { "n_bruto": 6685, "n_saneado": 6685, "retornos_imposibles": 0 },

  "P2_01_asimetria": {
    "global": -0.12,
    "por_regimen": { "BAJO": 0.05, "MEDIO": -0.08, "ALTO": -0.21 },
    "n": 6684
  },

  "P2_02_curtosis": {
    "global": 8.4,
    "por_regimen": { "BAJO": 2.1, "MEDIO": 3.0, "ALTO": 5.7 },
    "nota": "exceso de curtosis; el umbral de comparacion es 0",
    "robustez": "baja",
    "n": 6684
  },

  "P2_03_04_riesgo_cola": {
    "percentil": 5,
    "horizontes": [1, 2, 3, 5],
    "piso_efectivo": 20,
    "global":  { "1": { "largo": "<celda>", "corto": "<celda>" } },
    "por_regimen": { "ALTO": { "1": { "largo": "<celda>", "corto": "<celda>" } } },
    "por_regimen_estado": { "ALTO|EXPANSION": { "1": { "largo": "<celda>", "corto": "<celda>" } } }
  }
}
```

*Se muestra una sola combinación de cada nivel; la estructura se repite para los cuatro horizontes,
los tres regímenes y las seis combinaciones de régimen y estado. `<celda>` corresponde al objeto que
se define a continuación.*

Objeto de celda publicable:

```json
{
  "var_pct": -2.08,
  "es_pct": -3.25,
  "razon_es_var": 1.56,
  "n": 2228,
  "n_cola": 111,
  "n_efectivo": 111,
  "error_estandar": 0.21,
  "publicable": true
}
```

Objeto de celda suprimida:

```json
{
  "publicable": false,
  "motivo": "muestra efectiva insuficiente: 14 observaciones, minimo 20",
  "n_cola": 71,
  "n_efectivo": 14
}
```

## 8. Restricciones de muestra medidas

Observaciones en la cola del 5%, con la muestra efectiva entre paréntesis, sobre los instrumentos
disponibles al 2026-08-03:

| Instrumento | Condicionamiento | h=1 | h=2 | h=3 | h=5 |
| :-- | :-- | --: | --: | --: | --: |
| QQQ | régimen (celda menor) | 111 (111) | 111 (55) | 111 (37) | 111 (22) |
| QQQ | régimen × estado | 42 (42) | 42 (21) | 42 (14) | 42 (8) |
| USDCLP | régimen (celda menor) | 107 (107) | 107 (53) | 107 (35) | 107 (21) |
| USDCLP | régimen × estado | 38 (38) | 38 (19) | 38 (12) | 38 (7) |
| BTCUSD | régimen (celda menor) | 72 (72) | 72 (36) | 72 (24) | 71 (14) |
| BTCUSD | régimen × estado | 24 (24) | 24 (12) | 24 (8) | 23 (4) |

## 9. Integración con el informe

El bloque de distribución de `expert_nlg.py` conserva su estructura de tres niveles y cambia de
contenido:

| Nivel | Antes | Después |
| :-- | :-- | :-- |
| 1 · Clasificación | Colas gruesas o normales | Añade la cifra de pérdida esperada del régimen vigente, diferenciada por lado |
| 2 · Interpretación | *"el dimensionamiento no debe calibrarse solo con la media"* | *"una de cada veinte sesiones pierde más de X%; cuando ocurre, la pérdida media es Y%. El dimensionamiento debe soportar Y%, no X%"* |
| 3 · Detalle técnico | Asimetría, curtosis, Z-Score | Añade `n_cola`, `n_efectivo` y el error estándar |

Cuando la celda del régimen vigente no supera el piso, el nivel 2 recurre a la celda global e indica
explícitamente que la lectura condicionada no es medible con la muestra disponible.

## 10. Criterio de finalización

1. `/api/adn/pilar1` devuelve valores idénticos antes y después del refactor de `preparar_serie`.
2. `/api/adn/pilar2` responde para los cuatro instrumentos disponibles.
3. Al menos una celda devuelve `publicable: false` con su motivo, verificable en el horizonte de 5
   sesiones de BTCUSD.
4. `expert_nlg.generate_distribucion_nlg` no calcula asimetría ni curtosis: las recibe.
5. La clasificación de colas emplea el umbral 0 sobre exceso de curtosis. Verificable con cualquier
   celda cuyo valor esté entre 0 y 3: debe declararse gruesa, no normal.
5. La pérdida esperada en régimen ALTO supera a la de régimen BAJO en todos los instrumentos, lo que
   confirma que el condicionamiento aporta información.
6. El catálogo actualiza P2.01 a P2.04 al estado ACTIVO y registra el resultado en `docs/evidence/`.
