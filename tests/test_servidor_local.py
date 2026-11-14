import socket
import unittest
from urllib.parse import urlsplit
from urllib.request import urlopen

from src.ui.web_server import servidor_local


class TestServidorLocal(unittest.TestCase):
    def test_publica_interfaz_y_libera_puerto_al_salir(self):
        with servidor_local() as url:
            puerto = urlsplit(url).port
            self.assertEqual(urlsplit(url).hostname, "127.0.0.1")
            with urlopen(url, timeout=5) as respuesta:
                self.assertIn(b"tab-newton-raphson", respuesta.read())
        with socket.socket() as cliente:
            self.assertNotEqual(cliente.connect_ex(("127.0.0.1", puerto)), 0)

    def test_cierra_incluso_si_la_ventana_falla(self):
        with self.assertRaisesRegex(RuntimeError, "ventana"):
            with servidor_local() as url:
                puerto = urlsplit(url).port
                raise RuntimeError("ventana")
        with socket.socket() as cliente:
            self.assertNotEqual(cliente.connect_ex(("127.0.0.1", puerto)), 0)
