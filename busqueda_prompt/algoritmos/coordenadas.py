"""Búsqueda por coordenadas: mejora una ranura a la vez, con varios arranques.

Cada arranque parte de una config al azar. En una pasada recorre las ranuras y,
para cada una, prueba las demás opciones dejando fijo el resto; solo cambia si
la precisión sube estrictamente, así que nunca baja. Termina cuando una pasada
no mejora nada (óptimo local por ranura) o al llegar a `max_pasadas`.
"""

import csv  # módulo estándar para escribir/leer archivos CSV (tablas de texto separadas por comas)
import os  # módulo estándar para consultar el sistema de archivos (existencia y tamaño de un archivo)
import random  # módulo estándar de números aleatorios; usaremos su clase Random con semilla

from busqueda_prompt.contado import OraculoContado  # envoltorio que cuenta generaciones y aplica el presupuesto B
from busqueda_prompt.contratos import PresupuestoAgotado, ResultadoBusqueda, clave_config  # excepción, tipo de salida y texto estable de una config

# Tupla (inmutable) con los nombres de las columnas del CSV; el orden es el acordado en el reparto.
COLUMNAS = ("paso", "arranque", "ranura", "opcion", "config", "precision",
            "mejor_precision", "consultas", "decision")  # los paréntesis permiten partir la línea sin usar "\"


class _Registro:  # clase auxiliar; el "_" inicial indica que es de uso interno del módulo
    """Guarda cada paso en memoria y, si hay ruta, en CSV (abre y cierra el archivo en cada fila)."""

    def __init__(self, ruta, filas, mostrar=None):  # constructor: se ejecuta al crear _Registro(...)
        self.filas = filas  # lista compartida con quien llama; aquí se van agregando las filas
        self.mostrar = mostrar  # función opcional (p. ej. print) que recibe cada fila para verla en pantalla
        self.ruta = ruta  # ruta del CSV, o None si solo se quiere registro en memoria
        self.paso = 0  # contador del número de paso; sube 1 en cada anotación

    def _escribir(self, fila):  # agrega una fila al CSV abriendo y cerrando el archivo
        # Es archivo nuevo si no existe o está vacío; "or" corta: si no existe, no llama a getsize.
        nuevo = not os.path.exists(self.ruta) or os.path.getsize(self.ruta) == 0
        # "a" = append: agrega al final sin borrar lo previo; newline="" evita filas en blanco en Windows.
        # El "with" cierra el archivo al salir del bloque: así Drive lo sincroniza en cada fila y,
        # si Colab se cae, el historial ya quedó guardado.
        with open(self.ruta, "a", newline="", encoding="utf-8") as archivo:
            # DictWriter escribe diccionarios como filas, ordenando las columnas según fieldnames.
            escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS)
            if nuevo:  # si el archivo es nuevo hace falta la fila de encabezados
                escritor.writeheader()  # escribe los nombres de columna una sola vez
            escritor.writerow(fila)  # escribe la fila como una línea del CSV

    def anotar(self, **campos):  # **campos recoge los argumentos con nombre en un diccionario
        self.paso += 1  # avanza el contador antes de usarlo, así el primer paso es el 1
        fila = {"paso": self.paso, **campos}  # nuevo diccionario: "paso" más todos los campos recibidos (** desempaqueta)
        self.filas.append(fila)  # guarda la fila en la lista en memoria
        if self.ruta:  # si se pidió CSV, también se escribe allí
            self._escribir(fila)
        if self.mostrar:  # si hay función de visualización
            self.mostrar(fila)  # la llama con la fila (p. ej. imprime el progreso)

    def cerrar(self):  # se conserva por compatibilidad: ya no queda ningún archivo abierto
        pass  # cada fila cerró su archivo al escribirse


