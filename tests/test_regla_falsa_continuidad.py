"""Detección numérica de discontinuidades e intervalos candidatos para la regla falsa."""

import json
import math
import unittest

from src.regla_falsa.continuidad import analizar_continuidad, analizar_region, buscar_intervalos

REFERENCIA = "x^4 - 5*x^3 + 0.5*x^2 - 11*x + 10"  # raíces reales: 3 ± √5


class TestContinuidad(unittest.TestCase):
    def tipos(self, funcion, a, b):
        res = analizar_continuidad(funcion, a, b)
        self.assertEqual(res["continua"], not res["discontinuidades"])
        return [(d["tipo"], d["x"]) for d in res["discontinuidades"]]

    def test_funciones_continuas(self):
        casos = [(REFERENCIA, -10, 10), ("x^10-1", 0, 1.3), ("cos(x)-x", -10, 10),
                 ("exp(x)", 0, 50), ("abs(x)", -1, 1), ("x^3", -1, 2), ("5", 0, 1),
                 ("exp(-x^2)*1e12", -5, 5), ("1e300*(x-0.3)", 0, 1), ("sin(40*x)", -10, 10)]
        for funcion, a, b in casos:
            with self.subTest(funcion=funcion):
                res = analizar_continuidad(funcion, a, b)
                self.assertTrue(res["continua"])
                self.assertEqual(res["discontinuidades"], [])
                self.assertEqual(res["tramos"], [{"desde": a, "hasta": b,
                                                  "abierto_izquierda": False, "abierto_derecha": False}])
                self.assertEqual(res["muestras"], 401)

    def test_asintota_con_cambio_de_signo(self):
        # El polo coincide con una muestra en [-1, 1] y queda entre dos en [-1, 1.3].
        self.assertEqual(self.tipos("1/x", -1, 1), [("asintota", 0)])
        self.assertEqual(self.tipos("sin(x)/x", -10, 10), [("punto_indefinido", 0)])
        self.assertEqual(self.tipos("1/x", -1, 1.3), [("asintota", 0)])
        self.assertEqual(self.tipos("1/(x-0.123)", -1, 1.3), [("asintota", .123)])

    def test_asintota_sin_cambio_de_signo(self):
        self.assertEqual(self.tipos("1/x^2", -1, 1.3), [("asintota", 0)])
        self.assertEqual(self.tipos("ln(abs(x-0.1234))", -1, 1), [("asintota", .1234)])

    def test_asintotas_de_la_tangente(self):
        hallazgos = self.tipos("tan(x)", -5, 5)
        self.assertEqual([tipo for tipo, _ in hallazgos], ["asintota"] * 4)
        for (_, x), esperado in zip(hallazgos, [-1.5 * math.pi, -.5 * math.pi, .5 * math.pi, 1.5 * math.pi]):
            self.assertAlmostEqual(x, esperado, places=6)

    def test_salto_acotado_con_y_sin_cambio_de_signo(self):
        self.assertEqual(self.tipos("abs(x)/x", -1, 1.3), [("salto", 0)])
        self.assertEqual(self.tipos("abs(x)/x + 2", -1, 1.3), [("salto", 0)])

    def test_tramo_fuera_del_dominio(self):
        res = analizar_continuidad("ln(x)", -1, 2)
        self.assertFalse(res["continua"])
        self.assertEqual(res["discontinuidades"], [{"tipo": "fuera_de_dominio", "desde": -1, "hasta": 0, "x": -.5}])
        self.assertEqual(res["tramos"], [{"desde": 0, "hasta": 2,
                                          "abierto_izquierda": True, "abierto_derecha": False}])
        borde = analizar_continuidad("sqrt(x-0.123)", -1, 2)["discontinuidades"][0]
        self.assertAlmostEqual(borde["hasta"], .123)

    def test_tramos_continuos_entre_discontinuidades(self):
        res = analizar_continuidad("1/x", -1, 1.3)
        self.assertEqual(res["tramos"], [
            {"desde": -1, "hasta": 0, "abierto_izquierda": False, "abierto_derecha": True},
            {"desde": 0, "hasta": 1.3, "abierto_izquierda": True, "abierto_derecha": False}])

    def test_un_subintervalo_sin_la_discontinuidad_es_continuo(self):
        self.assertTrue(analizar_continuidad("1/x", .5, 2)["continua"])
        self.assertTrue(analizar_continuidad("tan(x)", -1, 1)["continua"])

    def test_entradas_invalidas(self):
        for a, b in [(1, 1), (2, 1), ("nan", 1), (0, "inf"), (None, 1)]:
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                analizar_continuidad("x", a, b)
        for muestras in [5, 5000, 10.5, True, "400"]:
            with self.subTest(muestras=muestras), self.assertRaises(ValueError):
                analizar_continuidad("x", 0, 1, muestras)
        with self.assertRaises(ValueError):
            analizar_continuidad("__import__('os')", 0, 1)

    def test_resultado_serializable(self):
        for funcion in ["1/x", "tan(x)", "ln(x)", "1e300*(x-0.3)"]:
            json.dumps(analizar_region(funcion, -3, 3), allow_nan=False)


