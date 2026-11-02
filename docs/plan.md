# Plan del Proyecto Oráculo

Plan de trabajo de Sebastián López y Dylber Cabrera. Las decisiones D1 a D16 están en
la sección 5 de `AGENTS.md`; este documento las desarrolla. Si hay diferencias, vale
`AGENTS.md`.

Lo marcado como **interpretación** no aparece en el enunciado ni en el repositorio base.

---

## 1. Resumen del enunciado

### 1.1 Problema

- Encontrar la mejor configuración de prompt para un modelo de lenguaje.
- Cada configuración concatena instrucciones de categorías discretas.
- Evaluar una configuración sobre una solicitud cuesta tiempo de GPU, así que se busca
  minimizar las consultas.
- Entrada: C, I = {i₁…iₙ} y el presupuesto B.
- Salida: m_j consultas por configuración c_j y una ganadora c* ∈ C.
- Objetivo: maximizar Acc(c*) sujeto a Σ m_j ≤ B.
- Clase: NP-difícil. El enunciado indica Cobertura Máxima y la guía de la primera entrega, 3-SAT (D13).

### 1.2 Requisitos

- Aplicar 3 de las 4 técnicas de §4.3; cada una se implementa, se analiza y se compara.
- Elegir una variante de §4.5.
- Para considerar "eficiente" la solución (§2):
  - definición precisa de n;
  - T(n) del exacto deducida paso a paso;
  - T(n) de cada heurística, con su garantía demostrada o citada si existe;
  - validación experimental: tiempos para n creciente, gráfica y contraste con T(n).

### 1.3 Entregables

- Informe técnico con sección de complejidad. El detalle de su formato sigue pendiente.
- Código reproducible con instancias sintéticas de al menos 5 tamaños, medición de
  tiempos y gráfica de tiempo contra n.
- Sustentación grupal de 15 a 20 minutos: la reducción y la T(n) del exacto se defienden
  sin notas.
- Sustentación individual, según se indique.
- `entrega.json`, definido por el repositorio base y calificado con un test privado.

Los pesos y el cronograma están en la sección 1 de `AGENTS.md`.

### 1.4 Primera entrega

Según `Guia_Primera_Entrega_ADAG_2026B_Actualizada_Grupo1.pdf`. La guía aclara que la fecha
única es una propuesta por confirmar; se prepara completa (D14).

| Producto | Contenido mínimo | Bloque |
|---|---|---|
| Informe | Formalización de las dos partes y NP-dureza; además, el proceso real que produjo `entrega.json` | B1, B3 |
| Repositorio | Código ejecutable, README con integrantes y versión, dependencias, semillas, resultados esperados y un caso que respete las restricciones | B0, B2, B6 |
| Manual técnico | Entorno, arquitectura, funcionamiento, uso, validación y límites | B13 |
| `entrega.json` | Grupo, semana, índices de las 5 ranuras y temperatura; JSON válido | B11 |
| Notebook de evaluación | Carga `entrega.json` y evalúa sobre datos privados sin editar nada | B12 |
| Notebook de búsqueda | Método, configuraciones probadas, precisiones, fallos, decisiones y `oraculo.validar` | B11 |

**Solución base:** búsqueda por coordenadas, `OraculoContado`, modelo sintético, fuerza bruta y
pruebas. **Interpretación:** backtracking, UCB1 y los barridos no son parte de la solución base;
el manual los declara como no desarrollados si aún no están listos.

Exigencias que el informe y el notebook deben cumplir:

- Distinguir el mejor resultado observado de un óptimo demostrado.
- Cada fallo analizado debe explicar qué opción descartó y cómo cambió la búsqueda.
- No confundir `oraculo.validar` con la evaluación privada de la docente.
- El informe referencia las celdas del notebook y permite reconstruir la decisión final.

---

## 2. Discrepancias del enunciado

El informe las presenta en una tabla, con la decisión tomada en cada caso.

