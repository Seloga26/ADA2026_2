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
`last_word:last_word_sent`, `punctuation:punctuation_dot` y
`startend:end_checker`.

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
- **Coincidencia sin comprobar:** el texto de `estilo 5` pide "never end a line
  with a period", y uno de los 3 ejemplos del arranque 1 viola
  `punctuation:punctuation_dot`. No se sabe qué verifica esa familia.

Textos de las opciones, leídos de `CATALOGO` (la celda los recorta a 90
caracteres; `estrategia 7` y `estilo 5` se leyeron completos con `texto_opcion`):

| Ranura | Opción | Texto |
|---|---|---|
| rol | 1 | "You are an engaging assistant. Open every reply with a relevant quote on its own line, the…" |
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
- **Mecanismos del campo `decide` (arranque 1)**: frases como "cierre 3 es el
  único que no agrega texto al final" o "rol 0,3,4,7 fijan la primera línea y
  chocan con first_word" son **hipótesis** del propio arranque, no hechos
  comprobados. Solo valen si se contrastan con el texto de `CATALOGO`. Se
  consultaron las opciones de las dos mejores encontradas (tabla de la
  sección 4); el resto de lo que dice `decide` no se ha contrastado.
- Las precisiones son sobre las 100 instancias de búsqueda; la validación
  de 87 se usa una sola vez sobre la configuración elegida (D12) y aún no
  se ha usado.
- La pasada de cada fila no está en el CSV: `resumir.py` la infiere
  (empieza una nueva al volver a una ranura ya visitada). En el arranque 1,
  las precisiones de la pasada 2 repiten las de la pasada 1 en `estilo` y
  `estrategia`, lo que **sugiere** lecturas de caché; no está registrado.
- Solo dos arranques; el subcatálogo (D8) no entra en esta entrega (D17).
