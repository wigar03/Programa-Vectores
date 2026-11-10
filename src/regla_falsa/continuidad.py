"""Análisis numérico de continuidad de f en una región [a, b].

La regla falsa exige continuidad en el intervalo: un cambio de signo también puede
deberse a un salto o a una asíntota vertical. Aquí se muestrea la función y se refina
cada indicio para clasificarlo. Es una exploración numérica, no una demostración:
puede pasar por alto discontinuidades más estrechas que la separación entre muestras.
"""

import math

from ..biseccion.expresiones import Expresion, numero_real

MUESTRAS = 400          # subdivisiones de la región explorada
_REFINAMIENTOS = 48     # bisecciones al estrechar un indicio
_MAX_CANDIDATOS = 25    # acota el trabajo en funciones muy oscilantes
_MAX_RAICES_EXACTAS = 20


def _evaluar(f, x):
    try:
        return f(x)
    except ValueError:
        return None


def _diferencia(u, v):
    """|u − v| / 2, sin desbordar cuando u y v son enormes y de signo opuesto."""
    return abs(u / 2 - v / 2)


def _discontinuidad(tipo, desde, hasta):
    return {"tipo": tipo, "desde": desde, "hasta": hasta, "x": desde + (hasta - desde) / 2}


def _limpiar(x, paso):
    """Redondea una posición refinada a una rejilla mucho más fina que el muestreo.

    El refinamiento deja restos como 1e-17 o 0.123399999; la rejilla (cinco órdenes
    por debajo del paso) los muestra como 0 y 0.1234 sin perder resolución útil.
    """
    return round(x, 5 - math.floor(math.log10(paso))) + 0.0


def _frontera(f, definido, indefinido):
    """Aproxima el borde del dominio entre un punto evaluable y otro que no lo es."""
    for _ in range(_REFINAMIENTOS):
        medio = definido + (indefinido - definido) / 2
        if medio == definido or medio == indefinido:
            break
        if _evaluar(f, medio) is None:
            indefinido = medio
        else:
            definido = medio
    return indefinido


def _estrechar(f, izq, der, y_izq, y_der, por_signo):
    """Reduce [izq, der] hacia el cambio de signo o hacia la mayor variación de f.

    En una función continua |f(der) − f(izq)| tiende a cero al reducir el intervalo;
    en un salto se mantiene y en una asíntota crece. Devuelve (tipo, x), con tipo None
    cuando la función cierra la brecha (cruce continuo o variación suave).
    """
    brecha = _diferencia(y_izq, y_der)
    altura = max(abs(y_izq), abs(y_der))
    for _ in range(_REFINAMIENTOS):
        medio = izq + (der - izq) / 2
        if not izq < medio < der:
            break
        y_medio = _evaluar(f, medio)
        if y_medio is None:
            crece = max(abs(y_izq), abs(y_der)) > 1e3 * altura
            return ("asintota" if crece else "punto_indefinido"), medio
        if por_signo:
            if y_medio == 0:
                return None, medio
            a_la_izquierda = (y_izq < 0) != (y_medio < 0)
        else:
            a_la_izquierda = _diferencia(y_izq, y_medio) >= _diferencia(y_medio, y_der)
        if a_la_izquierda:
            der, y_der = medio, y_medio
        else:
            izq, y_izq = medio, y_medio
    x = izq + (der - izq) / 2
    if _diferencia(y_izq, y_der) <= 1e-3 * brecha:
        return None, x
    return ("asintota" if max(abs(y_izq), abs(y_der)) > 1e3 * altura else "salto"), x


def _pico_singular(f, izq, der):
    """Busca el máximo de |f| en [izq, der] por búsqueda ternaria.

    Un máximo suave se estabiliza al estrechar; junto a una asíntota sin cambio de
    signo (1/x², ln|x|) |f| sigue creciendo o deja de poder evaluarse.
    """
    alturas = []
    for _ in range(2):
        for _ in range(18):
            m1, m2 = izq + (der - izq) / 3, der - (der - izq) / 3
            y1, y2 = _evaluar(f, m1), _evaluar(f, m2)
            if y1 is None or y2 is None:
                return m1 if y1 is None else m2
            if abs(y1) < abs(y2):
                izq = m1
            else:
                der = m2
        alturas.append(max(abs(y1), abs(y2)))
    return izq + (der - izq) / 2 if alturas[1] > 1.01 * alturas[0] else None


