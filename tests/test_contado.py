import pytest

from busqueda_prompt.contado import OraculoContado
from busqueda_prompt.contratos import PresupuestoAgotado
from busqueda_prompt.sintetico import generar


@pytest.fixture
def caso():
    ranuras, oraculo, instancias = generar((2, 2), n=4, reglas=3, semilla=1)
    return dict.fromkeys(ranuras, 0) | {"temperatura": 0.0}, oraculo, instancias


def test_cuenta_generaciones_nuevas(caso):
    config, oraculo, instancias = caso
    contado = OraculoContado(oraculo)
    contado.evaluar(config, instancias, 1)
    assert contado.consultas == 4


def test_no_cobra_lo_repetido(caso):
    config, oraculo, instancias = caso
    contado = OraculoContado(oraculo)
    contado.evaluar(config, instancias[:2], 1)
    contado.evaluar(config, instancias, 1)
    assert contado.consultas == 4


def test_orden_de_llaves_no_cambia_la_cuenta(caso):
    config, oraculo, instancias = caso
    contado = OraculoContado(oraculo)
    contado.evaluar(config, instancias, 1)
    contado.evaluar(dict(reversed(list(config.items()))), instancias, 1)
    assert contado.consultas == 4


def test_otra_semilla_si_se_cobra(caso):
    config, oraculo, instancias = caso
    contado = OraculoContado(oraculo)
    contado.evaluar(config, instancias, 1)
    contado.evaluar(config, instancias, 2)
    assert contado.consultas == 8


def test_presupuesto_exacto_se_permite(caso):
    config, oraculo, instancias = caso
    contado = OraculoContado(oraculo, presupuesto=4)
    contado.evaluar(config, instancias, 1)
    assert contado.consultas == 4


def test_presupuesto_agotado_no_consulta_ni_cobra(caso):
    config, oraculo, instancias = caso
    contado = OraculoContado(oraculo, presupuesto=3)
    with pytest.raises(PresupuestoAgotado):
        contado.evaluar(config, instancias, 1)
    assert contado.consultas == 0


def test_asignacion_registra_m_j(caso):
    config, oraculo, instancias = caso
    otra = config | {"temperatura": 0.3}
    contado = OraculoContado(oraculo)
    contado.evaluar(config, instancias, 1)
    contado.evaluar(otra, instancias[:1], 1)
    assert sorted(contado.asignacion.values()) == [1, 4]


def test_presupuesto_negativo_es_invalido(caso):
    with pytest.raises(ValueError):
        OraculoContado(caso[1], presupuesto=-1)
