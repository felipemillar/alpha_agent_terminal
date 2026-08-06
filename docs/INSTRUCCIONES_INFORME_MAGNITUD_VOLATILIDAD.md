---
title: "Instrucciones — Informe de Magnitud y Distribución de la Volatilidad"
tags: [instrucciones, agente, informe, volatilidad, qrt-solutions]
date: 2026-08-04
seccion: Línea de tiempo de volatilidad · Histograma de distribución de volatilidad
fuente_datos: GET /api/volatility?asset=<nombre>
aplica_a: cualquier instrumento cargado en el sistema
hermano: docs/INSTRUCCIONES_INFORME_CARACTERIZACION_ESTRUCTURAL.md
---

# Instrucciones — Informe de Magnitud y Distribución de la Volatilidad

Definen cómo el agente debe redactar la interpretación de la sección compuesta por **dos paneles**:
la línea de tiempo de volatilidad y el histograma de distribución.

**Pregunta que responde este informe:** cuánto se mueve normalmente este instrumento y hasta dónde
puede llegar.

Las reglas de destinatario, redacción y verificación son **las mismas** del
[informe de caracterización estructural](INSTRUCCIONES_INFORME_CARACTERIZACION_ESTRUCTURAL.md),
secciones 1, 6 y 7. Aquí solo se detalla lo específico de esta sección.

---

## Regla cero · El instrumento es un parámetro, no un dato conocido

**Este documento no describe ningún activo.** Describe un procedimiento que se aplica al instrumento
que el usuario tenga cargado en el dashboard en ese momento, sea cual sea.

El nombre del instrumento llega en tiempo de ejecución. **Todas las cifras deben recalcularse desde
el endpoint para ese instrumento concreto.** Nada de lo que sepas sobre un activo por otra vía puede
entrar en el informe: ni por su nombre, ni por su sector, ni por su reputación, ni por lo que hayas
leído en otro lugar, ni por lo que aparezca en los ejemplos de este documento.

**Antes de escribir una sola línea, comprueba:**

1. Obtuviste el JSON del endpoint para el instrumento solicitado.
2. Cada cifra que vas a publicar proviene de ese JSON.
3. Ejecutaste las cinco búsquedas sobre esos datos, sin dar por supuesto ningún resultado.

**Este documento no contiene ninguna cifra de ningún instrumento.** Es deliberado. El dashboard
incorpora activos nuevos con el tiempo y los datos se recargan periódicamente, de modo que cualquier
valor memorizado aquí quedaría obsoleto o sería directamente falso para el instrumento que tienes
delante. Las plantillas de la sección 7 usan marcadores entre llaves; **cada uno debe sustituirse por
un valor que hayas calculado**.

**Señales de que algo no proviene de los datos.** Si detectas cualquiera de estas, descarta lo escrito
y vuelve a empezar:

- Queda un marcador entre llaves sin sustituir.
- Aparece el nombre de un instrumento distinto al solicitado.
- Aparece una fecha o un período que no calculaste tú.
- Afirmas un hallazgo cuya búsqueda **no superó su criterio** en este instrumento.
- Alguna cifra procede de tu conocimiento general y no del JSON.

---

## 1. Alcance

| Panel | Qué muestra |
| :-- | :-- |
| Línea de tiempo de volatilidad | Cómo evolucionó el movimiento diario a lo largo de toda la historia, con alternancia entre vista en puntos y vista en porcentaje |
| Histograma de distribución | Con qué frecuencia se repite cada nivel de movimiento diario, separado por régimen |

**Fuera de alcance.** No comentes la persistencia de los regímenes, la dispersión de retornos, la
memoria de la serie ni el riesgo de cola por lado. Cada uno tiene su propio informe.

## 2. Fuente de datos

`GET /api/volatility?asset=<nombre>`, campo `chart_data`. Ninguna otra.

