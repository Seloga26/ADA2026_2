"""Backtracking con cota: algoritmo exacto sobre el contrato de `Oraculo`.

Recorre el árbol de configuraciones asignando una ranura por nivel, en el mismo orden
lexicográfico que `contratos.configuraciones`. En cada hoja evalúa la configuración
instancia por instancia y la abandona en cuanto sus aciertos más las instancias que
faltan no pueden superar a la mejor conocida (cota D5). Esa cota vale con cualquier
oráculo, porque una instancia aún no evaluada aporta a lo sumo un acierto.

`cota_parcial` es opcional: dada una asignación parcial, debe devolver una cota
superior de los aciertos de cualquier configuración que la complete. Solo se usa con el
modelo sintético, donde la estructura de reglas es conocida (D6); con el modelo real no
se poda con supuestos.

Devuelve la misma ganadora que `fuerza_bruta`: la primera del recorrido con la mayor
precisión. En el peor caso gasta |C|·n generaciones, igual que la fuerza bruta.
"""

from busqueda_prompt.contado import OraculoContado
from busqueda_prompt.contratos import ResultadoBusqueda


def resolver(oraculo, ranuras, opciones, instancias, semilla=1, presupuesto=None,
             cota_parcial=None, temperatura=0.0):
    if len(ranuras) != len(opciones) or not ranuras or min(opciones) <= 0:
        raise ValueError("cada ranura necesita al menos una opción")
    if not instancias:
        raise ValueError("no hay instancias para evaluar")

    contado = OraculoContado(oraculo, presupuesto)
    n = len(instancias)
    L = len(ranuras)
    estado = {"mejor": -1, "ganadora": None}
    est = {"nodos": 0, "hojas": 0, "podas_parciales": 0, "abandonos": 0}

    def evaluar_hoja(config):
        """Aciertos de `config`, o None si la cota D5 la descarta antes de terminar."""
        aciertos = 0
        for k, instancia in enumerate(instancias):
            if aciertos + (n - k) <= estado["mejor"]:
                est["abandonos"] += 1
                return None
            if contado.evaluar(config, [instancia], semilla).precision == 1.0:
                aciertos += 1
        return aciertos

    def explorar(nivel, parcial):
        est["nodos"] += 1
        if nivel == L:
            est["hojas"] += 1
            config = dict(parcial, temperatura=temperatura)
            aciertos = evaluar_hoja(config)
            if aciertos is not None and aciertos > estado["mejor"]:
                estado["mejor"] = aciertos
                estado["ganadora"] = config
            return
        if cota_parcial is not None and nivel > 0 and estado["mejor"] >= 0:
            if cota_parcial(parcial) <= estado["mejor"]:
                est["podas_parciales"] += 1
                return
        ranura = ranuras[nivel]
        for opcion in range(opciones[nivel]):
            parcial[ranura] = opcion
            explorar(nivel + 1, parcial)
            del parcial[ranura]

    explorar(0, {})
    return ResultadoBusqueda(
        estado["ganadora"],
        estado["mejor"] / n,
        contado.consultas,
        dict(contado.asignacion),
        est,
    )
