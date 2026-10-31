"""Lectura y validación de `entrega.json` y de los datos de evaluación."""

import json

from busqueda_prompt.contratos import OPCIONES_POR_RANURA, RANURAS, TEMPERATURAS


def validar_entrega(entrega):
    """Lanza ValueError si `entrega.json` no cumple el formato del proyecto."""
    faltan = {"grupo", "config", "semana"} - set(entrega)
    if faltan:
        raise ValueError(f"faltan campos: {sorted(faltan)}")
    if not isinstance(entrega["grupo"], str) or not entrega["grupo"]:
        raise ValueError("grupo debe ser un texto no vacío")
    semana = entrega["semana"]
    if not isinstance(semana, int) or isinstance(semana, bool) or semana <= 0:
        raise ValueError("semana debe ser un entero positivo")

    config = entrega["config"]
    esperadas = {*RANURAS, "temperatura"}
    if not isinstance(config, dict) or set(config) != esperadas:
        raise ValueError(f"config debe traer exactamente {sorted(esperadas)}")
    for ranura in RANURAS:
        indice = config[ranura]
        if not isinstance(indice, int) or isinstance(indice, bool):
            raise ValueError(f"{ranura} debe ser un entero")
        if not 0 <= indice < OPCIONES_POR_RANURA:
            raise ValueError(f"{ranura} fuera de rango: {indice}")
    if config["temperatura"] not in TEMPERATURAS:
        raise ValueError(f"temperatura no admitida: {config['temperatura']}")
    return entrega


def cargar_entrega(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        return validar_entrega(json.load(archivo))


def cargar_instancias(ruta):
    """Lee una lista JSON de instancias, con el formato de `datos_visibles.json`."""
    with open(ruta, encoding="utf-8") as archivo:
        instancias = json.load(archivo)
    if not isinstance(instancias, list) or not instancias:
        raise ValueError("el archivo debe traer una lista de instancias")
    for campo in ("id", "prompt", "ids", "kwargs"):
        if any(campo not in x for x in instancias):
            raise ValueError(f"hay instancias sin el campo {campo!r}")
    return instancias
