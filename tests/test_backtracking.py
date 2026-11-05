import pytest

from busqueda_prompt.algoritmos import backtracking, fuerza_bruta
from busqueda_prompt.contratos import PresupuestoAgotado, configuraciones
from busqueda_prompt.sintetico import OraculoSintetico, cota_estructural, generar


def _exacto_y_referencia(opciones, semilla, **kw):
    ranuras, oraculo, instancias = generar(opciones, semilla=semilla, **kw)
    bt = backtracking.resolver(oraculo, ranuras, opciones, instancias)
    fb = fuerza_bruta.resolver(oraculo, configuraciones(ranuras, opciones), instancias)
    return bt, fb


@pytest.mark.parametrize("semilla", range(30))
def test_coincide_con_fuerza_bruta(semilla):
    bt, fb = _exacto_y_referencia((3, 2, 3), semilla, n=12, reglas=6, conflictos=2)
    assert bt.ganadora == fb.ganadora
    assert bt.precision == fb.precision
    assert bt.consultas <= fb.consultas


@pytest.mark.parametrize("semilla", range(10))
def test_coincide_con_fuerza_bruta_con_ruido(semilla):
    bt, fb = _exacto_y_referencia((2, 3, 2), semilla, n=15, reglas=5, ruido=0.2)
    assert bt.ganadora == fb.ganadora
    assert bt.precision == fb.precision


@pytest.mark.parametrize("semilla", range(30))
def test_cota_estructural_conserva_la_ganadora(semilla):
    opciones = (3, 3, 2, 2)
    ranuras, oraculo, instancias = generar(opciones, n=15, reglas=8, semilla=semilla,
                                           reglas_por_instancia=3, densidad=0.2, conflictos=2)
    cota = cota_estructural(oraculo, ranuras, opciones, instancias)
    con_cota = backtracking.resolver(oraculo, ranuras, opciones, instancias, cota_parcial=cota)
    fb = fuerza_bruta.resolver(oraculo, configuraciones(ranuras, opciones), instancias)
    assert con_cota.ganadora == fb.ganadora
    assert con_cota.precision == fb.precision


@pytest.mark.parametrize("semilla", range(10))
def test_cota_estructural_es_cota_superior(semilla):
    opciones = (2, 3, 2)
    ranuras, oraculo, instancias = generar(opciones, n=10, reglas=6, semilla=semilla,
                                           conflictos=3)
    cota = cota_estructural(oraculo, ranuras, opciones, instancias)
    for config in configuraciones(ranuras, opciones):
        aciertos = round(oraculo.evaluar(config, instancias, 1).precision * len(instancias))
        for nivel in range(len(ranuras) + 1):
            parcial = {r: config[r] for r in ranuras[:nivel]}
            assert aciertos <= cota(parcial)


def test_cota_estructural_rechaza_ruido():
    ranuras, oraculo, instancias = generar((2, 2), n=3, reglas=2, semilla=1, ruido=0.1)
    with pytest.raises(ValueError):
        cota_estructural(oraculo, ranuras, (2, 2), instancias)


def test_peor_caso_gasta_c_por_n():
    # Ninguna configuración cumple nada: la cota D5 nunca alcanza a abandonar.
    oraculo = OraculoSintetico({})
    instancias = [{"id": i, "reglas": frozenset({0})} for i in range(7)]
    r = backtracking.resolver(oraculo, ("a", "b"), (3, 2), instancias)
    assert r.consultas == 6 * 7
    assert r.estadisticas["abandonos"] == 0


def test_mejor_caso_gasta_n():
    # La primera configuración cumple todo: las demás se abandonan sin consultar.
    oraculo = OraculoSintetico({("a", 0): frozenset({0})})
    instancias = [{"id": i, "reglas": frozenset({0})} for i in range(5)]
    r = backtracking.resolver(oraculo, ("a", "b"), (2, 3), instancias)
    assert r.precision == 1.0
    assert r.ganadora == {"a": 0, "b": 0, "temperatura": 0.0}
    assert r.consultas == 5
    assert r.estadisticas["abandonos"] == 5


def test_cuenta_nodos_del_arbol():
    oraculo = OraculoSintetico({})
    instancias = [{"id": 0, "reglas": frozenset()}]
    r = backtracking.resolver(oraculo, ("a", "b"), (2, 3), instancias)
    assert r.estadisticas["nodos"] == 1 + 2 + 6
    assert r.estadisticas["hojas"] == 6


def test_empate_gana_la_primera():
    oraculo = OraculoSintetico({})
    instancias = [{"id": 0, "reglas": frozenset({9})}]
    r = backtracking.resolver(oraculo, ("a",), (3,), instancias)
    assert r.ganadora == {"a": 0, "temperatura": 0.0}
    assert r.precision == 0.0


def test_reduccion_desde_3sat():
    from busqueda_prompt.sintetico import desde_3sat
    clausulas = [(1, 2, -3), (-1, -2, 3)]
    ranuras, oraculo, instancias = desde_3sat(clausulas, 3)
    r = backtracking.resolver(oraculo, ranuras, (2, 2, 2), instancias)
    assert r.precision == 1.0


def test_presupuesto_agotado():
    ranuras, oraculo, instancias = generar((2, 2), n=4, reglas=3, semilla=1)
    with pytest.raises(PresupuestoAgotado):
        backtracking.resolver(oraculo, ranuras, (2, 2), instancias, presupuesto=2)


def test_entradas_invalidas():
    oraculo = OraculoSintetico({})
    with pytest.raises(ValueError):
        backtracking.resolver(oraculo, ("a",), (2,), [])
    with pytest.raises(ValueError):
        backtracking.resolver(oraculo, ("a", "b"), (2,), [{"id": 0, "reglas": frozenset()}])
