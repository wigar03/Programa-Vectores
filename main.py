"""
Punto de Entrada Principal - Calculadora de Álgebra Lineal
Universidad Americana (UAM) - Facultad de Ingeniería y Arquitectura (FIA)
Álgebra Lineal (MTM0120) - Proyecto Integrador: Calculadora de Vectores y Matrices

EJECUCIÓN:
    python main.py
(Inicia un servidor local ligero 100% Python estándar y abre la interfaz web en el navegador)
"""

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
from src.ui.web_server import iniciar_servidor_web


def main():
    parser = argparse.ArgumentParser(
        description="Calculadora de Álgebra Lineal: Vectores, Combinación Lineal, Matrices y Ecuaciones Ax = b"
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

    # Encabezado informativo institucional en terminal
    print("=" * 76)
    print(f"  {INSTITUCION}")
    print(f"  {FACULTAD} | {ASIGNATURA}")
    print(f"  {PROYECTO}")
    print(f"  Docente: {DOCENTE} | {GRUPO}")
    print("  Integrantes:")
    for m in INTEGRANTES:
        print(f"    • {m}")
    print("=" * 76)

    iniciar_servidor_web(puerto=args.port, abrir_navegador=not args.no_browser)


if __name__ == "__main__":
    main()
