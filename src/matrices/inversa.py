"""
Módulo de Cálculo y Verificación de la Inversa de una Matriz A^(-1).
UAM - Facultad de Ingeniería y Arquitectura (FIA)
Álgebra Lineal (MTM0120) - Unidad 2.2: La Inversa de una Matriz

MARCO TEÓRICO Y PROCEDIMIENTO ALGEBRAICO (Unidad 2.2):
1. Definición Formal:
   Sea A una matriz cuadrada de orden n x n. A es invertible (o no singular) si existe
   una matriz C de orden n x n tal que:
       C · A = I_n   y   A · C = I_n
   En tal caso, la matriz C es única y se denota como C = A^(-1).
   Si no existe tal matriz, A se denomina matriz singular.

2. Teorema para Matrices 2 x 2:
   Sea A = [[a, b], [c, d]].
   Si det(A) = ad - bc != 0, entonces A es invertible y:
       A^(-1) = (1 / (ad - bc)) · [[d, -b], [-c, a]]
   Si ad - bc == 0, entonces A no es invertible.

3. Algoritmo de Inversión por Eliminación de Renglones (Gauss y Gauss-Jordan):
   Una matriz A de n x n es invertible si y solo si A es equivalente por filas a I_n.
   Cualquier secuencia de operaciones elementales de fila que transforme A en I_n
   transforma simultáneamente la matriz identidad I_n en A^(-1):
       [A | I_n]  ~ ... ~  [I_n | A^(-1)]

   Métodos disponibles:
   a) Método Gauss-Jordan:
      - Construir la matriz aumentada [A | I_n].
      - Para cada pivote (i = 1, ..., n):
        * Seleccionar pivote no nulo (intercambio de filas F_i <-> F_j si es necesario).
        * Normalizar el renglón pivote dividiendo entre el elemento pivote: F_i <- (1/p) · F_i.
        * Anular todos los demás elementos de la columna del pivote (tanto arriba como abajo).
      - Si en algún momento una fila del bloque izquierdo se anula por completo, A no es invertible.
      - Al finalizar, el bloque derecho corresponde a A^(-1).

   b) Método de Gauss (Eliminación hacia adelante + Sustitución regresiva):
      - Reducción gaussiana hacia adelante sobre [A | I_n] para obtener [U | B], donde U es triangular superior.
      - Comprobar que los n elementos de la diagonal de U son no nulos (rango = n).
      - Fase regresiva: escalamiento unitario de la diagonal y anulación hacia atrás de los elementos sobre la diagonal.

4. Verificación Rigurosa:
   No basta con obtener una matriz:
   - Comprobación 1: A · A^(-1) = I_n
   - Comprobación 2: A^(-1) · A = I_n
   - Cálculo del residuo matricial R = A · A^(-1) - I_n = 0.

RESTRICCIÓN DIDÁCTICA:
100% Python estándar con aritmética exacta (fractions.Fraction). Cero librerías externas.
"""

from fractions import Fraction
from typing import Any, List, Tuple, Dict, Optional, Union

from src.core.arithmetic import (
    parse_number,
    format_number,
    validar_matriz_numerica,
    formatear_matriz,
)
from src.solver.gauss_solver import Step, clonar_matriz
from src.matrices.operaciones import (
    obtener_dimensiones_matriz,
    crear_matriz_identidad,
    multiplicar_matrices,
)


class ResultadoInversa:
    """
    Estructura que encapsula el resultado completo del cálculo de la inversa A^(-1).
    """
    def __init__(self):
        self.orden_n: int = 0
        self.matriz_A: List[List[Fraction]] = []
        self.es_invertible: bool = False
        self.matriz_inversa: Optional[List[List[Fraction]]] = None
        self.metodo_utilizado: str = ""  # "gauss_jordan" o "gauss"
        self.determinante_2x2: Optional[Fraction] = None
        self.formula_2x2_detalle: Optional[str] = None
        self.matriz_aumentada_inicial: List[List[Fraction]] = []
        self.matriz_aumentada_final: List[List[Fraction]] = []
        self.pasos_reduccion: List[Step] = []
        self.verificacion_A_por_Ainv: List[str] = []
        self.verificacion_Ainv_por_A: List[str] = []
        self.residuo_cero: bool = False
        self.mensaje_diagnostico: str = ""


