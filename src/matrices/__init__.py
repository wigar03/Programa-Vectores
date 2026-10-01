"""
Módulo de operaciones matriciales básicas e inversa en R^(m x n).
"""

from src.matrices.operaciones import (
    suma_matrices,
    resta_matrices,
    multiplicar_escalar_matriz,
    multiplicar_matrices,
    transpuesta_matriz,
    crear_matriz_identidad,
    obtener_dimensiones_matriz,
)
from src.matrices.inversa import (
    calcular_inversa_matriz,
    ResultadoInversa,
)

__all__ = [
    "suma_matrices",
    "resta_matrices",
    "multiplicar_escalar_matriz",
    "multiplicar_matrices",
    "transpuesta_matriz",
    "crear_matriz_identidad",
    "obtener_dimensiones_matriz",
    "calcular_inversa_matriz",
    "ResultadoInversa",
]
