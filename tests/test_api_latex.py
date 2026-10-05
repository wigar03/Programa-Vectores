"""
Pruebas de Integración y Formato Matemático KaTeX para la API del Servidor Web.
UAM - Álgebra Lineal (MTM0120)
"""

import json
import socket
import threading
import urllib.request
import unittest
from http.server import HTTPServer

from src.ui.web_server import AlgebraLinearHandler


class TestApiLatexFormatting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Encontrar puerto libre de manera segura
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            cls.port = s.getsockname()[1]

        cls.server = HTTPServer(("127.0.0.1", cls.port), AlgebraLinearHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def post_json(self, path, payload):
        url = f"{self.base_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def test_vector_suma(self):
        res = self.post_json("/api/vectores/operar", {
            "operacion": "suma",
            "u": ["1/2", "3"],
            "v": ["-1/4", "5"]
        })
        self.assertIn("$\\mathbb{R}^n$", res["explicacion_teorica"])
        self.assertIn("(\\vec{u} + \\vec{v})_i = u_i + v_i", res["explicacion_teorica"])
        for paso in res["desglose_componentes"]:
            self.assertTrue(paso.startswith("Componente "))
            self.assertIn("$", paso)

    def test_vector_resta(self):
        res = self.post_json("/api/vectores/operar", {
            "operacion": "resta",
            "u": ["4", "-2"],
            "v": ["1", "3"]
        })
        self.assertIn("(\\vec{u} - \\vec{v})_i = u_i - v_i", res["explicacion_teorica"])
        for paso in res["desglose_componentes"]:
            self.assertIn("$", paso)

    def test_vector_escalar(self):
        res = self.post_json("/api/vectores/operar", {
            "operacion": "escalar_u",
            "u": ["2", "4", "-1"],
            "c": "3/2"
        })
        self.assertIn("(c \\cdot \\vec{u})_i = c \\cdot u_i", res["explicacion_teorica"])
        for paso in res["desglose_componentes"]:
            self.assertIn("$", paso)

    def test_vector_producto_punto(self):
        res = self.post_json("/api/vectores/operar", {
            "operacion": "producto_punto",
            "u": ["1", "2", "3"],
            "v": ["4", "5", "6"]
        })
        exp = res["explicacion_teorica"]
        self.assertIn("\\vec{u} \\cdot \\vec{v}", exp)
        self.assertIn("\\sum_{i=1}^{n}", exp)
        self.assertIn("\\|\\vec{u}\\|^2", exp)
        self.assertIn("\\|\\vec{v}\\|^2", exp)
        self.assertNotIn("sum(", exp)
        self.assertNotIn("||u||", exp)
        for paso in res["desglose_componentes"]:
            self.assertIn("$u_{", paso)
            self.assertIn("\\cdot", paso)

    def test_combinacion_lineal_scd(self):
        res = self.post_json("/api/vectores/combinacion", {
            "vectores": [["1", "2"], ["3", "4"]],
            "b": ["5", "6"]
        })
        self.assertTrue(res["es_combinacion"])
        self.assertEqual(res["tipo_solucion"], "UNICA")
        self.assertIn("\\vec{b}", res["justificacion_teorica"])
        self.assertIn("\\operatorname{rg}", res["justificacion_teorica"])
        for comp in res["comprobacion"]:
            self.assertIn("$", comp)
            self.assertIn("\\rightarrow", comp)
        for paso in res["pasos"]:
            self.assertIn("$", paso["title"])

    def test_combinacion_lineal_si(self):
        res = self.post_json("/api/vectores/combinacion", {
            "vectores": [["1", "0", "0"], ["0", "1", "0"]],
            "b": ["2", "3", "7"]
        })
        self.assertFalse(res["es_combinacion"])
        self.assertEqual(res["tipo_solucion"], "NO_COMBINACION")
        self.assertIn("\\notin \\operatorname{gen}", res["justificacion_teorica"])

    def test_matrices_multiplicacion(self):
        res = self.post_json("/api/matrices/operar", {
            "operacion": "multiplicacion",
            "A": [["1", "2"], ["3", "4"]],
            "B": [["5", "6"], ["7", "8"]]
        })
        self.assertIn("c_{ij} = \\sum_{k=1}^n", res["explicacion_teorica"])
        self.assertIn("matriz_resultado", res)
        for paso in res["pasos_multiplicacion"]:
            self.assertIn("c_{", paso)
            self.assertIn("\\cdot", paso)

    def test_matrices_transpuesta_analisis(self):
        res = self.post_json("/api/matrices/operar", {
            "operacion": "transpuesta_a",
            "A": [["1", "2"], ["2", "1"]]
        })
        self.assertEqual(res["dimensiones_original"], "2 \\times 2")
        self.assertEqual(res["dimensiones_transpuesta"], "2 \\times 2")
        self.assertTrue(res["es_cuadrada"])
        self.assertTrue(res["es_simetrica"])
        self.assertEqual(res["traza"], "2")
        self.assertTrue(len(res["propiedades"]) > 0)
        self.assertTrue(len(res["pasos_mapeo"]) > 0)
        for prop in res["propiedades"]:
            self.assertNotIn("pdf", prop.lower())
            self.assertNotIn("diapositiva", prop.lower())
            partes = prop.split("$")
            for idx, parte in enumerate(partes):
                if idx % 2 == 0:
                    self.assertNotIn("\\cdot", parte)
                    self.assertNotIn("\\rightarrow", parte)
                    self.assertNotIn("\\frac", parte)
                    self.assertNotIn("\\neq", parte)
                    self.assertNotIn("\\dim", parte)
                    self.assertNotIn("\\implies", parte)
                    self.assertNotIn("\\operatorname", parte)

    def test_matrices_inversa_2x2_api(self):
        res = self.post_json("/api/matrices/inversa", {
            "A": [["2", "5"], ["-3", "-7"]],
            "metodo": "gauss_jordan"
        })
        self.assertTrue(res["es_invertible"])
        self.assertEqual(res["orden_n"], 2)
        self.assertEqual(res["determinante_2x2"], "1")
        self.assertEqual(res["matriz_inversa"], [["-7", "-5"], ["3", "2"]])
        self.assertTrue(res["residuo_cero"])
        self.assertTrue(len(res["verificacion_A_por_Ainv"]) > 0)
        self.assertTrue(len(res["verificacion_Ainv_por_A"]) > 0)
        for v in res["verificacion_A_por_Ainv"]:
            self.assertIn("$", v)
            self.assertIn("(A \\cdot A^{-1})", v)
            self.assertIn("✓ Correcto", v)
            self.assertNotIn("pdf", v.lower())
            self.assertNotIn("diapositiva", v.lower())
            partes = v.split("$")
            for idx, parte in enumerate(partes):
                if idx % 2 == 0:
                    self.assertNotIn("\\cdot", parte)
                    self.assertNotIn("\\rightarrow", parte)
                    self.assertNotIn("\\frac", parte)
        for v in res["verificacion_Ainv_por_A"]:
            self.assertIn("$", v)
            self.assertIn("(A^{-1} \\cdot A)", v)
            self.assertIn("✓ Correcto", v)
            self.assertNotIn("pdf", v.lower())
            self.assertNotIn("diapositiva", v.lower())
            partes = v.split("$")
            for idx, parte in enumerate(partes):
                if idx % 2 == 0:
                    self.assertNotIn("\\cdot", parte)
                    self.assertNotIn("\\rightarrow", parte)
                    self.assertNotIn("\\frac", parte)

    def test_matrices_inversa_3x3_gauss_api(self):
        res = self.post_json("/api/matrices/inversa", {
            "A": [["0", "1", "2"], ["1", "0", "3"], ["4", "-3", "8"]],
            "metodo": "gauss"
        })
        self.assertTrue(res["es_invertible"])
        self.assertEqual(res["orden_n"], 3)
        self.assertEqual(res["matriz_inversa"], [
            ["-9/2", "7", "-3/2"],
            ["-2", "4", "-1"],
            ["3/2", "-2", "1/2"]
        ])

    def test_matrices_inversa_singular_api(self):
        res = self.post_json("/api/matrices/inversa", {
            "A": [["2", "3", "4"], ["2", "3", "4"], ["2", "3", "4"]],
            "metodo": "gauss_jordan"
        })
        self.assertFalse(res["es_invertible"])
        self.assertIsNone(res["matriz_inversa"])
        self.assertIn("singular", res["mensaje_diagnostico"].lower())

    def test_ecuacion_matricial_scd(self):
        res = self.post_json("/api/ecuaciones/resolver", {
            "A": [["2", "1"], ["1", "-1"]],
            "b": ["8", "1"]
        })
        self.assertEqual(res["tipo_sistema"], "SCD")
        self.assertIn("\\operatorname{rg}(A)", res["descripcion_sistema"])
        for verif in res["verificacion"]:
            self.assertIn("$", verif)
            self.assertIn("✓ Satisface", verif)
            self.assertIn("\\rightarrow", verif)
        for paso in res["pasos"]:
            self.assertIn("$", paso["title"])

    def test_determinante_api_lu_y_cofactores(self):
        # Probar cálculo de determinante 3x3 por LU
        A = [["1", "2", "3"], ["0", "1", "4"], ["5", "6", "0"]]
        res_lu = self.post_json("/api/matrices/determinante", {
            "A": A,
            "metodo": "lu"
        })
        self.assertEqual(res_lu["determinante"], "1")
        self.assertTrue(res_lu["es_invertible"])
        self.assertEqual(res_lu["orden_n"], 3)
        self.assertGreater(len(res_lu["pasos"]), 0)

        for p in res_lu["pasos"]:
            for text_field in [p["titulo"], p["descripcion"]] + p["detalles"]:
                self.assertNotIn("pdf", text_field.lower())
                self.assertNotIn("diapositiva", text_field.lower())
                partes = text_field.split("$")
                for idx, parte in enumerate(partes):
                    if idx % 2 == 0:
                        self.assertNotIn("\\det", parte)
                        self.assertNotIn("\\cdot", parte)
                        self.assertNotIn("\\prod", parte)
                        self.assertNotIn("\\leftrightarrow", parte)
                        self.assertNotIn("\\leftarrow", parte)
                        self.assertNotIn("\\frac", parte)

        # Probar cálculo por cofactores
        res_cof = self.post_json("/api/matrices/determinante", {
            "A": A,
            "metodo": "cofactores"
        })
        self.assertEqual(res_cof["determinante"], "1")
        self.assertTrue(res_cof["es_invertible"])
        for p in res_cof["pasos"]:
            for text_field in [p["titulo"], p["descripcion"]] + p["detalles"]:
                self.assertNotIn("pdf", text_field.lower())
                self.assertNotIn("diapositiva", text_field.lower())
                partes = text_field.split("$")
                for idx, parte in enumerate(partes):
                    if idx % 2 == 0:
                        self.assertNotIn("\\det", parte)
                        self.assertNotIn("\\cdot", parte)
                        self.assertNotIn("\\frac", parte)

    def test_eficiencia_determinante_api(self):
        # Probar endpoint de análisis de eficiencia previo
        res_ef = self.post_json("/api/matrices/eficiencia-determinante", {
            "n": 4
        })
        self.assertEqual(res_ef["orden_n"], 4)
        self.assertEqual(res_ef["metodo_recomendado"], "lu")
        self.assertIn("O(n!)", res_ef["complejidad_cofactores"])
        self.assertIn("O(n³)", res_ef["complejidad_lu"])
        self.assertNotIn("pdf", res_ef["justificacion"].lower())
        self.assertNotIn("diapositiva", res_ef["justificacion"].lower())


if __name__ == "__main__":
    unittest.main()
