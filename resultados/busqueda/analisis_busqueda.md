# Análisis de la búsqueda real (arranques 0 y 1)

> Este análisis incorpora la **pasada de verificación del arranque 0** (pasada 3,
> sin cambios aceptados). Las cifras salen de `resumir.py` o de la salida de la
> celda de verificación del notebook; lo no comprobado va marcado como
> **inferencia**. La versión anterior, con 2 pasadas, queda en los archivos
> `*_2pasadas`.

Reproducción:

```
python resumir.py historial_arranque_0.csv historial_arranque_1_limpio.csv \
    --presupuesto 14400 --esperado-cfg-0 92 --esperado-cfg-1 28 \
    --esperado-union 117 --esperado-generaciones 11700
```

`historial_arranque_0.csv` tiene 110 filas (3 pasadas). Sus primeras 75 filas son
idénticas a `historial_arranque_0_2pasadas.csv`, que queda como foto de la versión
anterior.

En todo el documento, "mejor encontrada" es la mejor configuración que halló cada arranque;
no se afirma que sea óptima, ni global ni del subcatálogo (D8).

Modelo `qwen17b`, temperatura 0.0, semilla 1, 100 instancias de búsqueda por
configuración (D2). Las 100 instancias por configuración se infieren en
`resumir.py` como consultas finales / configuraciones distintas (9 200 / 92).

## 1. Los dos arranques

| | Arranque 0 | Arranque 1 |
|---|---|---|
| Configuración final | rol 1, estrategia 1, formato 3, estilo 3, cierre 3 | rol 1, estrategia 7, formato 3, estilo 5, cierre 3 |
| Precisión (100 instancias de búsqueda) | 0.20 | 0.17 |
| Configuraciones distintas | 92 | 28 |
| Generaciones (distintas × 100) | 9 200 | 2 800 |
| Pasadas | 3 (la tercera sin cambios aceptados) | 2 |
| Parada | convergencia | convergencia (pasada 2 sin cambios aceptados; el último fue el paso 16) |
| Fallos de la mejor encontrada | 80 de 100 | 83 de 100 |
| Fuente | `historial_arranque_0.csv` | `historial_arranque_1_limpio.csv` |

Las ocho mejores de la unión (precisión sobre búsqueda, no sobre validación):

| Precisión | rol | estrategia | formato | estilo | cierre |
|---|---|---|---|---|---|
| 0.20 | 1 | 1 | 3 | 3 | 3 |
| 0.19 | 1 | 1 | 3 | 7 | 3 |
| 0.19 | 1 | 1 | 6 | 7 | 3 |
| 0.17 | 1 | 1 | 3 | 0 | 3 |
| 0.17 | 1 | 1 | 3 | 5 | 3 |
| 0.17 | 1 | 4 | 3 | 3 | 3 |
| 0.17 | 1 | 7 | 3 | 5 | 3 |
| 0.16 | 1 | 2 | 3 | 7 | 3 |

Las ocho comparten rol 1 y cierre 3, y siete de ocho comparten formato 3
(la excepción es formato 6, con estilo 7).

### Nota sobre `historial_arranque_1.csv` y su versión limpia

El original **no se modifica**. Tiene tres ejecuciones anexadas por
reanudaciones de la sesión (tres filas con paso 1, en las líneas 2, 26 y 55
del archivo). Las dos primeras son prefijos de la tercera. La tercera tiene
44 filas y está en `historial_arranque_1_limpio.csv`. La columna `arranque`
vale 0 en el archivo porque es el índice interno de la ejecución, no el número
de arranque.

Comprobado con `resumir.py`: con el original y con el limpio salen los mismos
conteos (28 configuraciones del arranque 1, 117 en la unión, 11 700 generaciones).
Lo único que cambia es "3 ejecuciones" frente a "1 ejecución" en el CSV.

## 2. Cómo se cuenta B (D11)

B cuenta generaciones nuevas por (configuración, instancia, semilla). Como el
caché no cobra lo ya generado, el gasto real es el de la **unión**:

| Conteo | Configuraciones | Generaciones |
|---|---|---|
| Arranque 0 | 92 | 9 200 |
| Arranque 1 | 28 | 2 800 |
| Suma por sesión | 120 | 12 000 |
| **Unión (cuenta para B)** | **117** | **11 700** |

