"""Fórmula, reemplazo, error aproximado y límites numéricos de la regla falsa."""

import json
import math
import unittest

from src.regla_falsa.metodo import (
    UMBRAL_ESTANCAMIENTO, falsa_posicion, resolver_regla_falsa, validar_intervalo,
)

REFERENCIA = "x^4 - 5*x^3 + 0.5*x^2 - 11*x + 10"  # raíces reales: 3 ± √5


class TestFalsaPosicion(unittest.TestCase):
    def test_formula_en_una_recta_es_exacta(self):
        # f(x) = 2x − 1 en [0, 2]: la recta secante coincide con la función.
        self.assertEqual(falsa_posicion(0, 2, -1, 3), .5)

    def test_formula_coincide_con_la_interseccion_de_la_secante(self):
        xl, xu, f_xl, f_xu = 4.95, 5.5, -38.263118749999975, 47.8125
        xr = falsa_posicion(xl, xu, f_xl, f_xu)
        pendiente = (f_xu - f_xl) / (xu - xl)
        self.assertAlmostEqual(f_xl + pendiente * (xr - xl), 0, places=9)
        self.assertAlmostEqual(xr, 5.194491014042232)


class TestValidarIntervalo(unittest.TestCase):
    def test_cambio_de_signo_cumple_la_condicion(self):
        res = validar_intervalo(REFERENCIA, 4.95, 5.5)
        self.assertTrue(res["cumple"])
        self.assertEqual(res["estado"], "valido")
        self.assertEqual(res["signo_producto"], "negativo")
        self.assertLess(res["f_xl"], 0)
        self.assertGreater(res["f_xu"], 0)
        self.assertAlmostEqual(res["producto"], res["f_xl"] * res["f_xu"])

    def test_sin_cambio_de_signo_se_informa_sin_excepcion(self):
        res = validar_intervalo("x^2+1", -1, 1)
        self.assertFalse(res["cumple"])
        self.assertEqual(res["estado"], "sin_cambio_de_signo")
        self.assertEqual(res["signo_producto"], "positivo")

    def test_raiz_en_un_extremo(self):
        for xl, xu, extremo in [(0, 1, "xl"), (-1, 0, "xu")]:
            res = validar_intervalo("x", xl, xu)
            self.assertFalse(res["cumple"])
            self.assertEqual(res["estado"], "raiz_en_extremo")
            self.assertEqual(res["raiz_en_extremo"], extremo)
            self.assertEqual(res["signo_producto"], "cero")

    def test_signo_sin_underflow_ni_overflow_del_producto(self):
        self.assertTrue(validar_intervalo("1e-300*(x-0.3)", 0, 1)["cumple"])
        res = validar_intervalo("1e300*(x-0.3)", 0, 1)
        self.assertTrue(res["cumple"])
        self.assertIsNone(res["producto"])
        json.dumps(res, allow_nan=False)

    def test_entradas_invalidas(self):
        for xl, xu in [(2, 1), (1, 1), ("nan", 1), (0, "inf"), (None, 1), (True, 2)]:
            with self.subTest(xl=xl, xu=xu), self.assertRaises(ValueError):
                validar_intervalo("x", xl, xu)
        for funcion, xl, xu in [("1/x", 0, 1), ("ln(x)", -1, 1), ("", 0, 1), ("__import__('os')", 0, 1)]:
            with self.subTest(funcion=funcion), self.assertRaises(ValueError):
                validar_intervalo(funcion, xl, xu)


