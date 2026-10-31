# Reparto de la primera entrega

**Límite:** lunes 2 de noviembre de 2026 a medianoche (23:59).
**Corte de trabajo nuevo:** lunes a las 20:00. Después, solo correcciones.

Este documento dice qué hace cada uno, cuándo y qué puede detener al otro. El detalle
técnico está en `docs/plan.md` y las decisiones, en la sección 5 de `AGENTS.md`.

---

## 1. Resumen

| Producto | Responsable | Revisa |
|---|---|---|
| Dependencias y contratos | Sebastián | Dylber |
| `OraculoContado`, modelo sintético, fuerza bruta y pruebas | Sebastián | Dylber |
| Medición de velocidad en Colab | Sebastián | Dylber |
| Informe: formalización | Dylber | Sebastián |
| Informe: reducción desde 3-SAT y análisis de muestreo | Sebastián | Dylber |
| Búsqueda por coordenadas | Dylber | Sebastián |
| Notebook de búsqueda y búsqueda real | Dylber | Sebastián |
| `entrega.json` y `oraculo.validar` | Dylber | Sebastián |
| Notebook de evaluación | Sebastián | Dylber |
| Informe: proceso de optimización y resultados | Dylber | Sebastián |
| Manual técnico | Dylber integra; Sebastián documenta sus módulos | Sebastián |
| README e integración final del informe | Sebastián | Dylber |
| Prueba desde un clon limpio | Sebastián | Dylber |

**Queda fuera de esta entrega:** backtracking, UCB1, barridos y gráficas de T(n). El manual
y el informe los declaran como no desarrollados.

---

## 2. Acuerdos antes de empezar

Se hacen el sábado, entre los dos, antes de escribir código o texto.

1. Revisar D1 a D16 de `AGENTS.md`. Cualquier objeción se resuelve hoy.
2. Sebastián agrega a Dylber como colaborador del repositorio y le pasa el enunciado y la guía.
3. Fijar la notación común del informe:

| Símbolo | Significado |
|---|---|
| L | número de categorías |
| k_i | opciones de la categoría i |
| C | conjunto de configuraciones; \|C\| = ∏ k_i |
| I | instancias; n = \|I\| |
| Acc(c) | fracción de instancias que c cumple por completo |
| B | presupuesto de generaciones |
| m_j | consultas gastadas en la configuración c_j |

4. Fijar estos formatos, para que nadie espere al otro:

```python
config = {"rol": 0, "estrategia": 0, "formato": 0, "estilo": 0, "cierre": 0, "temperatura": 0.0}

oraculo.evaluar(config, instancias, semilla)   # devuelve precision, trazas, n
oraculo.consultas                              # generaciones nuevas gastadas
```

```json
{"grupo": "POR_DEFINIR", "config": {"rol": 0, "estrategia": 0, "formato": 0, "estilo": 0, "cierre": 0, "temperatura": 0.0}, "semana": 0}
```

Los valores anteriores son de ejemplo, no una configuración recomendada.

5. El registro de la búsqueda se guarda en `resultados/historial_busqueda.csv` con estas columnas:
   `paso, arranque, ranura, opcion, config, precision, mejor_precision, consultas, decision`.

---

## 3. Sebastián López

### Sábado

| # | Tarea | Listo cuando | Desbloquea |
|---|---|---|---|
| S1 | Agregar a Dylber al repositorio y pasarle el enunciado y la guía | Dylber clona y abre ambos archivos | Todo Dylber |
| S2 | Crear `pyproject.toml` y `busqueda_prompt/` | `uv sync` y `pytest` corren | D3 |
| S3 | `contratos.py` y `contado.py` | El contador no cobra lo repetido y lanza `PresupuestoAgotado` | D3 |
| S4 | `sintetico.py` y `fuerza_bruta.py`, con semilla | Las pruebas pasan y el resultado se repite | D3 |
| S5 | Notebook de medición en Colab: 1 configuración sobre 100 instancias | Hay segundos por generación y uso de memoria anotados | D4, D5 |
| S6 | Revisar la implementación de coordenadas | PR aprobado | D5 |

### Domingo

| # | Tarea | Listo cuando | Desbloquea |
|---|---|---|---|
| S7 | Redactar `secciones/02_reduccion.tex`, parte 1 | Versión de decisión, construcción, polinomialidad, ambas direcciones y pertenencia a NP | Revisión de Dylber |
| S8 | Redactar la parte 2 de esa sección | El muestreo queda separado de la NP-dureza | Revisión de Dylber |
| S9 | `notebooks/evaluacion.ipynb` | Lee `entrega.json`; acepta `datos_privados.json` o carga manual, sin editar celdas | S11 |
| S10 | Probar el notebook con un archivo de ejemplo | Corre de principio a fin en un entorno limpio | S11 |

### Lunes

| # | Tarea | Listo cuando | Desbloquea |
|---|---|---|---|
| S11 | Conectar el notebook con el `entrega.json` definitivo | Evalúa la configuración ganadora | S14 |
| S12 | Completar el README | Tiene integrantes, versiones, dependencias, ejemplo pequeño y resultado esperado | S14 |
| S13 | Integrar `informe/main.tex` | Compila; las secciones no desarrolladas quedan fuera o declaradas | Entrega |
| S14 | Probar desde un clon limpio en Colab | Corren el ejemplo pequeño y la evaluación | Entrega |

---

## 4. Dylber Cabrera

### Sábado

