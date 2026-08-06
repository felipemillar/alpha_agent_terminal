---
title: "Instrucciones — Informe de Caracterización Estructural del Instrumento"
tags: [instrucciones, agente, informe, adn, pilar1, qrt-solutions]
date: 2026-08-04
seccion: Caracterización Estructural del Instrumento (Volatility Desk)
fuente_datos: GET /api/adn/pilar1?asset=<nombre>
aplica_a: cualquier instrumento cargado en el sistema
---

# Instrucciones — Informe de Caracterización Estructural del Instrumento

Definen cómo el agente debe redactar la interpretación de la sección **Caracterización Estructural
del Instrumento** para cualquier activo. El resultado debe ser idéntico en forma y distinto en
contenido para cada instrumento: la estructura es fija, los hallazgos salen de los datos.

---

## Regla cero · El instrumento es un parámetro, no un dato conocido

**Este documento no describe ningún activo.** Describe un procedimiento que se aplica al instrumento
que el usuario tenga cargado en el dashboard en ese momento, sea cual sea.

El nombre del instrumento llega en tiempo de ejecución. **Todas las cifras deben recalcularse desde
el endpoint para ese instrumento concreto.** Nada de lo que sepas sobre un activo por otra vía puede
entrar en el informe: ni por su nombre, ni por su sector, ni por su reputación, ni por lo que hayas
leído en otro lugar, ni por lo que aparezca en el ejemplo de este documento.

**Antes de escribir una sola línea, comprueba:**

1. Obtuviste el JSON del endpoint para el instrumento solicitado.
2. Cada cifra que vas a publicar proviene de ese JSON.
3. Ejecutaste las siete búsquedas sobre esos datos, sin dar por supuesto ningún resultado.

**Este documento no contiene ninguna cifra de ningún instrumento.** Es deliberado. El dashboard
incorpora activos nuevos con el tiempo y los datos se recargan periódicamente, de modo que cualquier
valor memorizado aquí quedaría obsoleto o sería directamente falso para el instrumento que tienes
delante. La sección 8 ofrece una **plantilla** con marcadores entre llaves; cada uno debe sustituirse
por un valor que hayas calculado.

**Señales de que algo no proviene de los datos.** Si detectas cualquiera de estas, descarta lo escrito
y vuelve a empezar:

- Queda un marcador entre llaves sin sustituir.
- Aparece el nombre de un instrumento distinto al solicitado.
- Aparece una fecha o un período que no calculaste tú.
- Afirmas un hallazgo cuya búsqueda **no superó su criterio** en este instrumento.
- Alguna cifra procede de tu conocimiento general y no del JSON.

---

## 1. Destinatario

**Un trader minorista que está aprendiendo.** Puede no saber qué es la volatilidad realizada, un
percentil o un régimen. Sabe lo que es comprar, vender, un stop loss y perder dinero.

Todo lo que escribas debe ser comprensible para esa persona sin consultar nada más. Si una frase
exige conocimiento previo, reescríbela.

## 2. Fuente de datos

Únicamente `GET /api/adn/pilar1?asset=<nombre>`. No uses ninguna otra fuente, ni web, ni tu
conocimiento general sobre el activo. Todo lo que afirmes debe poder rastrearse a ese JSON.

## 3. Prohibiciones absolutas

| No hagas esto | Motivo |
| :-- | :-- |
| Mencionar la sesión de hoy, el precio actual o el régimen vigente | Este informe describe la historia del instrumento, no su estado. El estado está en pantalla |
| Repetir tablas, porcentajes o cifras que el panel ya muestra | El lector las tiene delante. Tu aporte es lo que significan |
| Predecir, proyectar o sugerir hacia dónde irá el precio | El informe describe lo registrado |
| Afirmar algo sobre comprar o vender | La volatilidad no tiene signo. Esa lectura corresponde al informe de riesgo de cola |
| Usar metáforas, analogías o lenguaje figurado | Registro profesional. Sin peajes, colas que matan, ADN ni huellas |
| Usar jerga sin traducir: curtosis, percentil, exponente, estimador, varianza | Si necesitas el concepto, explícalo en palabras corrientes sin nombrarlo |
| Emojis, signos de exclamación, mayúsculas enfáticas | Norma del proyecto |
| Explicar cómo se calcula un indicador | Al lector le interesa qué significa, no la fórmula |

## 4. Estructura del documento

