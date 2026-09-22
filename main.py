"""
Punto de Entrada Principal - Calculadora de Álgebra Lineal
Universidad Americana (UAM) - Facultad de Ingeniería y Arquitectura (FIA)
Álgebra Lineal (MTM0120) - Proyecto Integrador: Calculadora de Vectores y Matrices

EJECUCIÓN:
1. Interfaz Web Interactiva Moderna (Por defecto):
       python main.py
   (Inicia un servidor local ligero 100% Python estándar y abre el navegador)

2. Interfaz Nativa de Escritorio (Tkinter):
       python main.py --tk
"""

import sys
import os
import shutil
import argparse

from src.core.config import (
    INSTITUCION,
    FACULTAD,
    ASIGNATURA,
    DOCENTE,
    PROYECTO,
    GRUPO,
    INTEGRANTES,
)


def _ejecutar_con_uv_fallback(script_path):
    uv_bin = shutil.which("uv")
    if uv_bin and os.environ.get("_ALGEBRA_UV_FALLBACK") != "1":
        print("Aviso: Iniciando interfaz gráfica nativa mediante entorno administrado ('uv')...\n")
        os.environ["_ALGEBRA_UV_FALLBACK"] = "1"
        os.execvp(
            uv_bin,
            [uv_bin, "run", "--python", "3.13", "python", os.path.abspath(script_path)] + sys.argv[1:],
        )
    else:
        print("ERROR: No se encontró la biblioteca gráfica Tkinter en el Python del sistema.", file=sys.stderr)
        print("Para usar la interfaz nativa en Arch/CachyOS, instale: sudo pacman -S tk", file=sys.stderr)
        print("O ejecute la versión web sin dependencias con: python main.py", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Calculadora de Álgebra Lineal: Vectores, Combinación Lineal, Matrices y Ecuaciones Ax = b"
    )
    parser.add_argument(
        "--tk",
        action="store_true",
        help="Iniciar la interfaz gráfica de escritorio nativa en Tkinter en lugar de la versión web.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Puerto para el servidor web interactivo (por defecto: 8080).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="No abrir automáticamente el navegador web al iniciar el servidor.",
    )
    args = parser.parse_args()

    # Imprimir encabezado informativo en consola
    print("=" * 76)
    print(f"  {INSTITUCION}")
    print(f"  {FACULTAD} | {ASIGNATURA}")
    print(f"  {PROYECTO}")
    print(f"  Docente: {DOCENTE} | {GRUPO}")
    print("  Integrantes:")
    for m in INTEGRANTES:
        print(f"    - {m}")
    print("=" * 76)

    if args.tk:
        try:
            import tkinter  # noqa: F401
            from src.ui.gui_tk import launch_gui_tk
            launch_gui_tk()
        except ImportError:
            _ejecutar_con_uv_fallback(__file__)
    else:
        from src.ui.web_server import iniciar_servidor_web
        iniciar_servidor_web(puerto=args.port, abrir_navegador=not args.no_browser)


if __name__ == "__main__":
    main()
