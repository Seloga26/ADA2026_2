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
    experimentos/         medir.py (las gráficas las dibuja LaTeX con pgfplots)
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

Última actualización: jueves 2026-11-05, cierre de la primera entrega en `docs/cierre-entrega`.
Antes de seguir, ejecuta `git fetch origin`, `git log origin/main --oneline -5` y `git branch -r`:
Dylber pudo haber subido trabajo.

**Entrega:** viernes 2026-11-06 (se movió desde el lunes 2026-11-02). Se entregan el enlace al
repositorio y el PDF del informe. `entrega.json`: grupo `ADAG1`, semana `6`, confirmada.

### Hecho y verificado

| Tarea | Estado | Evidencia |
|---|---|---|
| Archivos base | Listo | Idénticos a `4d8358d` |
| Código y pruebas | Listo | 174 pruebas pasan (`.venv/Scripts/python.exe -m pytest`; en la máquina de Sebastián `uv run` falla con "uv trampoline failed to canonicalize script path") |
| S5: velocidad en Colab | Listo | `resultados/velocidad.json`: 1,99 s por generación, 5,77 GB |
| Búsqueda real (D5 a D9) | Listo | Dos arranques; unión de 117 configuraciones y 11 700 generaciones de B = 14 400; validación una sola vez: 18,4 % sobre 87 |
| Configuración congelada | Listo | rol 1, estrategia 1, formato 3, estilo 3, cierre 3, temperatura 0.0; etiqueta `config-congelada` (`6e5d003`) |
| `entrega.json` | Listo | En `main`; pasa `cargar_entrega` |
| `notebooks/busqueda.ipynb` | Listo | Probado en Colab; guarda la salida real de B6 y el resultado de la validación, que remite a `resultados/validacion/` |
| `notebooks/evaluacion.ipynb` | Probado con datos de prueba | Falta la prueba S14 con `main` final |
| Exacto (B5) | Listo con el sintético | `backtracking.py` con cota D5 y cota estructural; barridos en `resultados/exacto/`; sección 03. Con el modelo real no se ejecutó |
| Informe | Compila sin advertencias | Secciones 01 a 07, ficha de identificación y anexo de decisiones; 18 páginas |
| Manual técnico | Listo | `docs/manual_tecnico.md`, enlazado desde el README |

Los cambios del 2026-11-05 sobre partes de Dylber (secciones 01 y 04, manual y notebook de
búsqueda) están en commits separados; Dylber los revisa después de la entrega. Detalle en la
bitácora, registro del 2026-11-05.

### Pendiente antes de entregar (Sebastián)

1. Push de `docs/cierre-entrega`, PR e integración en `main`.
2. S14: clon limpio en Colab sobre `main` final; correr el ejemplo y `notebooks/evaluacion.ipynb`.
3. Versionar el PDF en el último commit y crear la etiqueta `primera-entrega`; push de la etiqueta.
4. Entregar el enlace y el PDF.

### Pendiente después de la entrega

- Dylber: revisar los commits de `docs/cierre-entrega` y aceptar la sección 05.
- D12: revisar la reducción entre los dos.
- Decidir D18 (`MAX_PASADAS = 3`); el informe la reporta como propuesta.
- Siguiente etapa: reparto uniforme frente a UCB1 y, si hay GPU, el exacto en un subcatálogo (D8).

### Riesgos abiertos

- Datos privados: si traen familias que no estén en IFEvalG, `oraculo.py` lanza `KeyError` y el
  notebook de evaluación no carga verificadores extra. No se ha podido confirmar.
- `notebooks/evaluacion.ipynb` clona `main`: todo debe estar en `main` antes de S14.
- La velocidad sale de una sola configuración; otras pueden tardar más.

### Pendientes del equipo

- Fechas de las demás etapas del cronograma.
- Política de declaración de herramientas de apoyo: por definir.

---

## 9. Mantenimiento de esta guía

- Actualiza la sección 8 al cerrar cada sesión: es el punto de partida de la siguiente.
- Una decisión nueva entra en la sección 5 con ID estable y en la bitácora.