class TestReglaFalsa(unittest.TestCase):
    def test_ejemplo_de_referencia(self):
        res = resolver_regla_falsa(REFERENCIA, 4.95, 5.5, .01)
        self.assertTrue(res["convergio"])
        self.assertEqual(res["motivo"], "tolerancia")
        self.assertEqual(res["iteraciones"], 5)
        self.assertAlmostEqual(res["raiz"], 5.236055081129443)
        self.assertLess(abs(res["raiz"] - (3 + math.sqrt(5))), 1e-4)
        self.assertAlmostEqual(res["pasos"][0]["xr"], 5.194491014042232)
        self.assertEqual(res["intervalo_inicial"], [4.95, 5.5])

    def test_reemplazo_por_cambio_de_signo(self):
        res = resolver_regla_falsa("x^3-x", -.4, .7, 1e-10)
        for paso, siguiente in zip(res["pasos"], res["pasos"][1:]):
            if paso["signo_producto"] == "−":
                self.assertEqual(paso["decision"], "x_u ← x_r")
                self.assertEqual((siguiente["xl"], siguiente["xu"]), (paso["xl"], paso["xr"]))
            else:
                self.assertEqual(paso["decision"], "x_l ← x_r")
                self.assertEqual((siguiente["xl"], siguiente["xu"]), (paso["xr"], paso["xu"]))
            self.assertLess(siguiente["f_xl"] * siguiente["f_xu"], 0)
        self.assertEqual({p["decision"] for p in res["pasos"][:-1]}, {"x_u ← x_r", "x_l ← x_r"})
        self.assertEqual(res["pasos"][-1]["decision"], "Finalizar")

    def test_error_aproximado_porcentual(self):
        res = resolver_regla_falsa("x^2-2", 1, 2, .5)
        self.assertIsNone(res["pasos"][0]["error_relativo"])
        self.assertIsNone(res["pasos"][0]["error_absoluto"])
        for previo, paso in zip(res["pasos"], res["pasos"][1:]):
            esperado = abs((paso["xr"] - previo["xr"]) / paso["xr"]) * 100
            self.assertAlmostEqual(paso["error_relativo"], esperado)
        self.assertLessEqual(res["pasos"][-1]["error_relativo"], .5)
        self.assertGreater(res["pasos"][-2]["error_relativo"], .5)
        self.assertEqual(res["error_relativo"], res["pasos"][-1]["error_relativo"])

    def test_intervalo_final_encierra_la_raiz(self):
        res = resolver_regla_falsa("cos(x)-x", 0, 1, 1e-8)
        xl, xu = res["intervalo_final"]
        self.assertLessEqual(xl, .7390851332151607)
        self.assertGreaterEqual(xu, .7390851332151607)
        self.assertIn(res["raiz"], (xl, xu))
        self.assertAlmostEqual(res["raiz"], .7390851332151607, places=8)

    def test_raiz_en_extremo_y_raiz_evaluada(self):
        res = resolver_regla_falsa("x-0.5", "1/2", 1)
        self.assertEqual((res["iteraciones"], res["raiz"], res["motivo"]), (0, .5, "raiz_en_extremo"))
        res = resolver_regla_falsa("2*x-1", 0, 2)
        self.assertEqual((res["iteraciones"], res["raiz"], res["motivo"]), (1, .5, "raiz_evaluada"))
        self.assertEqual(res["residuo"], 0)

    def test_limite_de_iteraciones(self):
        res = resolver_regla_falsa("x^10-1", 0, 1.3, .0001, 5)
        self.assertFalse(res["convergio"])
        self.assertEqual(res["motivo"], "max_iteraciones")
        self.assertEqual(len(res["pasos"]), 5)

    def test_estancamiento_del_extremo_superior(self):
        res = resolver_regla_falsa("x^10-1", 0, 1.3)
        self.assertTrue(res["convergio"])
        self.assertGreater(res["iteraciones"], 40)
        self.assertEqual(res["estancamiento"]["extremo"], "xu")
        self.assertEqual(res["estancamiento"]["iteraciones"], res["iteraciones"])
        self.assertTrue(all(p["xu"] == 1.3 for p in res["pasos"]))
        rapido = resolver_regla_falsa(REFERENCIA, 4.95, 5.5)
        self.assertLess(rapido["iteraciones"], UMBRAL_ESTANCAMIENTO)
        self.assertIsNone(rapido["estancamiento"])

    def test_validaciones(self):
        casos = [dict(xl=2, xu=1), dict(xl=1, xu=1), dict(xl="nan"),
                 dict(tolerancia=0), dict(tolerancia=-1), dict(tolerancia="inf"),
                 dict(max_iteraciones=0), dict(max_iteraciones=1001),
                 dict(max_iteraciones=1.5), dict(max_iteraciones=True)]
        for cambio in casos:
            argumentos = dict(funcion="x^2-2", xl=1, xu=2)
            argumentos.update(cambio)
            with self.subTest(cambio=cambio), self.assertRaises(ValueError):
                resolver_regla_falsa(**argumentos)
        for funcion in ["x^2+1", "1/x", "ln(-x)"]:
            with self.subTest(funcion=funcion), self.assertRaises(ValueError):
                resolver_regla_falsa(funcion, -1, 1)

    def test_precision_agotada_y_json_finito(self):
        # Entre dos flotantes adyacentes no existe un x_r interior.
        res = resolver_regla_falsa("(x-1)-1e-16", 1, math.nextafter(1, 2), 1e-30)
        self.assertFalse(res["convergio"])
        self.assertEqual(res["motivo"], "precision_agotada")
        json.dumps(res, allow_nan=False)

    def test_escalas_extremas(self):
        for funcion in ["1e-300*(x-0.3)", "1e300*(x-0.3)"]:
            with self.subTest(funcion=funcion):
                res = resolver_regla_falsa(funcion, 0, 1)
                self.assertTrue(res["convergio"])
                self.assertAlmostEqual(res["raiz"], .3)
                json.dumps(res, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