| Tema | Enunciado | Repositorio base | Decisión |
|---|---|---|---|
| \|C\| | 3840 y 144; con temperatura 432 | 32 768; con temperatura 98 304 | 32 768 (D2) |
| Opciones por categoría | k_max = 4, de modo que el máximo sería 4⁵ = 1024 | 8 por ranura | 8 (D2) |
| Instancias | n = 150 | 100 de búsqueda y 87 de validación | n = 100 (D2) |
| Categorías | Rol, Estrategia, Formato, Verificación, Recordatorio | `rol`, `estrategia`, `formato`, `estilo`, `cierre` | Las del repositorio (D1) |
| Instancias "sintéticas" | Todas sintéticas | Modelo real en Colab | Ambas, con funciones distintas (D7) |
| Exacto | Fuerza bruta o PD en el cronograma; backtracking en §4.3 | Sin definir | Backtracking; fuerza bruta como referencia (D3) |
| Reducción | Cobertura Máxima | La guía de la primera entrega indica 3-SAT | 3-SAT (D9, D13) |

Otras inconsistencias comprobadas:

- 91 444 sí cuadra: 3840·2·log₂3840 = 91 444,92, y su parte entera es 91 444, la cifra del enunciado. Con ⌈log₂⌉ da 92 160.
- La fórmula de Successive Halving solo es exacta si \|C\| es potencia de 2.
- Con 5 categorías fijas, \|C\| es constante y el problema es polinomial. Por eso L y k_i
  son parte de la entrada de la reducción (D9).
- La fórmula de coordenadas omite L porque lo toma constante; con L variable,
  T = O(I·L·k_max·n).

---

## 3. Selección y justificación

### 3.1 Successive Halving: por qué se descarta

| Estrategia sobre \|C\| = 32 768 | Generaciones |
|---|---|
| Fuerza bruta con n = 100 | 3 276 800 |
| Successive Halving según la fórmula, n₀ = 2 | 983 040 |
| Successive Halving con tope n = 100 | 495 416 |
| Successive Halving con tope y caché | 247 808 |
| Una pasada de coordenadas | ≤ 4 000 |

Además, una configuración al azar queda bajo el 5 % y el puntaje es todo-o-nada: con
n₀ = 2 casi todas marcarían 0 % y no se podrían separar.

### 3.2 Búsqueda por coordenadas (aproximado principal)

- Arranca al azar y mejora una ranura a la vez, con el orden guiado por las familias de `violo`.
- Evalúa siempre sobre las 100 instancias.
- Se demuestra que la precisión no baja y que termina en un óptimo local.
- Un contraejemplo pequeño muestra que no hay razón de aproximación general.
- El riesgo de óptimos locales se mide con varios arranques; su número depende de la
  velocidad medida.

### 3.3 Backtracking (exacto)

- Cota: `aciertos + instancias restantes`. Es optimista, por lo que nunca descarta el óptimo.
- Nodos por nivel: Σ_ℓ ∏_{i≤ℓ} k_i ≤ 2\|C\| si k_i ≥ 2.
- Cada hoja cuesta como máximo n consultas, de modo que T = O(\|C\|·n) en el peor caso.
- Correctitud: invariante "la mejor solución encontrada es el máximo de lo ya explorado o podado".
- Sintético: exacto completo, con cotas por estructura de reglas, ya que allí se demuestran.
- Real: subcatálogo con las 3 mejores opciones por ranura según las pasadas de coordenadas
  (243 configuraciones, ≤ 24 300 generaciones), o 2 por ranura (32, ≤ 3 200) si la velocidad
  no alcanza. Se reporta "óptimo del subcatálogo".

### 3.4 Uniforme frente a UCB1 (técnica 4 y variante)

- Brazos: las configuraciones finalistas de las fases anteriores.
- Tirar un brazo es evaluar una instancia aún no vista para esa configuración.
- Ambos esquemas usan el mismo B; la gráfica muestra precisión frente a B.
- Garantía citada: Auer, Cesa-Bianchi y Fischer (2002). Antes de usarla en el informe hay
  que verificar el enunciado exacto en el artículo.
- Esa cota supone muestras independientes. Aquí se muestrea sin reposición sobre 100
  instancias, lo que se declara como aproximación.

### 3.5 Parte 1: reducción desde 3-SAT

