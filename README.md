# Proyecto Oráculo

Proyecto de Análisis y Diseño de Algoritmos, 2026-2. Busca una configuración de prompt
que maximice la precisión de un modelo de lenguaje, controlando el número de consultas.

**Integrantes:** Sebastián López y Dylber Cabrera.
**Versión:** solución base de la primera entrega, en desarrollo.

## Requisitos

- Python 3.12 y [`uv`](https://docs.astral.sh/uv/).
- Google Colab con GPU T4 para ejecutar el modelo real. `oraculo.py` no corre en local.

## Instalación y pruebas

```
uv sync
uv run pytest
```

## Ejemplo pequeño

Corre en local, con el oráculo sintético y semilla fija:

```
uv run python -m busqueda_prompt.ejemplo
```

Resultado esperado:

```
ganadora: {'r0': 1, 'r1': 1, 'r2': 0, 'temperatura': 0.0}
precision: 0.80
consultas: 160
```

Son 8 configuraciones por 20 instancias, por lo que la fuerza bruta gasta 160 consultas.

## Notebooks en Colab

Elija una GPU T4 y ejecute todas las celdas. La primera vez el entorno se instala y se
reinicia; después, ejecútelas otra vez.

| Notebook | Uso |
|---|---|
| `notebooks/medicion_velocidad.ipynb` | Mide cuánto tarda una generación del modelo real |
| `notebooks/evaluacion.ipynb` | Evalúa la configuración de `entrega.json` sobre datos de prueba |

## Estructura

| Ruta | Contenido |
|---|---|
| `busqueda_prompt/` | Contratos, oráculo contado, modelo sintético y algoritmos |
| `tests/` | Pruebas automáticas |
| `notebooks/` | Ejecución en Colab |
| `informe/` | Fuente LaTeX del informe |
| `docs/` | Plan, reparto y bitácora |

## Base del proyecto

`oraculo.py`, `ayudas.py`, `datos_visibles.json` y `proyecto_oraculo.ipynb` provienen sin cambios de [JuManoel/ADA-2026-2-GP01](https://github.com/JuManoel/ADA-2026-2-GP01), commit `4d8358d`.