La diferencia es 3 configuraciones (300 generaciones) que ambos arranques
evaluaron. Con B = 14 400 (D17) quedan 2 700 generaciones, con el 81.2 % usado.
Eso no alcanza para un tercer arranque con una pasada completa (hasta 3 500
generaciones, 35 opciones vecinas por 100 instancias), por lo que no se lanza y
queda como límite.

Que la unión sea el gasto real supone que el caché compartido evitó repetir
esas 3 configuraciones. Es una **inferencia**: el CSV no registra aciertos de
caché; solo se comprueba que las precisiones coinciden entre arranques
(`resumir.py` avisa si no coinciden; no avisó).

## 3. Interacción estrategia por estilo

Con rol 1, formato 3 y cierre 3 (valores del historial):

| Estrategia | Estilo 3 | Estilo 5 |
|---|---|---|
| 1 | 20 % | 17 % |
| 7 | 11 % | 17 % |

El mejor estilo depende de la estrategia: con estrategia 1 gana el estilo 3
y con estrategia 7 gana el 5. Por eso la búsqueda por coordenadas, que cambia
una ranura a la vez, puede quedar en un óptimo local según el punto de partida;
esto es lo que ilustran los dos arranques. Con una sola celda por combinación
(100 instancias, ruido de unos 4 puntos) la diferencia 20 frente a 17 de la
estrategia 1 **no es concluyente por sí sola**; la de 11 frente a 17 de la
estrategia 7 es mayor que ese ruido, pero tampoco se ha repetido.

## 4. Fallos de las dos mejores encontradas

Fuente: `fallos_ganadora.txt` (arranque 0) y `fallos_arranque_1.txt`
(arranque 1). Cada uno lista las familias que fallan y 3 ejemplos de salida.

**Familias que fallan siempre** (N fallos de N apariciones): 27 familias en
cada mejor encontrada, 23 comunes. Entre las comunes: `copy:copy` (6 de 6),
`new:copy_span_idx` (5 de 5), `change_case:capital_word_frequency` (4 de 4),
`letters:letter_counting2`, `keywords:keyword_specific_position`,
`first_word:first_word_sent`, `keywords:start_end` (3 de 3),
`copy:copying_multiple`, `copy:repeat_phrase`, `keywords:word_once`,
`language:response_language`, `detectable_format:sentence_hyphens`,
`detectable_format:title` y `length_constraints:number_paragraphs` (2 de 2).
Solo en el arranque 0: `detectable_format:number_bullet_lists`,
`detectable_format:number_highlighted_sections`, `keywords:frequency` y
`punctuation:no_comma`. Solo en el arranque 1: `first_word:first_word_answer`,
`last_word:last_word_sent` y `startend:end_checker`.
(`punctuation:punctuation_dot` figura como 1 de 1 solo en la tabla del arranque 1,
pero un ejemplo de `fallos_ganadora.txt`, del arranque 0, también la viola; ver la
sección 6.)

**Primera restricción violada (`violo`), top de cada mejor encontrada:**

| Arranque 0 | | Arranque 1 | |
|---|---|---|---|
| `last_word:last_word_sent` | 8 | `last_word:last_word_sent` | 8 |
| `copy:copy` | 6 | `copy:copy` | 6 |
| `new:copy_span_idx` | 5 | `new:copy_span_idx` | 5 |
| `keywords:keyword_specific_position`, `first_word:first_word_sent`, `detectable_format:sentence_hyphens`, `copy:repeat_phrase` | 4 cada una | `keywords:word_once`, `detectable_format:square_brackets`, `keywords:keyword_specific_position`, `first_word:first_word_sent`, `change_case:capital_word_frequency`, `keywords:start_end`, `change_case:english_capital` | 4 cada una |

Los tres primeros puestos coinciden y las dos listas se parecen mucho: las
dos mejores encontradas fallan casi en las mismas familias.

**Frase inicial.** Los fallos de las dos mejores encontradas difieren en la frase
"Before each part of the answer, write a paragraph of at least two sentences
analysing that part."

- **Origen (comprobado con `CATALOGO`):** el texto de la opción `estrategia 7`
  contiene esa frase literalmente. Ninguna de las cinco opciones de la mejor
  encontrada del arranque 0 la contiene.
