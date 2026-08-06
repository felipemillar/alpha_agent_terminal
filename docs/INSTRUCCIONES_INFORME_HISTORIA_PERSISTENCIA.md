---
title: "Instrucciones — Informe de Historia y Persistencia de la Volatilidad"
tags: [instrucciones, agente, informe, pilar4, persistencia, qrt-solutions]
date: 2026-08-04
seccion: Persistencia del régimen · Línea de tiempo · Histograma de distribución · Dispersión de retornos
fuente_datos: GET /api/streaks, GET /api/markov, GET /api/volatility
aplica_a: cualquier instrumento cargado en el sistema
hermano: docs/INSTRUCCIONES_INFORME_CARACTERIZACION_ESTRUCTURAL.md
---

# Instrucciones — Informe de Historia y Persistencia de la Volatilidad

Definen cómo el agente debe redactar la interpretación de la sección que contiene la línea de tiempo
de volatilidad y sus tres paneles acompañantes.

**Pregunta que responde este informe:** cuánto duran los estados de volatilidad de este instrumento y
cómo se ha repartido su historia.

Las reglas de destinatario, redacción y verificación son **las mismas** del
[informe de caracterización estructural](INSTRUCCIONES_INFORME_CARACTERIZACION_ESTRUCTURAL.md),
secciones 1, 6 y 7. Aquí solo se detalla lo específico de esta sección.

---

## Regla cero · El instrumento es un parámetro, no un dato conocido

**Este documento no describe ningún activo.** Describe un procedimiento que se aplica al instrumento
que el usuario tenga cargado en el dashboard en ese momento, sea cual sea.

El nombre del instrumento llega en tiempo de ejecución. **Todas las cifras deben recalcularse desde
los endpoints para ese instrumento concreto.** Nada de lo que sepas sobre un activo por otra vía puede
entrar en el informe: ni por su nombre, ni por su sector, ni por su reputación, ni por lo que hayas
leído en otro lugar, ni por lo que aparezca en el ejemplo de este documento.

**Antes de escribir una sola línea, comprueba:**

1. Obtuviste los JSON de los endpoints para el instrumento solicitado.
2. Cada cifra que vas a publicar proviene de esos JSON.
3. Ejecutaste las cinco búsquedas sobre esos datos, sin dar por supuesto ningún resultado.

**Este documento no contiene ninguna cifra de ningún instrumento.** Es deliberado. El dashboard
incorpora activos nuevos con el tiempo y los datos se recargan periódicamente, de modo que cualquier
valor memorizado aquí quedaría obsoleto o sería directamente falso para el instrumento que tienes
delante. La sección 8 ofrece una **plantilla** con marcadores entre llaves; cada uno debe sustituirse
por un valor que hayas calculado.

**Advertencia particular de esta sección.** Algunas de estas búsquedas pueden arrojar **el mismo
resultado en todos los instrumentos**, porque miden propiedades que derivan de cómo está definido el
régimen y no del comportamiento del activo. Eso eleva aquí el riesgo de dar un resultado por supuesto
sin comprobarlo. Calcúlalo siempre sobre el instrumento que tienes delante y, si compruebas que se
repite en todos, no lo presentes como rasgo distintivo: úsalo como enseñanza general para quien está
aprendiendo.

**Señales de que algo no proviene de los datos.** Si detectas cualquiera de estas, descarta lo escrito
y vuelve a empezar:

- Queda un marcador entre llaves sin sustituir.
- Aparece el nombre de un instrumento distinto al solicitado.
- Aparece una fecha o un período que no calculaste tú.
- Afirmas un hallazgo cuya búsqueda **no superó su criterio** en este instrumento.
- Alguna cifra procede de tu conocimiento general y no del JSON.

---

## 1. Paneles que cubre

| Panel | Qué aporta al informe |
| :-- | :-- |
| Persistencia del régimen | Duración de los episodios y probabilidad de cambio de estado |
| Línea de tiempo de volatilidad | La historia completa vista de corrido |
| Histograma de distribución | La forma de la distribución de la volatilidad |
| Dispersión de retornos diarios | Relación entre el nivel de volatilidad y el tamaño de los movimientos |

