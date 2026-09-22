"""
Pruebas de Integración y Formato Matemático KaTeX para la API del Servidor Web.
UAM - Álgebra Lineal (MTM0120)
"""

import json
import urllib.request
import unittest


BASE_URL = "http://localhost:8080"


def post_json(path, payload):
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


class TestApiLatexFormatting(unittest.TestCase):
    def test_vector_suma(self):
        res = post_json("/api/vectores/operar", {
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
        res = post_json("/api/vectores/operar", {
            "operacion": "resta",
            "u": ["4", "-2"],
            "v": ["1", "3"]
        })
        self.assertIn("(\\vec{u} - \\vec{v})_i = u_i - v_i", res["explicacion_teorica"])
        for paso in res["desglose_componentes"]:
            self.assertIn("$", paso)

    def test_vector_escalar(self):
        res = post_json("/api/vectores/operar", {
            "operacion": "escalar_u",
            "u": ["2", "4", "-1"],
            "c": "3/2"
        })
        self.assertIn("(c \\cdot \\vec{u})_i = c \\cdot u_i", res["explicacion_teorica"])
        for paso in res["desglose_componentes"]:
            self.assertIn("$", paso)

    def test_vector_producto_punto(self):
        res = post_json("/api/vectores/operar", {
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
        res = post_json("/api/vectores/combinacion", {
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
        res = post_json("/api/vectores/combinacion", {
            "vectores": [["1", "0", "0"], ["0", "1", "0"]],
            "b": ["2", "3", "7"]
        })
        self.assertFalse(res["es_combinacion"])
        self.assertEqual(res["tipo_solucion"], "NO_COMBINACION")
        self.assertIn("\\notin \\operatorname{gen}", res["justificacion_teorica"])

    def test_matrices_multiplicacion(self):
        res = post_json("/api/matrices/operar", {
            "operacion": "multiplicacion",
            "A": [["1", "2"], ["3", "4"]],
            "B": [["5", "6"], ["7", "8"]]
        })
        self.assertIn("c_{ij} = \\sum_{k=1}^n", res["explicacion_teorica"])
        self.assertIn("matriz_resultado", res)
        for paso in res["pasos_multiplicacion"]:
            self.assertIn("c_{", paso)
            self.assertIn("\\cdot", paso)

    def test_ecuacion_matricial_scd(self):
        res = post_json("/api/ecuaciones/resolver", {
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


if __name__ == "__main__":
    unittest.main()
