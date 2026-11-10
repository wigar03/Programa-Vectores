"""Regla falsa (regula falsi) con historial didáctico y aritmética de punto flotante.

Método cerrado: parte de un intervalo [x_l, x_u] con f(x_l)·f(x_u) < 0 y sustituye
el punto medio de la bisección por el corte con el eje X de la recta que une
(x_l, f(x_l)) y (x_u, f(x_u)). Reutiliza el evaluador seguro del módulo de bisección.
"""

import math

from ..biseccion.expresiones import Expresion, numero_real


def falsa_posicion(xl, xu, f_xl, f_xu):
    """x_r = x_u − f(x_u)·(x_l − x_u) / (f(x_l) − f(x_u)), por triángulos semejantes."""
    return xu - f_xu * (xl - xu) / (f_xl - f_xu)


def _signo_producto(u, v):
    """Signo de u·v comparando signos, sin multiplicar: evita desbordes y subdesbordes."""
    if u == 0 or v == 0:
        return 0
    return -1 if (u < 0) != (v < 0) else 1


def _leer_intervalo(xl, xu):
    xl, xu = numero_real(xl, "x_l"), numero_real(xu, "x_u")
    if xl >= xu or not math.isfinite(xu - xl):
        raise ValueError("El intervalo debe cumplir x_l < x_u y tener ancho finito.")
    return xl, xu


def validar_intervalo(funcion, xl, xu):
    """Comprueba la condición previa obligatoria f(x_l)·f(x_u) < 0.

    Con f continua en [x_l, x_u], el Teorema del Valor Intermedio garantiza al menos
    una raíz en el intervalo. La continuidad se analiza aparte (véase continuidad.py).
    Un intervalo sin cambio de signo no es un error de entrada: se devuelve con
    cumple=False para que la interfaz pueda mostrar las evaluaciones.
    """
    f = funcion if isinstance(funcion, Expresion) else Expresion(funcion)
    xl, xu = _leer_intervalo(xl, xu)
    f_xl, f_xu = f(xl), f(xu)
    signo = _signo_producto(f_xl, f_xu)
    producto = f_xl * f_xu
    raiz_en_extremo = "xl" if f_xl == 0 else ("xu" if f_xu == 0 else None)
    if raiz_en_extremo:
        estado = "raiz_en_extremo"
    elif signo < 0:
        estado = "valido"
    else:
        estado = "sin_cambio_de_signo"
    return {
        "funcion": f.texto, "xl": xl, "xu": xu, "f_xl": f_xl, "f_xu": f_xu,
        # El producto solo se informa; la decisión usa los signos.
        "producto": producto if math.isfinite(producto) else None,
        "signo_producto": {-1: "negativo", 0: "cero", 1: "positivo"}[signo],
        "cumple": signo < 0, "raiz_en_extremo": raiz_en_extremo, "estado": estado,
    }