- **Frecuencia medida** (celda de verificación del notebook, evaluando desde el
  caché; cuenta si la frase está en los primeros 300 caracteres de la salida):

  | Arranque | Fallos | Con la frase en los primeros 300 caracteres |
  |---|---|---|
  | 0 | 80 de 100 | 0 de 80 |
  | 1 | 83 de 100 | 32 de 83 (38.6 %) |

- **Los ejemplos de los `.txt` no son representativos:** en los 3 ejemplos del
  arranque 1 la frase aparece, pero entre los 83 fallos solo en el 38.6 %. Solo
  en 1 de esos 3 ejemplos abre el texto; en otro va tras el título
  `<<The Art of Being>>` y en el tercero tras unas comillas iniciales.
- **Lo que no se puede concluir:** que la frase cause los fallos. La celda solo
  ve las trazas de los fallos, así que no sabemos cuántas de las 17 salidas
  acertadas la contienen; si también aparece en ellas, no explicaría el fallo.
  El criterio de 300 caracteres es laxo (una frase en el carácter 280 cuenta
  igual). Que el modelo copie la instrucción en vez de cumplirla es una
  **hipótesis**.
- **Sin base para `estilo 5` y `punctuation_dot`:** el texto de `estilo 5` pide
  "never end a line with a period", pero el arranque 0 (que usa `estilo 3`)
  también tiene un ejemplo que viola `punctuation:punctuation_dot`. No se sabe
  qué verifica esa familia; no se afirma ninguna relación (sección 6).

Textos de las opciones de las dos mejores encontradas, leídos de `CATALOGO` con
`texto_opcion`. Los 40 textos completos están en `catalogo_opciones.txt`:

| Ranura | Opción | Texto |
|---|---|---|
| rol | 1 | "You are an engaging assistant. Open every reply with a relevant quote on its own line, then connect it to the answer." |
| estrategia | 1 | "Write out at least three candidate answers in full, then say which one you picked and why." |
| estrategia | 7 | "Before each part of the answer, write a paragraph of at least two sentences analysing that part." |
| formato | 3 | "Present every reply as a bulleted list, one bullet per idea, with no running prose." |
| estilo | 3 | "Use commas freely, and put an aside in parentheses in every sentence." |
| estilo | 5 | "Join every pair of related sentences with a semicolon instead of a full stop, and never end a line with a period." |
| cierre | 3 | "These are the requirements your response must satisfy:\n{restricciones}" |

## 5. Limitaciones

- **El arranque 0 paró por convergencia en la pasada 3.** Con 2 pasadas aún
  mejoraba (estrategia 1 en el paso 47, de 0.15 a 0.19, y estilo 3 en el paso
  64, a 0.20). La pasada 3 (pasos 76 a 110) evaluó las 35 opciones vecinas y
  no aceptó ninguna; la más cercana fue `estilo 7` con 0.19. Es un óptimo
  local por ranura, no un óptimo global: no se prueba ningún cambio de dos
  ranuras a la vez.
- **El arranque 1 no es independiente**: excluyó de antemano 7 opciones de
  `cierre` (todas menos la 3) y otras de `rol`, `formato` y `estrategia`
  (campo `decide` del CSV). Parte de la información del arranque 0 influyó
  en él; su coincidencia con el arranque 0 en rol 1, formato 3 y cierre 3
  no es evidencia independiente.
- **Ruido de unos 4 puntos por medición con 100 instancias.** Es una
  estimación de la desviación de una proporción cercana a 0.15 con n = 100
  (raíz de 0.15·0.85/100 ≈ 0.036), no medida entre semillas. Diferencias de
  1 a 3 puntos no distinguen configuraciones.
- **Mecanismos del campo `decide` (arranque 1)**, contrastados con `CATALOGO`:
  que `rol 0, 3, 4, 7` fijan una primera línea literal y que `cierre 3` es la única
  opción de `cierre` que no agrega texto tras la respuesta **están comprobados con
  el texto** (sección 6.2). Que esas primeras líneas **choquen con `first_word`**
  sigue siendo una hipótesis: no se conoce la regla de esa familia. Los motivos
  "nunca pasaron de 10 %" se contrastaron con el historial (sección 6.2).
- Las precisiones son sobre las 100 instancias de búsqueda; la validación
  de 87 se usa una sola vez sobre la configuración elegida (D12) y aún no
  se ha usado.
