import math
import unittest
from src.secante.metodo import resolver_secante
from src.derivadas import derivada_simbolica, analizar_derivada
from src.biseccion.expresiones import Expresion


class TestMotorDerivadas(unittest.TestCase):
    def test_inversas_y_regla_de_cadena(self):
        for nombre,esperado in [('asin',1/math.sqrt(.75)),('acos',-1/math.sqrt(.75)),('atan',.8)]:
            with self.subTest(nombre=nombre):
                self.assertAlmostEqual(derivada_simbolica(nombre+'(x)')(.5),esperado)
                self.assertIn('\\arc',analizar_derivada(nombre+'(x)')['funcion_latex'])
                self.assertAlmostEqual(derivada_simbolica(nombre+'(sin(x))')(.3),
                    (Expresion(nombre+'(sin(x))')(.300001)-Expresion(nombre+'(sin(x))')(.299999))/2e-6,places=6)

    def test_dominio_inversas(self):
        for f in ['asin(x)','acos(x)']:
            with self.assertRaises(ValueError): Expresion(f)(2)
            with self.assertRaises(ValueError): derivada_simbolica(f)(1)
        self.assertAlmostEqual(Expresion('atan(x)')(1),math.pi/4)

class TestSecante(unittest.TestCase):
    def test_presentacion(self):
        r=resolver_secante('x^3-x-2',1,2)
        self.assertTrue(r['convergio'])
        self.assertAlmostEqual(r['pasos'][0]['c'],4/3)
        esperados=[1.333333,1.462687,1.531169,1.520926,1.521376,1.521380]
        for p,x in zip(r['pasos'],esperados): self.assertAlmostEqual(p['c'],x,places=6)
        self.assertLess(r['residuo'],1e-6)
        for p,q in zip(r['pasos'][1:],r['pasos']):
            self.assertEqual((p['a'],p['b']),(q['b'],q['c']))

    def test_criterios_y_sin_cambio_de_signo(self):
        for c in ['absoluto','relativo','residuo']:
            r=resolver_secante('x^2-2','2','3',criterio=c)
            self.assertTrue(r['convergio']); self.assertTrue(r['cumple'][c])

    def test_raices_iniciales_y_cero(self):
        for a,b in [(0,1),(1,0)]:
            r=resolver_secante('x',a,b);self.assertEqual(r['iteraciones'],0);self.assertTrue(r['convergio'])
        r=resolver_secante('x',1,2); self.assertEqual(r['raiz'],0);self.assertIsNone(r['error_relativo'])

    def test_fallos_y_limites(self):
        r=resolver_secante('x^2+1',-1,1);self.assertEqual(r['motivo'],'denominador_nulo')
        r=resolver_secante('ln(x)+10',1,2);self.assertEqual(r['motivo'],'fuera_de_dominio')
        r=resolver_secante('x^3-x-2',1,2,max_iteraciones=1);self.assertFalse(r['convergio']);self.assertEqual(r['iteraciones'],1)
        for extras in [dict(x1=1),dict(x0=''),dict(x1=True),dict(tolerancia=0),dict(max_iteraciones=1.5),dict(criterio='otro')]:
            datos=dict(funcion='x^2-2',x0=1,x1=2);datos.update(extras)
            with self.subTest(extras=extras),self.assertRaises(ValueError):resolver_secante(**datos)
