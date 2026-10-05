"""
================================================================================
UNIVERSIDAD AMERICANA (UAM)
Facultad de Ingeniería y Arquitectura (FIA)
Álgebra Lineal (MTM0120)
Batería de Pruebas Unitarias: Cálculo de Determinantes (Cofactores vs LU)
================================================================================
Valida exhaustivamente:
1. Determinante de matrices 1x1.
2. Determinante de matrices 2x2 por fórmula directa y triangulación.
3. Determinante de matrices 3x3 por Sarrus/Laplace y LU con pivoteo.
4. Determinante de matrices 4x4 por ambos métodos y coincidencia exacta.
5. Matrices triangulares (determinante = producto de la diagonal).
6. Matrices singulares con filas linealmente dependientes (det = 0).
7. Matrices con elementos fraccionarios y negativos.
8. Análisis previo de eficiencia computacional (O(n!) vs O(n³)).
================================================================================
"""

import unittest
from fractions import Fraction

from src.matrices.determinante import (
    calcular_determinante,
    calcular_determinante_cofactores,
    calcular_determinante_lu,
    analizar_eficiencia_determinante,
    ResultadoDeterminante,
    AnalisisEficiencia,
)


class TestDeterminantes(unittest.TestCase):
    """Pruebas unitarias formales para el módulo de determinantes."""

    def test_matriz_1x1(self):
        """Prueba matriz 1x1 con escalar positivo y negativo."""
        A = [[7]]
        res_cof = calcular_determinante_cofactores(A)
        res_lu = calcular_determinante_lu(A)

        self.assertEqual(res_cof.determinante, Fraction(7, 1))
        self.assertEqual(res_lu.determinante, Fraction(7, 1))
        self.assertTrue(res_cof.es_invertible)
        self.assertTrue(res_lu.es_invertible)

        B = [[-5]]
        res_b = calcular_determinante(B, metodo="lu")
        self.assertEqual(res_b.determinante, Fraction(-5, 1))

    def test_matriz_2x2_estandar(self):
        """Prueba matriz 2x2 clásica: [[1, 2], [3, 4]] => det = 1*4 - 2*3 = -2."""
        A = [[1, 2], [3, 4]]
        res_cof = calcular_determinante_cofactores(A)
        res_lu = calcular_determinante_lu(A)

        self.assertEqual(res_cof.determinante, Fraction(-2, 1))
        self.assertEqual(res_lu.determinante, Fraction(-2, 1))
        self.assertTrue(res_cof.es_invertible)
        self.assertTrue(res_lu.es_invertible)

    def test_matriz_2x2_fracciones(self):
        """Prueba matriz 2x2 con fracciones exactas."""
        A = [
            [Fraction(1, 2), Fraction(3, 4)],
            [Fraction(2, 3), Fraction(5, 6)],
        ]
        # det = (1/2)*(5/6) - (3/4)*(2/3) = 5/12 - 6/12 = -1/12
        res_cof = calcular_determinante_cofactores(A)
        res_lu = calcular_determinante_lu(A)

        self.assertEqual(res_cof.determinante, Fraction(-1, 12))
        self.assertEqual(res_lu.determinante, Fraction(-1, 12))

    def test_matriz_3x3_estandar(self):
        """Prueba matriz 3x3 conocida."""
        # A = [[1, 2, 3], [0, 1, 4], [5, 6, 0]]
        # det = 1*(0 - 24) - 2*(0 - 20) + 3*(0 - 5) = -24 + 40 - 15 = 1
        A = [
            [1, 2, 3],
            [0, 1, 4],
            [5, 6, 0]
        ]
        res_cof = calcular_determinante_cofactores(A)
        res_lu = calcular_determinante_lu(A)

        self.assertEqual(res_cof.determinante, Fraction(1, 1))
        self.assertEqual(res_lu.determinante, Fraction(1, 1))
        self.assertTrue(res_cof.es_invertible)
        self.assertTrue(res_lu.es_invertible)

    def test_matriz_3x3_pivoteo_intercambio(self):
        """Prueba matriz 3x3 que requiere intercambio de filas para pivote."""
        # A = [[0, 2, 1], [3, -1, 2], [1, 1, 1]]
        # det: fila 1 -> -2*(3 - 2) + 1*(3 - (-1)) = -2(1) + 1(4) = 2
        A = [
            [0, 2, 1],
            [3, -1, 2],
            [1, 1, 1]
        ]
        res_cof = calcular_determinante_cofactores(A)
        res_lu = calcular_determinante_lu(A)

        self.assertEqual(res_cof.determinante, Fraction(2, 1))
        self.assertEqual(res_lu.determinante, Fraction(2, 1))

    def test_matriz_singular_det_cero(self):
        """Prueba matriz con filas linealmente dependientes (det = 0)."""
        # Fila 3 = Fila 1 + Fila 2
        A = [
            [1, 2, 3],
            [4, 5, 6],
            [5, 7, 9]
        ]
        res_cof = calcular_determinante_cofactores(A)
        res_lu = calcular_determinante_lu(A)

        self.assertEqual(res_cof.determinante, Fraction(0, 1))
        self.assertEqual(res_lu.determinante, Fraction(0, 1))
        self.assertFalse(res_cof.es_invertible)
        self.assertFalse(res_lu.es_invertible)

    def test_matriz_triangular_superior(self):
        """Prueba matriz triangular: determinante es el producto de la diagonal."""
        A = [
            [2, 5, 7, 9],
            [0, 3, -1, 4],
            [0, 0, -2, 6],
            [0, 0, 0, 5]
        ]
        # det = 2 * 3 * (-2) * 5 = -60
        res_cof = calcular_determinante_cofactores(A)
        res_lu = calcular_determinante_lu(A)

        self.assertEqual(res_cof.determinante, Fraction(-60, 1))
        self.assertEqual(res_lu.determinante, Fraction(-60, 1))

    def test_matriz_4x4_coincidencia(self):
        """Prueba matriz 4x4 general con coincidencia exacta entre ambos métodos."""
        A = [
            [2, 1, 0, 4],
            [-1, 0, 2, 1],
            [3, -2, 1, 0],
            [0, 1, 1, 2]
        ]
        res_cof = calcular_determinante_cofactores(A)
        res_lu = calcular_determinante_lu(A)

        # Ambos métodos deben arrojar exactamente el mismo resultado
        self.assertEqual(res_cof.determinante, Fraction(-15, 1))
        self.assertEqual(res_lu.determinante, Fraction(-15, 1))
        self.assertTrue(res_cof.es_invertible)
        self.assertTrue(res_lu.es_invertible)

    def test_matriz_identidad(self):
        """Prueba determinante de matriz identidad de orden 4."""
        I4 = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
        res = calcular_determinante(I4, metodo="lu")
        self.assertEqual(res.determinante, Fraction(1, 1))

    def test_analisis_eficiencia(self):
        """Prueba el módulo de comparación de eficiencia previa."""
        # Para n = 2
        analisis_2 = analizar_eficiencia_determinante(2)
        self.assertEqual(analisis_2.metodo_recomendado, "ambos")

        # Para n = 3
        analisis_3 = analizar_eficiencia_determinante(3)
        self.assertEqual(analisis_3.metodo_recomendado, "lu")

        # Para n = 4
        analisis_4 = analizar_eficiencia_determinante(4)
        self.assertEqual(analisis_4.metodo_recomendado, "lu")
        self.assertIn("O(n³)", analisis_4.complejidad_lu)
        self.assertIn("O(n!)", analisis_4.complejidad_cofactores)
        self.assertGreater(analisis_4.ops_cofactores, analisis_4.ops_lu)

        # Para n = 6
        analisis_6 = analizar_eficiencia_determinante(6)
        self.assertGreater(analisis_6.ops_cofactores, 1000)

    def test_validacion_matriz_no_cuadrada(self):
        """Debe rechazar matrices no cuadradas con ValueError."""
        A = [
            [1, 2, 3],
            [4, 5, 6]
        ]
        with self.assertRaises(ValueError):
            calcular_determinante(A, metodo="lu")
        with self.assertRaises(ValueError):
            calcular_determinante(A, metodo="cofactores")


if __name__ == "__main__":
    unittest.main()
