---
title: "Instrucciones — Informe de Textura del Movimiento"
tags: [instrucciones, agente, informe, hurst, kaufman, qrt-solutions]
date: 2026-08-04
seccion: Mapa de síntesis 2D — Memoria (Hurst) vs. Eficiencia (Kaufman)
fuente_datos: GET /api/volatility?asset=<nombre>
aplica_a: cualquier instrumento cargado en el sistema
---

# Instrucciones — Informe de Textura del Movimiento

Definen cómo el agente debe redactar la interpretación del **mapa de síntesis bidimensional**, que
sitúa cada sesión histórica según dos medidas: la memoria de la serie en el eje horizontal y la
eficiencia del movimiento en el vertical.

**Pregunta que responde este informe:** cuando este instrumento se mueve, ¿avanza de forma limpia o
se pierde en idas y vueltas?

Las reglas de destinatario, redacción y verificación son **las mismas** del
[informe de caracterización estructural](INSTRUCCIONES_INFORME_CARACTERIZACION_ESTRUCTURAL.md),
secciones 1, 6 y 7.

---

## Regla cero · El instrumento es un parámetro, no un dato conocido

**Este documento no describe ningún activo.** Describe un procedimiento que se aplica al instrumento
que el usuario tenga cargado en el dashboard en ese momento, sea cual sea.

El nombre del instrumento llega en tiempo de ejecución. **Todas las cifras deben recalcularse desde
el endpoint para ese instrumento concreto.** Nada de lo que sepas sobre un activo por otra vía puede
entrar en el informe.

**Este documento no contiene ninguna cifra de ningún instrumento.** Es deliberado. El dashboard
incorpora activos nuevos con el tiempo y los datos se recargan periódicamente, de modo que cualquier
valor memorizado aquí quedaría obsoleto o sería falso para el instrumento que tienes delante. La
sección 7 ofrece una **plantilla** con marcadores entre llaves; cada uno debe sustituirse por un
valor que hayas calculado.

**Señales de que algo no proviene de los datos.** Si detectas cualquiera de estas, descarta lo escrito
y vuelve a empezar:

- Queda un marcador entre llaves sin sustituir.
- Aparece el nombre de un instrumento distinto al solicitado.
- Afirmas un hallazgo cuya búsqueda **no superó su criterio** en este instrumento.
- Alguna cifra procede de tu conocimiento general y no del JSON.

**Toma el tamaño de muestra del dato, no del rótulo.** Este panel puede mostrar varias cifras de
población distintas en sus rótulos. Usa siempre el número de sesiones efectivamente representadas.

---

## 1. Alcance

Un único panel: la nube de puntos donde cada sesión histórica queda situada por dos medidas, con
cuatro cuadrantes delimitados y un selector de horizonte de memoria.

**Fuera de alcance.** No comentes la magnitud de la volatilidad, la duración de los regímenes, la
distribución de los retornos ni la pérdida esperada por lado. Cada uno tiene su propio informe.

## 2. Fuente de datos

`GET /api/volatility?asset=<nombre>`. Ninguna otra.

---

## 3. Prohibición crítica: el eje horizontal no separa sesiones

**La medida de memoria del eje horizontal sitúa la práctica totalidad de las sesiones del mismo
lado de su línea divisoria, en todos los instrumentos y en todos los horizontes.** No es una
particularidad del activo que estés analizando: es una limitación conocida del estimador cuando se
aplica a ventanas cortas, y la propia especificación del proyecto la advierte.

En consecuencia, está **terminantemente prohibido**:

| No escribas | Por qué |
| :-- | :-- |
| Que el activo "tiene memoria", "es persistente" o "tiende a seguir su dirección" | La medida no lo demuestra: arroja el mismo veredicto para cualquier activo |
| Que dos cuadrantes estén vacíos como si fuera un rasgo del instrumento | Están vacíos en todos los instrumentos, por construcción de la medida |
| Comparar los valores de esa medida entre horizontes como si el activo cambiara | El valor desciende al alargar la ventana por razones del cálculo, no del mercado |
| Presentar el mapa como un diagnóstico de cuatro estados posibles | En la práctica solo dos son alcanzables |

