"""Barridos del exacto con el oráculo sintético (D7, D10).

Uso: `uv run python -m busqueda_prompt.experimentos.medir`

Escribe en `resultados/exacto/`:
- `barrido_n.csv`: |C| = 256 fijo (4 ranuras de 4 opciones), n en {10, 25, 50, 75, 100}.
- `barrido_c.csv`: n = 50 fijo, |C| = 2^L con L de 4 a 10 (2 opciones por ranura).
- `ajuste.json`: pendientes del ajuste log-log de las generaciones frente a n y a |C|.

Cada punto promedia 5 semillas. Las columnas de generaciones son las nuevas que cuenta
`OraculoContado` (D11); `peor` es el peor caso |C|·n, que alcanza un oráculo sin aciertos.
Los tiempos son de pared, en segundos, y dependen de la máquina.
"""

import csv
import json
import math
import os
import time

from busqueda_prompt.algoritmos import backtracking, fuerza_bruta
from busqueda_prompt.contratos import configuraciones
from busqueda_prompt.sintetico import OraculoSintetico, cota_estructural, generar

SEMILLAS = (1, 2, 3, 4, 5)
TAMANOS_N = (10, 25, 50, 75, 100)
OPCIONES_FIJAS = (4, 4, 4, 4)
N_FIJO = 50
RANURAS_L = (4, 5, 6, 7, 8, 9, 10)
PARAMETROS = {"reglas": 12, "reglas_por_instancia": 3, "densidad": 0.2, "conflictos": 3}
COLUMNAS = ("fuerza_bruta", "backtracking", "backtracking_estructural", "peor",
            "nodos_bt", "abandonos_bt", "nodos_est", "podas_est", "segundos_bt")
SALIDA = os.path.join("resultados", "exacto")


def _medir_punto(opciones, n):
    """Promedio sobre las semillas de un tamaño (|C|, n)."""
    tamano_c = math.prod(opciones)
    suma = dict.fromkeys(COLUMNAS, 0.0)
    for semilla in SEMILLAS:
        ranuras, oraculo, instancias = generar(opciones, n=n, semilla=semilla, **PARAMETROS)
        fb = fuerza_bruta.resolver(oraculo, configuraciones(ranuras, opciones), instancias)
        inicio = time.perf_counter()
        bt = backtracking.resolver(oraculo, ranuras, opciones, instancias)
        segundos = time.perf_counter() - inicio
        cota = cota_estructural(oraculo, ranuras, opciones, instancias)
        est = backtracking.resolver(oraculo, ranuras, opciones, instancias, cota_parcial=cota)
        if not (bt.ganadora == est.ganadora == fb.ganadora):
            raise AssertionError(f"el exacto no coincide con la fuerza bruta (semilla {semilla})")
        vacio = OraculoSintetico({})
        peor = backtracking.resolver(vacio, ranuras, opciones, instancias).consultas
        for columna, valor in (
            ("fuerza_bruta", fb.consultas), ("backtracking", bt.consultas),
            ("backtracking_estructural", est.consultas), ("peor", peor),
            ("nodos_bt", bt.estadisticas["nodos"]), ("abandonos_bt", bt.estadisticas["abandonos"]),
            ("nodos_est", est.estadisticas["nodos"]), ("podas_est", est.estadisticas["podas_parciales"]),
            ("segundos_bt", segundos),
        ):
            suma[columna] += valor
    fila = {"C": tamano_c, "n": n}
    fila.update({c: round(v / len(SEMILLAS), 4) for c, v in suma.items()})
    return fila


def _pendiente(xs, ys):
    """Pendiente por mínimos cuadrados de log10(y) frente a log10(x)."""
    lx = [math.log10(x) for x in xs]
    ly = [math.log10(y) for y in ys]
    mx, my = sum(lx) / len(lx), sum(ly) / len(ly)
    return sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)


def _escribir(ruta, filas):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    barrido_n = [_medir_punto(OPCIONES_FIJAS, n) for n in TAMANOS_N]
    barrido_c = [_medir_punto((2,) * L, N_FIJO) for L in RANURAS_L]
    _escribir(os.path.join(SALIDA, "barrido_n.csv"), barrido_n)
    _escribir(os.path.join(SALIDA, "barrido_c.csv"), barrido_c)

    ajuste = {"semillas": list(SEMILLAS), "parametros": PARAMETROS}
    for nombre, filas, eje in (("frente_a_n", barrido_n, "n"), ("frente_a_C", barrido_c, "C")):
        xs = [f[eje] for f in filas]
        ajuste[nombre] = {
            c: round(_pendiente(xs, [f[c] for f in filas]), 3)
            for c in ("fuerza_bruta", "backtracking", "backtracking_estructural", "peor")
        }
    with open(os.path.join(SALIDA, "ajuste.json"), "w", encoding="utf-8") as f:
        json.dump(ajuste, f, indent=1)
        f.write("\n")

    for nombre, filas in (("barrido_n", barrido_n), ("barrido_c", barrido_c)):
        print(nombre)
        for fila in filas:
            print("  ", fila)
    print(json.dumps(ajuste, indent=1))


if __name__ == "__main__":
    main()
