"""Contrato de entrada y aislamiento del evaluador del módulo de bisección."""

import math
import unittest

from src.biseccion.expresiones import Expresion, numero_real


class TestExpresiones(unittest.TestCase):
    def test_latex_polinomio(self):
        self.assertEqual(Expresion("x^4-5*x^3+0.5*x^2-11*x+10").latex(),
                         r"x^{4} - 5 \cdot x^{3} + 0.5 \cdot x^{2} - 11 \cdot x + 10")

    def test_latex_funciones(self):
        casos = {"sqrt(x)": r"\sqrt{x}", "abs(x)": r"\left|x\right|",
                 "ln(x)": r"\ln\left(x\right)", "log(x)": r"\log_{10}\left(x\right)",
                 "sin(pi*x)": r"\sin\left(\pi \cdot x\right)", "exp(x)": r"e^{x}"}
        for entrada, salida in casos.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(Expresion(entrada).latex(), salida)

    def test_latex_conserva_agrupacion_y_precedencia(self):
        casos = {"(x+1)^2": r"\left(x + 1\right)^{2}",
                 "x-(x+1)": r"x - \left(x + 1\right)",
                 "(x+1)/(x-1)": r"\frac{x + 1}{x - 1}",
                 "x*(x+1)": r"x \cdot \left(x + 1\right)",
                 "(-x)^2": r"\left(-x\right)^{2}",
                 "exp(x)^2": r"\left(e^{x}\right)^{2}",
                 "x**2**3": r"x^{2^{3}}"}
        for entrada, salida in casos.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(Expresion(entrada).latex(), salida)

    def test_latex_notacion_cientifica(self):
        self.assertEqual(Expresion("1e-10*x").latex(), r"1 \times 10^{-10} \cdot x")
        self.assertEqual(Expresion("1e-10^2").latex(), r"\left(1 \times 10^{-10}\right)^{2}")

    def test_polinomio_de_referencia(self):
        f = Expresion("x^4 - 5*x^3 + 0.5*x^2 - 11*x + 10")
        self.assertAlmostEqual(f(0.6), 2.6296)
        self.assertAlmostEqual(f(0.8), -0.6304)

    def test_funciones_y_precedencia(self):
        self.assertAlmostEqual(Expresion("cos(x)-x")(0), 1)
        self.assertAlmostEqual(Expresion("ln(e)+log(100)+sqrt(4)+abs(-2)+sin(pi/2)")(0), 8)
        self.assertEqual(Expresion("-x^2")(3), -9)
        self.assertEqual(Expresion("2**3**2")(0), 512)
        self.assertAlmostEqual(Expresion("exp(-x)")(1), math.exp(-1))

    def test_rechaza_codigo_y_sintaxis_no_admitida(self):
        for texto in ["", "2x", "x.y", "__import__('os')", "[x]", "True",
                      "x if x else 0", "sin(x, x)", "sqrt(x=1)", "lambda: 0",
                      "(1).__class__", "x%2", "1e999", "x" * 501]:
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                Expresion(texto)

    def test_dominio_y_limites_de_calculo(self):
        for texto, x in [("1/x", 0), ("sqrt(x)", -1), ("ln(x)", 0),
                         ("exp(x)", 1000), ("x^0.5", -1), ("2^1001", 0)]:
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                Expresion(texto)(x)

    def test_numeros_y_fracciones(self):
        self.assertEqual(numero_real("1/2"), 0.5)
        self.assertEqual(numero_real("1e-5"), 0.00001)
        for valor in [True, None, [], "", "1/0", "nan", "inf", float("inf")]:
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                numero_real(valor)