**Problema de decisión.** Dado un catálogo de L categorías, n instancias, un oráculo exacto
evaluable en tiempo polinomial y un umbral t, ¿existe c con Acc(c) ≥ t?

Construcción, dada una fórmula φ con m variables y q cláusulas:

1. Crear L = m categorías, una por variable, con 2 opciones: falso y verdadero.
2. Crear n = q instancias, una por cláusula. La instancia j exige la regla j.
3. La opción de x_i satisface la regla j si ese valor hace verdadero un literal de la cláusula j.
4. Fijar t = 1.

Una configuración es entonces una asignación de verdad, y la instancia j se cumple si y solo
si la cláusula j es verdadera. El tamaño es O(m + q), aunque \|C\| = 2^m, porque la entrada es
el catálogo y no la lista de configuraciones.

- (⇒) Si φ es satisfacible, su asignación da una configuración con Acc = 1.
- (⇐) Si Acc(c) = 1, c cumple todas las instancias y su asignación satisface φ.

Pertenece a NP porque el certificado c se verifica con n evaluaciones. Por lo tanto, la
versión de decisión es NP-completa y la de optimización, NP-difícil. La construcción no usa
ruido ni presupuesto: el caso L = 5 del proyecto es finito y no hereda dureza por sí solo.

### 3.6 Parte 2: consultas ruidosas o limitadas

No hereda la demostración anterior (D15). Se analiza cuántas muestras hacen falta:

- Si cada consulta es una muestra independiente con éxito Acc(c), Hoeffding y la unión dan que
  m ≥ ln(2\|C\|/δ) / (2ε²) consultas por configuración estiman todas con error ≤ ε, con
  probabilidad ≥ 1 − δ.
- Separar dos configuraciones con diferencia Δ exige m del orden de ln(1/δ)/Δ².
- Con n = 100 instancias fijas, la resolución de la medición es de 1 %.
- Costo: cada muestra es una generación en GPU, medida con `OraculoContado`.

---

## 4. Modelo sintético

**Interpretación:** sirve para medir el exacto y para las pruebas locales; no reemplaza al modelo real.

- Hay R reglas de formato; cada instancia exige un subconjunto R_i ⊆ R.
- Cada opción (categoría ℓ, índice o) satisface un conjunto de reglas S_{ℓ,o}.
- Los pares de opciones en conflicto anulan reglas, para modelar que las instrucciones no
  son independientes.
- El éxito ocurre si R_i ⊆ ∪S − conflictos. Con ruido, se invierte con probabilidad p,
  determinista por (semilla, c, i).
- El modo sin ruido, sin conflictos y con una regla por instancia coincide con la reducción.
- El peor caso se construye con instancias donde la cota no poda.

---

## 5. Pruebas

- **Normales:**
  - backtracking y fuerza bruta dan la misma precisión en espacios pequeños, con al menos 20 semillas;
  - uniforme gasta exactamente lo previsto;
  - UCB1 nunca supera B;
  - la precisión de coordenadas no baja entre pasos.
- **Límite:** \|C\| = 1, categoría con k = 1, n = 1, B exacto, B menor que \|C\|, empates
  con desempate determinista y todas las configuraciones en 0 %.
- **Errores:** `PresupuestoAgotado`, parámetros inválidos y reproducibilidad por semilla.
- **Reducción:** en fórmulas 3-SAT pequeñas, Acc = 1 se alcanza si y solo si la fuerza bruta
  sobre las asignaciones encuentra una que las satisface.
- **Entrega:** `entrega.json` es válido, sus índices están en rango y coincide con la ganadora
  del notebook de búsqueda.

---

## 6. Validación experimental

- Barridos de D10, con al menos 5 repeticiones por semilla, reportando media y desviación.
- Se miden consultas (deterministas) y tiempo (`time.perf_counter`).
- Gráficas:
  1. medición frente a c·T(n), con c ajustada por mínimos cuadrados;
  2. log-log con su pendiente y la pendiente teórica;
  3. cociente t/T(n), que debe estabilizarse;
  4. nodos y consultas frente a \|C\|·n, en casos favorable y peor;
  5. precisión de la ganadora frente a B, uniforme contra UCB1;
  6. `curva(historial)` de la búsqueda sobre el modelo real.

