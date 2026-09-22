"""
Servidor HTTP Estándar y API REST para la Interfaz Web Interactiva.
UAM - Álgebra Lineal (MTM0120)

CERO DEPENDENCIAS EXTERNAS:
Utiliza exclusivamente los módulos estándar de Python:
- http.server
- json
- urllib.parse
- threading
- webbrowser
"""

import os
import sys
import json
import socket
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from src.core.arithmetic import parse_number, format_number, formatear_vector, formatear_matriz
from src.vectores.operaciones import (
    suma_vectores,
    resta_vectores,
    multiplicar_escalar_vector,
    producto_punto,
    norma_cuadrada,
)
from src.vectores.combinacion_lineal import evaluar_combinacion_lineal
from src.matrices.operaciones import (
    suma_matrices,
    resta_matrices,
    multiplicar_escalar_matriz,
    multiplicar_matrices,
    transpuesta_matriz,
)
from src.ecuaciones.ecuacion_matricial import resolver_ecuacion_matricial


def serialize_fraction_or_str(val):
    if hasattr(val, "numerator") and hasattr(val, "denominator"):
        return format_number(val)
    return str(val)


class AlgebraLinearHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Directorio base de archivos estáticos
        web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
        super().__init__(*args, directory=web_dir, **kwargs)

    def log_message(self, format, *args):
        # Silenciar logs ruidosos para una terminal limpia
        pass

    def _send_json(self, data, status=200):
        body = json.dumps(data, default=serialize_fraction_or_str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            body = json.loads(raw_body)
        except Exception:
            body = {}

        try:
            if parsed.path == "/api/vectores/operar":
                self._handle_vectores_operar(body)
            elif parsed.path == "/api/vectores/combinacion":
                self._handle_vectores_combinacion(body)
            elif parsed.path == "/api/matrices/operar":
                self._handle_matrices_operar(body)
            elif parsed.path == "/api/ecuaciones/resolver":
                self._handle_ecuaciones_resolver(body)
            else:
                self._send_json({"error": f"Ruta API no encontrada: {parsed.path}"}, status=404)
        except Exception as err:
            self._send_json({"error": str(err)}, status=400)

    def _handle_vectores_operar(self, body):
        op = body.get("operacion", "")
        u = [parse_number(x) for x in body.get("u", [])]
        v = [parse_number(x) for x in body.get("v", [])]
        c = parse_number(body.get("c", "1"))

        desglose = []
        if op == "suma":
            res = suma_vectores(u, v)
            for i in range(len(res)):
                desglose.append(f"Componente {i+1}: $({format_number(u[i])}) + ({format_number(v[i])}) = {format_number(res[i])}$")
            data = {
                "titulo_operacion": "Suma Vectorial u + v",
                "resultado_str": formatear_vector(res),
                "explicacion_teorica": "La suma en $\\mathbb{R}^n$ se calcula componente a componente: $(\\vec{u} + \\vec{v})_i = u_i + v_i$.",
                "desglose_componentes": desglose,
            }
        elif op == "resta":
            res = resta_vectores(u, v)
            for i in range(len(res)):
                desglose.append(f"Componente {i+1}: $({format_number(u[i])}) - ({format_number(v[i])}) = {format_number(res[i])}$")
            data = {
                "titulo_operacion": "Resta Vectorial u - v",
                "resultado_str": formatear_vector(res),
                "explicacion_teorica": "La resta en $\\mathbb{R}^n$ equivale a sumar el inverso aditivo de $\\vec{v}$: $(\\vec{u} - \\vec{v})_i = u_i - v_i$.",
                "desglose_componentes": desglose,
            }
        elif op == "escalar_u":
            res = multiplicar_escalar_vector(c, u)
            for i in range(len(res)):
                desglose.append(f"Componente {i+1}: $({format_number(c)}) \\cdot ({format_number(u[i])}) = {format_number(res[i])}$")
            data = {
                "titulo_operacion": f"Multiplicación por Escalar {c} · u",
                "resultado_str": formatear_vector(res),
                "explicacion_teorica": "El producto por escalar distribuye el factor en cada componente: $(c \\cdot \\vec{u})_i = c \\cdot u_i$.",
                "desglose_componentes": desglose,
            }
        elif op == "producto_punto":
            p_punto = producto_punto(u, v)
            norma_u_sq = norma_cuadrada(u)
            norma_v_sq = norma_cuadrada(v)
            for i in range(len(u)):
                p_parcial = u[i] * v[i]
                desglose.append(f"Término {i+1}: $u_{{{i+1}}} \\cdot v_{{{i+1}}} = ({format_number(u[i])}) \\cdot ({format_number(v[i])}) = {format_number(p_parcial)}$")
            data = {
                "titulo_operacion": "Producto Punto u · v",
                "resultado_str": format_number(p_punto),
                "explicacion_teorica": (
                    f"El producto escalar euclídeo es la sumatoria de productos: $\\vec{{u}} \\cdot \\vec{{v}} = \\sum_{{i=1}}^{{n}} u_i v_i = {format_number(p_punto)}$.\n"
                    f"Norma al cuadrado de $\\vec{{u}}$: $\\|\\vec{{u}}\\|^2 = {format_number(norma_u_sq)}$, Norma al cuadrado de $\\vec{{v}}$: $\\|\\vec{{v}}\\|^2 = {format_number(norma_v_sq)}$."
                ),
                "desglose_componentes": desglose,
            }
        else:
            raise ValueError(f"Operación vectorial desconocida: '{op}'")

        self._send_json(data)

    def _handle_vectores_combinacion(self, body):
        vectores = body.get("vectores", [])
        b = body.get("b", [])
        resultado = evaluar_combinacion_lineal(vectores, b)

        pasos_serializables = []
        for p in resultado.pasos_reduccion:
            pasos_serializables.append({
                "step_number": p.step_number,
                "title": p.title,
                "description": p.description,
                "operation_code": p.operation_code,
            })

        data = {
            "es_combinacion": resultado.es_combinacion,
            "tipo_solucion": resultado.tipo_solucion,
            "expresion_algebraica": resultado.expresion_algebraica,
            "justificacion_teorica": resultado.justificacion_teorica,
            "escalares": {k: serialize_fraction_or_str(v) for k, v in resultado.escalares.items()},
            "escalares_vector": [serialize_fraction_or_str(x) for x in resultado.escalares_vector],
            "comprobacion": resultado.comprobacion_sustitucion,
            "pasos": pasos_serializables,
        }
        self._send_json(data)

    def _handle_matrices_operar(self, body):
        op = body.get("operacion", "")
        A = body.get("A", [])
        B = body.get("B", [])
        k = body.get("k", "1")

        pasos_mult = []
        if op == "suma":
            res = suma_matrices(A, B)
            data = {
                "titulo_operacion": "Suma Matricial A + B",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in res],
                "matriz_formateada": formatear_matriz(res),
                "explicacion_teorica": "Suma elemento a elemento $(A + B)_{ij} = a_{ij} + b_{ij}$ para matrices del mismo orden $m \\times n$.",
            }
        elif op == "resta":
            res = resta_matrices(A, B)
            data = {
                "titulo_operacion": "Resta Matricial A - B",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in res],
                "matriz_formateada": formatear_matriz(res),
                "explicacion_teorica": "Resta elemento a elemento $(A - B)_{ij} = a_{ij} - b_{ij}$ para matrices del mismo orden $m \\times n$.",
            }
        elif op == "escalar_a":
            res = multiplicar_escalar_matriz(k, A)
            data = {
                "titulo_operacion": f"Multiplicación por Escalar {k} · A",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in res],
                "matriz_formateada": formatear_matriz(res),
                "explicacion_teorica": "Multiplica cada elemento $a_{ij}$ por el factor escalar $k$: $(k \\cdot A)_{ij} = k \\cdot a_{ij}$.",
            }
        elif op == "multiplicacion":
            res, pasos_mult = multiplicar_matrices(A, B)
            data = {
                "titulo_operacion": "Multiplicación de Matrices A · B",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in res],
                "matriz_formateada": formatear_matriz(res),
                "explicacion_teorica": (
                    "Producto renglón por columna $c_{ij} = \\sum_{k=1}^n (a_{ik} \\cdot b_{kj})$. "
                    "El número de columnas de $A$ coincide con el número de filas de $B$."
                ),
                "pasos_multiplicacion": pasos_mult,
            }
        elif op == "transpuesta_a":
            res = transpuesta_matriz(A)
            data = {
                "titulo_operacion": "Transpuesta de la Matriz A^T",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in res],
                "matriz_formateada": formatear_matriz(res),
                "explicacion_teorica": "Las filas de $A$ se convierten en las columnas de $A^T$: $(A^T)_{ji} = a_{ij}$.",
            }
        elif op == "transpuesta_b":
            res = transpuesta_matriz(B)
            data = {
                "titulo_operacion": "Transpuesta de la Matriz B^T",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in res],
                "matriz_formateada": formatear_matriz(res),
                "explicacion_teorica": "Las filas de $B$ se convierten en las columnas de $B^T$: $(B^T)_{ji} = b_{ij}$.",
            }
        else:
            raise ValueError(f"Operación matricial desconocida: '{op}'")

        self._send_json(data)

    def _handle_ecuaciones_resolver(self, body):
        A = body.get("A", [])
        b = body.get("b", [])
        usar_gauss_jordan = body.get("usar_gauss_jordan", True)

        res = resolver_ecuacion_matricial(A, b, usar_gauss_jordan=usar_gauss_jordan)

        pasos_serializables = []
        for p in res.pasos_reduccion:
            pasos_serializables.append({
                "step_number": p.step_number,
                "title": p.title,
                "description": p.description,
                "operation_code": p.operation_code,
            })

        data = {
            "tipo_sistema": res.tipo_sistema,
            "descripcion_sistema": res.descripcion_sistema,
            "rango_A": res.rango_A,
            "rango_aumentada": res.rango_aumentada,
            "vector_solucion": [serialize_fraction_or_str(x) for x in res.vector_solucion],
            "solucion_dict": {k: serialize_fraction_or_str(v) for k, v in res.solucion_dict.items()},
            "pasos": pasos_serializables,
            "verificacion": res.verificacion_residual,
        }
        self._send_json(data)


def buscar_puerto_disponible(puerto_inicial: int = 8080) -> int:
    puerto = puerto_inicial
    while puerto < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", puerto)) != 0:
                return puerto
            puerto += 1
    return puerto_inicial


def iniciar_servidor_web(puerto: int = 8080, abrir_navegador: bool = True):
    puerto_libre = buscar_puerto_disponible(puerto)
    servidor = HTTPServer(("127.0.0.1", puerto_libre), AlgebraLinearHandler)
    url = f"http://127.0.0.1:{puerto_libre}"
    print("=" * 72)
    print("🚀 CALCULADORA DE ÁLGEBRA LINEAL - UAM (MTM0120)")
    print(f"🌐 Servidor web interactivo iniciado en: {url}")
    print("=" * 72)

    if abrir_navegador:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        servidor.server_close()
