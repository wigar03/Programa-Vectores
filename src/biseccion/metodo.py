"""Bisección con historial didáctico y aritmética de punto flotante.

Precondición: f debe ser continua en todo [a, b]. El cambio de signo
por sí solo no certifica continuidad ni unicidad de la raíz.
"""

import math

from .expresiones import Expresion, numero_real


CRITERIOS = {"intervalo", "relativo", "residuo"}


def resolver_biseccion(funcion, a, b, tolerancia=0.0001,
                      max_iteraciones=100, criterio="intervalo"):
    """Reduce el intervalo preservando signos opuestos, sin multiplicarlos.

    intervalo: ancho b-a <= tolerancia (cota de error en c: ancho/2).
    relativo: |c-c_anterior|/|c|*100 <= tolerancia, expresada en %.
    residuo: |f(c)| <= tolerancia; no es una cota de error en x.
    No se redondean los valores usados en las iteraciones.
    """
    f = Expresion(funcion)
    a, b = numero_real(a, "a"), numero_real(b, "b")
    tolerancia = numero_real(tolerancia, "La tolerancia")
    limite = numero_real(max_iteraciones, "El máximo de iteraciones")
    if a >= b or not math.isfinite(b - a):
        raise ValueError("El intervalo debe cumplir a < b y tener ancho finito.")
    if tolerancia <= 0:
        raise ValueError("La tolerancia debe ser mayor que cero.")
    if not limite.is_integer() or not 1 <= limite <= 1000:
        raise ValueError("El máximo de iteraciones debe ser un entero entre 1 y 1000.")
    if not isinstance(criterio, str) or criterio not in CRITERIOS:
        raise ValueError("Seleccione un criterio: intervalo, relativo o residuo.")

    inicial = [a, b]
    fa, fb = f(a), f(b)
    pasos = []

    def resultado(c, fc, motivo, convergio, cota):
        return {
            "funcion": f.texto, "intervalo_inicial": inicial,
            "intervalo_final": [a, b], "raiz": c, "f_raiz": fc,
            "residuo": abs(fc), "cota_error": cota,
            "criterio": criterio, "tolerancia": tolerancia,
            "convergio": convergio, "motivo": motivo,
            "iteraciones": len(pasos), "pasos": pasos,
        }

    if fa == 0 or fb == 0:
        c, fc = (a, fa) if fa == 0 else (b, fb)
        return resultado(c, fc, "raiz_en_extremo", True, 0.0)
    if (fa < 0) == (fb < 0):
        raise ValueError("Los extremos deben tener signos opuestos: f(a)·f(b) < 0. Pruebe otro intervalo.")

    anterior = None
    for numero in range(1, int(limite) + 1):
        ancho = b - a
        c = a + ancho / 2
        fc = f(c)
        error_abs = None if anterior is None else abs(c - anterior)
        error_rel = None
        if error_abs is not None and c != 0:
            porcentaje = error_abs / abs(c) * 100
            if math.isfinite(porcentaje):
                error_rel = porcentaje
        izquierda = (fa < 0) != (fc < 0)
        cota = max(c - a, b - c)
        estancado = c == a or c == b
        cumple = {
            "intervalo": ancho <= tolerancia,
            "relativo": error_rel is not None and error_rel <= tolerancia,
            "residuo": abs(fc) <= tolerancia,
        }[criterio]
        if fc == 0:
            motivo, convergio = "raiz_evaluada", True
        elif estancado:
            motivo, convergio = "precision_agotada", False
        elif cumple:
            motivo, convergio = "tolerancia", True
        elif numero == int(limite):
            motivo, convergio = "max_iteraciones", False
        else:
            motivo, convergio = None, False
        decision = "Finalizar" if motivo else ("b ← c" if izquierda else "a ← c")
        pasos.append({
            "numero": numero, "a": a, "b": b, "c": c,
            "fa": fa, "fb": fb, "fc": fc,
            "ancho": ancho, "cota_error": cota,
            "error_absoluto": error_abs, "error_relativo": error_rel,
            "signo_ac": "0" if fc == 0 else ("−" if izquierda else "+"),
            "decision": decision,
        })
        if motivo:
            return resultado(c, fc, motivo, convergio, 0.0 if fc == 0 else cota)
        if izquierda:
            b, fb = c, fc
        else:
            a, fa = c, fc
        anterior = c


def muestrear_funcion(funcion, a, b, cantidad=201):
    """Muestrea para la gráfica, separando los puntos fuera del dominio con null.

    La muestra es orientativa: no demuestra continuidad entre sus puntos.
    """
    f = Expresion(funcion)
    puntos = []
    for i in range(cantidad):
        t = i / (cantidad - 1)
        x = a * (1 - t) + b * t
        try:
            y = f(x)
        except ValueError:
            y = None
        puntos.append({"x": x, "y": y})
    return puntos
