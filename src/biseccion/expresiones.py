"""Evaluador de expresiones reales con una lista explícita de operaciones permitidas."""

import ast
import math
import operator


FUNCIONES = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "exp": math.exp, "ln": math.log, "log": math.log10,
    "sqrt": math.sqrt, "abs": abs,
}
CONSTANTES = {"pi": math.pi, "e": math.e}
OPERACIONES = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}


def numero_real(valor, nombre="valor"):
    """Admite números o decimales/fracciones textuales y exige un real finito."""
    try:
        if isinstance(valor, bool) or not isinstance(valor, (int, float, str)):
            raise ValueError()
        if isinstance(valor, str) and "/" in valor:
            numerador, denominador = valor.split("/")
            resultado = float(numerador) / float(denominador)
        else:
            resultado = float(valor)
        if not math.isfinite(resultado):
            raise ValueError()
        return resultado
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
        raise ValueError(f"{nombre} debe ser un número real finito.") from exc


class Expresion:
    """Interpreta un AST validado, sin eval, atributos, imports ni código arbitrario.

    Se aceptan potencias con ^ o ** y multiplicación explícita (2*x).
    Los límites de longitud, nodos y exponentes acotan el trabajo por evaluación.
    """

    def __init__(self, texto):
        if not isinstance(texto, str) or not texto.strip() or len(texto) > 500:
            raise ValueError("Ingrese una función de entre 1 y 500 caracteres.")
        self.texto = texto.strip()
        try:
            self.arbol = ast.parse(self.texto.replace("^", "**"), mode="eval").body
        except (SyntaxError, RecursionError) as exc:
            raise ValueError("Función inválida. Use, por ejemplo, x^3 - x - 2.") from exc
        if sum(1 for _ in ast.walk(self.arbol)) > 120:
            raise ValueError("La función es demasiado compleja.")
        self._validar(self.arbol)

    def _validar(self, nodo):
        if isinstance(nodo, ast.Constant) and type(nodo.value) in (int, float):
            numero_real(nodo.value, "La constante")
        elif isinstance(nodo, ast.Name) and nodo.id in {"x", *CONSTANTES}:
            return
        elif isinstance(nodo, ast.BinOp) and type(nodo.op) in OPERACIONES:
            self._validar(nodo.left)
            self._validar(nodo.right)
        elif isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, (ast.UAdd, ast.USub)):
            self._validar(nodo.operand)
        elif (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
              and nodo.func.id in FUNCIONES and len(nodo.args) == 1 and not nodo.keywords):
            self._validar(nodo.args[0])
        else:
            raise ValueError("Expresión no permitida. Use x, números, +, -, *, /, ^ y funciones admitidas.")

    def _evaluar(self, nodo, x):
        if isinstance(nodo, ast.Constant):
            return float(nodo.value)
        if isinstance(nodo, ast.Name):
            return x if nodo.id == "x" else CONSTANTES[nodo.id]
        if isinstance(nodo, ast.UnaryOp):
            valor = self._evaluar(nodo.operand, x)
            return -valor if isinstance(nodo.op, ast.USub) else valor
        if isinstance(nodo, ast.Call):
            return FUNCIONES[nodo.func.id](self._evaluar(nodo.args[0], x))
        izquierda = self._evaluar(nodo.left, x)
        derecha = self._evaluar(nodo.right, x)
        if isinstance(nodo.op, ast.Pow) and abs(derecha) > 1000:
            raise ValueError("El exponente excede el límite de 1000.")
        return numero_real(OPERACIONES[type(nodo.op)](izquierda, derecha), "f(x)")

    def latex(self):
        """Representa el mismo árbol validado sin evaluar la función ni aceptar LaTeX libre."""
        def parentesis(texto):
            return rf"\left({texto}\right)"

        def convertir(nodo):
            if isinstance(nodo, ast.Constant):
                texto = str(nodo.value)
                if "e" in texto.lower():
                    mantisa, exponente = texto.lower().split("e")
                    return rf"{mantisa} \times 10^{{{int(exponente)}}}"
                return texto
            if isinstance(nodo, ast.Name):
                return r"\pi" if nodo.id == "pi" else nodo.id
            if isinstance(nodo, ast.UnaryOp):
                argumento = convertir(nodo.operand)
                if isinstance(nodo.operand, ast.BinOp):
                    argumento = parentesis(argumento)
                return ("-" if isinstance(nodo.op, ast.USub) else "+") + argumento
            if isinstance(nodo, ast.Call):
                argumento = convertir(nodo.args[0])
                nombre = nodo.func.id
                if nombre == "sqrt":
                    return rf"\sqrt{{{argumento}}}"
                if nombre == "abs":
                    return rf"\left|{argumento}\right|"
                if nombre == "exp":
                    return rf"e^{{{argumento}}}"
                nombre = r"\log_{10}" if nombre == "log" else "\\" + nombre
                return nombre + parentesis(argumento)
            izquierda, derecha = convertir(nodo.left), convertir(nodo.right)
            if isinstance(nodo.op, ast.Div):
                return rf"\frac{{{izquierda}}}{{{derecha}}}"
            if isinstance(nodo.op, ast.Pow):
                if (isinstance(nodo.left, (ast.BinOp, ast.UnaryOp, ast.Call))
                        or isinstance(nodo.left, ast.Constant)
                        and (nodo.left.value < 0 or "e" in str(nodo.left.value).lower())):
                    izquierda = parentesis(izquierda)
                return rf"{izquierda}^{{{derecha}}}"
            if isinstance(nodo.op, ast.Mult):
                if isinstance(nodo.left, ast.BinOp) and isinstance(nodo.left.op, (ast.Add, ast.Sub)):
                    izquierda = parentesis(izquierda)
                if (isinstance(nodo.right, ast.UnaryOp) or isinstance(nodo.right, ast.BinOp)
                        and isinstance(nodo.right.op, (ast.Add, ast.Sub))):
                    derecha = parentesis(derecha)
                return izquierda + r" \cdot " + derecha
            if isinstance(nodo.right, ast.UnaryOp) or (isinstance(nodo.op, ast.Sub)
                    and isinstance(nodo.right, ast.BinOp) and isinstance(nodo.right.op, (ast.Add, ast.Sub))):
                derecha = parentesis(derecha)
            return izquierda + (" + " if isinstance(nodo.op, ast.Add) else " - ") + derecha

        return convertir(self.arbol)

    def __call__(self, x):
        """Evalúa en un punto real y traduce errores de dominio a mensajes de entrada."""
        x = numero_real(x, "x")
        try:
            return numero_real(self._evaluar(self.arbol, x), "f(x)")
        except (ValueError, ZeroDivisionError, OverflowError) as exc:
            raise ValueError(f"No se puede evaluar f(x) en x={x:g}: {exc}") from exc
