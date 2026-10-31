"""Cuenta las generaciones nuevas de un oráculo y aplica el presupuesto B."""

from collections import Counter

from busqueda_prompt.contratos import PresupuestoAgotado, Resultado, clave_config


class OraculoContado:
    """Envuelve un oráculo sin tocar su interior.

    Una generación es nueva si (config, instancia, semilla) no se había pedido.
    Las repetidas no se cobran, igual que en el caché del oráculo real.
    `presupuesto=None` cuenta sin limitar.
    """

    def __init__(self, oraculo, presupuesto=None):
        if presupuesto is not None and presupuesto < 0:
            raise ValueError("el presupuesto no puede ser negativo")
        self.oraculo = oraculo
        self.presupuesto = presupuesto
        self.consultas = 0
        self.asignacion = Counter()
        self._vistas = set()

    def evaluar(self, config, instancias, semilla=1) -> Resultado:
        """Evalúa solo si todo el lote cabe en el presupuesto restante."""
        clave = clave_config(config)
        nuevas = {(clave, x["id"], semilla) for x in instancias} - self._vistas
        if self.presupuesto is not None and self.consultas + len(nuevas) > self.presupuesto:
            raise PresupuestoAgotado(
                f"faltan {self.consultas + len(nuevas) - self.presupuesto} consultas"
            )

        resultado = self.oraculo.evaluar(config, instancias, semilla)
        self._vistas |= nuevas
        self.consultas += len(nuevas)
        self.asignacion[clave] += len(nuevas)
        return resultado
