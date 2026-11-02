# Manual técnico: Proyecto Oráculo

> Lo marcado *inferencia* no está comprobado. Lo marcado `PENDIENTE` es una verificación
> que falta. La configuración que se reporta es la **mejor encontrada**; no se afirma que
> sea óptima.

Materia: Análisis y Diseño de Algoritmos, 2026-2. Grupo `ADAG1`. Integrantes: Sebastián
López y Dylber Cabrera. Las decisiones citadas (D1 a D17, y la propuesta D18) están en
`AGENTS.md`, sección 5. El análisis teórico (formalización, reducción, costo y cotas) está
en el informe, `informe/main.tex`.

## 1. Qué hace el proyecto

Dado un modelo de lenguaje y un catálogo de opciones de prompt, busca la configuración
que maximiza la precisión gastando pocas generaciones. Una configuración elige una
opción en cada una de 5 ranuras (`rol`, `estrategia`, `formato`, `estilo`, `cierre`),
con 8 opciones por ranura y una temperatura. Hay 32 768 configuraciones con temperatura
fija (98 304 con las 3 temperaturas). La precisión es la fracción de instancias cuyas
restricciones se cumplen todas (puntaje todo-o-nada).

Salida del proyecto: una configuración y el historial de cómo se halló. El archivo
`entrega.json` guarda esa configuración para el notebook de evaluación.

## 2. Entorno

| Pieza | Detalle |
|---|---|
| Local | Python 3.12 con `uv`, `pytest` y `matplotlib`. Sin GPU. |
| Colab | GPU T4, modelo `qwen17b`. |
| Restricción | `oraculo.py` importa `torch` y verificadores de `/content/open-instruct`; **no corre en local**. |
| Local | Solo se usa el oráculo sintético y las pruebas. |

Instalación y pruebas locales:

```
uv sync
uv run pytest
```

Ejemplo pequeño con oráculo sintético:

```
uv run python -m busqueda_prompt.ejemplo
```

Resultado esperado (el mismo que está en `README.md`, comprobado el 2026-11-02):

```
ganadora: {'r0': 1, 'r1': 1, 'r2': 0, 'temperatura': 0.0}
precision: 0.80
consultas: 160
```

Datos del repositorio base (`datos_visibles.json`): 100 instancias de búsqueda, 87 de
validación y 263 descartadas. Parámetros fijados: temperatura 0.0, semilla 1 (D2).

## 3. Arquitectura

```
busqueda_prompt/
  contratos.py        tipos y constantes comunes
  contado.py          OraculoContado: cuenta generaciones y aplica B
  sintetico.py        OraculoSintetico: oráculo sin modelo, para pruebas
  entrega.py          lectura y validación de entrega.json y de datos
  ejemplo.py          ejemplo pequeño
  algoritmos/
    fuerza_bruta.py   referencia exacta para espacios pequeños
    coordenadas.py    búsqueda por coordenadas (aproximado)
notebooks/            medicion_velocidad, busqueda, evaluacion
resultados/           busqueda/ (historiales y análisis), validacion/, velocidad.json
tests/                pruebas automáticas
informe/              fuente LaTeX del informe
```

Los módulos propios no importan `oraculo.py`; los notebooks de Colab sí lo usan.

### 3.1 Contratos (`contratos.py`)

- `RANURAS`, `OPCIONES_POR_RANURA = 8`, `TEMPERATURAS = (0.0, 0.3, 0.7)`.
- `Config` es un diccionario con una opción por ranura más `temperatura`.
- `Oraculo.evaluar(config, instancias, semilla) -> Resultado`, con `precision`, `trazas` y `n`.
- `ResultadoBusqueda`: `ganadora`, `precision`, `consultas` y `asignacion` (consultas por config).
- `clave_config`: texto estable de una config, independiente del orden de las llaves.
- `PresupuestoAgotado`: se lanza cuando un lote superaría B.

### 3.2 `OraculoContado` (`contado.py`)

Envuelve cualquier oráculo sin tocar su interior. Una generación es **nueva** si la
tupla (config, instancia, semilla) no se había pedido; solo esas se cobran, igual que el
caché del oráculo real. Si el lote completo no cabe en el presupuesto restante, lanza
`PresupuestoAgotado` antes de consultar. Con `presupuesto=None` cuenta sin limitar.

El parámetro `presupuesto=` del oráculo real es un tope de memoria de GPU y **no es B**.
B se aplica aquí (D11).

### 3.3 `OraculoSintetico` (`sintetico.py`)

Una instancia se cumple si la config cubre todas sus reglas. Admite conflictos entre
opciones y ruido determinista por (semilla, config, instancia). Sirve para pruebas y
barridos de tiempo en local (D7). Los resultados de precisión salen del modelo real.

