"""Los recursos que necesita la página deben viajar dentro del paquete."""

import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit
from urllib.request import urlopen

from src.ui.web_server import servidor_local

WEB = Path(__file__).resolve().parents[1] / "src/ui/web"


class Recursos(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rutas = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "img", "link"):
            ruta = attrs.get("src") or attrs.get("href")
            if ruta:
                self.rutas.append(ruta)


class TestRecursosOffline(unittest.TestCase):
    def test_html_y_fuentes_se_sirven_sin_recursos_remotos(self):
        parser = Recursos()
        parser.feed((WEB / "index.html").read_text(encoding="utf-8"))
        rutas = set(parser.rutas)
        for css in WEB.rglob("*.css"):
            for ruta in re.findall(r"url\(['\"]?([^)'\"]+)", css.read_text(encoding="utf-8")):
                if ruta.startswith("data:"):
                    continue
                self.assertFalse(urlsplit(ruta).scheme, ruta)
                recurso = (css.parent / ruta).resolve()
                rutas.add(recurso.relative_to(WEB.resolve()).as_posix())
        with servidor_local() as url:
            for ruta in sorted(rutas):
                with self.subTest(ruta=ruta):
                    self.assertFalse(urlsplit(ruta).scheme, ruta)
                    with urlopen(url + "/" + ruta, timeout=5) as respuesta:
                        self.assertEqual(respuesta.status, 200)
                        self.assertTrue(respuesta.read())

    def test_integridad_de_recursos_de_terceros(self):
        vendor = WEB / "vendor"
        for linea in (vendor / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
            esperado, ruta = linea.split("  ", 1)
            with self.subTest(ruta=ruta):
                self.assertEqual(hashlib.sha256((vendor / ruta).read_bytes()).hexdigest(), esperado)
