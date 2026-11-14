"""Entrada de escritorio; reutiliza íntegramente la interfaz y la API local."""

import argparse
import ctypes
import logging
import os
from pathlib import Path
import sys
import threading

from src.core.version import APP_NAME, VERSION
from src.ui.web_server import servidor_local


def main():
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--diagnostico", type=Path, help="Guardar comprobación de escritorio en JSON y salir.")
    args = parser.parse_args()
    datos = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "CalculadoraAlgebraLineal"
    datos.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=datos / "desktop.log", level=logging.WARNING, encoding="utf-8")
    try:
        import webview

        with servidor_local() as url:
            ventana = webview.create_window(
                f"{APP_NAME} · {VERSION}", url, width=1280, height=850,
                min_size=(800, 600), hidden=bool(args.diagnostico),
            )
            cargada = threading.Event()
            ventana.events.loaded += cargada.set
            comprobar = None
            if args.diagnostico:
                from src.ui.diagnostico import comprobar_escritorio
                comprobar = lambda: comprobar_escritorio(ventana, cargada, url, args.diagnostico)
            webview.start(comprobar, gui="edgechromium" if sys.platform == "win32" else None,
                          storage_path=str(datos / "webview"), private_mode=False)
        if args.diagnostico:
            import json
            return 0 if json.loads(args.diagnostico.read_text(encoding="utf-8"))["ok"] else 1
        return 0
    except Exception:
        logging.exception("No se pudo iniciar la calculadora")
        if args.diagnostico:
            import json
            args.diagnostico.write_text(json.dumps({"ok": False, "error": "Consulte desktop.log"}), encoding="utf-8")
        elif sys.platform == "win32":
            ctypes.windll.user32.MessageBoxW(
                0, "No se pudo abrir la calculadora. Compruebe que Microsoft Edge WebView2 Runtime "
                f"esté instalado. Detalles: {datos / 'desktop.log'}", APP_NAME, 0x10,
            )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