### 3.4 Fuerza bruta (`algoritmos/fuerza_bruta.py`)

Evalúa todas las configuraciones recibidas y devuelve la primera de mayor precisión.
Peor caso O(|C|·n) generaciones. Con el modelo real no se ejecuta completa (3 276 800
generaciones, D7).

### 3.5 Búsqueda por coordenadas (`algoritmos/coordenadas.py`)

Cada arranque parte de una config al azar (generador con semilla `semilla_busqueda|a`,
reproducible; las opciones excluidas nunca salen como punto de partida). En una pasada
recorre las ranuras en `orden_ranuras`; en cada una prueba las demás opciones permitidas
con el resto fijo, y cambia solo si la precisión **sube estrictamente**. Por eso la
precisión de un arranque no baja. Termina cuando una pasada no mejora nada (óptimo local
por ranura), al llegar a `max_pasadas` o al agotarse B; en este último caso devuelve lo
mejor visto.

Parámetros principales de `resolver`:

| Parámetro | Efecto |
|---|---|
| `arranques` | Número de puntos de partida distintos. |
| `max_pasadas` | Tope de pasadas por arranque. |
| `presupuesto` | B; compartido por todos los arranques. Si se agota, devuelve lo mejor visto. |
| `orden_ranuras` | Orden de las ranuras en cada pasada. |
| `opciones_excluidas` | `{ranura: opciones}` que no se prueban ni se usan al partir. |
| `motivo` | Texto de esa decisión; queda en la columna `decision` del historial. |
| `ruta_historial` | CSV donde se agrega cada paso. |

Dos detalles de la implementación: la comparación `opción != actual` usa la opción
*actual en ese momento*, así que tras aceptar un cambio la opción anterior se vuelve a
probar más adelante en la misma ranura (sale del caché, sin generaciones nuevas); y el
punto de partida depende de las opciones permitidas, por lo que quitar exclusiones **cambia
el recorrido**, no lo completa.

Costo (informe, sección 4, teorema de costo): una pasada hace como máximo
Σ|O_i| evaluaciones, es decir 40 con 5 ranuras de 8 opciones, y cada evaluación cuesta
n = 100 generaciones. Cota por pasada: 4 000 generaciones, y por arranque con 3 pasadas,
100·(1 + 3·40) = 12 100. En general T = O(p·L·k_max·n), con p pasadas realizadas
(p ≤ min(P, n + 1)). El caché solo puede bajar esas cifras. Lo observado fue menor: 9 200
generaciones en el arranque 0 y 2 800 en el 1.

Garantías demostradas en el informe: la precisión no baja, hay a lo sumo n cambios y, si
para por convergencia, la config es un óptimo local por ranura (si el oráculo es
determinista). **No hay razón de aproximación**: un contraejemplo construido lo
muestra, y el riesgo de óptimos locales se mide con varios arranques.

El conteo de B usa un único `OraculoContado` para todos los arranques: una
(config, instancia, semilla) repetida entre arranques **no se cobra dos veces**.

## 4. Historial de la búsqueda (CSV)

Cada paso se agrega al CSV abriéndolo y cerrándolo en cada fila, de modo que Drive lo
sincroniza y, si Colab se corta, el historial ya quedó guardado. Columnas, en orden:
`paso`, `arranque`, `ranura`, `opcion`, `config`, `precision`, `mejor_precision`,
`consultas`, `decision`. La decisión es `inicio`, `acepta` o `descarta`; una fila inicial
`decide: ...` documenta las exclusiones del arranque cuando las hay.

Particularidades comprobadas en los archivos reales (`resultados/busqueda/`):

- Una reanudación **agrega otra ejecución** al mismo CSV; cada ejecución empieza con una
  fila de paso 1. `historial_arranque_1.csv` trae tres ejecuciones; las dos primeras son
  prefijos de la tercera.
- La columna `arranque` es el índice interno de la ejecución, no el número de arranque.
- La pasada no es una columna: `resumir.py` la infiere.

Para una ejecución limpia se toma la última (ver `historial_arranque_1_limpio.csv`). El
original no se modifica.

## 5. Uso

### 5.1 Notebooks en Colab

Elegir GPU T4 y ejecutar las celdas en orden. La primera vez el entorno se instala y se
reinicia; después se ejecutan otra vez.

| Notebook | Uso |
|---|---|
| `notebooks/medicion_velocidad.ipynb` | Mide cuánto tarda una generación del modelo real. |
| `notebooks/busqueda.ipynb` | Búsqueda real por coordenadas, con registro, análisis de fallos y validación. |
| `notebooks/evaluacion.ipynb` | Evalúa la config de `entrega.json` sobre datos de prueba. |

