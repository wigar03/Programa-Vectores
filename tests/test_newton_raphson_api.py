import json
import threading
import unittest
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import AlgebraLinearHandler


class TestNewtonAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor=HTTPServer(('127.0.0.1',0),AlgebraLinearHandler)
        cls.hilo=threading.Thread(target=cls.servidor.serve_forever,daemon=True); cls.hilo.start()
        cls.base=f'http://127.0.0.1:{cls.servidor.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown(); cls.servidor.server_close(); cls.hilo.join()

    def enviar(self,ruta,datos):
        req=Request(self.base+'/api/newton-raphson/'+ruta,data=json.dumps(datos).encode(),headers={'Content-Type':'application/json'})
        try: r=urlopen(req)
        except HTTPError as e: r=e
        with r: return r.status,json.loads(r.read())

    def test_flujo_completo(self):
        status,d=self.enviar('preparar',dict(funcion='x^3-x-2',a=0,b=2.5))
        self.assertEqual(status,200);self.assertEqual(len(d['grafica']),401)
        self.assertIn('derivada_latex',d); self.assertNotIn('x0',d)
        status,p=self.enviar('evaluar',dict(funcion=d['funcion'],x0='3/2'))
        self.assertEqual(status,200);self.assertTrue(p['valido'])
        status,r=self.enviar('resolver',dict(funcion=d['funcion'],x0='3/2'))
        self.assertEqual(status,200);self.assertTrue(r['convergio'])
        self.assertEqual(r['pasos'][0]['x'],1.5)

    def test_grafica_separa_dominio(self):
        status,d=self.enviar('graficar',dict(funcion='1/x',a=-1,b=1,cantidad=5))
        self.assertEqual(status,200); self.assertIsNone(d['grafica'][2]['y'])

    def test_errores_y_ruta_desconocida(self):
        for ruta,datos in [('preparar',[]),('preparar',dict(funcion='x',a=2,b=1)),
                           ('graficar',dict(funcion='x',a=0,b=1,cantidad=2.5)),
                           ('evaluar',dict(funcion='x',x0='')),
                           ('resolver',dict(funcion='x',x0=1,tolerancia=-1))]:
            with self.subTest(ruta=ruta,datos=datos):
                status,d=self.enviar(ruta,datos); self.assertEqual(status,400);self.assertIn('error',d)
        self.assertEqual(self.enviar('desconocida',{})[0],404)

    def test_recursos_de_interfaz(self):
        with urlopen(self.base) as r: html=r.read().decode()
        for nombre in ('newton-raphson.js','newton-raphson.css','grafica-funciones.js'):
            with urlopen(self.base+'/'+nombre) as r: self.assertEqual(r.status,200)
            self.assertIn(nombre,html)
        self.assertIn('id="tab-newton-raphson"',html)
        self.assertIn('data-tab="tab-newton-raphson"',html)

    def test_secante_y_motor_independiente(self):
        req=Request(self.base+'/api/secante/resolver',data=json.dumps(dict(funcion='x^3-x-2',x0=1,x1=2)).encode(),headers={'Content-Type':'application/json'})
        with urlopen(req) as r: d=json.loads(r.read())
        self.assertTrue(d['convergio']);self.assertAlmostEqual(d['pasos'][0]['c'],4/3)
        req=Request(self.base+'/api/derivadas/derivar',data=b'{"funcion":"asin(x)"}',headers={'Content-Type':'application/json'})
        with urlopen(req) as r:d=json.loads(r.read())
        self.assertIn('arcsin',d['funcion_latex']);self.assertIn('sqrt',d['derivada'])
        with urlopen(self.base+'/secante.js') as r:self.assertEqual(r.status,200)
