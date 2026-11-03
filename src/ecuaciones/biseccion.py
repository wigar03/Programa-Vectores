"""
Módulo de aproximación de raíces reales mediante el método de bisección.
UAM - Álgebra Lineal (MTM0120)
"""

import ast
import math
from typing import Callable, Dict, List

from src.core.arithmetic import parse_number


_ALLOWED_FUNCTIONS: Dict[str, Callable[..., float]] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil,
}

_ALLOWED_BIN_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
_ALLOWED_UNARY_OPS = (ast.UAdd, ast.USub)
_ALLOWED_NAMES = {"x", "pi", "e"}


class PasoBiseccion:
    def __init__(self, iteracion: int, a: float, b: float, c: float, f_a: float, f_b: float, f_c: float, error: float):
        self.iteracion = iteracion
        self.a = a
        self.b = b
        self.c = c
        self.f_a = f_a
        self.f_b = f_b
        self.f_c = f_c
        self.error = error


class ResultadoBiseccion:
    def __init__(self):
        self.funcion_original: str = ""
        self.funcion_normalizada: str = ""
        self.a_inicial: float = 0.0
        self.b_inicial: float = 0.0
        self.tolerancia: float = 1e-6
        self.max_iteraciones: int = 100
        self.convergencia: bool = False
        self.raiz_aproximada: float = 0.0
        self.f_raiz: float = 0.0
        self.error_estimado: float = 0.0
        self.iteraciones_ejecutadas: int = 0
        self.mensaje: str = ""
        self.pasos: List[PasoBiseccion] = []


def _validar_ast(node: ast.AST) -> None:
    if isinstance(node, ast.Expression):
        _validar_ast(node.body)
        return

    if isinstance(node, ast.BinOp):
        if not isinstance(node.op, _ALLOWED_BIN_OPS):
            raise ValueError("La expresión contiene operadores no permitidos.")
        _validar_ast(node.left)
        _validar_ast(node.right)
        return

    if isinstance(node, ast.UnaryOp):
        if not isinstance(node.op, _ALLOWED_UNARY_OPS):
            raise ValueError("La expresión contiene un operador unario no permitido.")
        _validar_ast(node.operand)
        return

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCTIONS:
            raise ValueError("La expresión usa una función no permitida.")
        if node.keywords:
            raise ValueError("No se permiten argumentos nombrados en la función.")
        for arg in node.args:
            _validar_ast(arg)
        return

    if isinstance(node, ast.Name):
        if node.id not in _ALLOWED_NAMES:
            raise ValueError(f"Nombre no permitido en la expresión: '{node.id}'.")
        return

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return
        raise ValueError("La expresión contiene constantes no numéricas.")

    raise ValueError("La expresión contiene sintaxis no permitida.")


def _crear_evaluador(funcion: str) -> Callable[[float], float]:
    expr = (funcion or "").strip().replace("^", "**")
    if not expr:
        raise ValueError("Debe ingresar una función en términos de x.")

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ValueError("La función ingresada no tiene una sintaxis válida.") from exc

    _validar_ast(tree)
    code = compile(tree, "<funcion_biseccion>", "eval")

    def evaluar(x: float) -> float:
        context = {"x": float(x), "pi": math.pi, "e": math.e, **_ALLOWED_FUNCTIONS}
        try:
            value = eval(code, {"__builtins__": {}}, context)
            if isinstance(value, bool):
                raise ValueError("La función no debe producir valores booleanos.")
            return float(value)
        except ZeroDivisionError as exc:
            raise ValueError(f"La función se indeterminó por división entre cero en x={x}.") from exc
        except OverflowError as exc:
            raise ValueError(f"La función produjo desbordamiento numérico en x={x}.") from exc
        except ValueError as exc:
            raise ValueError(f"La función no está definida para x={x}: {exc}") from exc

    return evaluar


def resolver_biseccion(
    funcion: str,
    a_in: str,
    b_in: str,
    tolerancia_in: str = "1e-6",
    max_iteraciones_in: int = 100,
) -> ResultadoBiseccion:
    """
    Aproxima una raíz real de f(x) en [a, b] con el método de bisección.
    """
    a = float(parse_number(a_in))
    b = float(parse_number(b_in))
    tol = float(parse_number(tolerancia_in))
    max_iter = int(max_iteraciones_in)

    if tol <= 0:
        raise ValueError("La tolerancia debe ser estrictamente positiva.")
    if max_iter <= 0:
        raise ValueError("El número máximo de iteraciones debe ser mayor que cero.")
    if a == b:
        raise ValueError("El intervalo inicial requiere extremos distintos: a ≠ b.")

    if a > b:
        a, b = b, a

    f = _crear_evaluador(funcion)
    fa = f(a)
    fb = f(b)

    if fa == 0:
        res = ResultadoBiseccion()
        res.funcion_original = funcion
        res.funcion_normalizada = funcion.strip().replace("^", "**")
        res.a_inicial = a
        res.b_inicial = b
        res.tolerancia = tol
        res.max_iteraciones = max_iter
        res.convergencia = True
        res.raiz_aproximada = a
        res.f_raiz = 0.0
        res.error_estimado = 0.0
        res.iteraciones_ejecutadas = 0
        res.mensaje = "El extremo izquierdo del intervalo ya es raíz exacta."
        return res

    if fb == 0:
        res = ResultadoBiseccion()
        res.funcion_original = funcion
        res.funcion_normalizada = funcion.strip().replace("^", "**")
        res.a_inicial = a
        res.b_inicial = b
        res.tolerancia = tol
        res.max_iteraciones = max_iter
        res.convergencia = True
        res.raiz_aproximada = b
        res.f_raiz = 0.0
        res.error_estimado = 0.0
        res.iteraciones_ejecutadas = 0
        res.mensaje = "El extremo derecho del intervalo ya es raíz exacta."
        return res

    if fa * fb > 0:
        raise ValueError(
            "El intervalo [a, b] no encierra raíz por bisección: f(a) y f(b) tienen el mismo signo."
        )

    res = ResultadoBiseccion()
    res.funcion_original = funcion
    res.funcion_normalizada = funcion.strip().replace("^", "**")
    res.a_inicial = a
    res.b_inicial = b
    res.tolerancia = tol
    res.max_iteraciones = max_iter

    c = a
    fc = fa
    error = abs(b - a) / 2.0

    for k in range(1, max_iter + 1):
        c = (a + b) / 2.0
        fc = f(c)
        error = abs(b - a) / 2.0
        res.pasos.append(PasoBiseccion(k, a, b, c, fa, fb, fc, error))

        if abs(fc) <= tol or error <= tol:
            res.convergencia = True
            break

        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc

    res.raiz_aproximada = c
    res.f_raiz = fc
    res.error_estimado = error
    res.iteraciones_ejecutadas = len(res.pasos)

    if res.convergencia:
        res.mensaje = "Convergencia alcanzada dentro de la tolerancia solicitada."
    else:
        res.mensaje = (
            "No se alcanzó convergencia con el máximo de iteraciones indicado; "
            "se devuelve la mejor aproximación obtenida."
        )

    return res