Secciones de `notebooks/busqueda.ipynb` (los códigos se citan desde el informe):

| Sección | Contenido |
|---|---|
| B1 | Parámetros y selector único de arranque (`ARRANQUE` = 0 o 1). |
| B2 | Prueba corta del caché (10 generaciones); hacerla antes de lanzar la búsqueda. |
| B3 | Limpieza del historial del arranque 0, solo si hace falta. |
| B4 | Búsqueda por coordenadas y su condición de parada. |
| B5 | Análisis de fallos y decisiones derivadas de las trazas (D6). |
| B6 | Registro de la búsqueda real, leído del repositorio (sin GPU). |
| B7 | Validación final con `oraculo.validar` (D12). |

El notebook de búsqueda clona la rama indicada en `RAMA` (por defecto `main`) y en cada
ejecución de esa celda hace `fetch`, `checkout` y `pull`. **Si se reanuda una corrida,
antes hay que comprobar que la rama no cambió**: de lo contrario la reanudación usaría
código distinto con la misma caché y la corrida deja de ser reproducible.

El caché del oráculo y el historial se guardan en Drive (`CARPETA` en B1) para poder
reanudar. Para reanudar un arranque, se borra su CSV y se vuelve a ejecutar B4: los pasos
se repiten desde el caché sin costo de GPU.

**B7 no se ejecuta otra vez.** La celda trae `CONFIRMO_VALIDAR = False` y con "Ejecutar
todo" no hace nada; D12 permite una sola validación.

### 5.2 Búsqueda real (D17)

`B = 14 400` generaciones, con dos arranques. Medido en T4: 1,99 s por generación y unas
4 h por arranque (de una sola configuración; otras pueden tardar más). El subcatálogo (D8)
no entra en esta entrega.

D17 decía hasta 2 pasadas por arranque; el notebook usa `MAX_PASADAS = 3` (**propuesta
D18, pendiente de aprobación del equipo**), porque el arranque 0 usó una tercera como
verificación y quedó dentro de B.

Para reproducir cada arranque: en B1 poner `ARRANQUE = 0` o `1` y ejecutar B4. El
arranque 0 usa el orden natural y no excluye nada; el arranque 1 aplica el orden y las
exclusiones decididas con las trazas del arranque 0 (informe, sección 6).

### 5.3 Resumir los historiales

```
python resultados/busqueda/resumir.py \
    resultados/busqueda/historial_arranque_0.csv \
    resultados/busqueda/historial_arranque_1_limpio.csv \
    --presupuesto 14400 --esperado-cfg-0 92 --esperado-cfg-1 28 \
    --esperado-union 117 --esperado-generaciones 11700
```

Solo biblioteca estándar. Imprime configuraciones distintas por arranque y en la unión,
generaciones distintas de la unión frente a B, las 8 mejores y la precisión por opción,
ranura y pasada. Si se pasa un valor esperado y no coincide, termina con código 1.

### 5.4 `entrega.json`

Campos obligatorios: `grupo` (texto no vacío), `semana` (entero positivo) y `config`
(las 5 ranuras con enteros de 0 a 7 y una `temperatura` de `TEMPERATURAS`).
`busqueda_prompt.entrega.validar_entrega` lanza `ValueError` si algo no cumple.
La misma configuración debe aparecer en `entrega.json` y en los dos notebooks (D16).

Contenido actual:

```json
{"grupo": "ADAG1", "semana": 6,
 "config": {"rol": 1, "estrategia": 1, "formato": 3, "estilo": 3, "cierre": 3, "temperatura": 0.0}}
```

El grupo `ADAG1` lo confirmó Dylber el 2026-11-02. La semana `6` es **provisional**:
`PENDIENTE` de confirmar (la guía no dice qué semana corresponde a esta entrega).

## 6. Resultados de la búsqueda

Fuente y análisis: `resultados/busqueda/analisis_busqueda.md` y informe, sección 6.

| | Arranque 0 | Arranque 1 |
|---|---|---|
| Mejor encontrada (rol, estrategia, formato, estilo, cierre) | 1, 1, 3, 3, 3 | 1, 7, 3, 5, 3 |
| Precisión sobre 100 instancias de búsqueda | 0.20 | 0.17 |
| Configuraciones distintas | 92 | 28 |
| Generaciones (distintas × 100) | 9 200 | 2 800 |
| Pasadas | 3 (la tercera sin cambios) | 2 (la segunda sin cambios) |
| Parada | convergencia | convergencia |