**Lo que sí debes hacer:** advertir al lector, una sola vez y en lenguaje llano, que todas las
sesiones de este activo caen del mismo lado en esa medida, de modo que **el cuadrante queda decidido
por el eje vertical**. Es la única forma de que no extraiga una conclusión falsa del gráfico que
tiene delante.

## 4. Prohibición adicional: el estado general del día

El panel muestra una etiqueta con el cuadrante correspondiente a la sesión en curso. **No la
interpretes.** Es el estado de hoy, se actualiza a diario y el lector lo tiene delante. Este informe
describe la historia del instrumento.

---

## 5. Cómo encontrar los hallazgos

Tres búsquedas más una advertencia obligatoria. Publica las búsquedas que superen su criterio. Si
obtienes menos de dos, aplica la regla de cupo incompleto.

### F1 · ¿Qué tan limpio es el movimiento de este activo?

Toma la eficiencia del movimiento: cuánto avanza el precio en términos netos frente a todo el camino
recorrido para lograrlo. Calcula su valor típico y la proporción de sesiones que superan el umbral
marcado en el gráfico.

- **Publícalo siempre.** Es la lectura central del panel.
- **Redacta:** el valor típico traducido a lenguaje corriente. Una eficiencia de 0,20 significa que
  por cada cinco unidades de recorrido el precio avanza una sola: las otras cuatro se consumen en
  idas y vueltas. Usa esa forma de expresarlo, no el número desnudo.
- **Cierre:** en un activo de baja eficiencia, la mayor parte del movimiento no se convierte en
  avance, y las estrategias que persiguen la dirección pagan ese desgaste.

### F2 · ¿Cambia la calidad del movimiento según el nivel de volatilidad?

Compara la proporción de sesiones de movimiento limpio entre el régimen de volatilidad baja y el de
volatilidad alta.

- **Hay hallazgo si** la proporción varía en más del doble entre ambos regímenes.
- **Redacta:** si el movimiento limpio se concentra en la calma, que la volatilidad de este activo
  destruye la dirección en lugar de crearla. Si se concentra en la volatilidad alta, lo contrario. Si
  apenas varía, que la calidad del movimiento es independiente del nivel de volatilidad, lo que
  también es informativo.
- **Cierre:** en qué condiciones conviene esperar y en cuáles el movimiento tiende a resolverse.
- **Este suele ser el hallazgo más discriminante entre instrumentos.**

### F3 · ¿Cómo cambia el mapa según el horizonte que elijas?

Compara la proporción de sesiones de movimiento limpio en el horizonte más corto frente al más largo
disponible en el selector.

- **Hay hallazgo si** la proporción cae de forma apreciable al alargar el horizonte, que es lo
  habitual.
- **Redacta:** que el movimiento parece limpio cuando se mira en plazos cortos y se vuelve ruidoso al
  mirarlo en plazos largos. Añade cuánta dirección limpia sobrevive en el horizonte largo, que es lo
  que distingue a un instrumento de otro.
- **Cierre:** el horizonte de la operación cambia por completo el diagnóstico, de modo que el lector
  debe elegir el que corresponde a cuánto tiempo piensa mantener la posición.
- **Cuidado:** atribuye la caída al horizonte de observación, nunca a un cambio en el activo.

### F4 · Advertencia obligatoria sobre el eje horizontal

**No es una búsqueda: se incluye siempre**, como último apartado y en dos o tres frases.

Explica en lenguaje llano que todas las sesiones de este activo se sitúan del mismo lado en la medida
del eje horizontal, que eso ocurre igual en cualquier instrumento, y que por tanto el cuadrante en
que cae cada punto lo determina únicamente la altura, es decir, la eficiencia. No entres en el motivo
técnico ni menciones el nombre de la medida.

