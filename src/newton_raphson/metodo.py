"""Newton-Raphson: historial sin redondeo y paradas explícitas."""

import math

from ..biseccion.expresiones import Expresion, numero_real
from ..derivadas import derivada_simbolica, analizar_derivada


def preparar_funcion(funcion):
    return analizar_derivada(funcion)


def _evaluar(f, d, x):
    res = {"x0": x, "f_x0": None, "df_x0": None, "x1": None,
           "valido": False, "derivada_pequena": False}
    try:
        res["f_x0"] = f(x)
    except ValueError:
        return dict(res, estado="fuera_de_dominio")
    try:
        res["df_x0"] = d(x)
    except ValueError:
        if res["f_x0"] != 0:
            return dict(res, estado="derivada_no_definida")
    if res["f_x0"] == 0:
        return dict(res, estado="raiz_en_x0", valido=True, x1=x)
    if res["df_x0"] == 0:
        return dict(res, estado="derivada_nula")
    res["derivada_pequena"] = abs(res["df_x0"]) < 1e-6
    siguiente = x - res["f_x0"] / res["df_x0"]
    if not math.isfinite(siguiente):
        return dict(res, estado="divergencia")
    return dict(res, estado="valido", valido=True, x1=siguiente)


def evaluar_inicial(funcion, x0):
    f = Expresion(funcion)
    return _evaluar(f, derivada_simbolica(f), numero_real(x0, "El valor inicial"))


def resolver_newton(funcion, x0, tolerancia=1e-6, max_iteraciones=50, criterio="absoluto"):
    f = Expresion(funcion)
    d = derivada_simbolica(f)
    x = numero_real(x0, "El valor inicial")
    tol = numero_real(tolerancia, "La tolerancia")
    limite = numero_real(max_iteraciones, "El máximo de iteraciones")
    if tol <= 0:
        raise ValueError("La tolerancia debe ser mayor que cero.")
    if not limite.is_integer() or not 1 <= limite <= 1000:
        raise ValueError("El máximo de iteraciones debe ser un entero entre 1 y 1000.")
    if criterio not in ("absoluto", "relativo", "residuo"):
        raise ValueError("Criterio desconocido: use absoluto, relativo o residuo.")
    inicial = _evaluar(f, d, x)
    if inicial["f_x0"] is None:
        raise ValueError("La función no está definida en el valor inicial elegido.")
    pasos = [{"n": 0, "x": x, "fx": inicial["f_x0"], "dfx": inicial["df_x0"],
              "error_absoluto": None, "error_relativo": None}]
    avisos = []

    def resultado(motivo, convergio):
        p = pasos[-1]
        cumple = {"absoluto": p["error_absoluto"] is not None and p["error_absoluto"] < tol,
                  "relativo": p["error_relativo"] is not None and p["error_relativo"] < tol,
                  "residuo": abs(p["fx"]) < tol}
        return {**preparar_funcion(f.texto), "x0": pasos[0]["x"], "raiz": p["x"],
                "f_raiz": p["fx"], "residuo": abs(p["fx"]),
                "error_absoluto": p["error_absoluto"], "error_relativo": p["error_relativo"],
                "criterio": criterio, "tolerancia": tol, "cumple": cumple,
                "convergio": convergio, "motivo": motivo, "pasos": pasos,
                "iteraciones": len(pasos) - 1, "advertencias": avisos}

    if inicial["f_x0"] == 0:
        return resultado("raiz_en_x0", True)
    if criterio == "residuo" and abs(inicial["f_x0"]) < tol:
        return resultado("tolerancia", True)
    actual = inicial
    vistos = {x}
    for n in range(1, int(limite) + 1):
        if not actual["valido"]:
            return resultado(actual["estado"], False)
        if actual["derivada_pequena"]:
            avisos.append({"tipo": "derivada_pequena", "n": n - 1})
        nuevo = actual["x1"]
        siguiente = _evaluar(f, d, nuevo)
        if siguiente["f_x0"] is None:
            return resultado("fuera_de_dominio", False)
        ea = abs(nuevo - x)
        er = ea / abs(nuevo) if nuevo != 0 else None
        # Un infinito no se emite como JSON no estándar.
        ea = ea if math.isfinite(ea) else None
        er = er if er is not None and math.isfinite(er) else None
        if ea is not None and pasos[-1]["error_absoluto"] is not None and ea > pasos[-1]["error_absoluto"]:
            avisos.append({"tipo": "paso_creciente", "n": n})
        pasos.append({"n": n, "x": nuevo, "fx": siguiente["f_x0"], "dfx": siguiente["df_x0"],
                      "error_absoluto": ea, "error_relativo": er})
        if siguiente["f_x0"] == 0:
            return resultado("raiz_evaluada", True)
        if nuevo == x:
            return resultado("sin_progreso", False)
        if nuevo in vistos:
            return resultado("ciclo", False)
        valor = {"absoluto": ea, "relativo": er, "residuo": abs(siguiente["f_x0"])}[criterio]
        if valor is not None and valor < tol:
            return resultado("tolerancia", True)
        vistos.add(nuevo)
        x, actual = nuevo, siguiente
    return resultado("max_iteraciones", False)
