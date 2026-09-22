"""
Pruebas Unitarias Automatizadas para el Módulo de Operaciones Vectoriales en R^n.
UAM - Álgebra Lineal (MTM0120)
"""

import unittest
from fractions import Fraction
from src.vectores.operaciones import (
    suma_vectores,
    resta_vectores,
    multiplicar_escalar_vector,
    producto_punto,
    norma_cuadrada,
    combinacion_lineal_directa,
)


class TestOperacionesVectoriales(unittest.TestCase):
    def test_suma_vectores_r3(self):
        u = [1, 2, 3]
        v = [4, 5, 6]
        res = suma_vectores(u, v)
        self.assertEqual(res, [Fraction(5), Fraction(7), Fraction(9)])

    def test_suma_vectores_fracciones(self):
        u = ["1/2", "-3/4", 2]
        v = ["3/2", "7/4", "-1"]
        res = suma_vectores(u, v)
        self.assertEqual(res, [Fraction(2), Fraction(1), Fraction(1)])

    def test_resta_vectores(self):
        u = [10, -5, 0]
        v = [3, 2, -4]
        res = resta_vectores(u, v)
        self.assertEqual(res, [Fraction(7), Fraction(-7), Fraction(4)])

    def test_multiplicar_escalar(self):
        v = [2, -4, 6]
        res = multiplicar_escalar_vector("3/2", v)
        self.assertEqual(res, [Fraction(3), Fraction(-6), Fraction(9)])

    def test_multiplicar_escalar_cero(self):
        v = [5, -1, 4]
        res = multiplicar_escalar_vector(0, v)
        self.assertEqual(res, [Fraction(0), Fraction(0), Fraction(0)])

    def test_producto_punto(self):
        u = [1, 3, -5]
        v = [4, -2, -1]
        # 1*4 + 3*(-2) + (-5)*(-1) = 4 - 6 + 5 = 3
        res = producto_punto(u, v)
        self.assertEqual(res, Fraction(3))

    def test_norma_cuadrada(self):
        v = [3, 4]
        # 3^2 + 4^2 = 25
        self.assertEqual(norma_cuadrada(v), Fraction(25))

    def test_combinacion_lineal_directa(self):
        v1 = [1, 0]
        v2 = [0, 1]
        c = [3, -5]
        res = combinacion_lineal_directa(c, [v1, v2])
        self.assertEqual(res, [Fraction(3), Fraction(-5)])

    def test_error_dimension_distinta(self):
        u = [1, 2]
        v = [1, 2, 3]
        with self.assertRaises(ValueError):
            suma_vectores(u, v)
        with self.assertRaises(ValueError):
            resta_vectores(u, v)
        with self.assertRaises(ValueError):
            producto_punto(u, v)

    def test_dimension_arbitraria_r5(self):
        u = [1, 2, 3, 4, 5]
        v = [5, 4, 3, 2, 1]
        res = suma_vectores(u, v)
        self.assertEqual(res, [Fraction(6)] * 5)


if __name__ == "__main__":
    unittest.main()
