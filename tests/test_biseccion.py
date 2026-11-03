"""
Pruebas unitarias para el módulo de bisección.
"""

import unittest

from src.ecuaciones.biseccion import resolver_biseccion


class TestMetodoBiseccion(unittest.TestCase):
    def test_raiz_polinomica_convergente(self):
        res = resolver_biseccion("x^3 - x - 2", "1", "2", "1e-8", 100)
        self.assertTrue(res.convergencia)
        self.assertAlmostEqual(res.raiz_aproximada, 1.5213797, places=6)
        self.assertLessEqual(abs(res.f_raiz), 1e-6)

    def test_raiz_trigonometrica_convergente(self):
        res = resolver_biseccion("cos(x) - x", "0", "1", "1e-8", 120)
        self.assertTrue(res.convergencia)
        self.assertAlmostEqual(res.raiz_aproximada, 0.739085, places=5)

    def test_intervalo_sin_cambio_de_signo(self):
        with self.assertRaises(ValueError):
            resolver_biseccion("x^2 + 1", "-1", "1", "1e-6", 50)

    def test_expresion_invalida(self):
        with self.assertRaises(ValueError):
            resolver_biseccion("__import__('os').system('echo x')", "0", "1", "1e-6", 10)


if __name__ == "__main__":
    unittest.main()
