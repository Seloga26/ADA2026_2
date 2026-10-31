import csv

import pytest

from busqueda_prompt.algoritmos import coordenadas, fuerza_bruta
from busqueda_prompt.contratos import PresupuestoAgotado, configuraciones
from busqueda_prompt.sintetico import generar

OPCIONES = (4, 3, 3)


def _caso(semilla, **kw):
    return generar(OPCIONES, n=12, reglas=6, semilla=semilla, **kw)


@pytest.mark.parametrize("semilla", range(15))
def test_la_precision_nunca_baja_y_no_supera_al_optimo(semilla):
    ranuras, oraculo, instancias = _caso(semilla, conflictos=2)
    hist = []
    r = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, arranques=2,
                             max_pasadas=3, historial=hist)
    for a in (0, 1):
        previos = [f["mejor_precision"] for f in hist if f["arranque"] == a]
        assert previos == sorted(previos)
    exacto = fuerza_bruta.resolver(oraculo, configuraciones(ranuras, OPCIONES), instancias)
    assert r.precision <= exacto.precision


def test_una_pasada_cuesta_a_lo_sumo_lo_esperado():
    ranuras, oraculo, instancias = _caso(3)
    r = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, max_pasadas=1)
    por_pasada = sum(k - 1 for k in OPCIONES)
    assert r.consultas <= (1 + por_pasada) * len(instancias)


def test_respeta_el_presupuesto():
    ranuras, oraculo, instancias = _caso(4)
    tope = 5 * len(instancias)
    r = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, presupuesto=tope,
                             arranques=3, max_pasadas=3)
    assert r.consultas <= tope


def test_presupuesto_que_no_alcanza_para_empezar():
    ranuras, oraculo, instancias = _caso(5)
    with pytest.raises(PresupuestoAgotado):
        coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, presupuesto=1)


def test_es_reproducible():
    ranuras, oraculo, instancias = _caso(6, conflictos=1)
    a = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, arranques=2)
    b = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, arranques=2)
    assert (a.ganadora, a.precision, a.consultas) == (b.ganadora, b.precision, b.consultas)


def test_varios_arranques_no_empeoran():
    ranuras, oraculo, instancias = _caso(7, conflictos=3)
    uno = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, arranques=1)
    cinco = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, arranques=5)
    assert cinco.precision >= uno.precision


def test_escribe_el_csv_con_las_columnas_acordadas(tmp_path):
    ranuras, oraculo, instancias = _caso(8)
    ruta = tmp_path / "historial.csv"
    coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, ruta_historial=str(ruta))
    with open(ruta, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    assert tuple(filas[0]) == coordenadas.COLUMNAS
    assert filas[0]["decision"] == "inicio"
    assert {f["decision"] for f in filas} <= {"inicio", "acepta", "descarta"}


def test_orden_invalido():
    ranuras, oraculo, instancias = _caso(9)
    with pytest.raises(ValueError):
        coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, orden_ranuras=["x"])
