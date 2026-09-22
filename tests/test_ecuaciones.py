"""
Pruebas Unitarias Automatizadas para el Módulo de Ecuaciones Matriciales Ax = b.
UAM - Álgebra Lineal (MTM0120)
"""

import unittest
from fractions import Fraction
from src.ecuaciones.ecuacion_matricial import resolver_ecuacion_matricial


class TestEcuacionesMatriciales(unittest.TestCase):
    def test_ecuacion_scd_2x2(self):
        A = [[2, 1], [1, -1]]
        b = [8, 1]
        # 2x + y = 8, x - y = 1 => 3x = 9 => x = 3, y = 2
        res = resolver_ecuacion_matricial(A, b, ["x", "y"])
        self.assertEqual(res.tipo_sistema, "SCD")
        self.assertEqual(res.solucion_dict["x"], Fraction(3))
        self.assertEqual(res.solucion_dict["y"], Fraction(2))
        self.assertTrue("✓ Satisface" in res.verificacion_residual[0])

    def test_ecuacion_scd_3x3(self):
        A = [[1, 1, 1], [0, 2, 5], [2, 5, -1]]
        b = [6, -4, 27]
        res = resolver_ecuacion_matricial(A, b, ["x", "y", "z"])
        self.assertEqual(res.tipo_sistema, "SCD")
        self.assertEqual(res.solucion_dict["x"], Fraction(5))
        self.assertEqual(res.solucion_dict["y"], Fraction(3))
        self.assertEqual(res.solucion_dict["z"], Fraction(-2))

    def test_ecuacion_si_incompatible(self):
        A = [[1, 2], [2, 4]]
        b = [3, 10]
        res = resolver_ecuacion_matricial(A, b)
        self.assertEqual(res.tipo_sistema, "SI")
        self.assertEqual(res.solucion_dict["x_1"], "Sin solución")

    def test_ecuacion_sci_infinitas(self):
        A = [[1, 2, 3], [2, 4, 6]]
        b = [5, 10]
        res = resolver_ecuacion_matricial(A, b)
        self.assertEqual(res.tipo_sistema, "SCI")

    def test_error_dimension_vector_b(self):
        A = [[1, 2], [3, 4], [5, 6]]  # 3 filas
        b = [1, 2]                     # 2 elementos (incompatible con m=3)
        with self.assertRaises(ValueError):
            resolver_ecuacion_matricial(A, b)


if __name__ == "__main__":
    unittest.main()
