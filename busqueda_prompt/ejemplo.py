"""Ejemplo pequeño y reproducible: `uv run python -m busqueda_prompt.ejemplo`."""

from busqueda_prompt.algoritmos import fuerza_bruta
from busqueda_prompt.contratos import configuraciones
from busqueda_prompt.sintetico import generar


def main():
    opciones = (2, 2, 2)
    ranuras, oraculo, instancias = generar(opciones, n=20, reglas=8, semilla=1)
    resultado = fuerza_bruta.resolver(oraculo, configuraciones(ranuras, opciones), instancias)
    print("ganadora:", resultado.ganadora)
    print(f"precision: {resultado.precision:.2f}")
    print("consultas:", resultado.consultas)


if __name__ == "__main__":
    main()
