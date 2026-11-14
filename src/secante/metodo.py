"""Secante con dos puntos manuales, historial y control de fallos numéricos."""
import math
from ..biseccion.expresiones import Expresion, numero_real


def resolver_secante(funcion, x0, x1, tolerancia=1e-6, max_iteraciones=50, criterio="absoluto"):
    f = Expresion(funcion)
    a, b = numero_real(x0, "x_0"), numero_real(x1, "x_1")
    tol = numero_real(tolerancia, "La tolerancia")
    limite = numero_real(max_iteraciones, "El máximo de iteraciones")
    if a == b:
        raise ValueError("Elija dos valores iniciales distintos.")
    if tol <= 0 or not limite.is_integer() or not 1 <= limite <= 1000:
        raise ValueError("Use tolerancia positiva y un máximo entero entre 1 y 1000.")
    if criterio not in ("absoluto", "relativo", "residuo"):
        raise ValueError("Use el criterio absoluto, relativo o residuo.")
    fa, fb = f(a), f(b)
    pasos = []
    avisos = []
    ea = er = None
    iniciales = [a,b]

    def resultado(motivo, convergio):
        return {"funcion": f.texto, "funcion_latex": f.latex(), "iniciales": iniciales,
                "raiz": b, "f_raiz": fb, "residuo": abs(fb), "error_absoluto": ea,
                "error_relativo": er, "iteraciones": len(pasos), "pasos": pasos,
                "convergio": convergio, "motivo": motivo, "advertencias": avisos,
                "tolerancia": tol, "criterio": criterio,
                "cumple": {"absoluto": ea is not None and ea < tol,
                           "relativo": er is not None and er < tol, "residuo": abs(fb) < tol}}
    if fa == 0:
        b, fb = a, fa
        return resultado("raiz_inicial", True)
    if fb == 0:
        return resultado("raiz_inicial", True)
    if criterio == "residuo" and abs(fb) < tol:
        return resultado("tolerancia", True)
    vistos = {(a,b)}
    for n in range(1, int(limite)+1):
        den = fb-fa
        if den == 0:
            return resultado("denominador_nulo", False)
        if not math.isfinite(den):
            return resultado("divergencia", False)
        # Escala relativa: una diferencia pequeña frente a las evaluaciones.
        if abs(den) < 1e-12*max(abs(fa),abs(fb)):
            avisos.append(n)
        c = b - (fb/den)*(b-a)
        if not math.isfinite(c):
            return resultado("divergencia", False)
        try:
            fc = f(c)
        except ValueError:
            return resultado("fuera_de_dominio", False)
        ea = abs(c-b)
        er = ea/abs(c) if c != 0 else None
        ea = ea if math.isfinite(ea) else None
        er = er if er is not None and math.isfinite(er) else None
        pasos.append({"n": n, "a": a, "b": b, "fa": fa, "fb": fb, "c": c,
                      "fc": fc, "denominador": den, "error_absoluto": ea, "error_relativo": er})
        sin_progreso = c == b
        a,b,fa,fb = b,c,fb,fc
        if fc == 0:
            return resultado("raiz_evaluada", True)
        if sin_progreso:
            return resultado("sin_progreso", False)
        if (a,b) in vistos:
            return resultado("ciclo", False)
        valor = {"absoluto":ea,"relativo":er,"residuo":abs(fc)}[criterio]
        if valor is not None and valor < tol:
            return resultado("tolerancia", True)
        vistos.add((a,b))
    return resultado("max_iteraciones", False)