def calcular_inversa_matriz(
    A_in: Any,
    metodo: str = "gauss_jordan"
) -> ResultadoInversa:
    """
    Calcula la inversa de una matriz cuadrada A paso a paso.
    
    Parámetros:
        A_in: Matriz numérica de entrada.
        metodo: "gauss_jordan" para reducción completa simultánea,
                o "gauss" para eliminación hacia adelante + fase regresiva.
                
    Retorna:
        ResultadoInversa con la matriz inversa, pasos de reducción y verificaciones.
        
    Lanza:
        ValueError: Si la matriz no es cuadrada o está vacía.
    """
    A = validar_matriz_numerica(A_in)
    m, n = obtener_dimensiones_matriz(A)
    
    if m != n:
        raise ValueError(
            f"Error dimensional en Inversa de Matriz: La matriz debe ser estrictamente cuadrada (n x n). "
            f"La matriz proporcionada tiene dimensiones {m} x {n}."
        )
    if n == 0:
        raise ValueError("La matriz no puede estar vacía.")
        
    resultado = ResultadoInversa()
    resultado.orden_n = n
    resultado.matriz_A = clonar_matriz(A)
    resultado.metodo_utilizado = metodo.lower()
    
    # Análisis específico para matrices 2 x 2 (Fórmula del determinante del Teorema)
    if n == 2:
        a = A[0][0]
        b = A[0][1]
        c = A[1][0]
        d = A[1][1]
        det = a * d - b * c
        resultado.determinante_2x2 = det
        det_str = format_number(det)
        if det != 0:
            inv_det = Fraction(1, 1) / det
            resultado.formula_2x2_detalle = (
                f"$$\\det(A) = ({format_number(a)})({format_number(d)}) - ({format_number(b)})({format_number(c)}) = {det_str} \\neq 0 \\implies "
                f"A^{{-1}} = \\frac{{1}}{{{det_str}}} \\begin{{pmatrix}} {format_number(d)} & {format_number(-b)} \\\\ {format_number(-c)} & {format_number(a)} \\end{{pmatrix}}$$"
            )
        else:
            resultado.formula_2x2_detalle = (
                f"$$\\det(A) = ({format_number(a)})({format_number(d)}) - ({format_number(b)})({format_number(c)}) = 0$$\n"
                f"Dado que $\\det(A) = 0$, la matriz $A$ es singular (no invertible)."
            )

    # Paso 1: Construcción de la matriz aumentada [A | I_n]
    num_filas = n
    num_cols = 2 * n
    M: List[List[Fraction]] = []
    for i in range(n):
        fila = [Fraction(A[i][j].numerator, A[i][j].denominator) for j in range(n)]
        # Bloque derecho: matriz identidad I_n
        fila.extend([Fraction(1, 1) if i == j else Fraction(0, 1) for j in range(n)])
        M.append(fila)
        
    resultado.matriz_aumentada_inicial = clonar_matriz(M)
    
    pasos: List[Step] = []
    step_num = 1
    pasos.append(
        Step(
            step_number=step_num,
            title=r"Paso 1: Construcción de la Matriz Aumentada $[A \mid I_n]$",
            description=f"Se yuxtapone la matriz $A$ de orden ${n} \\times {n}$ con la matriz identidad $I_{{{n}}}$ de orden ${n} \\times {n}$ para formar una matriz de orden ${n} \\times {2*n}$.",
            matrix_state=M,
            operation_code="Partimos de [A | I]",
        )
    )
    
    usar_jordan = (resultado.metodo_utilizado == "gauss_jordan")
    es_singular = False
    motivo_singular = ""
    
    if usar_jordan:
        # MÉTODO GAUSS-JORDAN:
        # Para cada columna j: pivoteo, normalización a 1 y anulación completa arriba y abajo
        for j in range(n):
            # Buscar pivote no nulo en fila r >= j
            best_row = j
            max_val = abs(M[j][j])
            for r in range(j + 1, n):
                if abs(M[r][j]) > max_val:
                    max_val = abs(M[r][j])
                    best_row = r
                    
            if max_val == 0:
                es_singular = True
                motivo_singular = (
                    f"En la columna {j + 1} no existe ningún pivote no nulo en las filas restantes ({j + 1} a {n}). "
                    f"La matriz no es equivalente por filas a $I_{{{n}}}$."
                )
                break
                
            # Intercambio de filas si corresponde
            if best_row != j:
                M[j], M[best_row] = M[best_row], M[j]
                step_num += 1
                pasos.append(
                    Step(
                        step_number=step_num,
                        title=f"Intercambio de Filas: $F_{{{j + 1}}} \\leftrightarrow F_{{{best_row + 1}}}$",
                        description=f"Se intercambia la fila {j + 1} con la fila {best_row + 1} para ubicar el pivote no nulo ${format_number(M[j][j])}$.",
                        matrix_state=M,
                        operation_code=f"F_{j+1} <-> F_{best_row+1}",
                        highlight_rows=[j, best_row],
                    )
                )
                
            pivot_val = M[j][j]
            
            # Normalización del renglón pivote: hacer 1 el elemento diagonal
            if pivot_val != 1:
                inv_p = Fraction(1, 1) / pivot_val
                calc_details = []
                for c in range(j, num_cols):
                    orig = M[j][c]
                    M[j][c] *= inv_p
                    calc_details.append(
                        f"F_{j+1}[{c+1}]: {format_number(orig)} · ({format_number(inv_p)}) = {format_number(M[j][c])}"
                    )
                step_num += 1
                pasos.append(
                    Step(
                        step_number=step_num,
                        title=f"Normalización de Pivote: $F_{{{j + 1}}} \\leftarrow \\left(\\frac{{1}}{{{format_number(pivot_val)}}}\\right) \\cdot F_{{{j + 1}}}$",
                        description=f"Se divide la fila {j + 1} entre el pivote ${format_number(pivot_val)}$ para transformarlo en 1 unitario.",
                        matrix_state=M,
                        operation_code=f"F_{j+1} <- ({format_number(inv_p)})·F_{j+1}",
                        highlight_rows=[j],
                        highlight_pivot=(j, j),
                        calculation_details=calc_details,
                    )
                )
                
            # Anular los demás elementos en la columna j (arriba y abajo)
            for r in range(n):
                if r == j:
                    continue
                factor = M[r][j]
                if factor != 0:
                    calc_details = []
                    for c in range(num_cols):
                        orig_val = M[r][c]
                        sub = factor * M[j][c]
                        M[r][c] -= sub
                        calc_details.append(
                            f"Col {c+1}: {format_number(orig_val)} - ({format_number(factor)})·({format_number(M[j][c])}) = {format_number(M[r][c])}"
                        )
                    op_sign = "-" if factor > 0 else "+"
                    step_num += 1
                    pasos.append(
                        Step(
                            step_number=step_num,
                            title=f"Eliminación: $F_{{{r + 1}}} \\leftarrow F_{{{r + 1}}} {op_sign} {format_number(abs(factor))} \\cdot F_{{{j + 1}}}$",
                            description=f"Se hace cero la entrada en la fila {r + 1}, columna {j + 1} usando el pivote de la fila {j + 1}.",
                            matrix_state=M,
                            operation_code=f"F_{r+1} <- F_{r+1} {op_sign} ({format_number(abs(factor))})·F_{j+1}",
                            highlight_rows=[r, j],
                            calculation_details=calc_details,
                        )
                    )
                    
    else:
        # MÉTODO DE GAUSS (Eliminación hacia adelante + Fase regresiva):
        # Fase 1: Triangulación superior (ceros solo debajo de los pivotes)
        for j in range(n):
            best_row = j
            max_val = abs(M[j][j])
            for r in range(j + 1, n):
                if abs(M[r][j]) > max_val:
                    max_val = abs(M[r][j])
                    best_row = r
                    
            if max_val == 0:
                es_singular = True
                motivo_singular = (
                    f"En la columna {j + 1} no existe pivote no nulo. "
                    f"El rango de la matriz es estrictamente menor a {n}, por lo que no es invertible."
                )
                break
                
            if best_row != j:
                M[j], M[best_row] = M[best_row], M[j]
                step_num += 1
                pasos.append(
                    Step(
                        step_number=step_num,
                        title=f"Fase Gauss: Intercambio $F_{{{j + 1}}} \\leftrightarrow F_{{{best_row + 1}}}$",
                        description=f"Se intercambia fila {j + 1} con fila {best_row + 1} para ubicar el pivote ${format_number(M[j][j])}$.",
                        matrix_state=M,
                        operation_code=f"F_{j+1} <-> F_{best_row+1}",
                        highlight_rows=[j, best_row],
                    )
                )
                
            current_pivot = M[j][j]
            # Eliminar SOLAMENTE hacia abajo (r > j)
            for r in range(j + 1, n):
                factor = M[r][j] / current_pivot
                if factor != 0:
                    calc_details = []
                    for c in range(num_cols):
                        orig = M[r][c]
                        sub = factor * M[j][c]
                        M[r][c] -= sub
                        calc_details.append(
                            f"Col {c+1}: {format_number(orig)} - ({format_number(factor)})·({format_number(M[j][c])}) = {format_number(M[r][c])}"
                        )
                    op_sign = "-" if factor > 0 else "+"
                    step_num += 1
                    pasos.append(
                        Step(
                            step_number=step_num,
                            title=f"Eliminación Hacia Adelante: $F_{{{r + 1}}} \\leftarrow F_{{{r + 1}}} {op_sign} {format_number(abs(factor))} \\cdot F_{{{j + 1}}}$",
                            description=f"Se genera un cero debajo del pivote en fila {r + 1}, columna {j + 1}.",
                            matrix_state=M,
                            operation_code=f"F_{r+1} <- F_{r+1} {op_sign} ({format_number(abs(factor))})·F_{j+1}",
                            highlight_rows=[r, j],
                            calculation_details=calc_details,
                        )
                    )
                    
        # Verificar diagonal en la forma triangular superior
        if not es_singular:
            for j in range(n):
                if M[j][j] == 0:
                    es_singular = True
                    motivo_singular = f"El pivote en la diagonal en la fila {j + 1} es cero. Matriz singular."
                    break
                    
        # Fase 2: Reducción regresiva (sustitución hacia atrás de la identidad)
        if not es_singular:
            # Normalizar diagonales
            for j in range(n):
                p_diag = M[j][j]
                if p_diag != 1:
                    inv_diag = Fraction(1, 1) / p_diag
                    for c in range(num_cols):
                        M[j][c] *= inv_diag
                    step_num += 1
                    pasos.append(
                        Step(
                            step_number=step_num,
                            title=f"Normalización Diagonal: $F_{{{j + 1}}} \\leftarrow \\left(\\frac{{1}}{{{format_number(p_diag)}}}\\right) \\cdot F_{{{j + 1}}}$",
                            description=f"Se normaliza el pivote diagonal de la fila {j + 1} a 1.",
                            matrix_state=M,
                            operation_code=f"F_{j+1} <- ({format_number(inv_diag)})·F_{j+1}",
                            highlight_rows=[j],
                        )
                    )
            # Anular hacia atrás (de abajo hacia arriba)
            for j in range(n - 1, 0, -1):
                for r in range(j - 1, -1, -1):
                    factor = M[r][j]
                    if factor != 0:
                        for c in range(num_cols):
                            M[r][c] -= factor * M[j][c]
                        op_sign = "-" if factor > 0 else "+"
                        step_num += 1
                        pasos.append(
                            Step(
                                step_number=step_num,
                                title=f"Sustitución Regresiva: $F_{{{r + 1}}} \\leftarrow F_{{{r + 1}}} {op_sign} {format_number(abs(factor))} \\cdot F_{{{j + 1}}}$",
                                description=f"Se anula el término sobre la diagonal en fila {r + 1}, columna {j + 1}.",
                                matrix_state=M,
                                operation_code=f"F_{r+1} <- F_{r+1} {op_sign} ({format_number(abs(factor))})·F_{j+1}",
                                highlight_rows=[r, j],
                            )
                        )

    resultado.matriz_aumentada_final = clonar_matriz(M)
    resultado.pasos_reduccion = pasos
    
    # Comprobar si el bloque izquierdo es la identidad I_n
    if not es_singular:
        for i in range(n):
            for j in range(n):
                esperado = Fraction(1, 1) if i == j else Fraction(0, 1)
                if M[i][j] != esperado:
                    es_singular = True
                    motivo_singular = "El bloque izquierdo de la matriz no pudo reducirse a la matriz identidad I_n."
                    break
            if es_singular:
                break
                
    if es_singular:
        resultado.es_invertible = False
        resultado.matriz_inversa = None
        resultado.mensaje_diagnostico = (
            f"LA MATRIZ NO ES INVERTIBLE (Matriz Singular).\n"
            f"Razón teórica (Teorema de la Matriz Invertible): {motivo_singular}\n"
            f"El rango por filas es menor que {n}, por lo que no existe ninguna matriz C tal que C · A = I_n."
        )
        return resultado
        
    # Extracción de la matriz inversa A^(-1) del bloque derecho
    A_inv: List[List[Fraction]] = []
    for i in range(n):
        fila_inv = [M[i][n + j] for j in range(n)]
        A_inv.append(fila_inv)
        
    resultado.es_invertible = True
    resultado.matriz_inversa = A_inv
    resultado.mensaje_diagnostico = (
        f"MATRIZ INVERTIBLE (No Singular).\n"
        f"A es equivalente por filas a $I_{{{n}}}$, por lo que $[A \\mid I_{{{n}}}] \\sim [I_{{{n}}} \\mid A^{{-1}}]$.\n"
        f"La matriz inversa $A^{{-1}}$ ha sido obtenida satisfactoriamente."
    )
    
    # Verificación Rigurosa:
    # Comprobación 1: P1 = A · A^(-1) == I_n
    P1, _ = multiplicar_matrices(A, A_inv)
    verif1 = []
    residuo_cero_1 = True
    for i in range(n):
        for j in range(n):
            esperado = Fraction(1, 1) if i == j else Fraction(0, 1)
            val = P1[i][j]
            if val != esperado:
                residuo_cero_1 = False
            simb = "✓ Correcto" if val == esperado else "✗ Discrepancia"
            verif1.append(
                f"Entrada ({i+1}, {j+1}): $(A \\cdot A^{{-1}})_{{{i+1},{j+1}}} = {format_number(val)}$ "
                f"(Esperado: $(I_{{{n}}})_{{{i+1},{j+1}}} = {format_number(esperado)}$) $\\rightarrow$ {simb}"
            )
            
    # Comprobación 2: P2 = A^(-1) · A == I_n
    P2, _ = multiplicar_matrices(A_inv, A)
    verif2 = []
    residuo_cero_2 = True
    for i in range(n):
        for j in range(n):
            esperado = Fraction(1, 1) if i == j else Fraction(0, 1)
            val = P2[i][j]
            if val != esperado:
                residuo_cero_2 = False
            simb = "✓ Correcto" if val == esperado else "✗ Discrepancia"
            verif2.append(
                f"Entrada ({i+1}, {j+1}): $(A^{{-1}} \\cdot A)_{{{i+1},{j+1}}} = {format_number(val)}$ "
                f"(Esperado: $(I_{{{n}}})_{{{i+1},{j+1}}} = {format_number(esperado)}$) $\\rightarrow$ {simb}"
            )
            
    resultado.verificacion_A_por_Ainv = verif1
    resultado.verificacion_Ainv_por_A = verif2
    resultado.residuo_cero = (residuo_cero_1 and residuo_cero_2)
    
    return resultado
