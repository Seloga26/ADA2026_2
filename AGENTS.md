# Proyecto Oráculo: guía del equipo

> Aquí está lo acordado para el proyecto. Si algo no coincide con el código,
> vale el código: revisa `git status` y `git log` antes de seguir.

---

## 0. Uso de esta guía

- Las decisiones de la sección 5 ya están cerradas; solo se reabren con evidencia nueva.
- Antes de proponer un cambio, revisa si la sección 5 ya lo resuelve.
- El plan completo está en `docs/plan.md`.
- El reparto de la primera entrega está en `docs/reparto_primera_entrega.md`.
- Anota cada sesión importante en `docs/bitacora/`.
- Forma de trabajo: se propone, se aprueba y se ejecuta.

---

## 1. Identidad del proyecto

| Campo | Valor |
| --- | --- |
| Materia | Análisis y Diseño de Algoritmos |
| Período | 2026-2 |
| Nombre del proyecto | Proyecto Oráculo |
| Repositorio remoto | `https://github.com/Seloga26/ADA2026_2.git` (`origin`) |
| Repositorio base indicado | `https://github.com/JuManoel/ADA-2026-2-GP01` |
| Enunciado | `Proyecto_ADAG1.docx` |
| Guía de la primera entrega | `Guia_Primera_Entrega_ADAG_2026B_Actualizada_Grupo1.pdf` |

**Problema.** Encontrar la mejor configuración de prompt para un modelo de lenguaje
gastando el menor número de consultas. Salida: consultas m_j por configuración y una
configuración ganadora c*. Objetivo: maximizar Acc(c*) sujeto a Σ m_j ≤ B.

| Componente de la nota | Peso |
| --- | --- |
| Formalización | 10 % |
| Reducción | 10 % |
| T(n) del exacto | 10 % |
| Aproximado (diseño, T(n) y cota) | 15 % |
| Validación experimental | 10 % |
| Sustentación | 45 % |

Cronograma del enunciado, sin fechas: S1-2 formalización, S3-4 reducción, S5-6 exacto,
S7-8 aproximado, S9-10 experimentación, S11 entrega final y sustentaciones.

---

## 2. Equipo y reparto

Los dos integrantes deben poder sustentar el proyecto completo: el revisor de un
bloque teórico lo rederiva solo antes de aprobar.

| Bloque | Principal | Revisor |
| --- | --- | --- |
| B0. Contratos, `pyproject.toml`, README | Sebastián López | Dylber Cabrera |
| B1. Formalización de las dos partes | Dylber Cabrera | Sebastián López |
| B2. `OraculoContado`, `OraculoSintetico`, fuerza bruta, velocidad real en Colab | Sebastián López | Dylber Cabrera |
| B3. Reducción desde 3-SAT y análisis de muestreo | Sebastián López | Dylber Cabrera |
| B4. Medición y gráficas (`medir.py`, `graficar.py`, ajuste log-log) | Dylber Cabrera | Sebastián López |
| B5. Backtracking con cota, sintético y subcatálogo | Sebastián López | Dylber Cabrera |
| B6. Búsqueda por coordenadas | Dylber Cabrera | Sebastián López |
| B7. Reparto uniforme frente a UCB1 | Dylber Cabrera | Sebastián López |
| B8. Experimentación final, validación y `entrega.json` | Los dos | Cruzado |
| B9. Informe | Sebastián López integra; cada uno redacta lo suyo | Cruzado |
| B10. Sustentación, demo y simulacros | Los dos | — |
| B11. Notebook de búsqueda y `entrega.json` | Dylber Cabrera | Sebastián López |
| B12. Notebook de evaluación | Sebastián López | Dylber Cabrera |
| B13. Manual técnico | Dylber Cabrera integra; cada uno documenta lo suyo | Sebastián López |

---

## 3. Reglas del equipo

- `main` siempre ejecutable; se integra solo por pull request aprobado por el otro integrante.
- Ramas cortas: `feat/<bloque>`, `docs/<tema>`, `fix/<tema>`, `exp/<barrido>`.
- Commits en Conventional Commits, en español, sin emojis y sin pies de herramienta.
  El mensaje termina en la descripción.