```
# Lo que la historia de <ACTIVO> te enseña sobre este activo

<línea de contexto: cuántos hallazgos y sobre cuántos años de historia>

### 1 · <título del hallazgo, en lenguaje corriente>
<uno o dos párrafos cortos>
**Por qué te importa.** <una o dos frases, en segunda persona, con una acción o un cuidado concreto>

### 2 · ...
### 3 · ...
### 4 · ...   (opcional)

### En una frase
<síntesis de los hallazgos en una sola oración>

**Dos cosas que este análisis no te dice.** <no predice; no distingue comprar de vender>
```

**Entre tres y cuatro hallazgos** es el objetivo habitual. Si encuentras más de cuatro, publica los
cuatro más relevantes para quien va a operar. Si encuentras menos de tres, aplica la regla del final
de la sección 5: publica los que haya y declara que el instrumento no presenta rasgos destacables en
las dimensiones restantes. **Nunca completes el cupo forzando un hallazgo débil.**

## 5. Cómo encontrar los hallazgos

Ejecuta las siete búsquedas siguientes sobre el JSON. Cada una tiene un criterio que determina si
hay hallazgo. Publica solo las que lo superen, ordenadas por utilidad para el operador y no por el
orden de esta lista.

**Advertencia central: el resultado de cada búsqueda depende del instrumento.** Un activo puede
haberse vuelto más tranquilo y otro más agitado; en uno puede predominar la contracción y en otro la
expansión. Varias de estas búsquedas admiten enunciados de sentido opuesto según lo que arrojen los
datos. Redacta lo que digan, sin dar por supuesto ningún resultado.

### B1 · ¿Cambió de naturaleza a lo largo de los años?

Compara el bloque temporal de mayor volatilidad media con el de menor.

- **Hay hallazgo si** la razón entre ambos supera 1,5.
- **Redacta:** si el bloque más volátil es antiguo, que el activo se ha vuelto más tranquilo; si es
  reciente, que se ha vuelto más agitado.
- **Añade la consecuencia:** los umbrales que definen volatilidad alta se calculan sobre toda la
  historia. Si el pasado fue más agitado, la etiqueta alta es hoy más exigente. Si fue más tranquilo,
  es más fácil de alcanzar y por tanto menos informativa.

### B2 · ¿El peor período es el que el operador recuerda?

Ordena los bloques por proporción de sesiones en régimen alto.

- **Hay hallazgo si** el bloque más severo no es ninguno de los dos más recientes.
- **Redacta:** el episodio que el lector tiene presente por cercanía no es el más severo del
  registro. Señala cuál lo fue y, sobre todo, si duró más.
- **Valor para el lector:** corrige su referencia mental de peor escenario.

### B3 · ¿Qué dirección predomina cuando la volatilidad es alta?

Mira el reparto entre expansión y contracción dentro de la fila de régimen alto.

- **Hay hallazgo si** una de las dos supera el 55%.
- **Redacta:** si predomina la contracción, que encontrar el activo en volatilidad alta suele
  significar que el episodio está resolviéndose. Si predomina la expansión, que suele significar que
  está construyéndose, lo que constituye una advertencia mucho mayor.
- Este suele ser el hallazgo más contraintuitivo y merece un lugar destacado.

### B4 · ¿Sube más rápido de lo que baja?

Compara la duración de las fases de expansión con las de contracción, en la duración típica, en las
prolongadas y en la máxima registrada.

- **Hay hallazgo si** la asimetría apunta en la misma dirección en las tres mediciones.
- **Redacta:** que la volatilidad sube de una forma y baja de otra, sin nombrar las tres mediciones
  por separado. Basta con afirmar la propiedad.
- Si B3 y B4 apuntan a lo mismo, **fúndelos en un solo hallazgo**. Refuerzan la misma idea.

### B5 · ¿Cuánto riesgo ocurre con el mercado cerrado?

Toma la fracción de riesgo fuera de sesión.

- **No aplica** a instrumentos que cotizan de forma continua, sin horario de cierre. En ese caso,
  omite la búsqueda por completo.
- **Si el segundo método de cálculo no está disponible**, dilo: indica que la cifra proviene de un
  solo método y es menos firme.
- **Escala de lectura:** por debajo del 15%, bajo; entre 15% y 30%, moderado; por encima del 30%,
  alto.
- **Redacta:** que un stop loss solo funciona con el mercado abierto, y que en ese intervalo el
  precio puede abrir más allá del nivel fijado. Cierra indicando que la protección en ese tramo es el
  tamaño de la posición.

### B6 · ¿Sirve toda la historia como referencia?

Compara la posición de la volatilidad reciente respecto de la historia completa contra su posición
respecto de los últimos cinco años.

- **Hay hallazgo si** ambas difieren en más de 15 puntos.
- **Redacta:** que la lectura del activo cambia según el período con el que se compare, e indica cuál
  conviene usar.
