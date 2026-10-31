import json

import pytest

from busqueda_prompt.entrega import cargar_entrega, cargar_instancias, validar_entrega


def entrega_valida():
    config = {"rol": 0, "estrategia": 1, "formato": 2, "estilo": 3, "cierre": 7, "temperatura": 0.0}
    return {"grupo": "G00", "config": config, "semana": 1}


def test_acepta_entrega_valida():
    assert validar_entrega(entrega_valida())


@pytest.mark.parametrize(
    "cambio",
    [
        {"grupo": ""},
        {"grupo": 1},
        {"semana": 0},
        {"semana": "3"},
        {"semana": True},
    ],
)
def test_rechaza_campos_invalidos(cambio):
    with pytest.raises(ValueError):
        validar_entrega(entrega_valida() | cambio)


@pytest.mark.parametrize(
    "cambio",
    [{"rol": 8}, {"rol": -1}, {"rol": 1.0}, {"rol": True}, {"temperatura": 0.5}],
)
def test_rechaza_config_invalida(cambio):
    entrega = entrega_valida()
    entrega["config"] |= cambio
    with pytest.raises(ValueError):
        validar_entrega(entrega)


def test_rechaza_ranura_faltante():
    entrega = entrega_valida()
    del entrega["config"]["cierre"]
    with pytest.raises(ValueError):
        validar_entrega(entrega)


def test_rechaza_campo_faltante():
    entrega = entrega_valida()
    del entrega["semana"]
    with pytest.raises(ValueError):
        validar_entrega(entrega)


def test_cargar_entrega(tmp_path):
    ruta = tmp_path / "entrega.json"
    ruta.write_text(json.dumps(entrega_valida()), encoding="utf-8")
    assert cargar_entrega(ruta) == entrega_valida()


def test_datos_visibles_tienen_formato_de_instancias():
    assert len(cargar_instancias("datos_visibles.json")) == 450


def test_rechaza_instancias_sin_campos(tmp_path):
    ruta = tmp_path / "datos.json"
    ruta.write_text(json.dumps([{"id": 1}]), encoding="utf-8")
    with pytest.raises(ValueError):
        cargar_instancias(ruta)