| # | Tarea | Listo cuando | Desbloquea |
|---|---|---|---|
| D1 | Revisar la notación y los formatos con Sebastián | Sección 2 acordada | S7 |
| D2 | Redactar `secciones/01_formalizacion.tex` | Cubre las dos partes: contexto, entradas y tamaño, salidas, objetivo, restricciones y supuestos | S7, informe |
| D3 | `algoritmos/coordenadas.py` y sus pruebas | La precisión no baja, respeta B y funciona con el sintético | S6, D4 |
| D4 | Primera pasada real en Colab, con caché en Drive | Queda el historial en CSV y el caché sobrevive a una desconexión | D5 |

### Domingo

| # | Tarea | Listo cuando | Desbloquea |
|---|---|---|---|
| D5 | Completar pasadas y arranques según la velocidad medida | Se alcanzó la condición de parada o se agotó el tiempo acordado | D6, D7 |
| D6 | Analizar las trazas de fallos | Cada fallo citado dice qué opción descartó y qué cambió en la búsqueda | D7, D10 |
| D7 | `notebooks/busqueda.ipynb` | Método, parámetros, parada, registro de configuraciones y análisis de fallos | D8 |
| D8 | Congelar la configuración ganadora | Domingo por la noche: no vuelve a cambiar | D9, S11, D10 |

### Lunes

| # | Tarea | Listo cuando | Desbloquea |
|---|---|---|---|
| D9 | Ejecutar `oraculo.validar` **una sola vez** y crear `entrega.json` | Resultado visible en el notebook; JSON válido | S11, D10 |
| D10 | Redactar `secciones/04_aproximados.tex` y `secciones/06_experimentos.tex` | Configuración, precisión, alternativas, límites y referencias a celdas | S13 |
| D11 | Escribir `docs/manual_tecnico.md` | Entorno, arquitectura, funcionamiento, uso, validación y límites | S14 |
| D12 | Revisar la reducción con Sebastián | Dylber la explica sola, sin notas | Sustentación |

---

## 5. Puntos que pueden bloquear al otro

| # | Punto de bloqueo | Quién lo causa | A quién detiene | Fecha límite | Si no llega a tiempo |
|---|---|---|---|---|---|
| 1 | Acceso al repositorio | Sebastián | Dylber | Sábado, primero | Dylber trabaja en una copia local y sube después |
| 2 | Notación y formatos | Los dos | Los dos | Sábado, antes de empezar | Se usa lo de la sección 2 sin más discusión |
| 3 | Contratos y `OraculoContado` | Sebastián | Dylber (D3) | Sábado al mediodía | Dylber programa contra `evaluar` y agrega el contador después |
| 4 | Velocidad medida | Sebastián | Dylber (D4, D5) | Sábado en la tarde | Dylber corre 1 arranque y mide en esa misma ejecución |
| 5 | Revisión de coordenadas | Sebastián | Dylber (D4) | Sábado en la tarde | Dylber corre igual y la corrección se aplica antes de D5 |
| 6 | Formalización | Dylber | Sebastián (S7) | Domingo temprano | Sebastián redacta con la notación acordada y se ajusta al final |
| 7 | Cuota de GPU o desconexión | Colab | Dylber (D4, D5) y Sebastián (S5) | Durante la corrida | Se sigue con la otra cuenta, usando el mismo caché en Drive |
| 8 | Configuración congelada | Dylber | Sebastián (S11, S13) y entrega | Domingo por la noche | Se usa la mejor hasta ese momento y se declara el límite |
| 9 | `entrega.json` definitivo | Dylber | Sebastián (S11, S14) | Lunes en la mañana | Sebastián prueba con el archivo de ejemplo y conecta al final |
| 10 | Secciones del informe | Los dos | Sebastián (S13) | Lunes 16:00 | Se integra lo que exista y se completa antes de las 20:00 |
| 11 | Manual técnico | Dylber | Sebastián (S14) | Lunes 18:00 | Se prueba con el README y el manual se cierra después |
| 12 | Identificador de grupo y semana | Los dos | Dylber (D9) | Antes de D9 | Se pregunta a la persona del grupo que lo conozca; no se inventa |

---

## 6. Reglas del fin de semana

- Hay dos revisiones de PR críticas: coordenadas y reducción. Máximo 2 horas de espera.
- Para el resto, si el otro no responde en 2 horas, se integra y se revisa después.
- Nadie espera en silencio: si algo se atrasa, se avisa de inmediato.
- `main` debe seguir funcionando. No se integra nada con pruebas fallidas.
- Después de congelar la configuración no se repite la validación ni se cambia la ganadora.
- No se usa `LIMPIA`, `PESADA`, los comentarios del catálogo ni los notebooks de solución.
- Cada uno debe poder explicar la reducción y la búsqueda sin notas.

---

## 7. Lista final antes de entregar

- [ ] `entrega.json` es válido y trae grupo y semana reales.
- [ ] La misma configuración aparece en `entrega.json` y en los dos notebooks.
- [ ] El notebook de evaluación corre sin editar nada.
- [ ] El notebook de búsqueda muestra método, registro, fallos, decisiones y `oraculo.validar`.
- [ ] El informe distingue "mejor encontrada" de "óptimo demostrado".
- [ ] La NP-dureza cubre solo la parte 1 y tiene ambas direcciones.
- [ ] El informe y el manual declaran lo no desarrollado.
- [ ] Un clon limpio ejecuta el ejemplo pequeño.
- [ ] El repositorio es accesible para la docente.
- [ ] El PDF del informe se compiló desde la versión final.
