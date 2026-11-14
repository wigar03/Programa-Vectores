"""Derivación del AST permitido por la calculadora, sin eval ni dependencias.

La fórmula resultante se evalúa en su dominio real. En puntos singulares no
se intenta extenderla por límites (por ejemplo abs(x) en cero).
"""

import ast
import math

from ..biseccion.expresiones import Expresion


def constante(n):
    return ast.Constant(value=n)


def es(nodo, valor):
    return isinstance(nodo, ast.Constant) and nodo.value == valor


def op(a, tipo, b):
    # Solo identidades sencillas: evita crecimiento artificial en reglas de cadena.
    if tipo in (ast.Add, ast.Sub) and es(b, 0):
        return a
    if tipo is ast.Add and es(a, 0):
        return b
    if tipo is ast.Mult:
        if es(a, 0) or es(b, 0):
            return constante(0)
        if es(a, 1):
            return b
        if es(b, 1):
            return a
    if tipo is ast.Pow:
        if es(b, 1):
            return a
        if es(b, 0):
            return constante(1)
    if isinstance(a, ast.Constant) and isinstance(b, ast.Constant):
        if tipo is ast.Sub:
            return constante(a.value - b.value)
    return ast.BinOp(left=a, op=tipo(), right=b)


def llamada(nombre, u):
    return ast.Call(func=ast.Name(id=nombre, ctx=ast.Load()), args=[u], keywords=[])


def depende(nodo):
    return any(isinstance(n, ast.Name) and n.id == "x" for n in ast.walk(nodo))


def derivar(nodo):
    if not depende(nodo):
        return constante(0)
    if isinstance(nodo, ast.Name):
        return constante(1)
    if isinstance(nodo, ast.UnaryOp):
        d = derivar(nodo.operand)
        return ast.UnaryOp(op=nodo.op, operand=d)
    if isinstance(nodo, ast.BinOp):
        u, v = nodo.left, nodo.right
        du, dv = derivar(u), derivar(v)
        if isinstance(nodo.op, (ast.Add, ast.Sub)):
            return op(du, type(nodo.op), dv)
        if isinstance(nodo.op, ast.Mult):
            return op(op(du, ast.Mult, v), ast.Add, op(u, ast.Mult, dv))
        if isinstance(nodo.op, ast.Div):
            return op(op(op(du, ast.Mult, v), ast.Sub, op(u, ast.Mult, dv)),
                      ast.Div, op(v, ast.Pow, constante(2)))
        if not depende(v):
            return op(op(v, ast.Mult, op(u, ast.Pow, op(v, ast.Sub, constante(1)))), ast.Mult, du)
        # u^v * (v' ln(u) + v u'/u), para base positiva.
        return op(nodo, ast.Mult, op(op(dv, ast.Mult, llamada("ln", u)), ast.Add,
                                     op(op(v, ast.Mult, du), ast.Div, u)))
    u = nodo.args[0]
    nombre, du = nodo.func.id, derivar(u)
    exteriores = {
        "asin": lambda: op(constante(1), ast.Div, llamada("sqrt", op(constante(1), ast.Sub, op(u, ast.Pow, constante(2))))),
        "acos": lambda: op(constante(-1), ast.Div, llamada("sqrt", op(constante(1), ast.Sub, op(u, ast.Pow, constante(2))))),
        "atan": lambda: op(constante(1), ast.Div, op(constante(1), ast.Add, op(u, ast.Pow, constante(2)))),
        "sin": lambda: llamada("cos", u),
        "cos": lambda: ast.UnaryOp(op=ast.USub(), operand=llamada("sin", u)),
        "tan": lambda: op(constante(1), ast.Div, op(llamada("cos", u), ast.Pow, constante(2))),
        "exp": lambda: llamada("exp", u),
        "ln": lambda: op(constante(1), ast.Div, u),
        "log": lambda: op(constante(1), ast.Div, op(u, ast.Mult, constante(math.log(10)))),
        "sqrt": lambda: op(constante(1), ast.Div, op(constante(2), ast.Mult, llamada("sqrt", u))),
        "abs": lambda: op(u, ast.Div, llamada("abs", u)),
    }
    return op(exteriores[nombre](), ast.Mult, du)


def derivada_simbolica(funcion):
    f = funcion if isinstance(funcion, Expresion) else Expresion(funcion)
    arbol = ast.fix_missing_locations(derivar(f.arbol))
    if sum(1 for _ in ast.walk(arbol)) > 4000:
        raise ValueError("La derivada es demasiado compleja. Simplifique la función.")
    # Árbol generado exclusivamente desde nodos ya validados. No se vuelve a
    # aplicar el límite de 500 caracteres de la entrada a la fórmula generada.
    d = Expresion.__new__(Expresion)
    d.arbol = arbol
    d.texto = ast.unparse(arbol).replace("**", "^")
    return d


def analizar_derivada(funcion):
    """Deriva composiciones del lenguaje admitido, independiente de Newton.

    Conserva el dominio de la fórmula obtenida; no extiende por límites los
    puntos singulares. Devuelve sintaxis editable y representación LaTeX.
    """
    f = funcion if isinstance(funcion, Expresion) else Expresion(funcion)
    d = derivada_simbolica(f)
    return {"funcion": f.texto, "funcion_latex": f.latex(),
            "derivada": d.texto, "derivada_latex": d.latex()}
