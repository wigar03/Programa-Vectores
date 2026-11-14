"""Verificación numérica independiente y casos de fallo del método abierto."""
import math
import random
import unittest

from src.biseccion.expresiones import Expresion
from src.newton_raphson.derivada import derivada_simbolica
from src.newton_raphson.metodo import evaluar_inicial, preparar_funcion, resolver_newton


class TestDerivada(unittest.TestCase):
    def test_reglas_con_valores_analiticos(self):
        casos = [('x^3-x-2', 1.5, 5.75), ('sin(x)', 0, 1), ('cos(x)', 0, 0),
                 ('tan(x)', 0, 1), ('exp(x)', 0, 1), ('ln(x)', 2, .5),
                 ('log(x)', 10, 1/(10*math.log(10))), ('sqrt(x)', 4, .25),
                 ('abs(x)', -2, -1), ('x^x', 2, 4*(math.log(2)+1)),
                 ('2^x', 3, 8*math.log(2)), ('x^-2', -2, .25),
                 ('x^0', 0, 0), ('pi*x', 1, math.pi), ('sqrt(0)', 0, 0)]
        for f, x, esperado in casos:
            with self.subTest(f=f):
                self.assertAlmostEqual(derivada_simbolica(f)(x), esperado)

    def test_derivada_en_dominio_singular(self):
        for f in ('abs(x)', 'sqrt(x)', 'ln(x)', '1/x'):
            with self.subTest(f=f), self.assertRaises(ValueError):
                derivada_simbolica(f)(0)

    def test_reglas_compuestas_con_diferencias_finitas(self):
        rng = random.Random(418)
        for _ in range(150):
            a,b,c = [rng.uniform(.5,3) for _ in range(3)]
            for texto in (f'sin({a}*x^2)+exp({b}*x)',
                          f'ln(x^2+{a})/({b}+x^2)',
                          f'(x^2+{a})^sin({c}*x)',
                          f'sqrt(x^2+{a})*cos({b}*x)'):
                x=rng.uniform(-1,1); h=1e-5; f=Expresion(texto)
                esperado=(f(x+h)-f(x-h))/(2*h)
                self.assertAlmostEqual(derivada_simbolica(f)(x), esperado,
                                       delta=1e-6*max(1,abs(esperado)), msg=texto)

    def test_entrada_segura_y_latex(self):
        for f in ("__import__('os')", 'x.real', 'x[0]', 'lambda: 1', '[x]', 'a*x'):
            with self.subTest(f=f), self.assertRaises(ValueError):
                preparar_funcion(f)
        self.assertIn('x^{2}', preparar_funcion('x^3-x-2')['derivada_latex'])


class TestNewton(unittest.TestCase):
    def test_presentacion_y_primera_iteracion(self):
        p=evaluar_inicial('x^3-x-2','3/2')
        self.assertEqual((p['f_x0'],p['df_x0']),(-.125,5.75))
        self.assertAlmostEqual(p['x1'],1.5217391304347827)
        r=resolver_newton('x^3-x-2',1.5)
        self.assertTrue(r['convergio']); self.assertEqual(r['iteraciones'],3)
        self.assertAlmostEqual(r['raiz'],1.5213797068045751)
        self.assertLess(r['residuo'],1e-12)
        self.assertEqual(r['pasos'][0]['error_absoluto'],None)
        for p,q in zip(r['pasos'][1:],r['pasos']):
            self.assertEqual(p['x'],q['x']-q['fx']/q['dfx'])
            self.assertEqual(p['error_relativo'],p['error_absoluto']/abs(p['x']))

    def test_criterios(self):
        for criterio in ('absoluto','relativo','residuo'):
            r=resolver_newton('x^3-2*x-5',2,criterio=criterio)
            self.assertTrue(r['convergio']); self.assertTrue(r['cumple'][criterio])
            self.assertAlmostEqual(r['raiz'],2.0945514815423,places=6)

    def test_estados_de_fallo(self):
        for f,x,motivo in [('x^2-4',0,'derivada_nula'),('sqrt(x)-1',0,'derivada_no_definida'),
                           ('ln(x)',3,'fuera_de_dominio'),('x^3-2*x+2',0,'ciclo'),
                           ('1e308*x+1e308',1,'fuera_de_dominio')]:
            with self.subTest(f=f):
                if f.startswith('1e308'):
                    with self.assertRaises(ValueError): resolver_newton(f,x)
                else:
                    r=resolver_newton(f,x); self.assertFalse(r['convergio']); self.assertEqual(r['motivo'],motivo)

    def test_derivada_pequena_y_limite(self):
        r=resolver_newton('x^3-1',.0001,max_iteraciones=1)
        self.assertEqual(r['motivo'],'max_iteraciones')
        self.assertEqual(r['advertencias'][0]['tipo'],'derivada_pequena')

    def test_raiz_inicial_incluso_con_derivada_nula(self):
        for f in ('x^2','abs(x)','sqrt(x)'):
            r=resolver_newton(f,0)
            self.assertEqual(r['motivo'],'raiz_en_x0'); self.assertEqual(r['iteraciones'],0)
            self.assertIsNone(r['error_relativo'])

    def test_raiz_cero_no_inventa_error_relativo(self):
        r=resolver_newton('x',1)
        self.assertEqual(r['raiz'],0); self.assertIsNone(r['error_relativo'])

    def test_validacion(self):
        for extras in ({'x0':''},{'x0':True},{'x0':'1/0'},{'tolerancia':0},
                       {'tolerancia':'NaN'},{'max_iteraciones':1.5},
                       {'max_iteraciones':1001},{'criterio':'porcentaje'}):
            datos=dict(funcion='x^2-2',x0=1);datos.update(extras)
            with self.subTest(extras=extras), self.assertRaises(ValueError): resolver_newton(**datos)

    def test_cambio_pequeno_no_implica_residuo_pequeno(self):
        r=resolver_newton('1e15*(x^2-2)',1,tolerancia=.01)
        self.assertTrue(r['cumple']['absoluto']); self.assertFalse(r['cumple']['residuo'])

    def test_tolerancia_estricta(self):
        r=resolver_newton('x^2-2',1,tolerancia=.5,max_iteraciones=1)
        self.assertFalse(r['convergio']); self.assertEqual(r['error_absoluto'],.5)

    def test_paso_no_finito_y_precision_agotada(self):
        r=resolver_newton('1e308+1e-308*x',0)
        self.assertEqual(r['motivo'],'divergencia'); self.assertFalse(r['convergio'])
        r=resolver_newton('x^2-5',1,tolerancia=1e-100)
        self.assertEqual(r['motivo'],'sin_progreso'); self.assertFalse(r['convergio'])