Unión de los dos arranques: 117 configuraciones, 11 700 generaciones, el 81,25 % de
B = 14 400 (D11). La suma por sesión es 12 000; la diferencia son 3 configuraciones que
ambos evaluaron. Que el caché las haya evitado es *inferencia*: el CSV no registra aciertos
de caché.

**Configuración final** (congelada el 2026-11-01, 18:30; registro y huellas de los
archivos en `docs/bitacora/2026-10.md`; etiqueta `config-congelada`): rol 1, estrategia 1,
formato 3, estilo 3, cierre 3, temperatura 0.0. Regla de elección, fijada antes de
validar: la mayor precisión en búsqueda entre las mejores de cada arranque (0.20 frente a
0.17; la diferencia está dentro del ruido).

**Validación** (D12, una sola vez, el 2026-11-01 a las 21:07 según indicó Dylber): 18,4 %
sobre 87 instancias (16 aciertos, cálculo propio, porque la salida solo imprime el
porcentaje). Evidencia: `resultados/validacion/busqueda_validado_2026-11-01.ipynb`. La
diferencia con la búsqueda (1,6 puntos) está dentro del ruido; es coherente con que el
20 % fuera algo optimista, por ser el máximo entre 117 configuraciones, pero no lo prueba.

**Vecindad completa del arranque 1** (experimento posterior al congelamiento, en otra
cuenta de Colab con una copia del caché): se evaluaron los 35 vecinos por una ranura de su
mejor. Ninguno supera el 17 %; el máximo es 17 % (un empate con la estrategia 1, ya en el
historial). Así, el 17 % es un óptimo local por ranura completo. No cambia la
configuración entregada. La salida impresa de esa celda y su código están en
`resultados/busqueda/vecindad_arranque_1.txt`; se resumen en el informe (sección 6). La
fecha exacta de la ejecución no quedó registrada.

## 7. Validación

- Las pruebas automáticas están en `tests/`. Con `uv run pytest` pasan **86 pruebas**
  (comprobado el 2026-11-02). En Windows puede fallar el directorio temporal de pytest con
  `PermissionError`; se resuelve con `uv run pytest --basetemp=<carpeta propia>`.
- La validación con `oraculo.validar` (87 instancias) ya se usó **una sola vez**, sobre la
  configuración ya elegida (D12). Si se eligiera con validación, dejaría de ser prueba.
- La nota final sale de un test privado con familias de restricciones que no están en
  los datos visibles. Si traen familias que no están en IFEvalG, `oraculo.py` lanza
  `KeyError` y el notebook de evaluación no carga verificadores extra; no se ha podido
  confirmar.
- `notebooks/evaluacion.ipynb` se probó en Colab con T4 y modelo real, con un
  `entrega.json` temporal y 8 instancias de búsqueda. Falta la prueba con el
  `entrega.json` definitivo y con datos privados reales.
- `notebooks/evaluacion.ipynb` clona `main`: `entrega.json` debe estar en `main` antes
  de la prueba final.

## 8. Límites y lo no desarrollado

- **No se afirma óptimo global ni del subcatálogo.** La configuración es la mejor
  encontrada (D8, D17).
- **Fuera de esta entrega:** backtracking con cota, reparto uniforme frente a UCB1,
  barridos y gráficas de T(n), y el exacto sobre un subcatálogo. Successive Halving se
  descarta con justificación (D4).
- **Óptimos locales:** la búsqueda por coordenadas puede quedar en un óptimo local; con
  dos arranques solo se muestrea ese riesgo. Los dos arranques pararon por convergencia
  (el 0 en su pasada 3 y el 1 en la 2).
- **El arranque 1 no es independiente:** usó exclusiones derivadas de las trazas del
  arranque 0. La premisa de excluir la estrategia 3 resultó falsa (15 % en la pasada 3 del
  arranque 0 y 12 % como vecino del arranque 1), sin cambiar ninguna ganadora.
- **Ruido de medición:** unos 4 puntos con 100 instancias (estimación teórica, no medida
  entre semillas).
- **Hipótesis sin comprobar:** los vínculos entre opciones y familias que fallan (por
  ejemplo, que la frase de `estrategia 7` cause fallos) son hipótesis; el detalle está en
  `analisis_busqueda.md`, sección 6.
- **Velocidad:** medida con una sola configuración.
- **Colab puede cortar la sesión.** Se reanuda con el CSV y la caché de Drive.
- **Datos privados:** quedan fuera del alcance del equipo.

## 9. Mantenimiento de este manual

Sebastián revisa los módulos que documenta (secciones 3.2 a 3.4); Dylber integra.
`PENDIENTE`: Sebastián debe leer las secciones 3.2 a 3.4 y confirmar que coinciden con
su código.
