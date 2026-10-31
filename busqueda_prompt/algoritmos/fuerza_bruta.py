"""Fuerza bruta: referencia exacta para espacios pequeños."""

from busqueda_prompt.contratos import ResultadoBusqueda
from busqueda_prompt.contado import OraculoContado


def resolver(oraculo, configs, instancias, semilla=1, presupuesto=None):
    """Evalúa todas las configs. En un empate gana la primera del recorrido."""
    contado = OraculoContado(oraculo, presupuesto)
    ganadora = None
    mejor = -1.0
    for config in configs:
        precision = contado.evaluar(config, instancias, semilla).precision
        if precision > mejor:
            mejor = precision
            ganadora = config
    if ganadora is None:
        raise ValueError("no hay configuraciones para evaluar")
    return ResultadoBusqueda(ganadora, mejor, contado.consultas, dict(contado.asignacion))