---

## 7. Estructura del informe

La plantilla está en `informe/`, en LaTeX, con un archivo por sección en `secciones/`.
Se compila con `latexmk main.tex` y el PDF queda en `informe/build/`. Solo se versiona
la fuente hasta la entrega final; las instrucciones están en `informe/README.md`.

| Sección | Responsable |
|---|---|
| 1 | Dylber |
| 2 y 3 | Sebastián |
| 4 y 5 | Dylber |
| 6 y 7 | Los dos |

Sebastián integra `main.tex` y compila la versión final.

1. Formalización.
2. Reducción desde 3-SAT y análisis de muestreo.
3. Exacto: algoritmo, pseudocódigo, correctitud y T(n).
4. Aproximados: coordenadas y UCB1, con T(n) y garantías.
5. Comparación de reparto y descarte de Successive Halving.
6. Proceso de optimización, resultados y validación, con referencias al notebook de búsqueda.
7. Discrepancias y limitaciones.
8. Referencias, en `referencias.bib`.

---

## 8. Dependencias y paralelismo

- **En paralelo desde el inicio:** B0, B1, B3 y B12.
- **Cadenas:**
  - B2 depende de B0.
  - B5, B6 y B7 dependen de B0 y B2; mientras tanto, avanzan con un doble de prueba.
  - B11 depende de B6 y de la velocidad medida en B2.
  - B13 se cierra cuando B6 y B12 están listos.
  - B3 no depende del código, pero B2 incluye el modo de la reducción.
  - B8 depende de B4 y de B5 a B7.
- **Regla:** nadie espera. Si falta algo, se programa contra el contrato.

---

## 9. Flujo de git

Las reglas básicas están en la sección 3 de `AGENTS.md`. Además:

- Lista de revisión del PR: pruebas en verde, sin tocar archivos ajenos sin avisar y teoría actualizada.
- Se integra con *squash merge*.
- Cada archivo tiene un dueño. `busqueda_prompt/contratos.py` y `pyproject.toml` solo cambian en PR dedicados.
- El informe va en un archivo por sección; `main.tex` y `preambulo.tex` solo cambian en PR dedicados.
- Antes de abrir un PR: `git pull --rebase origin main`.
- En GitHub, proteger `main` con un PR y una aprobación.

---

## 10. Hitos

Semanas relativas al cronograma; las fechas reales siguen pendientes.

| Hito | Semana | Integración y revisión |
|---|---|---|
| H1 | Primero | Contratos integrados y velocidad real medida |
| H2 | Antes de la primera entrega | Coordenadas, sintético, pruebas y borrador de formalización y reducción |
| H3 | Lunes 2026-11-02, medianoche | Búsqueda real ejecutada, los tres archivos coherentes, informe y manual |
| H4 | S6 | Backtracking y T(n) revisados |
| H5 | S8 | UCB1, uniforme y garantías; primer simulacro |
| H6 | S10 | Experimentos, gráficas e informe completos; segundo y tercer simulacro |
| H7 | S11 | Entrega final y sustentaciones |

---

## 11. Matriz de trazabilidad

