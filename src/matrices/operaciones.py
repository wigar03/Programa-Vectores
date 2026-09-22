"""
Módulo de Operaciones Matriciales Básicas en M_(m x n)(R).
UAM - Facultad de Ingeniería y Arquitectura (FIA)
Álgebra Lineal (MTM0120)

MARCO TEÓRICO Y PROCEDIMIENTO ALGEBRAICO:
Una matriz real A de orden m x n es una disposición rectangular de elementos escalares
distribuidos en m filas (renglones) y n columnas:
    A = [a_ij] donde 1 <= i <= m representa el renglón y 1 <= j <= n representa la columna.

El conjunto de todas las matrices de tamaño m x n denotado como M_(m x n)(R) forma un espacio
vectorial sobre R con las operaciones estándar de adición de matrices y producto por escalar.

1. Adición y Sustracción Matricial:
   - Condición de compatibilidad: Sean A, B matrices; A + B y A - B están definidas si y solo si
     dim(A) = dim(B) = m x n (mismo número de renglones y mismo número de columnas).
   - Definición elemento a elemento:
         (A + B)_ij = a_ij + b_ij
         (A - B)_ij = a_ij - b_ij = a_ij + (-1)·b_ij

2. Multiplicación por Escalar:
   - Sea c un escalar en R y A en M_(m x n)(R):
         (c · A)_ij = c · a_ij

3. Multiplicación de Matrices (Producto Interno de Renglón por Columna):
   - Condición de compatibilidad dimensional: Sean A una matriz de orden m x n y B una matriz de orden r x p.
     El producto matricial A · B está definido SI Y SOLO SI n = r, es decir, el número de COLUMNAS
     de la primera matriz A debe ser exactamente igual al número de FILAS de la segunda matriz B.
   - Definición del producto: La matriz resultante C = A · B tiene orden m x p, donde cada entrada
     c_ij es el producto punto del i-ésimo renglón de A por la j-ésima columna de B:
         c_ij = SUMATORIA_{k=1}^n (a_ik · b_kj) = a_i1·b_1j + a_i2·b_2j + ... + a_in·b_nj
   - Propiedad crucial: El producto de matrices es asociativo pero en general NO es conmutativo (A·B != B·A).

RESTRICCIÓN DIDÁCTICA:
Implementación 100% en Python estándar mediante bucles anidados for y listas,
sin librerías matriciales externas como NumPy o SciPy.
"""

from fractions import Fraction
from typing import Any, List, Tuple, Dict

from src.core.arithmetic import (
    parse_number,
    validar_matriz_numerica,
    format_number,
    formatear_matriz,
)


def obtener_dimensiones_matriz(matriz: List[List[Fraction]]) -> Tuple[int, int]:
    """
    Retorna la tupla de dimensiones (filas, columnas) = (m, n) de la matriz.
    
    Procedimiento algebraico:
    m = cardinal de los renglones (len(matriz))
    n = cardinal de las columnas de cualquier fila (len(matriz[0]))
    """
    m = len(matriz)
    n = len(matriz[0]) if m > 0 else 0
    return (m, n)


def validar_compatibilidad_suma(
    A: List[List[Fraction]], B: List[List[Fraction]], operacion: str = "Operación matricial"
) -> Tuple[int, int]:
    """
    Valida rigurosamente que dos matrices tengan exactamente el mismo orden m x n.
    
    Procedimiento algebraico:
    La adición de matrices es una operación binaria interna definida exclusivamente en el
    mismo espacio vectorial M_(m x n). Si dim(A) != dim(B), la operación carece de sentido algebraico.
    
    Lanza:
        ValueError: Si los órdenes difieren.
    """
    m_A, n_A = obtener_dimensiones_matriz(A)
    m_B, n_B = obtener_dimensiones_matriz(B)
    
    if m_A != m_B or n_A != n_B:
        raise ValueError(
            f"Incompatibilidad dimensional en {operacion}: "
            f"La matriz A es de orden {m_A}x{n_A} y la matriz B es de orden {m_B}x{n_B}. "
            f"Para sumar o restar, ambas matrices deben tener dimensiones idénticas (m x n)."
        )
    return (m_A, n_A)


def suma_matrices(A_in: Any, B_in: Any) -> List[List[Fraction]]:
    """
    Calcula la suma matricial C = A + B.
    
    Procedimiento algebraico equivalente:
    Sean A = [a_ij] y B = [b_ij] en M_(m x n)(R).
    La matriz suma C = [c_ij] se calcula como:
        c_ij = a_ij + b_ij,   para todo 1 <= i <= m, 1 <= j <= n.
        
    Parámetros:
        A_in: Primera matriz sumando.
        B_in: Segunda matriz sumando.
        
    Retorna:
        Matriz suma de orden m x n (lista de listas de Fraction).
    """
    A = validar_matriz_numerica(A_in)
    B = validar_matriz_numerica(B_in)
    m, n = validar_compatibilidad_suma(A, B, operacion="Suma de Matrices")
    
    C: List[List[Fraction]] = []
    # Recorrido por renglones (índice i)
    for i in range(m):
        fila_c: List[Fraction] = []
        # Recorrido por columnas (índice j)
        for j in range(n):
            suma_ij = A[i][j] + B[i][j]
            fila_c.append(suma_ij)
        C.append(fila_c)
        
    return C


