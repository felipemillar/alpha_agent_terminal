---
title: "Instrucciones — Informe de Distribución de Retornos"
tags: [instrucciones, agente, informe, retornos, zscore, qrt-solutions]
date: 2026-08-04
seccion: Dispersión de retornos diarios · Evaluación estocástica de retornos (Z-Score)
fuente_datos: GET /api/volatility?asset=<nombre>
aplica_a: cualquier instrumento cargado en el sistema
---

# Instrucciones — Informe de Distribución de Retornos

Definen cómo el agente debe redactar la interpretación de la sección compuesta por **dos paneles**:
la dispersión de retornos diarios y la evaluación estocástica con la campana.

**Pregunta que responde este informe:** cómo se reparten las ganancias y pérdidas diarias de este
instrumento, y hasta qué punto se puede confiar en la campana para anticiparlas.

Las reglas de destinatario, redacción y verificación son **las mismas** del
[informe de caracterización estructural](INSTRUCCIONES_INFORME_CARACTERIZACION_ESTRUCTURAL.md),
secciones 1, 6 y 7.

---

## Regla cero · El instrumento es un parámetro, no un dato conocido

**Este documento no describe ningún activo.** Describe un procedimiento que se aplica al instrumento
que el usuario tenga cargado en el dashboard en ese momento, sea cual sea.

El nombre del instrumento llega en tiempo de ejecución. **Todas las cifras deben recalcularse desde
el endpoint para ese instrumento concreto.** Nada de lo que sepas sobre un activo por otra vía puede
entrar en el informe: ni por su nombre, ni por su sector, ni por su reputación, ni por lo que hayas
leído en otro lugar.

**Este documento no contiene ninguna cifra de ningún instrumento.** Es deliberado. El dashboard
incorpora activos nuevos con el tiempo y los datos se recargan periódicamente, de modo que cualquier
valor memorizado aquí quedaría obsoleto o sería directamente falso para el instrumento que tienes
delante. La sección 7 ofrece una **plantilla** con marcadores entre llaves; cada uno debe sustituirse
por un valor que hayas calculado.

**Antes de escribir una sola línea, comprueba:**

1. Obtuviste el JSON del endpoint para el instrumento solicitado.
2. Cada cifra que vas a publicar proviene de ese JSON.
3. Ejecutaste las cinco búsquedas sobre esos datos, sin dar por supuesto ningún resultado.

**Señales de que algo no proviene de los datos.** Si detectas cualquiera de estas, descarta lo escrito
y vuelve a empezar:

- Queda un marcador entre llaves sin sustituir.
- Aparece el nombre de un instrumento distinto al solicitado.
- Afirmas un hallazgo cuya búsqueda **no superó su criterio** en este instrumento.
- Alguna cifra procede de tu conocimiento general y no del JSON.

---

## 1. Alcance

| Panel | Qué muestra |
| :-- | :-- |
| Dispersión de retornos diarios | Cada sesión situada según su retorno y el nivel de volatilidad de ese día, coloreada por régimen. Admite vista direccional y vista en valor absoluto |
| Evaluación estocástica de retornos | Retorno del día en desviaciones típicas, media histórica, dispersión, tamaño de muestra, medidas de forma y la campana con los umbrales de ±2 desviaciones |

**Fuera de alcance.** No comentes la magnitud de la volatilidad, la duración de los regímenes, la
memoria de la serie ni la pérdida esperada por lado de la posición. Cada uno tiene su propio informe.

## 2. Fuente de datos

`GET /api/volatility?asset=<nombre>`. Ninguna otra.

**Toma el tamaño de muestra del dato, no del rótulo.** Los rótulos descriptivos de este panel pueden
no coincidir con la serie efectivamente utilizada. Si el rótulo menciona un período y el campo de
muestra indica otro, **usa siempre el número de sesiones del dato** y calcula tú los años que
representa.

---

## 3. Prohibición crítica: el retorno del día

El número más visible de este panel es el retorno de la sesión en curso y su distancia respecto de la
media. **Ese dato no entra en el informe.**

