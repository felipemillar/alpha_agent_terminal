---
title: "Plan de implementación — Pilar 2: Riesgo de cola accionable por lado"
tags: [plan, implementacion, adn, pilar2]
date: 2026-08-03
estado: propuesto
implementa: docs/DISENO_PILAR2_RIESGO_COLA.md
---

# Plan de implementación — Pilar 2

Ejecuta el diseño aprobado en [`DISENO_PILAR2_RIESGO_COLA.md`](DISENO_PILAR2_RIESGO_COLA.md).
Siete fases, cada una verificable de forma independiente. Las fases 1 a 4 no tocan nada que el
dashboard consuma; el riesgo se concentra en las fases 5 y 6.

---

## Fase 0 · Línea base de regresión

El refactor de la fase 1 modifica una función de la que ya depende el dashboard. Antes de tocarla se
captura su salida actual como referencia.

**Acción.** Guardar la salida de `adn.caracterizar_pilar1()` para los cuatro instrumentos en
`scratch/base_pilar1.json`.

**Verificación.** El archivo existe y contiene las once claves de cada instrumento.

---

## Fase 1 · Extraer la calibración compartida

**Archivo:** `src/adn.py`

Nueva función `preparar_serie(df)` que absorbe el preámbulo hoy embebido en `caracterizar_pilar1`:

```
sanear(df)                              -> serie saneada + diagnóstico
epocas_efectivas(df)                    -> N1, N2, N3
kpis.calculate_natr                     -> columna NATR
kpis.classify_regimes_full              -> columna Regime
kpis.calculate_expansion_contraction    -> columna State
```

Devuelve `(df_calibrado, contexto)`, donde `contexto` agrupa `periodo`, `saneamiento` y
`epocas_efectivas`. Conserva la guarda de muestra mínima de 400 sesiones.

`caracterizar_pilar1` se reescribe para consumirla. **Su salida debe permanecer idéntica**: mismas
claves, mismos valores.

**Verificación.** Comparar contra `scratch/base_pilar1.json`. Diferencia esperada: ninguna.
Adicionalmente, `/api/adn/pilar1` sigue respondiendo y el dashboard renderiza los cinco paneles.

---

## Fase 2 · Momentos de la distribución (P2.01 y P2.02)

**Archivo:** `src/adn.py`

Nueva función `momentos_distribucion(df)`:

- Asimetría y exceso de curtosis de los retornos diarios simples, a nivel global y por régimen. (Nota: usar explícitamente `df.kurt()` o `scipy.stats.kurtosis(fisher=True)` para asegurar el cálculo del exceso de curtosis).
- Devuelve `n` en cada nivel.
- Marca explícitamente la convención: el campo `nota` declara que se trata de exceso de curtosis y
  que el umbral de comparación es 0.
- Incluye `robustez: "baja"` en el bloque de curtosis, para que el consumidor sepa que no puede
  encabezar un veredicto.

**Verificación.** Sobre QQQ, el exceso de curtosis global ronda 7,5 y los valores por régimen quedan
entre 0,7 y 2,7. Una distribución normal simulada devuelve un valor próximo a 0.

---

## Fase 3 · Riesgo de cola (P2.03 y P2.04)

**Archivo:** `src/adn.py`

Nueva función `riesgo_cola(df, horizontes=(1,2,3,5), percentil=5, piso_efectivo=20)`.

**Estructura interna, en tres capas:**

1. `_retornos_por_horizonte(df, h)` — retorno acumulado `Close(t+h)/Close(t) − 1` (implementado de forma vectorizada usando `(df['Close'].shift(-h) / df['Close']) - 1`), conservando el
   régimen y el estado del día de entrada `t`.
2. `_celda_cola(retornos, lado, h, piso)` — calcula umbral, pérdida esperada, razón entre ambos,
   tamaños de muestra, error estándar y el veredicto `publicable`. Es la unidad reutilizable.
3. `riesgo_cola(...)` — orquesta los tres niveles de condicionamiento y los cuatro horizontes.

**Convenciones que la función debe respetar:**

- Ambos lados se devuelven como pérdida en signo negativo.
- `n_efectivo = n_cola / h`, redondeado a la baja.
- Una celda con `n_efectivo < piso` devuelve `publicable: false` y `motivo`, **sin cifras de riesgo**.
- El nivel `por_regimen_estado` se calcula siempre; las celdas no publicables se incluyen con su
  motivo, para que el consumidor sepa que la combinación existe y por qué se omite.

**Verificación.**

- A horizonte 1, el umbral del lado largo coincide con el percentil 5 de los retornos diarios
  calculado directamente.
- La pérdida esperada del régimen ALTO supera a la del régimen BAJO en los cuatro instrumentos.
- BTCUSD a horizonte 5 en el nivel `por_regimen` devuelve al menos una celda no publicable.
- La razón entre pérdida esperada y umbral se sitúa en el entorno de 1,5, coherente con la evidencia
  ya registrada.

