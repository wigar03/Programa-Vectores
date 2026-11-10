"""Pruebas HTTP del flujo de regla falsa: graficar, analizar, validar y resolver."""

import json
import threading
import unittest
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import AlgebraLinearHandler

REFERENCIA = "x^4 - 5*x^3 + 0.5*x^2 - 11*x + 10"


class TestReglaFalsaApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = HTTPServer(("127.0.0.1", 0), AlgebraLinearHandler)
        cls.hilo = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.hilo.start()
        cls.url = f"http://127.0.0.1:{cls.servidor.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.hilo.join()

    def enviar(self, paso, datos):
        req = Request(f"{self.url}/api/regla-falsa/{paso}", json.dumps(datos).encode(),
                      {"Content-Type": "application/json"})
        try:
            respuesta = urlopen(req, timeout=5)
        except HTTPError as exc:
            respuesta = exc
        with respuesta:
            cuerpo = respuesta.read()
        json.loads(cuerpo, parse_constant=self.fail)  # sin NaN ni Infinity
        return respuesta.status, json.loads(cuerpo)

    def test_paso_1_graficar(self):
        estado, res = self.enviar("graficar", dict(funcion="cos(x)-x", a="-1", b="5/2"))
        self.assertEqual(estado, 200)
        self.assertEqual(res["funcion_latex"], r"\cos\left(x\right) - x")
        self.assertEqual(res["intervalo"], [-1, 2.5])
        self.assertEqual(len(res["grafica"]), 401)
        self.assertEqual((res["grafica"][0]["x"], res["grafica"][-1]["x"]), (-1, 2.5))
        estado, res = self.enviar("graficar", dict(funcion="1/x", a=-1, b=1, cantidad=5))
        self.assertEqual(estado, 200)
        self.assertEqual([p["y"] for p in res["grafica"]], [-1, -2, None, 2, 1])

    def test_paso_2_analizar_region_continua(self):
        estado, res = self.enviar("analizar", dict(funcion=REFERENCIA, a=0, b=6))
        self.assertEqual(estado, 200)
        self.assertTrue(res["continuidad"]["continua"])
        self.assertEqual([(i["xl"], i["xu"]) for i in res["intervalos"]], [(0, 3), (3, 6)])
        self.assertEqual(res["raices_exactas"], [])

    def test_paso_2_analizar_region_discontinua(self):
        estado, res = self.enviar("analizar", dict(funcion="tan(x)", a=-5, b=5))
        self.assertEqual(estado, 200)
        self.assertFalse(res["continuidad"]["continua"])
        self.assertEqual([d["tipo"] for d in res["continuidad"]["discontinuidades"]], ["asintota"] * 4)
        self.assertEqual(len(res["continuidad"]["tramos"]), 5)
        self.assertEqual([(i["xl"], i["xu"]) for i in res["intervalos"]], [(-4, -2), (-1, 1), (2, 4)])

    def test_paso_3_validar_intervalo(self):
        estado, res = self.enviar("validar", dict(funcion=REFERENCIA, xl="4.95", xu="5.5"))
        self.assertEqual(estado, 200)
        self.assertTrue(res["valido"])
        self.assertTrue(res["cumple"])
        self.assertEqual(res["estado"], "valido")
        self.assertLess(res["producto"], 0)
        self.assertTrue(res["continuidad"]["continua"])

    def test_paso_3_estados_no_validos(self):
        casos = [(dict(funcion="x^2+1", xl=0, xu=1), "sin_cambio_de_signo", False),
                 (dict(funcion="tan(x)", xl=1, xu=2), "discontinua", False),
                 (dict(funcion="1/x", xl=-1, xu=1), "discontinua", False),
                 (dict(funcion="1/x^2", xl=-1, xu=1.3), "sin_cambio_de_signo", False),
                 (dict(funcion="x", xl=0, xu=1), "raiz_en_extremo", True)]
        for datos, esperado, valido in casos:
            with self.subTest(datos=datos):
                estado, res = self.enviar("validar", datos)
                self.assertEqual(estado, 200)
                self.assertEqual((res["estado"], res["valido"]), (esperado, valido))
        _, res = self.enviar("validar", dict(funcion="tan(x)", xl=1, xu=2))
        self.assertTrue(res["cumple"])  # hay cambio de signo, pero lo causa la asíntota

    def test_paso_4_resolver(self):
        estado, res = self.enviar("resolver", dict(funcion=REFERENCIA, xl="4.95", xu="5.5",
                                                   tolerancia="0.01", max_iteraciones="100"))
        self.assertEqual(estado, 200)
        self.assertTrue(res["convergio"])
        self.assertEqual(res["iteraciones"], 5)
        self.assertAlmostEqual(res["raiz"], 5.2360550811, places=9)
        self.assertLessEqual(res["error_relativo"], .01)
        self.assertEqual(len(res["grafica"]), 201)
        self.assertEqual(res["pasos"][0]["decision"], "x_l ← x_r")
        self.assertIn("x^{4}", res["funcion_latex"])

    def test_paso_4_no_convergencia_y_raiz_en_extremo_son_resultados(self):
        estado, res = self.enviar("resolver", dict(funcion="x^10-1", xl=0, xu=1.3, max_iteraciones=3))
        self.assertEqual((estado, res["convergio"], res["motivo"]), (200, False, "max_iteraciones"))
        estado, res = self.enviar("resolver", dict(funcion="x-0.5", xl="1/2", xu=1))
        self.assertEqual((estado, res["iteraciones"], res["raiz"]), (200, 0, .5))

    def test_paso_4_rechaza_intervalos_sin_validar(self):
        for datos, fragmento in [(dict(funcion="tan(x)", xl=1, xu=2), "discontinuidad"),
                                 (dict(funcion="x^2+1", xl=0, xu=1), "signos opuestos")]:
            with self.subTest(datos=datos):
                estado, res = self.enviar("resolver", datos)
                self.assertEqual(estado, 400)
                self.assertIn(fragmento, res["error"])

    def test_errores_son_json_400(self):
        casos = {
            "graficar": [{}, [], None, dict(funcion="x", a=1, b=1), dict(funcion="x^", a=0, b=1),
                         dict(funcion="x", a=0, b=1, cantidad="muchos")],
            "analizar": [{}, [], dict(funcion="x", a=2, b=1), dict(funcion="__import__('os')", a=0, b=1)],
            "validar": [{}, None, dict(funcion="x", xl=1, xu=0), dict(funcion="1/x", xl=0, xu=1),
                        dict(funcion="x", xl="nan", xu=1)],
            "resolver": [{}, [], dict(funcion="x^2-2", xl=1, xu=2, tolerancia=0),
                         dict(funcion="x^2-2", xl=1, xu=2, max_iteraciones=1001)],
        }
        for paso, cuerpos in casos.items():
            for cuerpo in cuerpos:
                with self.subTest(paso=paso, cuerpo=cuerpo):
                    estado, res = self.enviar(paso, cuerpo)
                    self.assertEqual(estado, 400)
                    self.assertIsInstance(res["error"], str)

    def test_recursos_de_interfaz_disponibles(self):
        for ruta in ["/regla-falsa.js", "/regla-falsa.css"]:
            with self.subTest(ruta=ruta), urlopen(self.url + ruta, timeout=5) as res:
                self.assertEqual(res.status, 200)
                self.assertTrue(res.read())
        with urlopen(self.url + "/", timeout=5) as res:
            pagina = res.read().decode("utf-8")
        for fragmento in ['id="tab-regla-falsa"', 'data-tab="tab-regla-falsa"', "regla-falsa.js", "regla-falsa.css"]:
            self.assertIn(fragmento, pagina)

    def test_vista_previa_compartida(self):
        estado, res = self.enviar("preview", {"funcion": "1/(x-1)"})
        self.assertEqual((estado, res), (200, {"latex": r"\frac{1}{x - 1}"}))


if __name__ == "__main__":
    unittest.main()