- `git push` y el borrado de ramas los hace cada integrante manualmente.
- Código e identificadores en español y `snake_case`. Sin rutas absolutas. Semillas explícitas.
- Ningún dato inventado: lo que no esté comprobado se marca como inferencia.

### Límites de integridad

- `oraculo.py` **se consulta, no se abre**. No usar `LIMPIA`, `PESADA` ni los
  comentarios del catálogo. Las opciones se leen imprimiendo `CATALOGO`.
- No abrir los notebooks de solución del commit `0db1c26` del repositorio base.
- La configuración ganadora sale de una ejecución reproducible, con su historial guardado.

---

## 4. Entorno técnico

- Python 3.12 con `uv`, `pytest` y `matplotlib`.
- Modelo real: Colab con GPU T4, modelo `qwen17b`. `oraculo.py` importa `torch` y
  verificadores desde `/content/open-instruct`, así que **no corre en local**.
- Pruebas y barridos de tiempo: oráculo sintético en local.
- Informe: PDF desde LaTeX, en `informe/`. Se compila con `latexmk main.tex`; ver `informe/README.md`.

Datos comprobados del repositorio base:

- 5 ranuras (`rol`, `estrategia`, `formato`, `estilo`, `cierre`) con 8 opciones cada una.
- `espacio()` da 32 768 configuraciones; con 3 temperaturas, 98 304.
- `datos_visibles.json`: 100 de búsqueda, 87 de validación, 263 descartadas. El
  notebook dice 150 y 300, pero está desactualizado.
- Puntaje todo-o-nada; 2.45 restricciones por instancia en búsqueda.
- El caché no cobra lo ya generado para (modelo, config, instancia, semilla).
- El parámetro `presupuesto=` del oráculo es un tope de memoria de GPU, **no es B**.
- La nota de `entrega.json` sale de un test privado con familias de restricciones
  que no están en los datos visibles.

---

## 5. Decisiones del proyecto

Se tomaron sin posibilidad de nueva consulta a la docente.

| ID | Decisión | Justificación |
| --- | --- | --- |
| **D1** | El repositorio base manda en datos y ejecución; el enunciado, en entregables, pesos y rigor. El informe lleva una tabla de discrepancias. | Es la base indicada y lo único ejecutable. |
| **D2** | L = 5, k_i = 8, \|C\| = 32 768, n = 100, validación con 87, temperatura 0.0, `qwen17b`, semilla 1. | Valores comprobados; con temperatura 0.0 la generación es determinista. |
| **D3** | Técnicas: 1 backtracking, 3 coordenadas y 4 uniforme frente a UCB1. UCB1 también es la variante de §4.5. | El enunciado pide 3 de 4. |
| **D4** | Successive Halving no se implementa; el informe justifica el descarte. | 983 040 consultas por fórmula, 247 808 con tope n = 100 y caché, y con n₀ = 2 casi todo daría 0 %. |
| **D5** | Cota del exacto: `aciertos + instancias restantes`. Si no alcanza al mejor, se abandona la configuración. | Vale con cualquier oráculo. El peor caso sigue siendo O(\|C\|·n). |
| **D6** | Las cotas por estructura de reglas solo se usan en el modelo sintético. Con el modelo real no se poda con supuestos. | Una poda no demostrada deja de ser exacta. |
| **D7** | El modelo sintético mide el exacto con al menos 5 tamaños; el real da los resultados de precisión. | El exacto completo real serían 3 276 800 generaciones. |
| **D8** | Con el modelo real, el exacto corre en un subcatálogo: 3 mejores opciones por ranura (243 configuraciones) o 2 (32) según la velocidad medida. Se reporta "óptimo del subcatálogo". | Nunca se afirma óptimo global. |
| **D9** | Reducción desde 3-SAT, versión de decisión, con L y k_i como parte de la entrada; el proyecto es el caso L = 5. | Lo indica la guía para ADAG1. Con L fijo, \|C\| es constante. |
| **D10** | Dos barridos: n ∈ {10, 25, 50, 75, 100} con \|C\| fijo, y \|C\| = 2^L con n fijo. | T depende de ambas variables. |
| **D11** | B se fija y se cuenta aquí: generaciones nuevas por (config, instancia, semilla). | El oráculo no limita consultas. |
| **D12** | `validar` con n = 87 se usa una sola vez, sobre la configuración ya elegida. | Si se elige con validación, deja de ser prueba. |
| **D13** | La guía de la primera entrega manda sobre el enunciado en esa entrega y en la reducción. El informe registra la discrepancia con Cobertura Máxima. | Es más reciente y específica de ADAG1. |
| **D14** | Se prepara la primera entrega consolidada: informe, repositorio, manual técnico y los tres archivos de ADAG1. | La guía aclara que es una propuesta por confirmar; cumplirla completa es lo más seguro. |
| **D15** | La NP-dureza cubre solo la parte 1, configuración óptima con oráculo exacto. La parte 2, consultas ruidosas o limitadas, se analiza por complejidad de muestreo. | La guía prohíbe trasladar la demostración sin justificarla. |
| **D16** | Rutas: `entrega.json` en la raíz, `notebooks/busqueda.ipynb`, `notebooks/evaluacion.ipynb` y `docs/manual_tecnico.md`. La configuración debe ser la misma en los tres primeros. | La guía exige coherencia entre ellos. |
| **D17** | Búsqueda real: `B = 14 400` generaciones, con dos arranques de hasta 2 pasadas cada uno. Un tercer arranque solo si sobra GPU antes del congelamiento. | Medido: 1,99 s por generación en T4, unas 4 h por arranque. El subcatálogo no entra en esta entrega. |

