"""
Pruebas Unitarias para el Módulo de Inversa y Transpuesta de Matrices.
UAM - Facultad de Ingeniería y Arquitectura (FIA)
Álgebra Lineal (MTM0120) - Unidad 2.2: La Inversa de una Matriz
"""

from fractions import Fraction
import unittest

from src.matrices.inversa import calcular_inversa_matriz, ResultadoInversa
from src.matrices.operaciones import (
    transpuesta_matriz,
    analizar_transpuesta_matriz,
    multiplicar_matrices,
)


class TestInversaMatriz(unittest.TestCase):
    def test_inversa_2x2_ejemplo1(self):
        """
        Inversa de matriz 2x2:
        A = [[2, 5], [-3, -7]]
        Inversa esperada: C = [[-7, -5], [3, 2]]
        """
        A = [[2, 5], [-3, -7]]
        res = calcular_inversa_matriz(A, metodo="gauss_jordan")
        self.assertTrue(res.es_invertible)
        self.assertEqual(res.orden_n, 2)
        self.assertEqual(res.matriz_inversa, [
            [Fraction(-7, 1), Fraction(-5, 1)],
            [Fraction(3, 1), Fraction(2, 1)]
        ])
        self.assertEqual(res.determinante_2x2, Fraction(1, 1))
        self.assertTrue(res.residuo_cero)
        self.assertTrue(len(res.pasos_reduccion) > 0)
        self.assertTrue(len(res.verificacion_A_por_Ainv) > 0)
        self.assertTrue(len(res.verificacion_Ainv_por_A) > 0)
        # Validar que las cadenas de verificación contengan delimitadores $ para KaTeX
        for v in res.verificacion_A_por_Ainv:
            self.assertIn("$", v)
            self.assertIn("(A \\cdot A^{-1})", v)
        for v in res.verificacion_Ainv_por_A:
            self.assertIn("$", v)
            self.assertIn("(A^{-1} \\cdot A)", v)

    def test_inversa_2x2_ejemplo2_teorema(self):
        """
        Inversa por fórmula del Teorema 2x2:
        A = [[3, 4], [5, 6]]
        det(A) = 3(6) - 4(5) = -2 != 0
        Inversa: [[-3, 2], [5/2, -3/2]]
        """
        A = [[3, 4], [5, 6]]
        res = calcular_inversa_matriz(A, metodo="gauss_jordan")
        self.assertTrue(res.es_invertible)
        self.assertEqual(res.determinante_2x2, Fraction(-2, 1))
        esperada = [
            [Fraction(-3, 1), Fraction(2, 1)],
            [Fraction(5, 2), Fraction(-3, 2)]
        ]
        self.assertEqual(res.matriz_inversa, esperada)
        self.assertTrue(res.residuo_cero)

    def test_inversa_3x3_ejemplo(self):
        """
        Inversa de matriz 3x3:
        A = [[0, 1, 2], [1, 0, 3], [4, -3, 8]]
        Inversa esperada:
        [[-9/2, 7, -3/2],
         [-2,   4, -1],
         [3/2, -2, 1/2]]
        """
        A = [
            [0, 1, 2],
            [1, 0, 3],
            [4, -3, 8]
        ]
        # Probar con Gauss-Jordan
        res_gj = calcular_inversa_matriz(A, metodo="gauss_jordan")
        self.assertTrue(res_gj.es_invertible)
        esperada = [
            [Fraction(-9, 2), Fraction(7, 1), Fraction(-3, 2)],
            [Fraction(-2, 1), Fraction(4, 1), Fraction(-1, 1)],
            [Fraction(3, 2), Fraction(-2, 1), Fraction(1, 2)]
        ]
        self.assertEqual(res_gj.matriz_inversa, esperada)
        self.assertTrue(res_gj.residuo_cero)

        # Probar con Método de Gauss (Eliminación + Sustitución regresiva)
        res_gauss = calcular_inversa_matriz(A, metodo="gauss")
        self.assertTrue(res_gauss.es_invertible)
        self.assertEqual(res_gauss.matriz_inversa, esperada)
        self.assertTrue(res_gauss.residuo_cero)

    def test_inversa_3x3_singular_practica(self):
        """
        Matriz 3x3 singular:
        A = [[1, -2, -1], [-1, 5, 6], [5, -4, 5]].
        det(A) = 1(49) - (-2)(-35) + (-1)(-21) = 49 - 70 + 21 = 0.
        La matriz es singular y por tanto NO existe inversa.
        """
        A = [
            [1, -2, -1],
            [-1, 5, 6],
            [5, -4, 5]
        ]
        res = calcular_inversa_matriz(A, metodo="gauss_jordan")
        self.assertFalse(res.es_invertible)
        self.assertIsNone(res.matriz_inversa)
        self.assertIn("singular", res.mensaje_diagnostico.lower())

    def test_inversa_3x3_verificacion_identidad(self):
        """
        Verificación de que A · A^(-1) = I_3 y A^(-1) · A = I_3
        para una matriz 3x3 invertible general.
        """
        A = [
            [1, 2, 3],
            [0, 1, 4],
            [5, 6, 0]
        ]
        res = calcular_inversa_matriz(A, metodo="gauss_jordan")
        self.assertTrue(res.es_invertible)
        self.assertTrue(res.residuo_cero)

        prod1, _ = multiplicar_matrices(A, res.matriz_inversa)
        prod2, _ = multiplicar_matrices(res.matriz_inversa, A)
        identidad_3 = [
            [Fraction(1, 1), Fraction(0, 1), Fraction(0, 1)],
            [Fraction(0, 1), Fraction(1, 1), Fraction(0, 1)],
            [Fraction(0, 1), Fraction(0, 1), Fraction(1, 1)]
        ]
        self.assertEqual(prod1, identidad_3)
        self.assertEqual(prod2, identidad_3)

    def test_matriz_singular_filas_iguales(self):
        """
        Matriz singular con filas idénticas:
        A = [[2, 3, 4], [2, 3, 4], [2, 3, 4]]
        Filas idénticas -> Rango = 1 < 3 -> Singular (No invertible).
        """
        A = [
            [2, 3, 4],
            [2, 3, 4],
            [2, 3, 4]
        ]
        res = calcular_inversa_matriz(A, metodo="gauss_jordan")
        self.assertFalse(res.es_invertible)
        self.assertIsNone(res.matriz_inversa)
        self.assertIn("singular", res.mensaje_diagnostico.lower())

    def test_matriz_no_cuadrada_rechazo(self):
        """
        Verifica que se rechacen matrices no cuadradas (debe ser cuadrada).
        """
        A = [[1, 2, 3], [4, 5, 6]]
        with self.assertRaises(ValueError) as ctx:
            calcular_inversa_matriz(A)
        self.assertIn("cuadrada", str(ctx.exception))

    def test_analizar_transpuesta_propiedades(self):
        """
        Verifica el análisis detallado de transpuesta, simetría y Teorema 2.2.
        """
        # Matriz simétrica 2x2
        S = [[4, 7], [7, 9]]
        analisis_s = analizar_transpuesta_matriz(S)
        self.assertTrue(analisis_s.es_cuadrada)
        self.assertTrue(analisis_s.es_simetrica)
        self.assertFalse(analisis_s.es_antisimetrica)
        self.assertEqual(analisis_s.traza, Fraction(13, 1))

        # Matriz rectangular 2x3
        R = [[1, 2, 3], [4, 5, 6]]
        analisis_r = analizar_transpuesta_matriz(R)
        self.assertFalse(analisis_r.es_cuadrada)
        self.assertEqual(analisis_r.dimensiones_original, (2, 3))
        self.assertEqual(analisis_r.dimensiones_transpuesta, (3, 2))
        self.assertEqual(len(analisis_r.pasos_mapeo), 2)

        # Propiedad (A^T)^(-1) = (A^(-1))^T (Teorema Unidad 2.2 c)
        A = [[2, 5], [-3, -7]]
        inv_A = calcular_inversa_matriz(A).matriz_inversa
        trans_inv_A = transpuesta_matriz(inv_A)

        trans_A = transpuesta_matriz(A)
        inv_trans_A = calcular_inversa_matriz(trans_A).matriz_inversa

        self.assertEqual(trans_inv_A, inv_trans_A)


if __name__ == "__main__":
    unittest.main()