def resolver(oraculo, ranuras, opciones, instancias, semilla=1, presupuesto=None,
             arranques=1, max_pasadas=2, temperatura=0.0, semilla_busqueda=0,
             orden_ranuras=None, historial=None, ruta_historial=None, mostrar=None,
             opciones_excluidas=None, motivo=None):
    """Devuelve la mejor config hallada entre todos los arranques.

    `historial` (lista) recibe una fila por evaluación con las columnas de
    `COLUMNAS`; `ruta_historial` las agrega además a un CSV. `mostrar` es un
    callable opcional que recibe cada fila (por ejemplo `print`). Si el
    presupuesto se agota, devuelve lo mejor visto hasta ese momento.

    `opciones_excluidas` ({ranura: opciones}) descarta opciones que el análisis de
    fallos mostró inútiles: ni se prueban ni se usan al arrancar. `motivo` es el
    texto de esa decisión; queda escrito en la columna `decision` al inicio.
    """
    # --- Validación de argumentos: fallar pronto y con mensaje claro ---
    if arranques < 1 or max_pasadas < 1:  # sin al menos un arranque y una pasada no hay búsqueda
        raise ValueError("arranques y max_pasadas deben ser al menos 1")  # "raise" lanza la excepción y corta la función
    if len(ranuras) != len(opciones):  # cada ranura necesita su número de opciones
        raise ValueError("ranuras y opciones deben tener la misma longitud")
    # Si se dio un orden, se copia a lista; si no (None), se usa el orden natural de las ranuras.
    orden = list(orden_ranuras) if orden_ranuras is not None else list(ranuras)
    if sorted(orden) != sorted(ranuras):  # el orden debe contener exactamente las mismas ranuras, sin faltar ni repetir
        raise ValueError("orden_ranuras debe ser una permutación de ranuras")
    tam = dict(zip(ranuras, opciones))  # zip empareja ranura↔nº de opciones; dict lo vuelve diccionario {ranura: k}
    excluidas = {r: set(v) for r, v in (opciones_excluidas or {}).items()}  # copia a conjuntos; "or {}" cubre el caso None
    if set(excluidas) - set(ranuras):  # diferencia de conjuntos: llaves que no son ranuras
        raise ValueError("opciones_excluidas trae ranuras desconocidas")
    # Opciones permitidas por ranura: todas las 0..k-1 menos las excluidas (comprensión de diccionario con lista).
    permitidas = {r: [o for o in range(tam[r]) if o not in excluidas.get(r, ())] for r in ranuras}
    if any(not p for p in permitidas.values()):  # una ranura sin ninguna opción permitida no se puede buscar
        raise ValueError("opciones_excluidas deja una ranura sin opciones")

    # Un solo contador para todos los arranques: no cobra dos veces la misma (config, instancia, semilla).
    contado = OraculoContado(oraculo, presupuesto)
    # Si no pasaron lista de historial se crea una nueva; así evitamos el error clásico del argumento mutable por defecto.
    registro = _Registro(ruta_historial, historial if historial is not None else [], mostrar)
    mejor_global = None  # guardará la tupla (precisión, config) de la mejor config vista en todos los arranques

    def evaluar(config):  # función interna (closure): usa contado, instancias y semilla del entorno
        return contado.evaluar(config, instancias, semilla).precision  # consulta al oráculo y devuelve solo la precisión

    try:  # el try permite atrapar PresupuestoAgotado y devolver lo mejor hallado en vez de fallar
        for a in range(arranques):  # a = 0, 1, ..., arranques-1: un punto de partida distinto por vuelta
            # Generador aleatorio propio; la semilla es un texto "semilla|a", así cada arranque es distinto pero reproducible.
            rng = random.Random(f"{semilla_busqueda}|{a}")
            # Config inicial: una opción al azar por ranura (comprensión de diccionario) y se une la temperatura con "|" (unión de dicts).
            # rng.choice elige una opción permitida al azar (las excluidas nunca salen como punto de partida).
            actual = {r: rng.choice(permitidas[r]) for r in ranuras} | {"temperatura": temperatura}
            if motivo:  # si hay una decisión tomada con las trazas, queda escrita antes de buscar
                detalle = f"decide: {motivo}; orden={orden}; excluidas={ {r: sorted(v) for r, v in excluidas.items()} }"  # texto con orden y exclusiones aplicadas
                registro.anotar(arranque=a, ranura="", opcion="", config="", precision="",  # fila sin evaluación: solo documenta
                                mejor_precision="", consultas=contado.consultas, decision=detalle)
            p_actual = evaluar(actual)  # precisión de la config de partida (cuesta n generaciones)
            registro.anotar(arranque=a, ranura="", opcion="", config=clave_config(actual),  # fila "inicio": aún no se cambia ninguna ranura
                            precision=p_actual, mejor_precision=p_actual,  # al inicio la mejor del arranque es la propia
                            consultas=contado.consultas, decision="inicio")  # consultas acumuladas hasta ahora
            if mejor_global is None or p_actual > mejor_global[0]:  # primera vez, o mejora a la mejor global
                mejor_global = (p_actual, dict(actual))  # guarda una COPIA (dict(...)) para que no cambie al mutar "actual"

            for _ in range(max_pasadas):  # "_" = variable que no se usa; repite hasta max_pasadas pasadas
                mejoro = False  # bandera: ¿esta pasada logró alguna mejora?
                for ranura in orden:  # recorre las ranuras en el orden configurado
                    for opcion in permitidas[ranura]:  # prueba cada opción permitida de esta ranura (sin las excluidas)
                        if opcion == actual[ranura]:  # esa opción ya es la actual y ya se midió
                            continue  # salta a la siguiente opción sin gastar consultas
                        candidata = dict(actual, **{ranura: opcion})  # copia de actual cambiando solo esta ranura
                        p = evaluar(candidata)  # precisión de la candidata
                        acepta = p > p_actual  # mejora estricta: en empate se conserva la actual, por eso la precisión nunca baja
                        if acepta:  # si mejoró, la candidata pasa a ser la actual
                            actual, p_actual, mejoro = candidata, p, True  # asignación múltiple en una línea
                            if p > mejor_global[0]:  # ¿también supera a la mejor de todos los arranques?
                                mejor_global = (p, dict(actual))  # actualiza la mejor global con una copia
                        registro.anotar(  # deja constancia del paso, se haya aceptado o no
                            arranque=a, ranura=ranura, opcion=opcion,
                            config=clave_config(candidata), precision=p,
                            mejor_precision=p_actual, consultas=contado.consultas,
                            decision="acepta" if acepta else "descarta")  # expresión condicional: texto según el caso
                if not mejoro:  # una pasada completa sin mejoras = óptimo local por ranura
                    break  # sale del bucle de pasadas: seguir sería repetir lo mismo
    except PresupuestoAgotado:  # el contador lanzó la excepción: ya no caben más generaciones
        pass  # no se hace nada: se sale del bucle y se devuelve lo mejor visto
    finally:  # se ejecuta siempre, haya o no excepción
        registro.cerrar()  # garantiza cerrar el CSV

    if mejor_global is None:  # nunca se pudo evaluar ni la config inicial
        raise PresupuestoAgotado("el presupuesto no alcanza ni para la primera evaluación")  # no hay nada que devolver
    # Empaqueta el resultado en el tipo común: ganadora, su precisión, consultas gastadas y reparto por config.
    return ResultadoBusqueda(mejor_global[1], mejor_global[0], contado.consultas,
                             dict(contado.asignacion))  # dict(...) convierte el Counter en diccionario normal
