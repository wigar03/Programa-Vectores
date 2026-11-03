"""Convergencia, intervalos, errores y límites numéricos de bisección."""

import json
import math
import unittest

from src.biseccion.metodo import resolver_biseccion, muestrear_funcion


class TestBiseccion(unittest.TestCase):
    def test_ejemplo_de_hoja_de_calculo(self):
        res = resolver_biseccion("x^4-5*x^3+0.5*x^2-11*x+10", .6, 1,
                                 criterio="residuo")
        self.assertTrue(res["convergio"])
        self.assertEqual(res["iteraciones"], 15)
        self.assertAlmostEqual(res["raiz"], .76392822265625)
        self.assertLessEqual(res["residuo"], .0001)
        self.assertEqual([p["c"] for p in res["pasos"][:4]], [.8, .7, .75, .775])

    def test_cota_y_reduccion_del_intervalo(self):
        res = resolver_biseccion("x^2-2", 1, 2, 1e-8)
        self.assertTrue(res["convergio"])
        self.assertLessEqual(abs(res["raiz"] - math.sqrt(2)), res["cota_error"])
        self.assertLessEqual(res["pasos"][-1]["ancho"], 1e-8)
        for anterior, actual in zip(res["pasos"], res["pasos"][1:]):
            self.assertEqual(actual["ancho"], anterior["ancho"] / 2)
            self.assertLess(actual["fa"] * actual["fb"], 0)

    def test_raiz_en_cada_extremo_y_punto_medio(self):
        for a, b, iteraciones in [(0, 2, 0), (-2, 0, 0), (-1, 1, 1)]:
            res = resolver_biseccion("x", a, b)
            self.assertEqual(res["raiz"], 0)
            self.assertEqual(res["iteraciones"], iteraciones)
            self.assertEqual(res["cota_error"], 0)

    def test_error_relativo_y_primera_iteracion(self):
        res = resolver_biseccion("x^2-2", 1, 2, 1, criterio="relativo")
        self.assertIsNone(res["pasos"][0]["error_relativo"])
        self.assertIsNone(res["pasos"][0]["error_absoluto"])
        ultimo, previo = res["pasos"][-1], res["pasos"][-2]
        self.assertAlmostEqual(ultimo["error_relativo"], abs((ultimo["c"]-previo["c"])/ultimo["c"])*100)
        self.assertLessEqual(ultimo["error_relativo"], 1)

    def test_cero_no_implica_error_relativo_definido(self):
        res = resolver_biseccion("x-0.1", -1, 1, criterio="relativo")
        self.assertEqual(res["pasos"][0]["c"], 0)
        self.assertIsNone(res["pasos"][0]["error_relativo"])
        self.assertTrue(res["convergio"])

    def test_limite_de_iteraciones(self):
        res = resolver_biseccion("cos(x)-x", 0, 1, 1e-15, 2)
        self.assertFalse(res["convergio"])
        self.assertEqual(res["motivo"], "max_iteraciones")
        self.assertEqual(len(res["pasos"]), 2)

    def test_validaciones(self):
        casos = [dict(a=2, b=1), dict(a=1, b=1), dict(a="nan"),
                 dict(tolerancia=0), dict(tolerancia=-1), dict(tolerancia="inf"),
                 dict(max_iteraciones=0), dict(max_iteraciones=1001),
                 dict(max_iteraciones=1.5), dict(max_iteraciones=True),
                 dict(criterio="otro"), dict(criterio=[])]
        for cambio in casos:
            argumentos = dict(funcion="x^2-2", a=1, b=2)
            argumentos.update(cambio)
            with self.subTest(cambio=cambio), self.assertRaises(ValueError):
                resolver_biseccion(**argumentos)
        for funcion in ["x^2+1", "1/x", "ln(-x)"]:
            with self.subTest(funcion=funcion), self.assertRaises(ValueError):
                resolver_biseccion(funcion, -1, 1)

    def test_signos_sin_underflow_del_producto(self):
        res = resolver_biseccion("1e-300*(x-0.3)", 0, 1)
        self.assertTrue(res["convergio"])
        self.assertLess(abs(res["raiz"] - .3), .0001)

    def test_precision_agotada_y_json_finito(self):
        # Signos opuestos entre dos flotantes adyacentes; no existe otro punto medio.
        res = resolver_biseccion("(x-1)-1e-16", 1, math.nextafter(1, 2), 1e-30)
        self.assertFalse(res["convergio"])
        self.assertEqual(res["motivo"], "precision_agotada")
        json.dumps(res, allow_nan=False)

    def test_grafica_separa_dominio_invalido(self):
        puntos = muestrear_funcion("1/x", -1, 1)
        self.assertEqual(len(puntos), 201)
        self.assertIsNone(puntos[100]["y"])
        json.dumps(puntos, allow_nan=False)
