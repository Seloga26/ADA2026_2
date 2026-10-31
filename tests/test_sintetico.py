import itertools
import random

import pytest

from busqueda_prompt.contratos import configuraciones
from busqueda_prompt.sintetico import OraculoSintetico, desde_3sat, generar


def test_misma_semilla_mismo_resultado():
    a = generar((3, 3), n=10, reglas=5, semilla=7, conflictos=2, ruido=0.2)
    b = generar((3, 3), n=10, reglas=5, semilla=7, conflictos=2, ruido=0.2)
    assert a[2] == b[2]
    for config in configuraciones(a[0], (3, 3)):
        assert a[1].evaluar(config, a[2], 1) == b[1].evaluar(config, b[2], 1)


def test_cumple_si_cubre_todas_las_reglas():
    oraculo = OraculoSintetico({("a", 0): frozenset({1}), ("b", 0): frozenset({2})})
    instancias = [{"id": 0, "reglas": frozenset({1, 2})}, {"id": 1, "reglas": frozenset({3})}]
    r = oraculo.evaluar({"a": 0, "b": 0, "temperatura": 0.0}, instancias, 1)
    assert r.precision == 0.5
    assert r.trazas == [{"id": 1, "violo": "regla:3", "salida": ""}]
    assert r.n == 2


def test_conflicto_anula_reglas():
    oraculo = OraculoSintetico(
        {("a", 0): frozenset({1}), ("b", 0): frozenset({2})},
        conflictos=[(("a", 0), ("b", 0), frozenset({1}))],
    )
    instancias = [{"id": 0, "reglas": frozenset({1})}]
    assert oraculo.evaluar({"a": 0, "b": 0}, instancias, 1).precision == 0.0
    assert oraculo.evaluar({"a": 0}, instancias, 1).precision == 1.0


def test_ruido_total_invierte_todo():
    oraculo = OraculoSintetico({("a", 0): frozenset({1})}, ruido=1.0)
    instancias = [{"id": 0, "reglas": frozenset({1})}]
    r = oraculo.evaluar({"a": 0}, instancias, 1)
    assert r.precision == 0.0
    assert r.trazas[0]["violo"] == "ruido"


@pytest.mark.parametrize(
    "parametros",
    [
        {"opciones": (0, 2), "n": 1, "reglas": 1},
        {"opciones": (), "n": 1, "reglas": 1},
        {"opciones": (2,), "n": 0, "reglas": 1},
        {"opciones": (2,), "n": 1, "reglas": 0},
    ],
)
def test_generar_rechaza_parametros_invalidos(parametros):
    with pytest.raises(ValueError):
        generar(semilla=1, **parametros)


def test_ruido_invalido():
    with pytest.raises(ValueError):
        OraculoSintetico({}, ruido=1.5)


def _satisfacible(clausulas, variables):
    for valores in itertools.product((False, True), repeat=variables):
        if all(any(valores[abs(l) - 1] == (l > 0) for l in c) for c in clausulas):
            return True
    return False


def _formula(rng):
    variables = rng.randint(3, 6)
    clausulas = []
    for _ in range(rng.randint(1, 16)):
        elegidas = rng.sample(range(1, variables + 1), 3)
        clausulas.append([v if rng.random() < 0.5 else -v for v in elegidas])
    return clausulas, variables


def test_reduccion_acc_1_si_y_solo_si_satisfacible():
    rng = random.Random(1)
    resultados = set()
    for _ in range(300):
        clausulas, variables = _formula(rng)
        ranuras, oraculo, instancias = desde_3sat(clausulas, variables)
        mejor = max(
            oraculo.evaluar(c, instancias, 1).precision
            for c in configuraciones(ranuras, [2] * variables)
        )
        esperado = _satisfacible(clausulas, variables)
        assert (mejor == 1.0) == esperado
        resultados.add(esperado)
    assert resultados == {True, False}


def test_reduccion_formula_insatisfacible_conocida():
    clausulas = [
        [a * 1, b * 2, c * 3]
        for a, b, c in itertools.product((1, -1), repeat=3)
    ]
    ranuras, oraculo, instancias = desde_3sat(clausulas, 3)
    precisiones = [
        oraculo.evaluar(c, instancias, 1).precision
        for c in configuraciones(ranuras, [2] * 3)
    ]
    assert max(precisiones) == pytest.approx(7 / 8)
