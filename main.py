"""
================================================================================
UNIVERSIDAD AMERICANA (UAM)
Facultad de Ingeniería y Arquitectura (FIA)
Álgebra Lineal (MTM0120) - Proyecto Integrador
Punto de Entrada Principal - Calculadora de Álgebra Lineal y Matrices
================================================================================
EJECUCIÓN:
    python main.py
(Inicia un servidor local ligero 100% Python estándar y abre la interfaz web interactiva)

MÓDULOS INTEGRADOS:
1. Operaciones Vectoriales en R^n (dimensión arbitraria n).
2. Evaluación formal de Combinación Lineal y Teorema de Rouché-Capelli.
3. Operaciones Matriciales Básicas (suma, resta, escalar, producto A·B y transpuesta A^T).
4. Inversa de una Matriz A^(-1) con métodos Gauss / Gauss-Jordan y verificación dual A·A^(-1) = I.
5. Resolución computacional de Ecuaciones Matriciales Ax = b y cálculo de residuo nulo.
6. Determinante de Matrices Cuadradas |A| con selección entre Cofactores (Laplace) y
   Descomposición LU (PA = LU), con análisis comparativo previo de eficiencia (O(n!) vs O(n³)).
================================================================================
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


# ==============================================================================
# BLOQUE 1: PROCESAMIENTO DE PARÁMETROS DE EJECUCIÓN
# ==============================================================================

def construir_parser_argumentos() -> argparse.ArgumentParser:
    """
    Configura y retorna el analizador de argumentos de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description="Calculadora de Álgebra Lineal: Vectores, Matrices, Inversa, Ax = b y Determinantes"
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
    return parser


# ==============================================================================
# BLOQUE 2: FUNCIÓN PRINCIPAL DE EJECUCIÓN (MAIN)
# ==============================================================================

def main():
    """
    Punto de entrada principal del sistema. Inicia el servidor web interactivo
    y despliega la aplicación completa con todos sus módulos algebraicos.
    """
    parser = construir_parser_argumentos()
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
    print("-" * 76)
    print("  MÓDULOS DE ÁLGEBRA LINEAL ACTIVOS:")
    print("    • Módulo 1: Operaciones con Vectores en R^n")
    print("    • Módulo 2: Combinación Lineal y Subespacios")
    print("    • Módulo 3: Operaciones con Matrices y Transpuesta A^T")
    print("    • Módulo 4: Inversa de una Matriz A^(-1) (Gauss y Gauss-Jordan)")
    print("    • Módulo 5: Ecuaciones Matriciales A·x = b")
    print("    • Módulo 6: Determinante |A| (Cofactores vs LU con Análisis de Eficiencia)")
    print("=" * 76)

    # Iniciar el servidor web interactivo
    iniciar_servidor_web(puerto=args.port, abrir_navegador=not args.no_browser)


if __name__ == "__main__":
    main()
