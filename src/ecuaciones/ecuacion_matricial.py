"""
Módulo de Evaluación y Resolución Computacional de Ecuaciones Matriciales Ax = b.
UAM - Facultad de Ingeniería y Arquitectura (FIA)
Álgebra Lineal (MTM0120)

MARCO TEÓRICO Y PROCEDIMIENTO ALGEBRAICO:
Una ecuación matricial fundamental en álgebra lineal posee la estructura:
    A · x = b
donde:
    - A en M_(m x n)(R) es la matriz de coeficientes del sistema.
    - x en R^n (o M_(n x 1)(R)) es el vector columna de incógnitas a determinar.
    - b en R^m (o M_(m x 1)(R)) es el vector columna de términos independientes.

1. Compatibilidad Dimensional:
   Por las reglas de la multiplicación matricial:
       dim(A) = m x n
       dim(x) = n x 1
       dim(A · x) = m x 1  ==>  dim(b) DEBE ser estrictamente m x 1 (o longitud m en R^m).
   Si la longitud del vector b no es igual al número de renglones de la matriz A (m),
   la ecuación carece de sentido dimensional.

2. Dualidad Renglón-Columna de la Ecuación Matricial:
   - Vista por renglones: Cada renglón de A define un hiperplano afín en R^n. El vector solución x
     representa el punto geométrico de intersección de los m hiperplanos.
   - Vista por columnas (Vectorial): La ecuación Ax = b afirma que el vector b es una combinación lineal
     de las columnas de A ponderadas por las componentes de x:
         x_1 · Col_1(A) + x_2 · Col_2(A) + ... + x_n · Col_n(A) = b

3. Resolución Computacional y Conexión con el Programa Anterior:
   Conforme al requerimiento de la guía ("El programa debe ser capaz de llamar el programa que han
   elaborado anteriormente"), este módulo construye la matriz aumentada [A | b] y delega la
   reducción sistemática por renglones al motor Gauss-Jordan desarrollado en la Semana #3.

4. Verificación de la Solución:
   Una vez calculado el vector solución x*, se verifica algebraicamente evaluando el producto
   matriz-vector A · x* y comprobando que el residuo r = A · x* - b sea idénticamente nulo.
"""

from fractions import Fraction
from typing import Any, List, Dict, Tuple, Optional, Union

from src.core.arithmetic import (
    parse_number,
    format_number,
    validar_vector_numerico,
    validar_matriz_numerica,
    formatear_vector,
    formatear_matriz,
)
from src.solver.gauss_solver import GaussResult, Step
from src.solver.anterior_programa import resolver_sistema_con_programa_anterior


class ResultadoEcuacionMatricial:
    """
    Estructura que recopila el análisis integral de la ecuación matricial Ax = b.
    """
    def __init__(self):
        self.filas_m: int = 0
        self.columnas_n: int = 0
        self.matriz_A: List[List[Fraction]] = []
        self.vector_b: List[Fraction] = []
        self.matriz_aumentada_inicial: List[List[Fraction]] = []
        self.matriz_reducida: List[List[Fraction]] = []
        self.tipo_sistema: str = ""  # "SCD", "SCI", "SI"
        self.descripcion_sistema: str = ""
        self.rango_A: int = 0
        self.rango_aumentada: int = 0
        self.solucion_dict: Dict[str, Union[Fraction, str]] = {}
        self.vector_solucion: List[Union[Fraction, str]] = []
        self.pasos_reduccion: List[Step] = []
        self.pasos_sustitucion: List[str] = []
        self.verificacion_residual: List[str] = []


