"""Búsqueda por coordenadas: mejora una ranura a la vez, con varios arranques.

Cada arranque parte de una config al azar. En una pasada recorre las ranuras y,
para cada una, prueba las demás opciones dejando fijo el resto; solo cambia si
la precisión sube estrictamente, así que nunca baja. Termina cuando una pasada
no mejora nada (óptimo local por ranura) o al llegar a `max_pasadas`.
"""

import csv
import os
import random

from busqueda_prompt.contado import OraculoContado
from busqueda_prompt.contratos import PresupuestoAgotado, ResultadoBusqueda, clave_config

COLUMNAS = ("paso", "arranque", "ranura", "opcion", "config", "precision",
            "mejor_precision", "consultas", "decision")


class _Registro:
    """Guarda cada paso en memoria y, si hay ruta, en CSV (se vacía en cada fila)."""

    def __init__(self, ruta, filas, mostrar=None):
        self.filas = filas
        self.mostrar = mostrar
        self.paso = 0
        self._archivo = None
        if ruta:
            nuevo = not os.path.exists(ruta) or os.path.getsize(ruta) == 0
            self._archivo = open(ruta, "a", newline="", encoding="utf-8")
            self._csv = csv.DictWriter(self._archivo, fieldnames=COLUMNAS)
            if nuevo:
                self._csv.writeheader()

    def anotar(self, **campos):
        self.paso += 1
        fila = {"paso": self.paso, **campos}
        self.filas.append(fila)
        if self._archivo:
            self._csv.writerow(fila)
            self._archivo.flush()
        if self.mostrar:
            self.mostrar(fila)

    def cerrar(self):
        if self._archivo:
            self._archivo.close()


def resolver(oraculo, ranuras, opciones, instancias, semilla=1, presupuesto=None,
             arranques=1, max_pasadas=2, temperatura=0.0, semilla_busqueda=0,
             orden_ranuras=None, historial=None, ruta_historial=None, mostrar=None):
    """Devuelve la mejor config hallada entre todos los arranques.

    `historial` (lista) recibe una fila por evaluación con las columnas de
    `COLUMNAS`; `ruta_historial` las agrega además a un CSV. `mostrar` es un
    callable opcional que recibe cada fila (por ejemplo `print`). Si el
    presupuesto se agota, devuelve lo mejor visto hasta ese momento.
    """
    if arranques < 1 or max_pasadas < 1:
        raise ValueError("arranques y max_pasadas deben ser al menos 1")
    if len(ranuras) != len(opciones):
        raise ValueError("ranuras y opciones deben tener la misma longitud")
    orden = list(orden_ranuras) if orden_ranuras is not None else list(ranuras)
    if sorted(orden) != sorted(ranuras):
        raise ValueError("orden_ranuras debe ser una permutación de ranuras")
    tam = dict(zip(ranuras, opciones))

    contado = OraculoContado(oraculo, presupuesto)
    registro = _Registro(ruta_historial, historial if historial is not None else [], mostrar)
    mejor_global = None  # (precision, config)

    def evaluar(config):
        return contado.evaluar(config, instancias, semilla).precision

    try:
        for a in range(arranques):
            rng = random.Random(f"{semilla_busqueda}|{a}")
            actual = {r: rng.randrange(tam[r]) for r in ranuras} | {"temperatura": temperatura}
            p_actual = evaluar(actual)
            registro.anotar(arranque=a, ranura="", opcion="", config=clave_config(actual),
                            precision=p_actual, mejor_precision=p_actual,
                            consultas=contado.consultas, decision="inicio")
            if mejor_global is None or p_actual > mejor_global[0]:
                mejor_global = (p_actual, dict(actual))

            for _ in range(max_pasadas):
                mejoro = False
                for ranura in orden:
                    for opcion in range(tam[ranura]):
                        if opcion == actual[ranura]:
                            continue
                        candidata = dict(actual, **{ranura: opcion})
                        p = evaluar(candidata)
                        acepta = p > p_actual
                        if acepta:
                            actual, p_actual, mejoro = candidata, p, True
                            if p > mejor_global[0]:
                                mejor_global = (p, dict(actual))
                        registro.anotar(
                            arranque=a, ranura=ranura, opcion=opcion,
                            config=clave_config(candidata), precision=p,
                            mejor_precision=p_actual, consultas=contado.consultas,
                            decision="acepta" if acepta else "descarta")
                if not mejoro:
                    break
    except PresupuestoAgotado:
        pass
    finally:
        registro.cerrar()

    if mejor_global is None:
        raise PresupuestoAgotado("el presupuesto no alcanza ni para la primera evaluación")
    return ResultadoBusqueda(mejor_global[1], mejor_global[0], contado.consultas,
                             dict(contado.asignacion))
