import csv  # para leer de vuelta el CSV que escribe el algoritmo

import pytest  # framework de pruebas: aporta raises, parametrize y la fixture tmp_path

from busqueda_prompt.algoritmos import coordenadas, fuerza_bruta  # algoritmo a probar y el exacto de referencia
from busqueda_prompt.contratos import PresupuestoAgotado, configuraciones  # excepción esperada y generador de todas las configs
from busqueda_prompt.sintetico import generar  # crea oráculo sintético e instancias reproducibles

OPCIONES = (4, 3, 3)  # 3 ranuras con 4, 3 y 3 opciones: 36 configs, espacio pequeño que la fuerza bruta recorre al instante


def _caso(semilla, **kw):  # ayudante (el "_" indica uso interno); **kw reenvía opciones como conflictos=2
    # n=12 instancias y 6 reglas posibles; la semilla fija el problema, así que cada prueba es reproducible
    return generar(OPCIONES, n=12, reglas=6, semilla=semilla, **kw)  # devuelve (ranuras, oraculo, instancias)


@pytest.mark.parametrize("semilla", range(15))  # ejecuta la prueba 15 veces, con semilla = 0..14
def test_la_precision_nunca_baja_y_no_supera_al_optimo(semilla):
    ranuras, oraculo, instancias = _caso(semilla, conflictos=2)  # desempaqueta la tupla; conflictos hacen el problema más difícil
    hist = []  # lista donde el algoritmo anotará cada paso
    r = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, arranques=2,
                             max_pasadas=3, historial=hist)  # 2 arranques y hasta 3 pasadas cada uno
    for a in (0, 1):  # revisa cada arranque por separado
        previos = [f["mejor_precision"] for f in hist if f["arranque"] == a]  # sucesión de mejores precisiones de ese arranque
        assert previos == sorted(previos)  # si ya está ordenada de menor a mayor, nunca bajó
    exacto = fuerza_bruta.resolver(oraculo, configuraciones(ranuras, OPCIONES), instancias)  # óptimo real, probando las 36 configs
    assert r.precision <= exacto.precision  # un método aproximado jamás puede superar al óptimo


def test_una_pasada_cuesta_a_lo_sumo_lo_esperado():
    ranuras, oraculo, instancias = _caso(3)
    r = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, max_pasadas=1)  # una sola pasada
    por_pasada = sum(k - 1 for k in OPCIONES)  # por ranura se prueban k-1 opciones (la actual ya se midió): 3+2+2 = 7
    assert r.consultas <= (1 + por_pasada) * len(instancias)  # 1 config inicial + 7 candidatas, cada una sobre n instancias


def test_respeta_el_presupuesto():
    ranuras, oraculo, instancias = _caso(4)
    tope = 5 * len(instancias)  # presupuesto de solo 5 configs completas, muy por debajo de lo que pediría la búsqueda
    r = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, presupuesto=tope,
                             arranques=3, max_pasadas=3)  # pide mucho más de lo que cabe
    assert r.consultas <= tope  # al agotarse devuelve lo mejor visto sin pasarse del tope


def test_presupuesto_que_no_alcanza_para_empezar():
    ranuras, oraculo, instancias = _caso(5)
    with pytest.raises(PresupuestoAgotado):  # la prueba pasa solo si dentro del bloque se lanza esta excepción
        coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, presupuesto=1)  # 1 consulta no alcanza ni para la config inicial


def test_es_reproducible():
    ranuras, oraculo, instancias = _caso(6, conflictos=1)
    a = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, arranques=2)  # primera ejecución
    b = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, arranques=2)  # segunda, con los mismos argumentos
    assert (a.ganadora, a.precision, a.consultas) == (b.ganadora, b.precision, b.consultas)  # misma semilla, mismo resultado


def test_varios_arranques_no_empeoran():
    ranuras, oraculo, instancias = _caso(7, conflictos=3)
    uno = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, arranques=1)  # un solo arranque
    cinco = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, arranques=5)  # incluye el arranque 0, igual al anterior
    assert cinco.precision >= uno.precision  # más arranques solo pueden dejar igual o mejorar la mejor global


def test_escribe_el_csv_con_las_columnas_acordadas(tmp_path):  # tmp_path: carpeta temporal que pytest crea y borra sola
    ranuras, oraculo, instancias = _caso(8)
    ruta = tmp_path / "historial.csv"  # el operador "/" une rutas en pathlib
    coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, ruta_historial=str(ruta))  # str(...) porque el algoritmo espera texto
    with open(ruta, encoding="utf-8") as f:  # "with" cierra el archivo al salir del bloque
        filas = list(csv.DictReader(f))  # cada línea se vuelve un diccionario {columna: valor}
    assert tuple(filas[0]) == coordenadas.COLUMNAS  # las llaves de la primera fila son las columnas, en el orden acordado
    assert filas[0]["decision"] == "inicio"  # la primera fila registrada es siempre la config de partida
    assert {f["decision"] for f in filas} <= {"inicio", "acepta", "descarta"}  # conjunto de decisiones contenido en las permitidas (<= es subconjunto)


def test_orden_invalido():
    ranuras, oraculo, instancias = _caso(9)
    with pytest.raises(ValueError):  # se espera un ValueError por validación de argumentos
        coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, orden_ranuras=["x"])  # "x" no es una ranura, no es permutación


def test_las_opciones_excluidas_nunca_se_evaluan():  # las excluidas no aparecen ni al arrancar ni al probar candidatas
    ranuras, oraculo, instancias = _caso(10, conflictos=2)
    excl = {ranuras[0]: {0, 1}, ranuras[2]: {2}}  # dos opciones de la primera ranura y una de la tercera
    hist = []
    r = coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, arranques=3,
                             opciones_excluidas=excl, historial=hist)
    for fila in hist:  # revisa cada config evaluada
        if fila["config"]:  # las filas de decisión no traen config
            import json  # la config está guardada como texto JSON
            c = json.loads(fila["config"])
            for ranura, malas in excl.items():
                assert c[ranura] not in malas  # ninguna config usa una opción excluida
    for ranura, malas in excl.items():
        assert r.ganadora[ranura] not in malas  # la ganadora tampoco


def test_excluir_todas_las_opciones_de_una_ranura_falla():
    ranuras, oraculo, instancias = _caso(11)
    with pytest.raises(ValueError):
        coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias,
                             opciones_excluidas={ranuras[1]: {0, 1, 2}})  # la ranura 1 tiene 3 opciones: se excluyen todas


def test_excluir_una_ranura_desconocida_falla():
    ranuras, oraculo, instancias = _caso(12)
    with pytest.raises(ValueError):
        coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, opciones_excluidas={"zzz": {0}})


def test_el_motivo_queda_escrito_en_decision(tmp_path):
    ranuras, oraculo, instancias = _caso(13)
    ruta = tmp_path / "h.csv"
    coordenadas.resolver(oraculo, ranuras, OPCIONES, instancias, ruta_historial=str(ruta),
                         motivo="fallan las listas", orden_ranuras=list(reversed(ranuras)),
                         opciones_excluidas={ranuras[0]: {3}})
    with open(ruta, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    assert filas[0]["decision"].startswith("decide: fallan las listas")  # la decisión es la primera fila
    assert "excluidas=" in filas[0]["decision"] and "orden=" in filas[0]["decision"]  # y trae orden y exclusiones
    assert filas[1]["decision"] == "inicio"  # después viene el arranque normal
