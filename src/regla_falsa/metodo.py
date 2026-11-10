"""Regla falsa (regula falsi) con historial didáctico y aritmética de punto flotante.

Método cerrado: parte de un intervalo [x_l, x_u] con f(x_l)·f(x_u) < 0 y sustituye
el punto medio de la bisección por el corte con el eje X de la recta que une
(x_l, f(x_l)) y (x_u, f(x_u)). Reutiliza el evaluador seguro del módulo de bisección.
"""

import math

from ..biseccion.expresiones import Expresion, numero_real

# Iteraciones consecutivas con el mismo extremo fijo a partir de las cuales se avisa.
UMBRAL_ESTANCAMIENTO = 10


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


def resolver_regla_falsa(funcion, xl, xu, tolerancia=0.0001, max_iteraciones=100):
    """Itera la falsa posición hasta que ε_a ≤ tolerancia o se agota el límite.

    ε_a = |x_r − x_r_anterior| / |x_r| · 100 %; la tolerancia se expresa en %.
    Reemplazo: si f(x_l)·f(x_r) < 0, x_u ← x_r; si es > 0, x_l ← x_r; si es 0, x_r es raíz.
    No se redondean los valores usados en las iteraciones.

    Estancamiento: en curvas muy convexas o cóncavas un extremo queda fijo y la
    convergencia se vuelve unilateral y lenta. Se informa el extremo retenido durante
    la racha más larga cuando alcanza UMBRAL_ESTANCAMIENTO iteraciones seguidas.
    """
    f = Expresion(funcion)
    tolerancia = numero_real(tolerancia, "La tolerancia")
    limite = numero_real(max_iteraciones, "El máximo de iteraciones")
    if tolerancia <= 0:
        raise ValueError("La tolerancia debe ser mayor que cero.")
    if not limite.is_integer() or not 1 <= limite <= 1000:
        raise ValueError("El máximo de iteraciones debe ser un entero entre 1 y 1000.")
    previa = validar_intervalo(f, xl, xu)
    xl, xu, f_xl, f_xu = previa["xl"], previa["xu"], previa["f_xl"], previa["f_xu"]
    inicial = [xl, xu]
    pasos = []
    racha = {"extremo": None, "actual": 0, "mayor": 0, "extremo_mayor": None}

    def resultado(xr, f_xr, motivo, convergio, error):
        estancamiento = None
        if racha["mayor"] >= UMBRAL_ESTANCAMIENTO:
            estancamiento = {"extremo": racha["extremo_mayor"], "iteraciones": racha["mayor"]}
        return {
            "funcion": f.texto, "intervalo_inicial": inicial,
            "intervalo_final": [xl, xu], "raiz": xr, "f_raiz": f_xr,
            "residuo": abs(f_xr), "error_relativo": error,
            "tolerancia": tolerancia, "convergio": convergio, "motivo": motivo,
            "estancamiento": estancamiento,
            "iteraciones": len(pasos), "pasos": pasos,
        }

    if previa["raiz_en_extremo"]:
        xr, f_xr = (xl, f_xl) if previa["raiz_en_extremo"] == "xl" else (xu, f_xu)
        return resultado(xr, f_xr, "raiz_en_extremo", True, None)
    if not previa["cumple"]:
        raise ValueError("Los extremos deben tener signos opuestos: f(x_l)·f(x_u) < 0. Pruebe otro intervalo.")

    anterior = None
    for numero in range(1, int(limite) + 1):
        xr = falsa_posicion(xl, xu, f_xl, f_xu)
        # El redondeo puede sacar a x_r del intervalo abierto; ya no hay progreso posible.
        agotado = not math.isfinite(xr) or not xl < xr < xu
        if agotado:
            xr = min(max(xr, xl), xu) if math.isfinite(xr) else xu
        f_xr = f(xr)
        error_abs = None if anterior is None else abs(xr - anterior)
        error_rel = None
        if error_abs is not None and xr != 0:
            porcentaje = error_abs / abs(xr) * 100
            if math.isfinite(porcentaje):
                error_rel = porcentaje
        signo = _signo_producto(f_xl, f_xr)
        if f_xr == 0:
            motivo, convergio = "raiz_evaluada", True
        elif error_rel is not None and error_rel <= tolerancia:
            motivo, convergio = "tolerancia", True
        elif agotado:
            motivo, convergio = "precision_agotada", False
        elif numero == int(limite):
            motivo, convergio = "max_iteraciones", False
        else:
            motivo, convergio = None, False
        reemplazo = None if signo == 0 else ("xu" if signo < 0 else "xl")
        pasos.append({
            "numero": numero, "xl": xl, "xu": xu, "f_xl": f_xl, "f_xu": f_xu,
            "xr": xr, "f_xr": f_xr,
            "error_absoluto": error_abs, "error_relativo": error_rel,
            "signo_producto": {-1: "−", 0: "0", 1: "+"}[signo],
            "decision": "Finalizar" if motivo else ("x_u ← x_r" if signo < 0 else "x_l ← x_r"),
        })
        # El intervalo final incorpora el último reemplazo: es el encierro más estrecho conocido.
        if reemplazo == "xu":
            xu, f_xu = xr, f_xr
        elif reemplazo == "xl":
            xl, f_xl = xr, f_xr
        if reemplazo:
            fijo = "xl" if reemplazo == "xu" else "xu"
            racha["actual"] = racha["actual"] + 1 if fijo == racha["extremo"] else 1
            racha["extremo"] = fijo
            if racha["actual"] > racha["mayor"]:
                racha["mayor"], racha["extremo_mayor"] = racha["actual"], fijo
        if motivo:
            return resultado(xr, f_xr, motivo, convergio, error_rel)
        anterior = xr