def resta_matrices(A_in: Any, B_in: Any) -> List[List[Fraction]]:
    """
    Calcula la resta matricial C = A - B.
    
    Procedimiento algebraico equivalente:
    Equivale a sumar a A el inverso aditivo (-1)·B:
        c_ij = a_ij - b_ij,   para todo 1 <= i <= m, 1 <= j <= n.
        
    Parámetros:
        A_in: Matriz minuendo de orden m x n.
        B_in: Matriz sustraendo de orden m x n.
        
    Retorna:
        Matriz diferencia de orden m x n (lista de listas de Fraction).
    """
    A = validar_matriz_numerica(A_in)
    B = validar_matriz_numerica(B_in)
    m, n = validar_compatibilidad_suma(A, B, operacion="Resta de Matrices")
    
    C: List[List[Fraction]] = []
    for i in range(m):
        fila_c: List[Fraction] = []
        for j in range(n):
            resta_ij = A[i][j] - B[i][j]
            fila_c.append(resta_ij)
        C.append(fila_c)
        
    return C


def multiplicar_escalar_matriz(c_in: Any, A_in: Any) -> List[List[Fraction]]:
    """
    Calcula el producto de un escalar c por una matriz A: C = c · A.
    
    Procedimiento algebraico equivalente:
    Multiplica cada entrada a_ij por el escalar c:
        (c · A)_ij = c · a_ij,   para todo 1 <= i <= m, 1 <= j <= n.
        
    Parámetros:
        c_in: Escalar (entero, decimal o fracción).
        A_in: Matriz de orden m x n.
        
    Retorna:
        Matriz ponderada c·A en M_(m x n).
    """
    c = parse_number(c_in)
    A = validar_matriz_numerica(A_in)
    m, n = obtener_dimensiones_matriz(A)
    
    C: List[List[Fraction]] = []
    for i in range(m):
        fila_c: List[Fraction] = []
        for j in range(n):
            fila_c.append(c * A[i][j])
        C.append(fila_c)
        
    return C


def multiplicar_matrices(A_in: Any, B_in: Any) -> Tuple[List[List[Fraction]], List[str]]:
    """
    Calcula el producto matricial C = A_(m x n) · B_(n x p).
    
    Procedimiento algebraico equivalente:
    Para que el producto esté definido, el número de columnas de A (n) debe ser igual
    al número de renglones de B (n).
    
    Cada entrada c_ij de la matriz C_(m x p) se obtiene calculando la sumatoria:
        c_ij = SUMATORIA_{k=1}^n (a_ik · b_kj) = a_i1·b_1j + a_i2·b_2j + ... + a_in·b_nj
        
    Parámetros:
        A_in: Matriz izquierda de orden m x n.
        B_in: Matriz derecha de orden n x p.
        
    Retorna:
        Tupla con:
        1. C: Matriz producto resultante de orden m x p.
        2. pasos: Lista detallada con el desglose algebraico de cada componente c_ij.
        
    Lanza:
        ValueError: Si columnas(A) != filas(B).
    """
    A = validar_matriz_numerica(A_in)
    B = validar_matriz_numerica(B_in)
    
    m, n_A = obtener_dimensiones_matriz(A)
    m_B, p = obtener_dimensiones_matriz(B)
    
    # Verificación de compatibilidad dimensional según la teoría de matrices
    if n_A != m_B:
        raise ValueError(
            f"Error dimensional en Multiplicación de Matrices A · B: "
            f"La matriz A tiene orden {m}x{n_A} (columnas = {n_A}) y la matriz B tiene orden {m_B}x{p} (filas = {m_B}). "
            f"Para multiplicar A · B, el número de columnas de A ({n_A}) debe ser idéntico al número de filas de B ({m_B})."
        )
        
    C: List[List[Fraction]] = []
    pasos_detalle: List[str] = []
    
    # Bucle i: recorre los m renglones de A
    for i in range(m):
        fila_c: List[Fraction] = []
        # Bucle j: recorre las p columnas de B
        for j in range(p):
            suma_terminos = Fraction(0, 1)
            terminos_explicacion: List[str] = []
            
            # Bucle k: realiza el producto punto del renglón i de A con la columna j de B
            for k in range(n_A):
                producto_parcial = A[i][k] * B[k][j]
                suma_terminos += producto_parcial
                terminos_explicacion.append(
                    f"({format_number(A[i][k])}) \\cdot ({format_number(B[k][j])})"
                )
                
            fila_c.append(suma_terminos)
            
            # Registrar el paso algebraico explícito
            desglose = " + ".join(terminos_explicacion)
            pasos_detalle.append(
                f"c_{{{i+1},{j+1}}} = {desglose} = {format_number(suma_terminos)}"
            )
            
        C.append(fila_c)
        
    return (C, pasos_detalle)


def transpuesta_matriz(A_in: Any) -> List[List[Fraction]]:
    """
    Calcula la transpuesta de una matriz A: C = A^T.
    
    Procedimiento algebraico equivalente:
    Si A es de orden m x n, su transpuesta A^T es de orden n x m, donde las filas
    de A se convierten en las columnas de A^T:
        (A^T)_ji = a_ij,   para todo 1 <= i <= m, 1 <= j <= n.
    """
    A = validar_matriz_numerica(A_in)
    m, n = obtener_dimensiones_matriz(A)
    
    A_T: List[List[Fraction]] = []
    for j in range(n):
        fila_t: List[Fraction] = []
        for i in range(m):
            fila_t.append(A[i][j])
        A_T.append(fila_t)
        
    return A_T


def crear_matriz_identidad(n: int) -> List[List[Fraction]]:
    """
    Construye la matriz identidad I_n de orden n x n.
    
    Procedimiento algebraico:
    I_n = [delta_ij] donde delta_ij = 1 si i == j, y 0 si i != j (Delta de Kronecker).
    Cumple A · I_n = A e I_m · A = A.
    """
    if n <= 0:
        raise ValueError(f"El orden de la matriz identidad debe ser n >= 1, recibido: {n}.")
        
    I: List[List[Fraction]] = []
    for i in range(n):
        fila = [Fraction(1, 1) if i == j else Fraction(0, 1) for j in range(n)]
        I.append(fila)
    return I