| Requisito | Tarea | Responsable | Terminado cuando… |
|---|---|---|---|
| §2/§4.2 Definir n, entrada, salida y objetivo | B1 | Dylber | Documento entregado, con L variable y la tabla de discrepancias |
| §4.4 y guía: NP-dureza desde 3-SAT | B3 | Sebastián | Versión de decisión, construcción, polinomialidad y ambas direcciones; ambos la exponen sin notas |
| Guía §7.4: consultas ruidosas | B3 | Sebastián | Análisis de muestreo separado de la demostración |
| §4.3-1 Backtracking con poda | B5 | Sebastián | Coincide con fuerza bruta en al menos 20 semillas y pasa las pruebas límite |
| §4.3-1 Derivar O(\|C\|·n) y medir la poda | B5, B8 | Sebastián | Deducción en el informe y gráfica de nodos y consultas en casos favorable y peor |
| §4.3-3 Coordenadas y riesgo de óptimos locales | B6 | Dylber | T(n), demostración de monotonía, contraejemplo y medición con varios arranques |
| §2 Garantía del aproximado | B6, B7 | Dylber | Cota de UCB1 citada, con hipótesis verificadas y la salvedad declarada |
| §4.3-4 Uniforme frente a adaptativo | B7, B8 | Dylber | Gráfica de precisión frente a B, con repeticiones y conclusión cuantitativa |
| §4.5 Variante UCB1 | B7 | Dylber | Implementada, analizada y presente en la comparación |
| §5 Al menos 5 tamaños, tiempos y gráfica | B2, B4, B8 | Los dos | `medir.py` reproduce los CSV con una orden; gráficas con c·T(n), log-log y t/T(n) |
| §5 Código reproducible | B0, B9 | Los dos | Un clon limpio regenera los resultados siguiendo el README |
| §5 Informe técnico | B9 | Sebastián integra | Secciones completas y revisadas por ambos |
| §5 Sustentación grupal | B10 | Los dos | 3 simulacros cronometrados; cada uno expone reducción y T(n) sin notas |
| §5 Sustentación individual | B10 | Cada uno | Cada uno modifica en vivo una métrica o formato de salida en cualquier módulo |
| Guía §7.2: `entrega.json` | B11 | Dylber | JSON válido, con grupo y semana reales, y la misma configuración de los notebooks |
| Guía §7.2-7.3: notebook de búsqueda | B11 | Dylber | Método, registro, fallos con decisiones y `oraculo.validar` visibles |
| Guía §7.2: notebook de evaluación | B12 | Sebastián | Corre sin editar nada y sin datos privados durante su preparación |
| Guía §5: repositorio | B0, B6 | Los dos | Un clon limpio ejecuta el ejemplo pequeño con su resultado esperado |
| Guía §6: manual técnico | B13 | Dylber integra | Otra persona instala y ejecuta sin ayuda |

---

## 12. Riesgos

| Riesgo | Mitigación |
|---|---|
| La docente esperaba que el enunciado mandara sobre el repositorio | Tabla de discrepancias con la justificación de cada decisión |
| Reducción mal planteada | Construcción de 3.5, rederivada por ambos antes de entregar |
| Trasladar la NP-dureza a consultas ruidosas | Partes separadas en 3.5 y 3.6 (D15) |
| La docente esperaba Cobertura Máxima | Se registra en la tabla de discrepancias y se cita la guía |
| Notebook de evaluación falla con datos privados desconocidos | Aceptar un archivo con nombre fijo o una carga manual sin editar celdas; probar con un archivo de ejemplo |
| Los notebooks no pueden clonar el repositorio | Mantener el repositorio accesible y probar en un entorno limpio de Colab |
| Configuración distinta entre archivos | Prueba automática y lectura directa desde `entrega.json` |
| La GPU no alcanza para el subcatálogo | Medir velocidad primero; pasar de 243 a 32 configuraciones |
| Colab se desconecta | Caché en Drive |
| Búsqueda sin señal por todo-o-nada | Evaluar sobre las 100 instancias |
| Sobreajuste a búsqueda frente a familias ocultas | Validar una sola vez y reportar la diferencia |
| Tiempos ruidosos | Medir también consultas; repeticiones en la misma máquina |
| Un integrante bloquea al otro | Contratos al inicio, dobles de prueba y PR pequeños |
| Asimetría de dominio: la sustentación vale el 45 % | Rederivación cruzada y simulacros cruzados |
| La demo en vivo falla | `busqueda_prompt` con tamaños preconfigurados y ensayo previo |

---

## 13. Pendientes antes de implementar

1. Confirmar entre los dos las decisiones D1 a D16 y el reparto.
2. Crear `pyproject.toml`.
3. Integrar los contratos.
4. Agregar a Dylber como colaborador y proteger `main`.
5. Instalar el entorno en ambos equipos y verificar que `pytest` corre.
6. Medir la velocidad real en Colab.
7. Definir identificador de grupo, semana y fechas.