El lector lo tiene delante y se actualiza cada día; un informe que lo comente queda obsoleto en
horas. Tu trabajo es el contrario: **enseñarle a leer ese número por sí mismo**. Explica qué
representa una desviación típica en este activo concreto, qué movimiento equivale al umbral marcado
en el gráfico y con qué frecuencia se alcanza. Con eso, el lector interpretará cualquier valor que
vea mañana sin necesitar otro informe.

## 4. Prohibición adicional: describir la campana

No digas que la distribución "presenta colas pesadas" ni que "se aproxima a una normal". El lector
está viendo la curva y la etiqueta correspondiente. Traduce esa forma a consecuencias: con qué
frecuencia ocurren realmente los movimientos extremos y en qué medida difiere de lo que la curva
sugiere.

## 5. Frontera con los demás informes

| Corresponde a otro informe | Corresponde a este |
| :-- | :-- |
| Cuánto se mueve el activo en un día corriente | Cómo se reparten esos movimientos alrededor de su media |
| Cuánto duran los episodios de volatilidad | Con qué frecuencia aparecen los retornos extremos |
| La pérdida esperada según se compre o se venda | Si las subidas y las bajadas tienen tamaños comparables |

---

## 6. Cómo encontrar los hallazgos

Cinco búsquedas. Publica las que superen su criterio, entre tres y cuatro, ordenadas por utilidad
para el operador. Si obtienes menos de tres, aplica la regla de cupo incompleto.

### E1 · ¿Cuánto vale una desviación típica en este activo?

Toma la dispersión de los retornos diarios y tradúcela a un movimiento porcentual concreto. Calcula
también a cuánto equivale el umbral de dos desviaciones marcado en el gráfico.

- **Publícalo siempre.** Es la clave para que el lector interprete el panel por su cuenta, y no está
  escrita en pantalla en términos de dinero.
- **Redacta:** a qué movimiento porcentual equivale una desviación típica, y a cuál equivale el
  umbral marcado. Evita la palabra sigma y el símbolo: di "una desviación típica" o directamente el
  porcentaje.
- **Cierre:** cuando el lector vea el indicador cerca del umbral, sabrá qué movimiento tiene delante.

### E2 · ¿Dónde deja de funcionar la campana?

Compara la frecuencia **real** con que este activo supera dos, tres y cuatro desviaciones típicas
contra la frecuencia que predice una distribución normal para esos mismos umbrales.

- **Hay hallazgo si** la frecuencia real de los movimientos de cuatro desviaciones supera en más de
  diez veces a la teórica. En la práctica esto ocurre en casi todos los instrumentos financieros.
- **Redacta:** las frecuencias en formato "uno de cada N días" y, cuando N sea grande, también en
  años. Muestra que en el entorno de dos desviaciones la curva es razonablemente fiel y que la
  discrepancia crece a medida que el movimiento se hace más extremo.
- **Cierre:** el umbral marcado en el gráfico es una referencia útil; más allá de él, la curva
  subestima gravemente lo que este activo puede hacer.
- **Este suele ser el hallazgo más valioso de la sección** y conviene situarlo en primer lugar.

### E3 · ¿Son comparables las subidas y las bajadas?

Toma la medida de asimetría de la distribución.

- **Hay hallazgo si** su valor absoluto supera 0,3.
- **Redacta:** si es negativa, que las caídas grandes superan en tamaño a las subidas grandes; si es
  positiva, lo contrario. No nombres la medida: describe el efecto.
- **Si el valor es próximo a cero**, publícalo igualmente como observación breve: significa que las
  sesiones extremas tienen tamaño parecido en ambos sentidos, de modo que el lector no debe esperar
  que un lado le duela más que el otro por razón del tamaño.

### E4 · ¿Crece el tamaño de los movimientos con la volatilidad?

Compara el tamaño medio del movimiento diario, sin signo, en régimen bajo frente al de régimen alto.
Es la lectura del panel de dispersión.

- **Hay hallazgo si** la razón supera 2, o si **no se cumple la relación esperada**, en cuyo caso es
  un hallazgo mucho más importante y debe encabezar el informe.
