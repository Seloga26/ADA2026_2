# Análisis de la búsqueda real (arranques 0 y 1)

> Este análisis describe la **versión de 2 pasadas del arranque 0**
> (`historial_arranque_0_2pasadas.csv`). Se actualizará cuando exista la pasada
> de verificación. Las cifras salen de `resumir.py`; lo no comprobado va marcado
> como **inferencia**.

Reproducción:

```
python resumir.py historial_arranque_0_2pasadas.csv historial_arranque_1_limpio.csv \
    --presupuesto 14400 --esperado-cfg-0 71 --esperado-cfg-1 28 \
    --esperado-union 97 --esperado-generaciones 9700
```

Modelo `qwen17b`, temperatura 0.0, semilla 1, 100 instancias de búsqueda por
configuración (D2). Las 100 instancias por configuración se infieren en
`resumir.py` como consultas finales / configuraciones distintas (7 100 / 71).

## 1. Los dos arranques

| | Arranque 0 | Arranque 1 |
|---|---|---|
| Configuración final | rol 1, estrategia 1, formato 3, estilo 3, cierre 3 | rol 1, estrategia 7, formato 3, estilo 5, cierre 3 |
| Precisión (100 instancias de búsqueda) | 0.20 | 0.17 |
| Configuraciones distintas | 71 | 28 |
| Generaciones (distintas × 100) | 7 100 | 2 800 |
| Fallos de la ganadora | 80 de 100 | 83 de 100 |
| Fuente | `historial_arranque_0_2pasadas.csv` | `historial_arranque_1_limpio.csv` |

Las ocho mejores de la unión (precisión sobre búsqueda, no sobre validación):

| Precisión | rol | estrategia | formato | estilo | cierre |
|---|---|---|---|---|---|
| 0.20 | 1 | 1 | 3 | 3 | 3 |
| 0.19 | 1 | 1 | 3 | 7 | 3 |
| 0.19 | 1 | 1 | 6 | 7 | 3 |
| 0.17 | 1 | 1 | 3 | 0 | 3 |
| 0.17 | 1 | 1 | 3 | 5 | 3 |
| 0.17 | 1 | 7 | 3 | 5 | 3 |
| 0.16 | 1 | 2 | 3 | 7 | 3 |
| 0.15 | 1 | 4 | 3 | 7 | 3 |

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
conteos (28 configuraciones del arranque 1, 97 en la unión, 9 700 generaciones).
Lo único que cambia es "3 ejecuciones" frente a "1 ejecución" en el CSV.

## 2. Cómo se cuenta B (D11)

B cuenta generaciones nuevas por (configuración, instancia, semilla). Como el
caché no cobra lo ya generado, el gasto real es el de la **unión**:

| Conteo | Configuraciones | Generaciones |
|---|---|---|
| Arranque 0 | 71 | 7 100 |
| Arranque 1 | 28 | 2 800 |
| Suma por sesión | 99 | 9 900 |
| **Unión (cuenta para B)** | **97** | **9 700** |

La diferencia es 2 configuraciones (200 generaciones) que ambos arranques
evaluaron. Con B = 14 400 (D17) quedan 4 700 generaciones, el 67.4 % usado.

Que la unión sea el gasto real supone que el caché compartido evitó repetir
esas 2 configuraciones. Es una **inferencia**: el CSV no registra aciertos de
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

## 4. Fallos de las dos ganadoras

Fuente: `fallos_ganadora.txt` (arranque 0) y `fallos_arranque_1.txt`
(arranque 1). Cada uno lista las familias que fallan y 3 ejemplos de salida.

**Familias que fallan siempre** (N fallos de N apariciones): 27 familias en
cada ganadora, 23 comunes. Entre las comunes: `copy:copy` (6 de 6),
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

**Primera restricción violada (`violo`), top de cada ganadora:**

| Arranque 0 | | Arranque 1 | |
|---|---|---|---|
| `last_word:last_word_sent` | 8 | `last_word:last_word_sent` | 8 |
| `copy:copy` | 6 | `copy:copy` | 6 |
| `new:copy_span_idx` | 5 | `new:copy_span_idx` | 5 |
| `keywords:keyword_specific_position`, `first_word:first_word_sent`, `detectable_format:sentence_hyphens`, `copy:repeat_phrase` | 4 cada una | `keywords:word_once`, `detectable_format:square_brackets`, `keywords:keyword_specific_position`, `first_word:first_word_sent`, `change_case:capital_word_frequency`, `keywords:start_end`, `change_case:english_capital` | 4 cada una |

Los tres primeros puestos coinciden y las dos listas se parecen mucho: las
dos ganadoras fallan casi en las mismas familias.

**Frase inicial (inferencia, no prueba).** En los 3 ejemplos de salida fallida
del arranque 1 aparece la frase "Before each part of the answer, write a
paragraph of at least two sentences analysing that part."; en los 3 del
arranque 0 no aparece. Precisión sobre lo observado: la frase abre el texto
solo en 1 de los 3 ejemplos (el segundo); en el primero va tras el título
`<<The Art of Being>>` y en el tercero va dentro de unas comillas iniciales.
Con tres ejemplos por lado, sin muestreo aleatorio (son los primeros
fallos del listado), esto es una observación que sugiere que la estrategia 7
puede estar produciendo esa frase. No demuestra qué la causa ni qué
frecuencia tiene.

## 5. Limitaciones

- **El arranque 0 paró por el tope de pasadas**, no por convergencia: en la
  pasada 2 todavía aceptó dos cambios (estrategia 1 en el paso 47, de 0.15 a
  0.19, y estilo 3 en el paso 64, a 0.20). Como la pasada 2 aún mejoró, no
  se ha comprobado que 0.20 sea un óptimo local; falta la pasada de
  verificación (una pasada 3 sin mejoras lo confirmaría).
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
  comprobados. Solo valen si se contrastan con el texto de `CATALOGO`, que
  aquí no se consultó.
- Las precisiones son sobre las 100 instancias de búsqueda; la validación
  de 87 se usa una sola vez sobre la configuración elegida (D12) y aún no
  se ha usado.
- La pasada de cada fila no está en el CSV: `resumir.py` la infiere
  (empieza una nueva al volver a una ranura ya visitada). En el arranque 1,
  las precisiones de la pasada 2 repiten las de la pasada 1 en `estilo` y
  `estrategia`, lo que **sugiere** lecturas de caché; no está registrado.
- Solo dos arranques; el subcatálogo (D8) no entra en esta entrega (D17).