def resolver_ecuacion_matricial(
    A_in: Any,
    b_in: Any,
    nombres_variables: Optional[List[str]] = None,
    usar_gauss_jordan: bool = True
) -> ResultadoEcuacionMatricial:
    """
    Evalúa y resuelve computacionalmente la ecuación matricial A · x = b.
    
    Procedimiento algebraico:
    1. Valida y normaliza la matriz de coeficientes A en M_(m x n)(R).
    2. Valida y normaliza el vector independiente b en R^m.
    3. Verifica la coherencia dimensional: len(b) == m (número de renglones de A).
    4. Ensambla la matriz aumentada [A | b] de dimensiones m x (n + 1).
    5. Invoca el motor de eliminación de renglones del programa anterior.
    6. Clasifica el sistema (SCD, SCI, SI) mediante los rangos rg(A) y rg(A|b).
    7. Si existe solución, comprueba A · x = b sustituyendo las soluciones obtenidas.
    
    Parámetros:
        A_in: Matriz de coeficientes A.
        b_in: Vector de términos independientes b.
        nombres_variables: Opcional, lista de nombres para las variables [x_1, ..., x_n].
        usar_gauss_jordan: Si es True aplica reducción completa Gauss-Jordan; si es False, Gauss simple.
        
    Retorna:
        Instancia de ResultadoEcuacionMatricial.
        
    Lanza:
        ValueError: Si las dimensiones no concuerdan o las entradas son inconsistentes.
    """
    A = validar_matriz_numerica(A_in)
    b = validar_vector_numerico(b_in)
    
    m = len(A)
    n = len(A[0])
    
    # 1. Validación de compatibilidad dimensional estricta
    if len(b) != m:
        raise ValueError(
            f"Incompatibilidad dimensional en la ecuación matricial A · x = b: "
            f"La matriz A tiene {m} filas, pero el vector b tiene dimensión {len(b)}. "
            f"Para que el sistema sea válido, el vector b debe tener exactamente {m} componentes."
        )
        
    # Variables por defecto
    if nombres_variables is None or len(nombres_variables) != n:
        nombres_variables = [f"x_{j + 1}" for j in range(n)]
        
    # 2. Construcción de la matriz aumentada [ A | b ]
    matriz_aumentada: List[List[Fraction]] = []
    for i in range(m):
        fila = [A[i][j] for j in range(n)] + [b[i]]
        matriz_aumentada.append(fila)
        
    # 3. Llamada al solucionador del programa anterior
    gauss_res: GaussResult = resolver_sistema_con_programa_anterior(
        matriz_aumentada,
        usar_gauss_jordan=usar_gauss_jordan
    )
    
    # Reasignar nombres de variables correctos si se especificaron
    if nombres_variables:
        for idx, var in enumerate(nombres_variables):
            clave_original = f"x_{idx+1}"
            if clave_original in gauss_res.solution:
                gauss_res.solution[var] = gauss_res.solution.pop(clave_original)
                
    # 4. Empaquetar el resultado
    res = ResultadoEcuacionMatricial()
    res.filas_m = m
    res.columnas_n = n
    res.matriz_A = A
    res.vector_b = b
    res.matriz_aumentada_inicial = matriz_aumentada
    res.matriz_reducida = gauss_res.final_matrix
    res.tipo_sistema = gauss_res.system_type
    res.descripcion_sistema = gauss_res.system_type_desc
    res.rango_A = gauss_res.rank_A
    res.rango_aumentada = gauss_res.rank_Aug
    res.solucion_dict = gauss_res.solution
    res.vector_solucion = gauss_res.solution_vector
    res.pasos_reduccion = gauss_res.steps
    res.pasos_sustitucion = gauss_res.backward_substitution_steps
    
    # 5. Comprobación de consistencia si el sistema es compatible
    if res.tipo_sistema == "SCD":
        res.verificacion_residual = []
        for i in range(m):
            eval_lhs = Fraction(0, 1)
            detalles_prod = []
            for j in range(n):
                c_val = res.vector_solucion[j]
                if isinstance(c_val, Fraction):
                    eval_lhs += A[i][j] * c_val
                    detalles_prod.append(f"({format_number(A[i][j])}) \\cdot ({format_number(c_val)})")
            
            diferencia = eval_lhs - b[i]
            valido = (diferencia == 0)
            simbolo = "✓ Satisface" if valido else "✗ Discrepancia"
            suma_str = " + ".join(detalles_prod)
            res.verificacion_residual.append(
                f"Fila {i + 1}: ${suma_str} = {format_number(eval_lhs)}$ (Esperado: ${format_number(b[i])}$) $\\rightarrow$ {simbolo}"
            )
            
    elif res.tipo_sistema == "SCI":
        res.verificacion_residual = [
            "El sistema admite infinitas soluciones parametrizadas. "
            "Cualquier asignación concreta a los parámetros libres satisface $A\\vec{x} = \\vec{b}$."
        ]
    else:
        res.verificacion_residual = [
            "Sistema Incompatible: No existe ningún vector $\\vec{x} \\in \\mathbb{R}^n$ tal que $A\\vec{x} = \\vec{b}$."
        ]
        
    return res