def _explorar(f, a, b, muestras):
    """Muestrea f y devuelve (xs, ys, discontinuidades, cruces) ordenados por x."""
    xs = [a * (1 - i / muestras) + b * (i / muestras) for i in range(muestras + 1)]
    ys = [_evaluar(f, x) for x in xs]
    paso = (b - a) / muestras
    hallazgos, cruces = [], []

    # 1. Muestras que no pueden evaluarse: puntos aislados o tramos fuera del dominio.
    i = 0
    while i <= muestras:
        if ys[i] is not None:
            i += 1
            continue
        j = i
        while j < muestras and ys[j + 1] is None:
            j += 1
        desde = _frontera(f, xs[i - 1], xs[i]) if i > 0 else xs[i]
        hasta = _frontera(f, xs[j + 1], xs[j]) if j < muestras else xs[j]
        if hasta - desde > paso * 1e-3:
            tipo = "fuera_de_dominio"
        else:
            # Punto aislado: es una asíntota si |f| se dispara al acercarse a él.
            cerca = [_evaluar(f, x) for x in (desde - paso * 1e-6, hasta + paso * 1e-6)]
            lejos = [y for y in (ys[i - 1] if i else None, ys[j + 1] if j < muestras else None)
                     if y is not None]
            crece = any(y is not None and lejos and abs(y) > 1e3 * max(map(abs, lejos)) for y in cerca)
            tipo = "asintota" if crece else "punto_indefinido"
        hallazgos.append(_discontinuidad(tipo, desde, hasta))
        i = j + 1

    # 2. Cambios de signo entre muestras vecinas: cruce continuo, salto o asíntota.
    variaciones = [None] * muestras
    for i in range(muestras):
        y_izq, y_der = ys[i], ys[i + 1]
        if y_izq is None or y_der is None:
            continue
        variaciones[i] = _diferencia(y_izq, y_der)
        if y_izq != 0 and y_der != 0 and (y_izq < 0) != (y_der < 0):
            variaciones[i] = None  # ya se clasifica aquí; no es candidato a salto acotado
            tipo, x = _estrechar(f, xs[i], xs[i + 1], y_izq, y_der, True)
            if tipo:
                hallazgos.append(_discontinuidad(tipo, x, x))
            else:
                cruces.append({"x": x, "desde": xs[i], "hasta": xs[i + 1]})
    for i in range(1, muestras):
        vecinos = (ys[i - 1], ys[i + 1])
        if ys[i] == 0 and None not in vecinos and 0 not in vecinos and (vecinos[0] < 0) != (vecinos[1] < 0):
            cruces.append({"x": xs[i], "desde": xs[i - 1], "hasta": xs[i + 1]})

    # 3. Saltos acotados sin cambio de signo: una variación muy superior a las vecinas.
    candidatos = []
    for i, variacion in enumerate(variaciones):
        vecinas = [v for v in (variaciones[i - 1] if i else None,
                               variaciones[i + 1] if i + 1 < muestras else None) if v is not None]
        if variacion and vecinas and variacion > 8 * max(vecinas):
            candidatos.append((variacion, i))
    for _, i in sorted(candidatos, reverse=True)[:_MAX_CANDIDATOS]:
        tipo, x = _estrechar(f, xs[i], xs[i + 1], ys[i], ys[i + 1], False)
        if tipo:
            hallazgos.append(_discontinuidad(tipo, x, x))

    # 4. Picos de |f| con signo constante: posibles asíntotas que no cambian de signo.
    candidatos = []
    for i in range(muestras + 1):
        trio = ys[max(i - 1, 0):i + 2]
        if None in trio or 0 in trio or min(trio) < 0 < max(trio):
            continue
        alturas = [abs(y) for y in trio]
        if abs(ys[i]) == max(alturas) and abs(ys[i]) > min(alturas):
            candidatos.append((abs(ys[i]), i))
    for _, i in sorted(candidatos, reverse=True)[:_MAX_CANDIDATOS]:
        x = _pico_singular(f, xs[max(i - 1, 0)], xs[min(i + 1, muestras)])
        if x is not None:
            hallazgos.append(_discontinuidad("asintota", x, x))

    # Un mismo punto puede detectarse por dos vías: se conserva una sola entrada.
    discontinuidades = []
    for hallazgo in hallazgos:
        desde = min(max(_limpiar(hallazgo["desde"], paso), a), b)
        hasta = min(max(_limpiar(hallazgo["hasta"], paso), a), b)
        hallazgo.update(_discontinuidad(hallazgo["tipo"], desde, hasta))
    for hallazgo in sorted(hallazgos, key=lambda d: (d["desde"], d["hasta"])):
        if discontinuidades and hallazgo["desde"] - discontinuidades[-1]["hasta"] <= paso * 1e-3:
            previa = discontinuidades[-1]
            previa["hasta"] = max(previa["hasta"], hallazgo["hasta"])
            previa["x"] = previa["desde"] + (previa["hasta"] - previa["desde"]) / 2
        else:
            discontinuidades.append(hallazgo)
    cruces.sort(key=lambda c: c["x"])
    return xs, ys, discontinuidades, cruces


def _tramos_continuos(a, b, discontinuidades):
    """Subintervalos de [a, b] entre discontinuidades; los extremos junto a ellas son abiertos."""
    tramos, inicio, abierto = [], a, False
    for d in discontinuidades:
        if d["desde"] > inicio:
            tramos.append({"desde": inicio, "hasta": d["desde"],
                           "abierto_izquierda": abierto, "abierto_derecha": True})
        inicio, abierto = max(inicio, d["hasta"]), True
    if inicio < b:
        tramos.append({"desde": inicio, "hasta": b,
                       "abierto_izquierda": abierto, "abierto_derecha": False})
    return tramos