**Razona siempre en porcentaje, nunca en puntos.** El panel permite ver el movimiento en unidades de
precio, pero esa cifra no es comparable entre instrumentos ni entre épocas: un movimiento de 3 puntos
significa cosas distintas con el activo a 50 o a 500. La vista en puntos sirve para colocar una orden;
la interpretación se hace en porcentaje.

---

## 3. Frontera con el informe de caracterización estructural

Ambos informes miran la historia de la volatilidad. No invadas el otro.

| Corresponde al informe estructural | Corresponde a este informe |
| :-- | :-- |
| Cómo se repartieron los regímenes por décadas | Cuánto se mueve un día corriente |
| Qué época fue la más severa en proporción de días agitados | Hasta dónde llega un día extremo |
| Si el activo cambió de naturaleza | Con qué frecuencia ocurren los días grandes |
| El riesgo fuera de sesión | En qué fechas concretas estuvieron los peaks |

En resumen: el otro informe habla de **épocas**; este habla de **magnitudes y frecuencias**.

## 4. Prohibición específica

**No describas la forma del histograma.** El lector la está viendo. Frases como "la distribución
presenta una cola derecha pronunciada" no aportan nada. Tu trabajo es traducir esa forma a
consecuencias: cuánto se mueve un día normal, cuánto uno malo, y cada cuánto ocurre.

---

## 5. Cómo encontrar los hallazgos

Cinco búsquedas. Publica las que superen su criterio, entre tres y cuatro, ordenadas por utilidad
para el operador. Si obtienes menos de tres, aplica la regla de cupo incompleto.

### D1 · ¿Cuánto se mueve un día corriente frente al promedio?

Compara el movimiento del día típico con el movimiento promedio.

- **Hay hallazgo si** el promedio supera al típico en más de un 20%.
- **Redacta:** ambas cifras, y que la diferencia proviene de unas pocas sesiones muy grandes que
  elevan la media. Nombra el número del día corriente: es la referencia que el lector necesita
  memorizar sobre este activo.
- **Cierre:** usar el promedio para calcular el tamaño de una posición sobreestima el día normal.
- **Si no hay hallazgo**, es decir, si ambas cifras son parecidas, publícalo igualmente como
  observación breve dentro de otro punto: significa que el activo tiene un comportamiento diario
  regular, sin sesiones que se salgan de la norma. Es información valiosa.

### D2 · ¿Hasta dónde llega un día extremo?

Compara el movimiento del 5% de días más agitados con el del día típico, y también el máximo
histórico.

- **Hay hallazgo si** la razón entre ambos supera 2.
- **Redacta:** cuántas veces más grande es un día extremo frente a uno corriente. Añade el máximo
  histórico como referencia del techo alcanzado.
- **Cierre:** un stop calibrado para un día corriente no sobrevive a un día extremo, y estos no son
  tan raros como el lector supone.

### D3 · ¿Con qué frecuencia ocurren los días grandes?

Calcula qué proporción de sesiones supera el doble del movimiento del día típico, y conviértela en
frecuencia.

- **Publícalo siempre.** Es la traducción más útil de todo el panel y no está en pantalla.
- **Redacta:** "uno de cada N días", nunca un porcentaje. Si el resultado ronda una frecuencia
  reconocible, dilo así: una vez por semana, una vez al mes, un par de veces al año.
- **Cierre:** con qué periodicidad el lector debe esperar una sesión que duplique lo habitual.

### D4 · ¿Qué tan cerca está la calma de la turbulencia?

Calcula cuánto debe subir el movimiento diario desde el día típico para que el sistema lo clasifique
como volatilidad alta.

- **Hay hallazgo si** la distancia es inferior al 25%.
- **Redacta:** que basta un aumento pequeño respecto de lo habitual para que el activo cambie de
  clasificación, y que por tanto la etiqueta alta aparece con facilidad en este instrumento.
- **Cierre:** en este activo la etiqueta de volatilidad alta es sensible y conviene mirar la cifra,
  no solo el color.
- **Si la distancia es grande**, el enunciado se invierte: la etiqueta alta exige un cambio
  considerable y por eso es una señal más contundente.