## 2. Fuente de datos

`GET /api/streaks?asset=<nombre>&regime=ALL`, `GET /api/markov?asset=<nombre>` y
`GET /api/volatility?asset=<nombre>`. Ninguna otra.

---

## 3. Prohibición crítica: los ceros de la matriz de transición

En prácticamente todo instrumento, la matriz de transición muestra **probabilidad cero** de pasar
directamente de volatilidad baja a alta, o de alta a baja, en una sola sesión.

**Está terminantemente prohibido interpretar ese cero como un rasgo del mercado.**

Es una consecuencia matemática de cómo se define el régimen. La clasificación se apoya en un promedio
de catorce sesiones, y una media suavizada no puede cruzar dos terciles en un día. El cero describe el
comportamiento del indicador, no el del precio.

Un agente que escriba *"este activo nunca pasa de la calma a la crisis sin avisar"* estaría induciendo
a un error grave: el precio **sí** salta, y de hecho una parte sustancial del riesgo de muchos
instrumentos se materializa entre el cierre y la apertura siguiente. Confundir ambas cosas puede
llevar al lector a subestimar precisamente el riesgo que no puede controlar.

**Regla:** no menciones las transiciones entre extremos. Usa la matriz únicamente para comparar la
estabilidad relativa de los tres estados, que es lo que sí aporta información.

## 4. Prohibición adicional: la cobertura de los regímenes

La proporción de la historia que corresponde a cada régimen es siempre cercana a un tercio, porque los
umbrales se definen así. **No la publiques como hallazgo.** No dice nada sobre el instrumento.

## 5. Frontera con el informe de caracterización estructural

Ambos informes miran la historia, pero responden preguntas distintas. No invadas la del otro.

| Corresponde al informe estructural | Corresponde a este informe |
| :-- | :-- |
| Cómo cambió el **nivel** de volatilidad entre épocas | Cuánto **duran** los episodios |
| Qué período fue el más severo | Si un episodio concreto domina la historia |
| Qué dirección predomina dentro de un régimen | Qué estado es el menos estable |
| Riesgo fuera de sesión | Relación entre volatilidad y tamaño de los movimientos |

Si al ejecutar las búsquedas obtienes un hallazgo que ya pertenece al informe estructural, descártalo.

---

## 6. Cómo encontrar los hallazgos

Cinco búsquedas. Publica las que superen su criterio, entre tres y cuatro, ordenadas por utilidad
para el operador. Si obtienes menos de tres, aplica la regla de cupo incompleto: publica los que haya
y declara que el instrumento no presenta rasgos destacables en las dimensiones restantes.

### C1 · ¿Cuánto dura un episodio de volatilidad?

Compara la duración típica de los episodios con su duración promedio.

- **Hay hallazgo si** el promedio supera al doble de la duración típica.
- **Redacta:** que la mitad de los episodios son breves, pero unos pocos muy prolongados elevan el
  promedio. Expresa las duraciones en semanas o meses, no en número de sesiones.
- **Cierre:** el promedio no sirve para anticipar cuánto durará el episodio en curso.

### C2 · ¿Hay un episodio que domine la historia?

Toma el episodio más largo registrado, con su régimen y sus fechas.

- **Hay hallazgo si** representa más del 5% de la historia total del instrumento.
- **Redacta:** el período concreto, su duración en años o meses, y qué fracción de la historia
  completa representa. Si el instrumento tiene un nombre reconocible para ese período, no lo
  interpretes ni lo expliques: limítate a las fechas.
- **Cierre:** cuando este activo entra en un período difícil, puede permanecer así durante mucho más
  que unas semanas.

### C3 · ¿Qué estado es el menos estable?

Compara la estabilidad relativa de los tres regímenes en la matriz de transición.

- **Hay hallazgo si** uno de los tres es apreciablemente menos estable que los otros dos.
- **Redacta:** que el activo tiende a permanecer donde está, salvo en ese estado, que atraviesa en
  lugar de habitar.