---

## 6. Algoritmos

**Coordenadas (aproximado principal).** Arranca al azar y mejora una ranura a la vez,
con el orden guiado por las familias de `violo`. Una pasada cuesta ≤ 40·100 = 4 000
generaciones; en general T = O(I·L·k_max·n). Se demuestra que la precisión no baja y
que termina en un óptimo local; un contraejemplo muestra que no hay razón de
aproximación general. El riesgo de óptimos locales se mide con varios arranques.

**Backtracking (exacto).** Peor caso O(\|C\|·n), comparado con fuerza bruta y midiendo
nodos y podas. Coincide con D5 a D8.

**Uniforme frente a UCB1.** Los brazos son las configuraciones finalistas; tirar un
brazo es evaluar una instancia aún no vista para esa configuración. Ambos usan el
mismo B. La cota de Auer, Cesa-Bianchi y Fischer (2002) supone muestras independientes;
aquí se muestrea sin reposición, lo que se declara como aproximación.

---

## 7. Estructura del repositorio

```
ADA2026_2/
  AGENTS.md, CLAUDE.md, README.md, pyproject.toml
  oraculo.py, ayudas.py, datos_visibles.json, proyecto_oraculo.ipynb   base, sin cambios
  busqueda_prompt/        paquete propio; `oraculo` ya es un módulo de la base
    contratos.py, sintetico.py, contado.py
    algoritmos/           fuerza_bruta, backtracking, coordenadas, reparto_uniforme, ucb1
    experimentos/         medir.py, graficar.py
  entrega.json
  notebooks/              medicion_velocidad.ipynb, busqueda.ipynb, evaluacion.ipynb
  tests/
  resultados/
  informe/
  docs/                   plan.md, manual_tecnico.md, bitacora/
```

`proyecto_oraculo.ipynb` queda como referencia. Los notebooks propios importan `busqueda_prompt`.

Contratos:

```python
Config = dict   # {rol, estrategia, formato, estilo, cierre, temperatura}

class Oraculo(Protocol):
    def evaluar(self, config, instancias, semilla) -> Resultado: ...   # precision, trazas, n
```

`OraculoContado` envuelve al real o al sintético, cuenta generaciones nuevas sin tocar
su interior y lanza `PresupuestoAgotado`.

---

## 8. Estado actual del repositorio

Última actualización: sábado 2026-10-31, 17:00. Antes de seguir, ejecuta `git fetch origin`,
`git log origin/main --oneline -5` y `git branch -r`: Dylber pudo haber subido trabajo.