### D5 · ¿Cuáles fueron los momentos más volátiles de su historia?

Identifica los episodios de mayor volatilidad de toda la serie y sus fechas.

- **Hay hallazgo si** los peaks se concentran en uno o dos períodos identificables.
- **Redacta:** las fechas y el nivel alcanzado, comparado con el día típico. **Limítate a las
  fechas.** No expliques qué ocurrió en el mercado ni nombres el evento: no dispones de esa
  información y afirmarla sería inventar.
- **Cierre:** el techo que este activo ha demostrado alcanzar.

---

## 6. Estructura del documento

```
# Cuánto se mueve <ACTIVO> y hasta dónde puede llegar

<línea de contexto>

### 1 · <título como afirmación en lenguaje corriente>
<uno o dos párrafos cortos>
**Por qué te importa.** <una o dos frases en segunda persona>

### 2 · ...
### 3 · ...
### 4 · ...   (opcional)

### En una frase
<síntesis>

**Dos cosas que este análisis no te dice.** <no predice; no distingue comprar de vender>
```

---

## 7. Plantillas de forma

**No hay ejemplos con datos reales en este documento.** Solo plantillas. Cada marcador entre llaves
se sustituye por un valor calculado desde el endpoint para el instrumento solicitado.

### 7.1 · Plantilla cuando disparan cuatro búsquedas

*Supuesto: disparan D1, D2, D3 y D5; no dispara D4.*

---

> # Cuánto se mueve {INSTRUMENTO} y hasta dónde puede llegar
>
> *Cuatro cifras que conviene memorizar sobre este activo, sacadas de {años de historia} años de historia.*
>
> ### 1 · Un día corriente se mueve {día típico}, pero el promedio dice {promedio}
>
> Si tomas todos los días de la historia de este activo y buscas el del medio, ese día se movió un
> {día típico}. Esa es la cifra que describe una jornada normal.
>
> El promedio, en cambio, es {promedio}. La diferencia no es un error: unas pocas sesiones muy
> grandes elevan el promedio por encima de lo que ocurre habitualmente.
>
> **Por qué te importa.** Si calculas el tamaño de tus posiciones con el promedio, estás asumiendo un
> día más agitado del que vas a vivir la mayoría de las veces. La cifra a memorizar es {día típico}.
>
> ### 2 · Un día extremo se mueve {razón} veces más que uno corriente
>
> El 5% de días más agitados de este activo se mueven alrededor de {valor del percentil 95}. Y el día
> más volátil de toda su historia llegó a {máximo}, {razón del máximo} veces el día corriente.
>
> **Por qué te importa.** Un stop pensado para un día normal no aguanta un día extremo.
>
> ### 3 · Uno de cada {N} días dobla al día corriente
>
> Un {proporción} de las sesiones se mueven más del doble que una jornada normal. Traducido:
> aproximadamente {frecuencia en lenguaje corriente}.
>
> **Por qué te importa.** {Consecuencia según la frecuencia obtenida: si es alta, que debe contarlo
> como algo habitual; si es baja, que puede planificar con la cifra normal.}
>
> ### 4 · Sus momentos más volátiles se concentran en {período calculado}
>
> Los períodos de mayor volatilidad de la historia registrada de este activo ocurrieron entre
> {fecha inicial} y {fecha final}. En el más intenso, el movimiento diario llegó a {pico}.
>
> **Por qué te importa.** Ese es el techo que este activo ha demostrado alcanzar.
>
> ### En una frase
>
> {Síntesis de los cuatro hallazgos en una sola oración.}
>
> **Dos cosas que este análisis no te dice.** No predice cuánto se moverá mañana: describe lo que ha
> hecho antes. Y no distingue entre comprar y vender, porque mide cuánto se mueve el precio, no hacia
> dónde.

---

### 7.2 · Plantilla cuando disparan tres búsquedas