def _leer_region(funcion, a, b, muestras):
    f = funcion if isinstance(funcion, Expresion) else Expresion(funcion)
    a, b = numero_real(a, "a"), numero_real(b, "b")
    if a >= b or not math.isfinite(b - a):
        raise ValueError("La región debe cumplir a < b y tener ancho finito.")
    if isinstance(muestras, bool) or not isinstance(muestras, int) or not 10 <= muestras <= 2000:
        raise ValueError("La cantidad de muestras debe ser un entero entre 10 y 2000.")
    return f, a, b


def _resumen_continuidad(f, a, b, muestras, discontinuidades):
    return {
        "funcion": f.texto, "intervalo": [a, b], "muestras": muestras + 1,
        "continua": not discontinuidades,
        "discontinuidades": discontinuidades,
        "tramos": _tramos_continuos(a, b, discontinuidades),
    }


def analizar_continuidad(funcion, a, b, muestras=MUESTRAS):
    """Indica si se detectan discontinuidades de f en [a, b] y dónde.

    Tipos: fuera_de_dominio (tramo sin evaluar), punto_indefinido, salto y asintota.
    "continua" significa que no se detectó ninguna con el muestreo utilizado.
    """
    f, a, b = _leer_region(funcion, a, b, muestras)
    _, _, discontinuidades, _ = _explorar(f, a, b, muestras)
    return _resumen_continuidad(f, a, b, muestras, discontinuidades)


def _redondear_dentro(x, minimo, maximo):
    """El número con menos decimales cercano a x que sigue dentro de (minimo, maximo)."""
    for decimales in range(7):
        candidato = round(x, decimales) + 0.0
        if minimo < candidato < maximo:
            return candidato
    return x


def _intervalos_con_raiz(f, a, b, xs, ys, discontinuidades, cruces):
    """Amplía cada cruce continuo hasta un intervalo [x_l, x_u] que encierra solo esa raíz.

    Los límites se toman a medio camino de la barrera vecina (otra raíz, una
    discontinuidad o el borde de la región), de modo que f sea continua y cambie de
    signo una sola vez. Si la ampliación no conserva el cambio de signo se usa el
    par de muestras que lo detectó.
    """
    paso = (b - a) / (len(xs) - 1)
    ceros = [x for x, y in zip(xs, ys) if y == 0]
    barreras = sorted([(d["desde"], d["hasta"]) for d in discontinuidades]
                      + [(c["desde"], c["hasta"]) for c in cruces]
                      + [(x, x) for x in ceros])
    intervalos = []
    for cruce in cruces:
        izquierda = [hasta for _, hasta in barreras if hasta <= cruce["desde"]]
        derecha = [desde for desde, _ in barreras if desde >= cruce["hasta"]]
        xl, xu = a, b
        if izquierda:
            tope = max(izquierda)
            xl = cruce["desde"] if tope == cruce["desde"] else _redondear_dentro(
                tope + (cruce["desde"] - tope) / 2, tope, cruce["desde"])
        if derecha:
            tope = min(derecha)
            xu = cruce["hasta"] if tope == cruce["hasta"] else _redondear_dentro(
                cruce["hasta"] + (tope - cruce["hasta"]) / 2, cruce["hasta"], tope)
        xl, xu = _limpiar(xl, paso), _limpiar(xu, paso)
        f_xl, f_xu = _evaluar(f, xl), _evaluar(f, xu)
        if None in (f_xl, f_xu) or f_xl == 0 or f_xu == 0 or (f_xl < 0) == (f_xu < 0):
            xl, xu = cruce["desde"], cruce["hasta"]
            f_xl, f_xu = f(xl), f(xu)
        intervalos.append({"xl": xl, "xu": xu, "f_xl": f_xl, "f_xu": f_xu,
                           "raiz_aprox": _limpiar(cruce["x"], paso)})
    return intervalos, [_limpiar(x, paso) for x in ceros[:_MAX_RAICES_EXACTAS]]


def analizar_region(funcion, a, b, muestras=MUESTRAS):
    """Continuidad e intervalos candidatos de la región con una sola exploración.

    Cada intervalo cumple f(x_l)·f(x_u) < 0 y no contiene discontinuidades detectadas.
    "raices_exactas" lista (hasta 20) muestras donde f se evalúa como cero; las que
    no cambian de signo (raíces de multiplicidad par) no pueden encerrarse.
    """
    f, a, b = _leer_region(funcion, a, b, muestras)
    xs, ys, discontinuidades, cruces = _explorar(f, a, b, muestras)
    intervalos, ceros = _intervalos_con_raiz(f, a, b, xs, ys, discontinuidades, cruces)
    return {
        "continuidad": _resumen_continuidad(f, a, b, muestras, discontinuidades),
        "intervalos": intervalos, "raices_exactas": ceros,
    }


def buscar_intervalos(funcion, a, b, muestras=MUESTRAS):
    """Intervalos [x_l, x_u] de la región aptos para la regla falsa."""
    return analizar_region(funcion, a, b, muestras)["intervalos"]