- La pasada de cada fila no está en el CSV: `resumir.py` la infiere
  (empieza una nueva al volver a una ranura ya visitada). En el arranque 1,
  las precisiones de la pasada 2 repiten las de la pasada 1 en `estilo` y
  `estrategia`, lo que **sugiere** lecturas de caché; no está registrado.
- Solo dos arranques; el subcatálogo (D8) no entra en esta entrega (D17).

## 6. Fallos, opciones y decisiones de la búsqueda (D6)

Esta sección enlaza las familias que fallan con las opciones del catálogo y con lo
que hizo la búsqueda. Cada fila dice qué está **comprobado** (cifras de los `.txt`,
de `historial_arranque_*.csv` y textos leídos de `CATALOGO`) y qué es **hipótesis**.
No hay datos por familia de las otras 115 configuraciones evaluadas, solo de las
dos mejores encontradas; por eso ninguna fila demuestra que una opción cause un fallo.

### 6.1 Familias citadas

Arranque 0: `estrategia 1`, `estilo 3`. Arranque 1: `estrategia 7`, `estilo 5`.
Comparten `rol 1`, `formato 3` y `cierre 3`. Los números salen de las tablas de
familias de `fallos_ganadora.txt` y `fallos_arranque_1.txt`.

| Familia | Arranque 0 | Arranque 1 | Opción del catálogo relacionada | Qué hizo la búsqueda | Estado |
|---|---|---|---|---|---|
| `copy:copy`, `new:copy_span_idx` | 6 de 6; 5 de 5 | 6 de 6; 5 de 5 | Ninguna de las 40 opciones pide copiar el texto del enunciado; la más cercana, `estrategia 5` ("Write out everything the request asks for, item by item…"), no está en ninguna de las dos mejores. Falla igual con `estrategia 1` y `7` y con `estilo 3` y `5`, así que no depende de esas cuatro opciones; solo queda lo compartido (`rol 1`, `formato 3`, `cierre 3`) o el modelo. | Nada: no hay dato por familia de otras configuraciones. | Deducción; no comprobado |
| `first_word:first_word_sent` | 3 de 3 | 3 de 3 | `rol 0`, `3`, `4` y `7` prescriben una primera línea literal ("Happy to help!", "Answer:", "Topic:", "Sure thing!"). `rol 1` pide "a relevant quote on its own line" (contenido libre), como `rol 2` (reformula la pregunta) y `rol 6` (una frase sobre el alcance). | El arranque 1 excluyó `rol 0, 3, 4, 7` y conservó `rol 1`. | Que las cuatro excluidas prescriben una primera línea literal está comprobado con el texto; que choquen con `first_word` no, porque no se conoce la regla de la familia |
| `punctuation:no_comma` | 3 de 3 | 2 de 3 | `estilo 3`: "Use commas freely, and put an aside in parentheses in every sentence." | La búsqueda no descartó `estilo 3`: con `estrategia 1` da 20 % frente a 17 % con `estilo 5`, diferencia dentro del ruido de unos 4 puntos. | Consistente con el texto; con 3 casos por lado es solo hipótesis |
| `length_constraints:number_paragraphs`; `paragraphs:paragraphs` | 2 de 2; 4 de 5 | 2 de 2; 3 de 5 | `formato 3` (compartido): "Present every reply as a bulleted list, one bullet per idea, with no running prose." En el arranque 1, `estrategia 7` pide "a paragraph of at least two sentences" y `formato 3` pide no escribir prosa corrida: instrucciones opuestas en la misma configuración. | `formato 3` se conservó en los dos arranques. En la pasada 3 del arranque 0, ninguna otra opción de `formato` superó 16 % (`formato 7`) frente a 20 %. | Hipótesis (viñetas frente a párrafos); no comprobado |
| `last_word:last_word_sent` | 3 de 4 | 4 de 4 | Ninguna opción lo nombra. `estrategia 1` (arranque 0) pide tres respuestas candidatas y decir cuál eligió, y `estrategia 7` (arranque 1) pide un párrafo de análisis por parte; las dos añaden texto alrededor de la respuesta. Es la primera restricción violada más frecuente en las dos (8 casos). | Nada. | Hipótesis; no comprobado |
| Frase "Before each part of the answer…" (no es una familia) | 0 de 80 fallos | 32 de 83 | `estrategia 7` contiene la frase literalmente (comprobado con `CATALOGO`). | El arranque 0 descartó `estrategia 7` (11 % en su contexto final); el arranque 1 la eligió junto con `estilo 5` (17 %). | Origen comprobado; que cause fallos, no |
| `punctuation:punctuation_dot` | no figura en su tabla | 1 de 1 | `estilo 5` pide no terminar líneas con punto, pero el arranque 0 (`estilo 3`) también tiene un ejemplo que la viola. | Nada. | Inconsistencia sin resolver entre la tabla y los ejemplos de `fallos_ganadora.txt`; no se afirma nada |

