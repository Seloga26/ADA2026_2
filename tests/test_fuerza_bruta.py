import pytest

from busqueda_prompt.algoritmos import fuerza_bruta
from busqueda_prompt.contratos import PresupuestoAgotado, configuraciones
from busqueda_prompt.sintetico import OraculoSintetico, generar


def test_gasta_c_por_n_consultas():
    opciones = (2, 3, 2)
    ranuras, oraculo, instancias = generar(opciones, n=5, reglas=4, semilla=2)
    r = fuerza_bruta.resolver(oraculo, configuraciones(ranuras, opciones), instancias)
    assert r.consultas == 12 * 5
    assert len(r.asignacion) == 12


@pytest.mark.parametrize("semilla", range(20))
def test_ninguna_config_supera_a_la_ganadora(semilla):
    opciones = (3, 2, 2)
    ranuras, oraculo, instancias = generar(opciones, n=10, reglas=5, semilla=semilla, conflictos=2)
    r = fuerza_bruta.resolver(oraculo, configuraciones(ranuras, opciones), instancias)
    for config in configuraciones(ranuras, opciones):
        assert oraculo.evaluar(config, instancias, 1).precision <= r.precision


def test_espacio_de_una_sola_config():
    ranuras, oraculo, instancias = generar((1,), n=1, reglas=1, semilla=1)
    r = fuerza_bruta.resolver(oraculo, configuraciones(ranuras, (1,)), instancias)
    assert r.consultas == 1


def test_empate_gana_la_primera():
    oraculo = OraculoSintetico({})
    instancias = [{"id": 0, "reglas": frozenset({9})}]
    r = fuerza_bruta.resolver(oraculo, configuraciones(("a",), (3,)), instancias)
    assert r.precision == 0.0
    assert r.ganadora == {"a": 0, "temperatura": 0.0}


def test_presupuesto_menor_que_el_espacio():
    ranuras, oraculo, instancias = generar((2, 2), n=2, reglas=2, semilla=1)
    with pytest.raises(PresupuestoAgotado):
        fuerza_bruta.resolver(oraculo, configuraciones(ranuras, (2, 2)), instancias, presupuesto=3)


def test_sin_configs_es_error():
    with pytest.raises(ValueError):
        fuerza_bruta.resolver(OraculoSintetico({}), [], [{"id": 0, "reglas": frozenset()}])
