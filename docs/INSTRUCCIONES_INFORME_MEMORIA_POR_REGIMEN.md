---
title: "Instrucciones — Informe de Memoria por Régimen y Dirección"
tags: [instrucciones, agente, informe, hurst, matriz, qrt-solutions]
date: 2026-08-04
seccion: Diagnóstico econométrico de memoria por régimen-estado y dirección (matriz 7×3)
fuente_datos: GET /api/volatility?asset=<nombre>
aplica_a: cualquier instrumento cargado en el sistema
---

# Instrucciones — Informe de Memoria por Régimen y Dirección

Definen cómo el agente debe redactar la interpretación de la **matriz de siete filas por tres
columnas** que mide la memoria de la serie en cada combinación de régimen, estado direccional de la
volatilidad y signo del movimiento.

**Pregunta que responde este informe:** ¿en qué condiciones el precio de este instrumento tiende a
prolongar su movimiento, y en cuáles se comporta como una sucesión de idas y vueltas sin dirección?

Las reglas de destinatario, redacción y verificación son **las mismas** del
[informe de caracterización estructural](INSTRUCCIONES_INFORME_CARACTERIZACION_ESTRUCTURAL.md),
secciones 1, 6 y 7.

---

## Regla cero · El instrumento es un parámetro, no un dato conocido

**Este documento no describe ningún activo.** Describe un procedimiento que se aplica al instrumento
que el usuario tenga cargado en el dashboard en ese momento, sea cual sea.

**Este documento no contiene ninguna cifra de ningún instrumento.** Es deliberado. El dashboard
incorpora activos nuevos con el tiempo y los datos se recargan periódicamente, de modo que cualquier
valor memorizado aquí quedaría obsoleto o sería falso para el instrumento que tienes delante. La
sección 6 ofrece una **plantilla** con marcadores entre llaves; cada uno debe sustituirse por un valor
que hayas calculado.

**Señales de que algo no proviene de los datos.** Si detectas cualquiera de estas, descarta lo escrito
y vuelve a empezar:

- Queda un marcador entre llaves sin sustituir.
- Aparece el nombre de un instrumento distinto al solicitado.
- Afirmas un hallazgo cuya búsqueda **no superó su criterio** en este instrumento.
- Alguna cifra procede de tu conocimiento general y no del JSON.

---

## 1. Cómo se construye esta matriz, y qué implica

Cada celda aplica la medida de memoria a un **subconjunto filtrado de sesiones**, no a un tramo
continuo de la serie. Al filtrar por régimen, por estado o por signo del movimiento, los días
seleccionados dejan de ser consecutivos.

Eso tiene tres consecuencias que gobiernan toda la interpretación:

**Primera: el valor de referencia no es 0,50.** Un subconjunto de días tomado completamente al azar
—sin ninguna estructura de memoria— arroja un valor cercano a 0,55, no a 0,50. Comparar una celda
contra 0,50 declara persistente algo que es puro azar.

**Segunda: ese valor de referencia sube cuando la celda es pequeña.** Las celdas con menos sesiones
marcan más alto solo por tener menos datos. Comparar celdas de tamaños muy distintos mezcla el efecto
que se busca con el del tamaño de muestra.

**Tercera: la fila global no es comparable con las demás.** Se calcula sobre la serie completa y
continua; las otras seis, sobre subconjuntos discontinuos. Es habitual que el valor global resulte
**inferior al de todas sus filas**, y eso no es una contradicción ni un error: son dos cálculos
distintos sobre objetos distintos.

## 2. Prohibiciones absolutas

| No escribas | Por qué |
| :-- | :-- |
| Que una celda indica memoria persistente por superar 0,50 | El azar ya produce valores cercanos a 0,55 en esta construcción |
| Que una celda contradice el veredicto global | No son comparables: distinta construcción |
| Comparaciones entre celdas cuyos tamaños de muestra difieran mucho | El tamaño distorsiona el valor |
| Diferencias menores a 0,05 como si fueran hallazgos | Están dentro del ruido del estimador, sobre todo en celdas pequeñas |
| El nombre de la medida, o los términos memoria persistente, antipersistencia, caminata aleatoria o proceso estocástico | Jerga. El lector necesita la idea, no el término |

**Regla que sustituye a todo lo anterior:** compara las celdas **entre sí**, nunca contra un umbral
absoluto, y solo cuando sus tamaños de muestra sean del mismo orden.

## 3. Prohibición adicional: la celda seleccionada

El panel permite seleccionar una combinación y muestra un veredicto para ella. Ese es un estado de
navegación del usuario, no una propiedad del instrumento. **No lo comentes.** El informe describe la
matriz completa.

---

## 4. Cómo encontrar los hallazgos

Cuatro búsquedas. Publica las que superen su criterio, entre dos y cuatro. Si obtienes menos de dos,
aplica la regla de cupo incompleto.

Trabaja siempre sobre la **columna global** de la matriz para G1 y G2, que es donde las celdas tienen
tamaños comparables.

### G1 · ¿Cambia la continuidad del movimiento según el nivel de volatilidad?

Compara las celdas de régimen bajo con las de régimen alto.

- **Hay hallazgo si** la diferencia entre ambos extremos supera 0,10.
- **Redacta:** si el valor es mayor en volatilidad baja, que en los períodos tranquilos los
  movimientos de este activo tienden a prolongarse, mientras que en los agitados se interrumpen y
  revierten con frecuencia. Si es mayor en volatilidad alta, lo contrario.