---

## 6. Estructura del documento

```
# Cuando {INSTRUMENTO} se mueve, ¿avanza o da vueltas?

<línea de contexto>

### 1 · <título como afirmación en lenguaje corriente>
<uno o dos párrafos cortos>
**Por qué te importa.** <una o dos frases en segunda persona>

### 2 · ...
### 3 · ...   (opcional)

### Cómo leer este gráfico
<advertencia F4, dos o tres frases>

### En una frase
<síntesis>

**Dos cosas que este análisis no te dice.** <no predice; no distingue comprar de vender>
```

---

## 7. Plantilla de forma

**No hay ejemplos con datos reales en este documento.** Cada marcador entre llaves se sustituye por
un valor calculado.

---

> # Cuando {INSTRUMENTO} se mueve, ¿avanza o da vueltas?
>
> *{Número} cosas que conviene entender sobre la calidad de su movimiento, sacadas de {años} años de
> historia.*
>
> ### 1 · Por cada {N} unidades de recorrido, el precio avanza {M}
>
> {Traducción de la eficiencia típica a esa forma de expresarla, y proporción de sesiones que
> superan el umbral de movimiento limpio.}
>
> **Por qué te importa.** {Consecuencia sobre el desgaste que sufre una estrategia direccional.}
>
> ### 2 · {Título del segundo hallazgo, según lo que arroje F2}
>
> {Comparación de la proporción de movimiento limpio entre regímenes.}
>
> **Por qué te importa.** {En qué condiciones el movimiento tiende a resolverse.}
>
> ### 3 · Cuanto más largo el plazo, más ruidoso se ve el movimiento
>
> {Proporción de sesiones limpias en el horizonte corto frente al largo, y cuánta dirección limpia
> sobrevive al alargar la mirada.}
>
> **Por qué te importa.** Elige el horizonte del selector según cuánto tiempo pienses mantener la
> posición: el diagnóstico cambia por completo entre uno y otro.
>
> ### Cómo leer este gráfico
>
> {Advertencia F4: todas las sesiones de este activo caen del mismo lado en la medida horizontal, lo
> mismo ocurre en cualquier instrumento, y por tanto lo que decide el cuadrante es la altura del
> punto.}
>
> ### En una frase
>
> {Síntesis de los hallazgos en una sola oración.}
>
> **Dos cosas que este análisis no te dice.** No predice si el próximo movimiento será limpio o
> ruidoso: describe lo que ocurrió antes. Y no indica si conviene comprar o vender.

---

**Comprueba antes de terminar.** Si tu informe reproduce el número de apartados o el orden de esta
plantilla sin que tus búsquedas lo justifiquen, la estás rellenando en lugar de aplicar el
procedimiento.

---

## 8. Validación del método

F2 es la búsqueda que mejor distingue unos instrumentos de otros: hay activos donde el movimiento
limpio se concentra de forma marcada en los períodos de calma, y otros donde la calidad del
movimiento apenas depende del nivel de volatilidad. F1 y F3 producen resultados más parecidos entre
activos, de modo que aportan enseñanza general más que rasgo distintivo.

**Los resultados de validación sobre instrumentos concretos no se registran aquí.** Corresponden a la
capa de evidencia (`docs/evidence/`). Este documento describe el procedimiento; la evidencia describe
lo que se obtuvo al aplicarlo, y caduca cuando los datos se recargan o se incorporan activos nuevos.

---

## 9. Trazabilidad

| Búsqueda | Campos |
| :-- | :-- |
| F1 | Serie de eficiencia del movimiento y umbral marcado en el gráfico |
| F2 | Serie de eficiencia y etiqueta de régimen de cada sesión |
| F3 | Serie de eficiencia recalculada en el horizonte corto y en el largo del selector |
| F4 | No requiere cálculo: es una advertencia fija sobre la lectura del gráfico |
