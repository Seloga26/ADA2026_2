"""Contratos compartidos por los oráculos y los algoritmos.

No importa `oraculo.py`: ese módulo necesita `torch` y solo corre en Colab.
"""

import itertools
import json
from dataclasses import dataclass, field
from typing import Protocol

RANURAS = ("rol", "estrategia", "formato", "estilo", "cierre")
OPCIONES_POR_RANURA = 8
TEMPERATURAS = (0.0, 0.3, 0.7)

Config = dict
Instancia = dict


class PresupuestoAgotado(Exception):
    """Una consulta superaría el presupuesto B."""


@dataclass
class Resultado:
    """Mismos campos que el resultado del oráculo real."""

    precision: float
    trazas: list
    n: int


@dataclass
class ResultadoBusqueda:
    """Salida común de los algoritmos: ganadora, precisión y consultas m_j."""

    ganadora: Config
    precision: float
    consultas: int
    asignacion: dict = field(default_factory=dict)


class Oraculo(Protocol):
    def evaluar(self, config: Config, instancias: list, semilla: int) -> Resultado: ...


def clave_config(config: Config) -> str:
    """Texto estable de una config: no depende del orden de sus llaves."""
    return json.dumps(config, sort_keys=True)


def configuraciones(ranuras, opciones, temperatura=0.0):
    """Recorre el producto cartesiano de opciones, en orden lexicográfico."""
    for combo in itertools.product(*(range(k) for k in opciones)):
        yield dict(zip(ranuras, combo), temperatura=temperatura)