- **Nunca uses el número desnudo.** Traduce: "los movimientos tienden a continuar" o "los movimientos
  se cortan y vuelven sobre sus pasos".
- **Cierre:** en qué régimen tiene sentido acompañar un movimiento y en cuál esperar que se deshaga.
- **Este es el hallazgo principal de la sección.**

### G2 · ¿Importa que la volatilidad esté subiendo o bajando?

Dentro de cada régimen, compara la celda de expansión con la de contracción.

- **Hay hallazgo si** la diferencia supera 0,05 **y** apunta en el mismo sentido en al menos dos de
  los tres regímenes.
- **Redacta:** el efecto en lenguaje corriente, sin nombrar los estados como los nombra el panel.
- **Si el sentido no es consistente entre regímenes, no hay hallazgo.** Una diferencia en un solo
  régimen es ruido.

### G3 · ¿Se comportan igual las subidas y las bajadas?

Compara las dos columnas de dirección, fila por fila.

- **Hay hallazgo si** la diferencia supera 0,05 **y** mantiene el mismo signo en al menos cuatro de
  las seis filas de régimen.
- **Ten presente que estas celdas tienen aproximadamente la mitad de sesiones que su fila**, de modo
  que el umbral de ruido es más alto. Sé exigente.
- **Si no hay hallazgo, publícalo igualmente** como observación breve: significa que las subidas y las
  bajadas de este activo tienen la misma estructura, y que por tanto no cabe esperar que un lado se
  prolongue más que el otro. Es información útil y frecuente.

### G4 · ¿Cuál es la combinación más favorable y cuál la menos?

Identifica la celda de mayor y la de menor valor entre las que tengan tamaño de muestra suficiente.

- **Hay hallazgo si** la separación entre ambas supera 0,15.
- **Redacta:** las dos condiciones concretas, en lenguaje del lector: "cuando la volatilidad es baja y
  está subiendo" en lugar de la etiqueta del panel.
- **Cierre:** cuáles son las condiciones en que este instrumento ofrece movimientos más aprovechables
  y cuáles conviene evitar.

---

## 5. Estructura del documento

```
# Cuándo los movimientos de {INSTRUMENTO} tienden a continuar

<línea de contexto>

### 1 · <título como afirmación en lenguaje corriente>
<uno o dos párrafos cortos>
**Por qué te importa.** <una o dos frases en segunda persona>

### 2 · ...
### 3 · ...   (opcional)

### En una frase
<síntesis>

**Dos cosas que este análisis no te dice.** <no predice; no indica si comprar o vender>
```

---

## 6. Plantilla de forma

**No hay ejemplos con datos reales en este documento.** Cada marcador entre llaves se sustituye por
un valor calculado.

---

> # Cuándo los movimientos de {INSTRUMENTO} tienden a continuar
>
> *{Número} cosas que conviene saber sobre en qué condiciones este activo mantiene su dirección.*
>
> ### 1 · {Título según el sentido que arroje G1}
>
> {Comparación entre las condiciones de volatilidad baja y alta, expresada como continuidad o
> interrupción del movimiento, sin cifras desnudas ni nombres técnicos.}
>
> **Por qué te importa.** {En qué condiciones acompañar el movimiento y en cuáles esperar que se
> deshaga.}
>
> ### 2 · {Título según lo que arroje G3}
>
> {Comparación entre subidas y bajadas. Si no hay diferencia apreciable, dilo: ambos lados se
> comportan igual.}
>
> **Por qué te importa.** {Consecuencia sobre esperar o no un comportamiento distinto según el lado.}
>
> ### 3 · La combinación más favorable y la menos
>
> {Las dos condiciones extremas, descritas en lenguaje del lector.}
>
> **Por qué te importa.** {Cuándo el movimiento resulta más aprovechable y cuándo conviene apartarse.}
>
> ### En una frase
>
> {Síntesis en una sola oración.}
>
> **Dos cosas que este análisis no te dice.** No predice si el próximo movimiento continuará:
> describe lo que ocurrió antes en cada condición. Y no indica si conviene comprar o vender.

---

**Comprueba antes de terminar.** Si tu informe reproduce el número de apartados o el orden de esta
plantilla sin que tus búsquedas lo justifiquen, la estás rellenando en lugar de aplicar el
procedimiento.

---

## 7. Validación del método

G1 es la búsqueda que sostiene la sección y suele producir un gradiente ordenado entre regímenes. G3
suele **no** superar su criterio, y esa ausencia es un resultado válido que conviene publicar.

Antes de dar por bueno un gradiente entre celdas, conviene comprobar que no procede del tamaño de
muestra: subconjuntos tomados al azar del mismo tamaño que cada celda deben producir valores
claramente inferiores a los observados. Si no es así, el gradiente no es una propiedad del
instrumento.

**Los resultados de validación sobre instrumentos concretos no se registran aquí.** Corresponden a la
capa de evidencia (`docs/evidence/`). Este documento describe el procedimiento; la evidencia describe
lo que se obtuvo al aplicarlo, y caduca cuando los datos se recargan o se incorporan activos nuevos.

---

## 8. Trazabilidad

| Búsqueda | Celdas de la matriz |
| :-- | :-- |
| G1 | Columna global, filas de régimen bajo frente a régimen alto |
| G2 | Columna global, expansión frente a contracción dentro de cada régimen |
| G3 | Columnas de dirección, comparadas fila por fila |
| G4 | Todas las celdas con muestra suficiente |