- **Prohibido:** citar probabilidades de la matriz. Son cercanas a 1 por construcción y su magnitud
  no es informativa. Habla de estabilidad relativa, no de porcentajes.

### C4 · ¿Cómo es la forma de la distribución de la volatilidad?

Compara el movimiento del día típico con el movimiento promedio.

- **Hay hallazgo si** el promedio supera en más de un 20% al día típico.
- **Redacta:** que el día corriente se mueve bastante menos que el promedio, y que la diferencia
  proviene de unas pocas sesiones muy violentas.
- **Cierre:** dimensionar con el promedio sobreestima el día corriente y subestima el extremo.

### C5 · ¿Crecen los movimientos con la volatilidad?

Compara el tamaño medio del movimiento diario en régimen bajo contra el de régimen alto.

- **Hay hallazgo si** la razón supera 2, o si **no se cumple la relación esperada**, en cuyo caso es
  un hallazgo mucho más importante y debe encabezar el informe.
- **Redacta:** cuántas veces mayor es el movimiento de un día de volatilidad alta frente a uno de
  volatilidad baja.
- **Cierre:** el mismo tamaño de posición representa un riesgo muy distinto según el régimen.

---

## 7. Estructura del documento

Idéntica a la del informe estructural:

```
# Lo que la historia de <ACTIVO> te enseña sobre sus períodos de volatilidad

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

## 8. Plantilla de forma

**No hay ejemplos con datos reales en este documento.** Solo una plantilla. Cada marcador entre
llaves se sustituye por un valor calculado desde los endpoints para el instrumento solicitado.

---

> # Lo que la historia de {INSTRUMENTO} te enseña sobre sus períodos de volatilidad
>
> *{Número} cosas que conviene saber sobre cuánto duran sus momentos difíciles.*
>
> ### 1 · {Título del primer hallazgo, como afirmación en lenguaje corriente}
>
> {Uno o dos párrafos cortos. Expresa las duraciones en semanas o meses, no en número de sesiones.}
>
> **Por qué te importa.** {Una o dos frases en segunda persona.}
>
> ### 2 · {Título del segundo hallazgo}
>
> {Desarrollo.}
>
> **Por qué te importa.** {Consecuencia.}
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
> **Dos cosas que este análisis no te dice.** No predice cuánto durará el episodio actual: describe lo
> que ocurrió antes. Y no distingue entre comprar y vender.

---

**Comprueba antes de terminar.** Si tu informe reproduce el número de apartados o el orden de esta
plantilla sin que tus búsquedas lo justifiquen, la estás rellenando en lugar de aplicar el
procedimiento.

---

## 9. Validación del método

Las búsquedas deben producir resultados distintos según el instrumento: distinta cantidad de
hallazgos, distintos criterios superados y, en varias de ellas, enunciados de sentido opuesto. Esa
variación es la prueba de que caracterizan al activo y no al método.

**Los resultados de validación sobre instrumentos concretos no se registran aquí.** Corresponden a la
capa de evidencia (`docs/evidence/`), que es donde el proyecto guarda las mediciones fechadas y
reproducibles. Este documento describe el procedimiento; la evidencia describe lo que se obtuvo al
aplicarlo, y caduca cuando los datos se recargan o se incorporan activos nuevos.

Advertencia general para el redactor: si una búsqueda arroja **el mismo resultado en todos los
instrumentos** que hayas analizado, es probable que derive de la definición de los indicadores y no
del comportamiento del activo. Sigue siendo útil como enseñanza para quien está aprendiendo, pero no
la presentes como rasgo distintivo del instrumento.

## 10. Trazabilidad

| Búsqueda | Endpoint | Campos |
| :-- | :-- | :-- |
| C1 | `/api/streaks` | `summary.median_duration`, `summary.avg_duration`, `summary.total_streaks` |
| C2 | `/api/streaks` | `streaks[].duration`, `regime`, `start_date`, `end_date` |
| C3 | `/api/markov` | `persistence` |
| C4 | `/api/volatility` | `chart_data.natr` |
| C5 | `/api/volatility` | `chart_data.return`, `chart_data.regimes` |