- **Redacta:** cuántas veces mayor es el movimiento de una sesión de volatilidad alta frente a una de
  volatilidad baja.
- **Cierre:** el mismo tamaño de posición representa un riesgo muy distinto según el régimen, y la
  dispersión del panel lo muestra como dos nubes separadas.

### E5 · ¿Tiene este activo una tendencia media apreciable?

Compara la media de los retornos diarios con su propia precisión, dada la dispersión y el tamaño de
la muestra.

- **Hay hallazgo en ambos sentidos.** Si la media no es distinguible de cero, ese es el hallazgo. Si
  lo es, también.
- **Redacta:** cuando no sea distinguible de cero, que a lo largo de toda su historia este activo no
  muestra una inclinación media apreciable en ninguna dirección, y que por tanto el resultado de
  operarlo no proviene de mantenerlo sino de cuándo se entra y se sale. Cuando sí lo sea, indica el
  sentido y la magnitud anualizada.
- **Prohibido:** presentar la media diaria como una expectativa de ganancia. Es un promedio
  histórico, no una previsión.

---

## 7. Plantilla de forma

**No hay ejemplos con datos reales en este documento.** Cada marcador entre llaves se sustituye por
un valor calculado desde el endpoint para el instrumento solicitado.

---

> # Cómo se reparten las ganancias y pérdidas de {INSTRUMENTO}
>
> *{Número} cosas que conviene entender para leer este panel, sacadas de {años} años de historia.*
>
> ### 1 · La campana funciona en el centro y falla en los extremos
>
> {Frecuencia real y teórica en el entorno de dos desviaciones, mostrando que son parecidas.}
>
> {Frecuencia real y teórica en cuatro desviaciones, mostrando la magnitud de la discrepancia,
> expresada en "uno de cada N días" y su equivalente en años.}
>
> **Por qué te importa.** El umbral marcado en el gráfico es una referencia razonable. Más allá de
> él, la curva subestima gravemente lo que este activo puede hacer en un solo día.
>
> ### 2 · Una desviación típica equivale a un movimiento de {valor}
>
> {Traducción de la dispersión a un movimiento porcentual, y del umbral marcado a su equivalente.}
>
> **Por qué te importa.** {Cómo usar esa equivalencia para leer el indicador cualquier día.}
>
> ### 3 · {Título del tercer hallazgo}
>
> {Desarrollo.}
>
> **Por qué te importa.** {Consecuencia.}
>
> ### En una frase
>
> {Síntesis de todos los hallazgos en una sola oración.}
>
> **Dos cosas que este análisis no te dice.** No predice el retorno de mañana: describe cómo se
> repartieron los de toda su historia. Y no indica si conviene comprar o vender.

---

**Comprueba antes de terminar.** Si tu informe reproduce el número de apartados o el orden de esta
plantilla sin que tus búsquedas lo justifiquen, la estás rellenando en lugar de aplicar el
procedimiento.

---

## 8. Validación del método

Las cinco búsquedas deben producir resultados distintos según el instrumento. E2 es la excepción
parcial: la discrepancia entre la frecuencia real y la teórica en los extremos aparece en
prácticamente todos los activos financieros, aunque su magnitud varía de forma apreciable entre
unos y otros. Publícala siempre con las cifras del instrumento analizado, nunca con cifras
recordadas.

**Los resultados de validación sobre instrumentos concretos no se registran aquí.** Corresponden a la
capa de evidencia (`docs/evidence/`), que es donde el proyecto guarda las mediciones fechadas y
reproducibles. Este documento describe el procedimiento; la evidencia describe lo que se obtuvo al
aplicarlo, y caduca cuando los datos se recargan o se incorporan activos nuevos.

---

## 9. Trazabilidad

| Búsqueda | Campos |
| :-- | :-- |
| E1 | Dispersión de los retornos diarios y umbral marcado en el gráfico |
| E2 | Serie de retornos normalizados; frecuencia observada por encima de cada umbral |
| E3 | Medida de asimetría de la distribución |
| E4 | Serie de retornos y etiqueta de régimen de cada sesión |
| E5 | Media de los retornos, su dispersión y el tamaño de la muestra |
