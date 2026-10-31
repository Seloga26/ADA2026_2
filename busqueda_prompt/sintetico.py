"""Oráculo sintético: mismo contrato que el real, sin modelo ni GPU."""

import hashlib
import random

from busqueda_prompt.contratos import Resultado, clave_config


class OraculoSintetico:
    """Una instancia se cumple si la config cubre todas sus reglas.

    `reglas_por_opcion` mapea (ranura, opción) a las reglas que satisface.
    `conflictos` lista (opción_a, opción_b, reglas): si la config elige ambas
    opciones, esas reglas dejan de contar. Con `ruido`, el resultado se invierte
    con esa probabilidad, de forma determinista por (semilla, config, instancia).
    """

    def __init__(self, reglas_por_opcion, conflictos=(), ruido=0.0, semilla_ruido=0):
        if not 0.0 <= ruido <= 1.0:
            raise ValueError("el ruido debe estar entre 0 y 1")
        self.reglas_por_opcion = reglas_por_opcion
        self.conflictos = tuple(conflictos)
        self.ruido = ruido
        self.semilla_ruido = semilla_ruido

    def _cubiertas(self, config):
        elegidas = {(r, o) for r, o in config.items() if r != "temperatura"}
        cubiertas = set()
        for opcion in elegidas:
            cubiertas |= self.reglas_por_opcion.get(opcion, frozenset())
        for a, b, reglas in self.conflictos:
            if a in elegidas and b in elegidas:
                cubiertas -= reglas
        return cubiertas

    def _invierte(self, config, instancia_id, semilla):
        if self.ruido == 0.0:
            return False
        texto = f"{self.semilla_ruido}|{semilla}|{clave_config(config)}|{instancia_id}"
        huella = hashlib.sha256(texto.encode()).digest()
        return int.from_bytes(huella[:8], "big") / 2**64 < self.ruido

    def evaluar(self, config, instancias, semilla=1) -> Resultado:
        cubiertas = self._cubiertas(config)
        aciertos = 0
        trazas = []
        for x in instancias:
            faltan = sorted(x["reglas"] - cubiertas)
            exito = not faltan
            if self._invierte(config, x["id"], semilla):
                exito = not exito
            if exito:
                aciertos += 1
            else:
                violo = f"regla:{faltan[0]}" if faltan else "ruido"
                trazas.append({"id": x["id"], "violo": violo, "salida": ""})
        return Resultado(aciertos / len(instancias), trazas, len(instancias))


def generar(opciones, n, reglas, semilla, reglas_por_instancia=2, densidad=0.3,
            conflictos=0, ruido=0.0):
    """Crea (ranuras, oráculo, instancias) reproducibles para una semilla."""
    if n <= 0 or reglas <= 0 or not opciones or min(opciones) <= 0:
        raise ValueError("opciones, n y reglas deben ser positivos")
    rng = random.Random(semilla)
    ranuras = tuple(f"r{i}" for i in range(len(opciones)))
    universo = range(reglas)
    reglas_por_opcion = {
        (r, o): frozenset(x for x in universo if rng.random() < densidad)
        for r, k in zip(ranuras, opciones)
        for o in range(k)
    }
    lista_conflictos = []
    if len(ranuras) >= 2:
        for _ in range(conflictos):
            r_a, r_b = rng.sample(ranuras, 2)
            a = (r_a, rng.randrange(opciones[ranuras.index(r_a)]))
            b = (r_b, rng.randrange(opciones[ranuras.index(r_b)]))
            lista_conflictos.append((a, b, frozenset(rng.sample(universo, 1))))
    tamano = min(reglas_por_instancia, reglas)
    instancias = [
        {"id": i, "reglas": frozenset(rng.sample(universo, tamano))} for i in range(n)
    ]
    oraculo = OraculoSintetico(reglas_por_opcion, lista_conflictos, ruido, semilla)
    return ranuras, oraculo, instancias


def desde_3sat(clausulas, variables):
    """Construcción de la reducción: cláusulas con literales ±i, de 1 a `variables`.

    Cada variable es una categoría con opciones 0 (falso) y 1 (verdadero). Cada
    cláusula es una instancia que exige su regla. Devuelve (ranuras, oráculo,
    instancias).
    """
    ranuras = tuple(f"x{i}" for i in range(1, variables + 1))
    reglas_por_opcion = {}
    for i, ranura in enumerate(ranuras, start=1):
        for opcion, signo in ((0, -1), (1, 1)):
            reglas_por_opcion[(ranura, opcion)] = frozenset(
                j for j, clausula in enumerate(clausulas) if signo * i in clausula
            )
    instancias = [{"id": j, "reglas": frozenset({j})} for j in range(len(clausulas))]
    return ranuras, OraculoSintetico(reglas_por_opcion), instancias