*Supuesto: disparan D3, D4 y D5; no disparan D1 ni D2, de modo que se aplica la variante de D1 como
observación breve dentro de otro punto.*

**Compara la extensión con la plantilla anterior.** Un informe con tres hallazgos no es un informe
incompleto: es el resultado correcto cuando el instrumento no presenta rasgos destacables en las
dimensiones restantes.

---

> # Cuánto se mueve {INSTRUMENTO} y hasta dónde puede llegar
>
> *Tres cifras que conviene memorizar sobre este activo, sacadas de {años de historia} años de historia.*
>
> ### 1 · Sus días grandes son poco frecuentes: uno de cada {N}
>
> Solo un {proporción} de las sesiones se mueven más del doble que una jornada normal. Traducido:
> aproximadamente {frecuencia en lenguaje corriente}.
>
> Conviene añadir algo: en este activo el día corriente y el día promedio se parecen mucho, cerca de
> {valor} ambos. Se comporta con regularidad, sin sesiones que se salgan demasiado de la norma.
>
> **Por qué te importa.** Puedes planificar con la cifra del día normal y acertarás la mayor parte
> del tiempo.
>
> ### 2 · Basta un alza pequeña para que aparezca la etiqueta de volatilidad alta
>
> El sistema lo clasifica como de volatilidad alta cuando su movimiento diario supera en apenas un
> {distancia} al de una jornada normal. Es una distancia corta.
>
> **Por qué te importa.** En este instrumento la etiqueta alta se enciende con facilidad y no siempre
> señala una situación grave. Mira la cifra concreta antes de reaccionar al color.
>
> ### 3 · {Título del hallazgo de peaks históricos, redactado según lo que arroje D5}
>
> {Fechas y niveles calculados.}
>
> **Por qué te importa.** Ese es el techo que este activo ha demostrado alcanzar.
>
> ### En una frase
>
> {Síntesis de los tres hallazgos en una sola oración.}
>
> **Dos cosas que este análisis no te dice.** No predice cuánto se moverá mañana: describe lo que ha
> hecho antes. Y no distingue entre comprar y vender, porque mide cuánto se mueve el precio, no hacia
> dónde.

---

### 7.3 · Cómo varían los informes entre instrumentos

Las plantillas anteriores difieren en número de hallazgos, en cuáles disparan y en el mensaje
central. Esa variación es el resultado esperado del procedimiento, no una excepción.

Antes de dar por terminado el informe, comprueba que su forma responde a **tus** búsquedas. Si tu
informe reproduce el número de hallazgos, el orden o el énfasis de una plantilla sin que tus datos lo
justifiquen, la estás copiando.

---

## 8. Validación del método

Las cinco búsquedas deben producir resultados distintos según el instrumento: distinta cantidad de
hallazgos, distintos criterios superados y, en el caso de D4, enunciados de sentido opuesto. Esa
variación es la prueba de que caracterizan al activo y no al método.

**Los resultados de validación sobre instrumentos concretos no se registran aquí.** Corresponden a la
capa de evidencia (`docs/evidence/`), que es donde el proyecto guarda las mediciones fechadas y
reproducibles. Este documento describe el procedimiento; la evidencia describe lo que se obtuvo al
aplicarlo, y caduca cuando los datos se recargan.

Advertencia general para el redactor: si una búsqueda arroja **el mismo resultado en todos los
instrumentos** que hayas analizado, es probable que derive de la definición de los indicadores y no
del comportamiento del activo. Sigue siendo útil como enseñanza para quien está aprendiendo, pero no
la presentes como rasgo distintivo del instrumento.
## 9. Trazabilidad

| Búsqueda | Campos de `chart_data` |
| :-- | :-- |
| D1 | `natr` — valor central y promedio |
| D2 | `natr` — percentil 95 y máximo |
| D3 | `natr` — proporción sobre el doble del valor central |
| D4 | `natr` — umbral superior de régimen frente al valor central |
| D5 | `natr`, `dates` — sesiones más extremas agrupadas en episodios |
