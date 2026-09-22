"""
Pruebas Unitarias Automatizadas para el Módulo de Combinación Lineal en R^n.
UAM - Álgebra Lineal (MTM0120)
"""

import unittest
from fractions import Fraction
from src.vectores.combinacion_lineal import evaluar_combinacion_lineal


class TestCombinacionLineal(unittest.TestCase):
    def test_combinacion_lineal_unica_r2(self):
        v1 = [1, 2]
        v2 = [3, 4]
        b = [5, 6]
        res = evaluar_combinacion_lineal([v1, v2], b)
        self.assertTrue(res.es_combinacion)
        self.assertEqual(res.tipo_solucion, "UNICA")
        self.assertEqual(res.escalares_particulares, [Fraction(-1), Fraction(2)])

    def test_combinacion_lineal_unica_r3(self):
        v1 = [1, 0, 0]
        v2 = [0, 1, 0]
        v3 = [0, 0, 1]
        b = [4, -7, 9]
        res = evaluar_combinacion_lineal([v1, v2, v3], b)
        self.assertTrue(res.es_combinacion)
        self.assertEqual(res.tipo_solucion, "UNICA")
        self.assertEqual(res.escalares_particulares, [Fraction(4), Fraction(-7), Fraction(9)])

    def test_combinacion_lineal_imposible(self):
        # Dos vectores en el plano xy nunca pueden generar una componente z no nula
        v1 = [1, 0, 0]
        v2 = [0, 1, 0]
        b = [1, 1, 5]
        res = evaluar_combinacion_lineal([v1, v2], b)
        self.assertFalse(res.es_combinacion)
        self.assertEqual(res.tipo_solucion, "NO_COMBINACION")

    def test_combinacion_lineal_infinitas(self):
        # Vectores dependientes pero que sí generan b
        v1 = [1, 2]
        v2 = [2, 4]
        b = [3, 6]
        res = evaluar_combinacion_lineal([v1, v2], b)
        self.assertTrue(res.es_combinacion)
        self.assertEqual(res.tipo_solucion, "INFINITAS")

    def test_error_dimensiones_desiguales(self):
        v1 = [1, 2]
        v2 = [1, 2, 3]
        b = [1, 2]
        with self.assertRaises(ValueError):
            evaluar_combinacion_lineal([v1, v2], b)

    def test_error_dimension_vector_objetivo(self):
        v1 = [1, 2, 3]
        v2 = [4, 5, 6]
        b = [7, 8]  # Dimensión 2 vs 3
        with self.assertRaises(ValueError):
            evaluar_combinacion_lineal([v1, v2], b)


if __name__ == "__main__":
    unittest.main()