---

## Fase 4 · Orquestador y salida legible

**Archivo:** `src/adn.py`

`caracterizar_pilar2(df)` con la misma forma que su equivalente del Pilar 1: consume
`preparar_serie`, devuelve `periodo`, `saneamiento`, `P2_01_asimetria`, `P2_02_curtosis` y
`P2_03_04_riesgo_cola`.

Extender el bloque `__main__` para que `python src/adn.py [ACTIVO]` imprima ambos pilares, con una
tabla de riesgo de cola por régimen y lado, y las celdas suprimidas mostradas con su motivo.

**Verificación.** `python src/adn.py` recorre los cuatro instrumentos sin excepciones y la salida es
legible en consola.

---

## Fase 5 · Endpoint

**Archivo:** `src/server.py`

`GET /api/adn/pilar2?asset=<nombre>`, inmediatamente después del endpoint de Pilar 1 y replicando su
estructura: validación del parámetro, comprobación de existencia del activo, `json.dumps` con
`ensure_ascii=False`, y traza al registro ante excepción.

**Verificación.** Respuesta correcta para los cuatro instrumentos; 400 sin parámetro `asset`; 404 con
un activo inexistente.

---

## Fase 6 · Integración con el informe

**Archivos:** `src/generate_analysis.py` y `src/expert_nlg.py`

**En `generate_analysis.py`**, dentro de `generate_deterministic_report`:

- Llamar una vez a `adn.caracterizar_pilar2()` y guardar el resultado en `stats['pilar2']`.
- Sustituir el cálculo local de `kurt` y `skw` (líneas 227-228) por su lectura desde ese resultado.
  **Las claves `stats['kurt']` y `stats['skw']` se conservan** para no romper a otros consumidores
  del diccionario.

**En `expert_nlg.py`**, `generate_distribucion_nlg`:

- Corregir el umbral de clasificación de colas de `kurt > 3` a `kurt > 0`, dado que el valor es
  exceso de curtosis.
- Añadir al nivel 2 la cifra de pérdida esperada del régimen vigente, diferenciada por lado.
- Añadir al nivel 3 los campos `n_cola`, `n_efectivo` y el error estándar.
- Cuando la celda del régimen vigente no sea publicable, recurrir a la celda global y declararlo
  expresamente inyectando la frase: *"Debido a insuficiencia estadística en este régimen específico, se expone el riesgo de cola de la distribución global"*.
- Mantener una vía de repliegue: si `stats` no trae `pilar2`, la función opera con el comportamiento
  anterior. Evita que un fallo del Pilar 2 deje al informe sin bloque de distribución.

**Verificación.** El informe generado para un instrumento contiene la cifra de pérdida esperada;
forzando la ausencia de `pilar2` en `stats`, sigue produciendo el bloque completo.

---

## Fase 7 · Documentación

| Documento | Actualización |
| :-- | :-- |
| `docs/CATALOGO_KPIS_ADN.md` | P2.01 a P2.04 pasan a ACTIVO. Añadir columna *Panel* con valor «no» para los cuatro. Registrar en deuda técnica el cálculo de asimetría y curtosis que permanece en JavaScript |
| `docs/evidence/` | Nuevo registro con las cifras de riesgo de cola de los cuatro instrumentos y el comando de reproducción |
| `docs/BITACORA.md` | Hito nuevo, con mención del defecto de convención de curtosis corregido |

---

## Secuencia y dependencias

```
Fase 0 ─→ Fase 1 ─→ Fase 2 ─┐
                            ├─→ Fase 4 ─→ Fase 5 ─→ Fase 6 ─→ Fase 7
                   Fase 3 ──┘
```

Las fases 2 y 3 son independientes entre sí. Las fases 1 a 4 se ejecutan por completo dentro de
`adn.py` y no afectan a ningún consumidor.

## Riesgos

| Riesgo | Mitigación |
| :-- | :-- |
| El refactor de la fase 1 altera la salida del Pilar 1 y rompe los paneles del dashboard | Comparación contra la línea base de la fase 0 antes de continuar |
| `adn.py` supera las 600 líneas y pierde legibilidad | Si ocurre, separar el riesgo de cola en `src/adn_cola.py` conservando el orquestador en `adn.py` |
| Otra sesión modifica `adn.py`, `server.py` o `generate_analysis.py` en paralelo, como ya sucedió durante el Pilar 1 | Verificar el estado de cada archivo antes de editarlo y trabajar en bloques contiguos |
| La corrección del umbral de curtosis cambia el veredicto de informes ya emitidos | Es el comportamiento deseado. Se documenta en la bitácora como corrección, no como cambio de criterio |

## Criterio de finalización

Los seis criterios de la especificación, más:

7. `python src/adn.py` ejecuta ambos pilares sobre los cuatro instrumentos sin excepciones.
8. La línea base de la fase 0 coincide exactamente con la salida del Pilar 1 tras el refactor.