Con 3 a 5 casos por familia, las diferencias entre arranques (por ejemplo 3 de 4
frente a 4 de 4) no se distinguen del ruido de la medición.

### 6.2 Qué cambió en la búsqueda a partir de las trazas

El arranque 1 se lanzó con las trazas del arranque 0 y recortó el espacio:

| Ranura | Opciones excluidas | Motivo escrito en `decide` | Su precisión en el contexto final del arranque 0 (pasada 3) |
|---|---|---|---|
| `rol` | 0, 3, 4, 7 | "fijan la primera línea y chocan con first_word" | 0.06, 0.08, 0.08, 0.09 |
| `formato` | 1, 4, 5 | "nunca pasaron de 10 %" | 0.10, 0.07, 0.07 |
| `estrategia` | 3 | "nunca pasó de 10 %" | 0.15 |
| `cierre` | todas menos la 3 | "la 3 es la única que no agrega texto al final" | de 0.06 a 0.13 |

Con estas exclusiones, el arranque 1 buscó en 4 · 5 · 7 · 8 · 1 = 1 120 de las
32 768 configuraciones (3.4 %). El contexto final del arranque 0 es `rol 1`,
`estrategia 1`, `formato 3`, `estilo 3`, `cierre 3` (0.20).

- **Las exclusiones no habrían cambiado la mejor del arranque 0:** en ese contexto,
  ninguna opción excluida superó 0.15, frente a 0.20. Eso solo vale en ese contexto;
  con otras combinaciones no se midió.
- **Qué confirma el catálogo de los motivos del arranque 1:**
  - `rol 0`, `3`, `4` y `7` fijan una primera línea literal ("Happy to help!",
    "Answer:", "Topic:", "Sure thing!"). Eso es cierto; el choque con `first_word`
    no está comprobado.
  - Las otras siete opciones de `cierre` agregan texto tras la respuesta: línea fija
    (0), resumen (1), lista de requisitos (2), P.S. (4), pregunta (5), "In short:" (6)
    y "Next:" (7). Solo `cierre 3` no lo hace.
  - `cierre 3` es además la única opción que contiene el marcador `{restricciones}`.
    **Hipótesis:** las demás opciones de `cierre` no presentan los requisitos en el
    prompt, lo que explicaría por qué `cierre 3` supera a todas (0.20 frente a 0.13
    como máximo). No se comprobó cómo se arma el prompt completo.
- **Las opciones "obedientes" no ganaron:** `rol 5` ("Follow every formatting
  requirement exactly…") llegó a 0.12 y `estilo 6` ("Respect exact word counts,
  casing and punctuation rules…") a 0.15, ambas por debajo de la mejor encontrada.
- **Una premisa no se sostuvo:** `estrategia 3` "nunca pasó de 10 %" era cierto con
  las pasadas 1 y 2 del arranque 0 (0.06 y 0.10), pero en la pasada 3 llegó a 0.15.
  No cambia la ganadora, y esa pasada es posterior al lanzamiento del arranque 1.
- **Interacción:** el arranque 0 descartó `estrategia 7` (0.11 con `estilo 3`) y el
  arranque 1 la eligió (0.17 con `estilo 5`). Es la misma interacción de la sección 3.

### 6.3 Qué falta para comprobar el resto

No hace falta volver a correr la búsqueda ni gastar generaciones.

1. **Hecho:** los 40 textos de `CATALOGO` están en `catalogo_opciones.txt`, impresos
   desde Colab con `texto_opcion` (AGENTS.md permite consultarlo así; no se abre
   `oraculo.py`).
2. Opcional, desde el caché: comparar las familias que fallan en configuraciones ya
   evaluadas que cambian una sola opción. Solo es gratis si esas configuraciones
   están en el caché de Drive de esa sesión.
3. Aclarar qué cuenta la tabla de familias de `fallos_*.txt` (falta
   `punctuation_dot` en la del arranque 0, aunque un ejemplo la viola).
