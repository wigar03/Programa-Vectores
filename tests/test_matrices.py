"""
Pruebas Unitarias Automatizadas para el Módulo de Operaciones Matriciales.
UAM - Álgebra Lineal (MTM0120)
"""

import unittest
from fractions import Fraction
from src.matrices.operaciones import (
    suma_matrices,
    resta_matrices,
    multiplicar_escalar_matriz,
    multiplicar_matrices,
    transpuesta_matriz,
    crear_matriz_identidad,
)


class TestOperacionesMatriciales(unittest.TestCase):
    def test_suma_matrices_2x2(self):
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        C = suma_matrices(A, B)
        esperado = [[Fraction(6), Fraction(8)], [Fraction(10), Fraction(12)]]
        self.assertEqual(C, esperado)

    def test_resta_matrices_2x3(self):
        A = [[3, -1, 4], [2, 0, 5]]
        B = [[1, 2, -1], [3, 4, 2]]
        C = resta_matrices(A, B)
        esperado = [[Fraction(2), Fraction(-3), Fraction(5)], [Fraction(-1), Fraction(-4), Fraction(3)]]
        self.assertEqual(C, esperado)

    def test_multiplicar_escalar_matriz(self):
        A = [["1/2", 4], [-2, "3/4"]]
        C = multiplicar_escalar_matriz(2, A)
        esperado = [[Fraction(1), Fraction(8)], [Fraction(-4), Fraction(3, 2)]]
        self.assertEqual(C, esperado)

    def test_multiplicar_matrices_2x3_por_3x2(self):
        A = [[1, 2, 3], [4, 5, 6]]
        B = [[7, 8], [9, 1], [2, 3]]
        C, pasos = multiplicar_matrices(A, B)
        # C_11 = 1*7 + 2*9 + 3*2 = 7 + 18 + 6 = 31
        # C_12 = 1*8 + 2*1 + 3*3 = 8 + 2 + 9 = 19
        # C_21 = 4*7 + 5*9 + 6*2 = 28 + 45 + 12 = 85
        # C_22 = 4*8 + 5*1 + 6*3 = 32 + 5 + 18 = 55
        esperado = [[Fraction(31), Fraction(19)], [Fraction(85), Fraction(55)]]
        self.assertEqual(C, esperado)
        self.assertEqual(len(pasos), 4)

    def test_incompatibilidad_dimension_suma(self):
        A = [[1, 2], [3, 4]]
        B = [[1, 2, 3], [4, 5, 6]]
        with self.assertRaises(ValueError):
            suma_matrices(A, B)

    def test_incompatibilidad_dimension_multiplicacion(self):
        A = [[1, 2, 3], [4, 5, 6]]  # 2x3 (columnas = 3)
        B = [[1, 2], [3, 4]]         # 2x2 (filas = 2)
        with self.assertRaises(ValueError):
            multiplicar_matrices(A, B)

    def test_transpuesta_matriz(self):
        A = [[1, 2, 3], [4, 5, 6]]
        A_T = transpuesta_matriz(A)
        esperado = [[Fraction(1), Fraction(4)], [Fraction(2), Fraction(5)], [Fraction(3), Fraction(6)]]
        self.assertEqual(A_T, esperado)

    def test_propiedad_identidad(self):
        A = [[3, 5], [-1, 4]]
        I2 = crear_matriz_identidad(2)
        AI, _ = multiplicar_matrices(A, I2)
        self.assertEqual(AI, [[Fraction(3), Fraction(5)], [Fraction(-1), Fraction(4)]])


if __name__ == "__main__":
    unittest.main()
