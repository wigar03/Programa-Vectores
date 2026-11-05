"""Pruebas HTTP reales del nuevo contrato de bisección."""

import json
import threading
import unittest
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import AlgebraLinearHandler


class TestBiseccionApi(unittest.TestCase):
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

    def enviar(self, datos, ruta="/api/biseccion/resolver"):
        req = Request(self.url + ruta, json.dumps(datos).encode(),
                      {"Content-Type": "application/json"})
        try:
            respuesta = urlopen(req, timeout=5)
        except HTTPError as exc:
            respuesta = exc
        with respuesta:
            return respuesta.status, json.loads(respuesta.read())

    def test_resolucion_y_grafica(self):
        estado, res = self.enviar(dict(funcion="cos(x)-x", a="0", b="1",
                                      tolerancia="1e-8", max_iteraciones="100"))
        self.assertEqual(estado, 200)
        self.assertTrue(res["convergio"])
        self.assertEqual(res["funcion_latex"], r"\cos\left(x\right) - x")
        self.assertAlmostEqual(res["raiz"], .7390851332, places=7)
        self.assertEqual(len(res["grafica"]), 201)
        self.assertEqual(res["pasos"][0]["c"], .5)
        json.dumps(res, allow_nan=False)

    def test_no_convergencia_es_resultado_valido(self):
        estado, res = self.enviar(dict(funcion="x^2-2", a=1, b=2, max_iteraciones=1))
        self.assertEqual(estado, 200)
        self.assertFalse(res["convergio"])
        self.assertEqual(res["motivo"], "max_iteraciones")

    def test_errores_son_json_400(self):
        casos = [{}, [], None, {"funcion": "x^2+1", "a": 0, "b": 1},
                 {"funcion": "__import__('os')", "a": 0, "b": 1},
                 {"funcion": "1/x", "a": -1, "b": 1},
                 {"funcion": "x", "a": "nan", "b": 1}]
        for caso in casos:
            with self.subTest(caso=caso):
                estado, res = self.enviar(caso)
                self.assertEqual(estado, 400)
                self.assertIsInstance(res["error"], str)

    def test_extremo_y_fracciones(self):
        estado, res = self.enviar(dict(funcion="x-0.5", a="1/2", b=1))
        self.assertEqual(estado, 200)
        self.assertEqual(res["iteraciones"], 0)
        self.assertEqual(res["raiz"], .5)

    def test_recursos_de_interfaz_disponibles(self):
        for ruta in ["/", "/biseccion.js", "/biseccion.css", "/sidebar.js"]:
            with self.subTest(ruta=ruta), urlopen(self.url + ruta, timeout=5) as res:
                self.assertEqual(res.status, 200)
                self.assertTrue(res.read())

    def test_preview_representa_sin_evaluar_dominio(self):
        for funcion, latex in [("sqrt(x)", r"\sqrt{x}"),
                               ("1/(x-1)", r"\frac{1}{x - 1}")]:
            with self.subTest(funcion=funcion):
                estado, res = self.enviar({"funcion": funcion}, "/api/biseccion/preview")
                self.assertEqual(estado, 200)
                self.assertEqual(res["latex"], latex)
                self.assertNotIn("raiz", res)

    def test_preview_rechaza_codigo_y_expresiones_incompletas(self):
        for caso in [{}, [], None, {"funcion": "x^"}, {"funcion": "sqrt("},
                     {"funcion": "__import__('os')"}, {"funcion": r"\htmlClass{foo}{x}"}]:
            with self.subTest(caso=caso):
                estado, res = self.enviar(caso, "/api/biseccion/preview")
                self.assertEqual(estado, 400)
                self.assertIn("error", res)

    def test_muestrear_exitoso(self):
        estado, res = self.enviar(dict(funcion="cos(x)-x", a="-1", b="2", cantidad=51),
                                  ruta="/api/biseccion/muestrear")
        self.assertEqual(estado, 200)
        self.assertEqual(len(res["grafica"]), 51)
        self.assertAlmostEqual(res["grafica"][0]["x"], -1.0)
        self.assertAlmostEqual(res["grafica"][-1]["x"], 2.0)

    def test_muestrear_intervalo_invalido(self):
        for caso in [dict(funcion="x", a="2", b="1"), dict(funcion="1/x", a="-1", b="1", cantidad=5)]:
            with self.subTest(caso=caso):
                estado, res = self.enviar(caso, ruta="/api/biseccion/muestrear")
                if caso.get("a") == "2":
                    self.assertEqual(estado, 400)
                    self.assertIn("error", res)
                else:
                    # 1/x en -1 a 1: puntos fuera de dominio son válidos como null (200 OK con null en x=0)
                    self.assertEqual(estado, 200)
                    self.assertTrue(any(p["y"] is None for p in res["grafica"]))
