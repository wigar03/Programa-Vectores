"""
Módulo de Enlace e Invocación con el Programa Anterior de Álgebra Lineal (Semana #3).
UAM - Facultad de Ingeniería y Arquitectura (FIA)

Este módulo cumple el requerimiento explícito:
"Nota: El programa debe ser capaz de llamar el programa que han elaborado anteriormente"

Permite:
1. Localizar la ruta del solucionador de matrices elaborado en la Semana #3.
2. Invocar su ejecución en un subproceso o importar sus funciones de resolución.
"""

import os
import sys
import subprocess
from typing import Optional, Tuple, List
from fractions import Fraction

from src.solver.gauss_solver import solve_gaussian_elimination, GaussResult


def buscar_ruta_programa_anterior() -> Optional[str]:
    """
    Busca la ubicación del programa elaborado en la Semana #3 en rutas relativas probables.
    """
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    # Raíz del proyecto actual
    raiz_proyecto = os.path.abspath(os.path.join(directorio_actual, "..", ".."))
    carpeta_semestre = os.path.abspath(os.path.join(raiz_proyecto, ".."))
    
    rutas_candidatas = [
        os.path.join(carpeta_semestre, "Semana  #3", "Programa Matriz Gauss", "main.py"),
        os.path.join(carpeta_semestre, "Semana  #3", "Solución de Sistemas de Ecuaciones Lineales por Eliminación por Filas", "Programa 1_Grupo 10.py"),
        os.path.join(raiz_proyecto, "external", "Programa Matriz Gauss", "main.py"),
    ]
    
    for ruta in rutas_candidatas:
        if os.path.exists(ruta):
            return ruta
            
    return None


def ejecutar_programa_anterior() -> Tuple[bool, str]:
    """
    Lanza la ejecución del programa anterior en un proceso independiente.
    
    Retorna:
        (exito: bool, mensaje: str)
    """
    ruta_prog = buscar_ruta_programa_anterior()
    if not ruta_prog:
        return (
            False,
            "No se encontró la ruta del programa anterior en el directorio ../Semana  #3/.\n"
            "Sin embargo, su motor algebraico está integrado directamente en este módulo."
        )
        
    try:
        # Intentar ejecutar con el mismo intérprete o con uv si está disponible
        dir_trabajo = os.path.dirname(ruta_prog)
        # Si existe uv en el entorno, usar uv run --python 3.13 para compatibilidad con Tkinter
        import shutil
        uv_bin = shutil.which("uv")
        if uv_bin:
            cmd = [uv_bin, "run", "--python", "3.13", "python", os.path.basename(ruta_prog)]
        else:
            cmd = [sys.executable, os.path.basename(ruta_prog)]
            
        subprocess.Popen(cmd, cwd=dir_trabajo)
        return (True, f"Programa anterior iniciado con éxito desde:\n{ruta_prog}")
    except Exception as e:
        return (False, f"Error al iniciar el programa anterior: {e}")


def resolver_sistema_con_programa_anterior(
    matriz_aumentada: List[List[Fraction]],
    usar_gauss_jordan: bool = True
) -> GaussResult:
    """
    Resuelve el sistema utilizando el motor algebraico de eliminación por filas
    desarrollado en la Semana #3.
    """
    return solve_gaussian_elimination(matriz_aumentada, use_gauss_jordan=usar_gauss_jordan)