**Entrega:** lunes 2026-11-02 a medianoche (se asume 23:59). Corte de trabajo nuevo: lunes 20:00.
Qué hace cada uno y qué bloquea a quién: `docs/reparto_primera_entrega.md`.

### Hecho y verificado

| Tarea | Estado | Evidencia |
|---|---|---|
| Archivos base | Listo | Idénticos a `4d8358d` |
| S2 a S4: contratos, `OraculoContado`, sintético, fuerza bruta | Listo | 60 pruebas pasan con `uv run pytest` |
| S5: velocidad en Colab | Listo | `resultados/velocidad.json`: 1,99 s por generación, 5,77 GB |
| S7 y S8: reducción y muestreo | Redactado | `informe/secciones/02_reduccion.tex`; compila |
| S9: notebook de evaluación | Sin probar en Colab | Solo probado con modelo y oráculo simulados |
| S12: README | Listo | El ejemplo da el resultado esperado |

### Pendiente de Sebastián

1. Rehacer la reducción en papel, sin mirar; se defiende sin notas.
2. Verificar en la fuente las citas de `informe/referencias.bib` (Karp, Hoeffding, Auer).
3. S10: probar `notebooks/evaluacion.ipynb` en Colab.
   - `entrega.json` aún no existe: usar una celda temporal, sin guardarla en el repositorio,
     que escriba este archivo de prueba antes de `cargar_entrega`:
     `{"grupo": "G00", "semana": 1, "config": {"rol": 2, "estrategia": 1, "formato": 4, "estilo": 1, "cierre": 7, "temperatura": 0.0}}`
   - Subir a Colab una copia recortada de `datos_visibles.json` llamada `datos_privados.json`.
4. S6: revisar el PR de coordenadas en menos de 2 horas.
5. Lunes: S11 conectar el `entrega.json` definitivo, S13 integrar `informe/main.tex` antes de
   las 16:00 y S14 probar desde un clon limpio.

### Pendiente de Dylber

Al cierre de esta actualización no había subido nada y faltaba confirmar su acceso al repositorio.

1. D2: formalización. D3: `busqueda_prompt/algoritmos/coordenadas.py`, con `OraculoContado` y
   la forma de `fuerza_bruta.resolver`.
2. D4: primer arranque el sábado, con caché en Drive.
3. D5 a D9: búsqueda, análisis de fallos, notebook, configuración congelada el domingo por la
   noche, `oraculo.validar` una vez y `entrega.json`.
4. D10 y D11: secciones 04 y 06 del informe y `docs/manual_tecnico.md`.

**Plan de contingencia:** si el sábado por la noche no hay fecha clara para el primer arranque,
o el domingo al mediodía no hay una pasada real en curso, Sebastián toma coordenadas y la búsqueda.
Sin búsqueda real no hay entrega.

### Riesgos abiertos

- Colab puede cortar la sesión: 14 400 generaciones son unas 8 h, hasta 10 h con margen. Dividir
  entre las dos cuentas con el mismo caché en Drive.
- Datos privados: si traen familias que no estén en IFEvalG, `oraculo.py` lanza `KeyError` y el
  notebook de evaluación no carga verificadores extra. No se ha podido confirmar.
- `notebooks/evaluacion.ipynb` clona `main`: `entrega.json` debe estar en `main` antes de la prueba final.
- La velocidad sale de una sola configuración; otras pueden tardar más.

### Pendientes del equipo

- Identificador real del grupo y semana para `entrega.json`; el notebook trae `G07` y `3`, y el
  nombre de la guía sugiere Grupo 1, sin confirmar.
- Confirmar si "medianoche" es el final del lunes y cómo se entrega: enlace al repositorio, PDF o ambos.
- Fechas de las demás etapas del cronograma.
- Política de declaración de herramientas de apoyo: por definir.

---

## 9. Mantenimiento de esta guía

- Actualiza la sección 8 al cerrar cada sesión: es el punto de partida de la siguiente.
- Una decisión nueva entra en la sección 5 con ID estable y en la bitácora.