class TestIntervalos(unittest.TestCase):
    def test_una_raiz_por_intervalo_en_la_funcion_de_referencia(self):
        intervalos = buscar_intervalos(REFERENCIA, 0, 6)
        self.assertEqual([(i["xl"], i["xu"]) for i in intervalos], [(0, 3), (3, 6)])
        for intervalo, raiz in zip(intervalos, [3 - math.sqrt(5), 3 + math.sqrt(5)]):
            self.assertLess(intervalo["f_xl"] * intervalo["f_xu"], 0)
            self.assertLess(intervalo["xl"], raiz)
            self.assertGreater(intervalo["xu"], raiz)
            self.assertAlmostEqual(intervalo["raiz_aprox"], raiz, places=6)

    def test_los_intervalos_evitan_las_discontinuidades(self):
        intervalos = buscar_intervalos("tan(x)", -5, 5)
        self.assertEqual([(i["xl"], i["xu"]) for i in intervalos], [(-4, -2), (-1, 1), (2, 4)])
        for intervalo in intervalos:
            self.assertTrue(analizar_continuidad("tan(x)", intervalo["xl"], intervalo["xu"])["continua"])
            self.assertLess(intervalo["f_xl"] * intervalo["f_xu"], 0)

    def test_cambio_de_signo_por_asintota_no_es_intervalo(self):
        self.assertEqual(buscar_intervalos("1/x", -1, 1.3), [])
        self.assertEqual(buscar_intervalos("abs(x)/x", -1, 1.3), [])

    def test_raices_a_ambos_lados_de_una_asintota(self):
        intervalos = buscar_intervalos("1/(x-0.5)^2 - 4", -1, 2)
        self.assertEqual([(i["xl"], i["xu"], i["raiz_aprox"]) for i in intervalos],
                         [(-1, .3, 0), (.7, 2, 1)])

    def test_raices_cercanas_se_separan(self):
        intervalos = buscar_intervalos("(x-1)*(x-1.01)", 0, 2)
        self.assertEqual(len(intervalos), 2)
        self.assertEqual(intervalos[0]["xu"], intervalos[1]["xl"])
        self.assertTrue(1 < intervalos[0]["xu"] < 1.01)

    def test_raiz_sin_cambio_de_signo_no_se_encierra(self):
        res = analizar_region("x^2", -1, 1)
        self.assertEqual(res["intervalos"], [])
        self.assertEqual(res["raices_exactas"], [0])
        self.assertTrue(res["continuidad"]["continua"])

    def test_region_sin_raices(self):
        res = analizar_region("x^2+1", -3, 3)
        self.assertEqual((res["intervalos"], res["raices_exactas"]), ([], []))

    def test_raiz_exacta_en_una_muestra_con_cambio_de_signo(self):
        res = analizar_region("x^3", -1, 1)
        self.assertEqual(res["raices_exactas"], [0])
        self.assertEqual([(i["xl"], i["xu"], i["raiz_aprox"]) for i in res["intervalos"]], [(-1, 1, 0)])

    def test_extremos_como_fraccion_y_lista_acotada(self):
        self.assertEqual([(i["xl"], i["xu"]) for i in buscar_intervalos("x^2-2", "1/2", "5/2")], [(.5, 2.5)])
        self.assertEqual(len(analizar_region("0*x", 0, 1)["raices_exactas"]), 20)


if __name__ == "__main__":
    unittest.main()