- Si coinciden, no lo publiques como hallazgo; a lo sumo menciónalo como respaldo de otro.

### B7 · ¿Cuán raro es el estrés en este activo?

Toma la proporción de la historia que superó el umbral de expansión de horizonte medio.

- **Hay hallazgo si** es inferior al 10%.
- **Redacta:** que ese nivel marca episodios genuinamente excepcionales en este instrumento, y que
  alcanzarlo es una señal poco frecuente.

### Si menos de tres búsquedas producen hallazgo

No inventes ni fuerces. Publica los que haya y añade una línea indicando que el instrumento no
presenta rasgos estructurales destacables en las dimensiones restantes. Un activo estadísticamente
anodino es en sí mismo información útil.

## 6. Reglas de redacción

| Regla | Detalle |
| :-- | :-- |
| Una idea por párrafo | Dos o tres frases como máximo |
| Frases cortas | Si una frase tiene dos comas y una subordinada, pártela |
| Títulos como afirmación | "Hoy es un activo mucho más tranquilo que cuando empezó", no "Evolución temporal del régimen" |
| Segunda persona en el cierre | "Por qué te importa" habla directamente al lector |
| Proporciones antes que porcentajes | "Tres de cada cuatro días" se entiende mejor que "el 74,8% de las sesiones" |
| Cifras solo cuando la cifra es el hallazgo | Si el número está en el panel, descríbelo en palabras |
| Sin condicionales acumulados | Evita "podría eventualmente tender a" |

## 7. Lista de verificación antes de publicar

1. ¿Hay entre tres y cuatro hallazgos?
2. ¿Alguno menciona la sesión de hoy, el precio o el régimen actual? Debe eliminarse.
3. ¿Alguno repite una tabla o un porcentaje visible en pantalla?
4. ¿Alguno afirma algo sobre comprar o vender?
5. ¿Alguno predice?
6. ¿Queda alguna palabra que el destinatario no entendería sin buscarla?
7. ¿Cada hallazgo cierra con "Por qué te importa" y una acción o un cuidado concreto?
8. ¿Está el resumen en una frase y el aviso de los dos límites?
9. ¿Todo lo afirmado se rastrea al JSON del endpoint?
10. ¿Queda algún marcador entre llaves sin sustituir por un valor calculado?
11. ¿Coincide el número de apartados con el de la plantilla sin que las búsquedas lo justifiquen?

## 8. Plantilla de forma

**No hay ejemplos con datos reales en este documento.** Solo una plantilla. Cada marcador entre
llaves se sustituye por un valor calculado desde el endpoint para el instrumento solicitado.

El número de apartados depende de cuántas búsquedas superen su criterio: la plantilla muestra tres,
pero pueden ser cuatro.

---

> # Lo que la historia de {INSTRUMENTO} te enseña sobre este activo
>
> *{Número} cosas que conviene saber antes de operarlo. Todo sale de sus {años} años de historia.*
>
> ### 1 · {Título del primer hallazgo, como afirmación en lenguaje corriente}
>
> {Uno o dos párrafos cortos. Una idea por párrafo. Proporciones antes que porcentajes cuando se
> pueda: "tres de cada cuatro días" en lugar de una cifra con decimales.}
>
> **Por qué te importa.** {Una o dos frases en segunda persona, con una acción o un cuidado
> concreto.}
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
> **Dos cosas que este análisis no te dice.** No predice nada: solo describe lo que ya pasó. Y no
> distingue entre comprar y vender, porque la volatilidad mide cuánto se mueve el precio, no hacia
> dónde.

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

## 10. Trazabilidad de las búsquedas

Correspondencia entre cada búsqueda y el indicador del catálogo que la alimenta.

| Búsqueda | Indicador | Clave en el JSON |
| :-- | :-- | :-- |
| B1, B2 | P1.02 · Reparto de régimen por época | `P1_02_reparto_por_epoca.bloques` |
| B3 | P1.05 · Dependencia entre nivel y dirección | `P1_05_dependencia_ejes.reparto` |
| B4 | P1.04 · Persistencia del estado direccional | `P1_04_persistencia_estado` |
| B5 | P1.07 · Descomposición fuera de sesión | `P1_07_descomposicion_sesion` |
| B6 | P1.02 · Reparto de régimen por época | `percentil_historia_completa`, `percentil_ultimos_5a` |
| B7 | P1.08 · Razón de régimen a horizonte medio | `P1_08_vrr.expansion_pct` |

Los indicadores P1.01, P1.03 y P1.06 no alimentan hallazgos por sí solos: P1.01 y P1.03 aportan
contexto ya visible en pantalla, y P1.06 es insumo de B5.
