"""Resume los historiales de la busqueda por coordenadas.

Uso:
    python resumir.py HISTORIAL_ARRANQUE_0 HISTORIAL_ARRANQUE_1 \
        [--presupuesto B] [--esperado-cfg-0 N] [--esperado-cfg-1 N] \
        [--esperado-union N] [--esperado-generaciones N] [--top K]

Solo biblioteca estandar. Todo se reconstruye desde los CSV; no hay rutas ni
valores fijos. Si se pasa algun valor esperado y no coincide, sale con codigo 1.

Notas de lectura:
- Un CSV puede traer varias ejecuciones anexadas (por reanudaciones): cada una
  empieza con una fila de paso 1. Las configuraciones se cuentan sobre todas;
  las generaciones por configuracion se infieren de la ultima ejecucion.
- Las generaciones por configuracion (instancias) se infieren como
  consultas finales / configuraciones distintas de la ultima ejecucion.
- La pasada no esta en el CSV: se infiere, y una pasada nueva empieza cuando
  la busqueda vuelve a una ranura ya visitada en la pasada actual.
"""
import argparse
import csv
import json
import sys


def leer(ruta):
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    ejecuciones = []
    for fila in filas:
        if int(fila["paso"]) == 1:
            ejecuciones.append([])
        ejecuciones[-1].append(fila)
    return ejecuciones


def clave(config):
    return json.dumps(config, sort_keys=True)


def configuraciones(ejecuciones):
    """Dict clave -> (precision, config), en orden de primera aparicion."""
    vistas = {}
    for ejec in ejecuciones:
        for fila in ejec:
            if fila["config"]:
                vistas.setdefault(
                    clave(json.loads(fila["config"])),
                    (float(fila["precision"]), json.loads(fila["config"])),
                )
    return vistas


def instancias_por_config(ejecuciones):
    ultima = ejecuciones[-1]
    n_cfg = len({clave(json.loads(f["config"])) for f in ultima if f["config"]})
    consultas = max(int(f["consultas"]) for f in ultima)
    if n_cfg == 0 or consultas % n_cfg:
        raise SystemExit(
            f"No se pueden inferir las instancias: {consultas} consultas, {n_cfg} configuraciones"
        )
    return consultas // n_cfg


def pasadas(ejecucion):
    """Lista de (pasada, ranura, opcion, precision, decision), pasada desde 1."""
    salida, pasada, vistas, actual = [], 1, set(), None
    for fila in ejecucion:
        ranura = fila["ranura"]
        if not ranura:
            continue
        if ranura != actual:
            if ranura in vistas:
                pasada += 1
                vistas = set()
            vistas.add(ranura)
            actual = ranura
        salida.append((pasada, ranura, int(fila["opcion"]),
                       float(fila["precision"]), fila["decision"]))
    return salida


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("historial_0")
    p.add_argument("historial_1")
    p.add_argument("--presupuesto", type=int)
    p.add_argument("--esperado-cfg-0", type=int)
    p.add_argument("--esperado-cfg-1", type=int)
    p.add_argument("--esperado-union", type=int)
    p.add_argument("--esperado-generaciones", type=int)
    p.add_argument("--top", type=int, default=8)
    a = p.parse_args()

    ejec = [leer(a.historial_0), leer(a.historial_1)]
    cfgs = [configuraciones(e) for e in ejec]
    n_inst = [instancias_por_config(e) for e in ejec]
    if n_inst[0] != n_inst[1]:
        raise SystemExit(f"Instancias por configuracion distintas: {n_inst}")
    n = n_inst[0]

    union = {}
    conflictos = []
    for c in cfgs:
        for k, (prec, cfg) in c.items():
            if k in union and union[k][0] != prec:
                conflictos.append(k)
            union.setdefault(k, (prec, cfg))
    generaciones = len(union) * n

    print("== Conteos ==")
    for i in (0, 1):
        print(f"arranque {i}: {len(ejec[i])} ejecucion(es) en el CSV, "
              f"{len(cfgs[i])} configuraciones distintas")
    print(f"instancias por configuracion (inferidas): {n}")
    print(f"union: {len(union)} configuraciones distintas")
    print(f"generaciones distintas de la union: {generaciones}")
    print(f"suma por arranque (cada uno por separado): {(len(cfgs[0]) + len(cfgs[1])) * n}")
    if a.presupuesto is not None:
        estado = "dentro" if generaciones <= a.presupuesto else "FUERA"
        print(f"B = {a.presupuesto}: {estado} del presupuesto "
              f"({generaciones} de {a.presupuesto}, "
              f"{100 * generaciones / a.presupuesto:.1f} %)")
    if conflictos:
        print(f"AVISO: {len(conflictos)} configuraciones con precision distinta entre arranques")

    print(f"\n== Mejores {a.top} configuraciones de la union ==")
    orden = sorted(union.values(), key=lambda t: -t[0])[:a.top]
    for prec, cfg in orden:
        campos = " ".join(f"{k}={cfg[k]}" for k in
                          ("rol", "estrategia", "formato", "estilo", "cierre"))
        print(f"{prec:.2f}  {campos}  T={cfg['temperatura']}")

    print("\n== Precision por opcion, ranura y pasada (ultima ejecucion de cada CSV) ==")
    for i in (0, 1):
        print(f"-- arranque {i} --")
        filas = pasadas(ejec[i][-1])
        agrupado = {}
        for pas, ran, op, prec, dec in filas:
            agrupado.setdefault((pas, ran), []).append((op, prec, dec))
        for (pas, ran), lista in agrupado.items():
            texto = " ".join(f"{op}:{prec:.2f}" for op, prec, _ in lista)
            print(f"pasada {pas} {ran}: {texto}")

    errores = []
    for nombre, obtenido, esperado in (
        ("configuraciones arranque 0", len(cfgs[0]), a.esperado_cfg_0),
        ("configuraciones arranque 1", len(cfgs[1]), a.esperado_cfg_1),
        ("configuraciones union", len(union), a.esperado_union),
        ("generaciones union", generaciones, a.esperado_generaciones),
    ):
        if esperado is not None and obtenido != esperado:
            errores.append(f"{nombre}: esperado {esperado}, obtenido {obtenido}")
    if errores:
        print("\nERROR: no coinciden los valores esperados:", file=sys.stderr)
        for e in errores:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    if any(v is not None for v in (a.esperado_cfg_0, a.esperado_cfg_1,
                                   a.esperado_union, a.esperado_generaciones)):
        print("\nOK: los valores esperados coinciden.")


if __name__ == "__main__":
    main()
