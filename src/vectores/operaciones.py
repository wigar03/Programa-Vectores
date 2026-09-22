"""
Módulo de Operaciones Vectoriales en el Espacio Euclídeo R^n.
UAM - Facultad de Ingeniería y Arquitectura (FIA)
Álgebra Lineal (MTM0120)

MARCO TEÓRICO Y PROCEDIMIENTO ALGEBRAICO:
El conjunto R^n es el producto cartesiano de n copias del cuerpo de los números reales R:
    R^n = { (x_1, x_2, ..., x_n) : x_i en R, para todo 1 <= i <= n }

Dotado de las operaciones de adición interna (+) y producto por escalar externo (·),
(R^n, +, ·) constituye un Espacio Vectorial sobre el cuerpo R, satisfaciendo los 8 axiomas:
1. Conmutatividad de la suma: u + v = v + u
2. Asociatividad de la suma: (u + v) + w = u + (v + w)
3. Elemento neutro aditivo: Existe 0 = (0, ..., 0) tal que v + 0 = v
4. Elemento opuesto aditivo: Para cada v existe -v tal que v + (-v) = 0
5. Distributividad del escalar respecto a la suma vectorial: c · (u + v) = c·u + c·v
6. Distributividad de la suma de escalares: (c + d) · v = c·v + d·v
7. Asociatividad mixta: (c · d) · v = c · (d · v)
8. Identidad escalar: 1 · v = v

RESTRICCIÓN DIDÁCTICA:
Implementado 100% en Python estándar mediante bucles, condicionales y listas,
sin NumPy ni SciPy, con aritmética exacta mediante fractions.Fraction.
"""

from fractions import Fraction
from typing import Any, List, Union

from src.core.arithmetic import (
    parse_number,
    validar_vector_numerico,
    format_number,
    formatear_vector,
)


def obtener_dimension_vector(vector: List[Fraction]) -> int:
    """
    Retorna la dimensión n del vector en R^n.
    
    Procedimiento algebraico:
    La dimensión de un vector v = (v_1, ..., v_n) es el cardinal de sus componentes ordenadas.
    """
    return len(vector)


def validar_igualdad_dimension(u: List[Fraction], v: List[Fraction], operacion: str = "operación") -> int:
    """
    Verifica algebraicamente que dos vectores pertenezcan al mismo espacio vectorial R^n.
    
    Procedimiento algebraico:
    La suma y resta en álgebra lineal solo están definidas si ambos vectores pertenecen al mismo
    espacio vectorial. Si u en R^n y v en R^m con n != m, la operación no está definida.
    
    Lanza:
        ValueError: Si las dimensiones no coinciden.
    """
    dim_u = len(u)
    dim_v = len(v)
    if dim_u != dim_v:
        raise ValueError(
            f"Error dimensional en {operacion}: los vectores pertenecen a espacios vectoriales diferentes. "
            f"u pertenece a R^{dim_u} mientras que v pertenece a R^{dim_v}. "
            f"Ambos vectores deben tener exactamente la misma dimensión n."
        )
    return dim_u


def suma_vectores(u_in: Any, v_in: Any) -> List[Fraction]:
    """
    Calcula la suma algebraica de dos vectores en R^n: w = u + v.
    
    Procedimiento algebraico equivalente:
    Sean u = (u_1, u_2, ..., u_n) y v = (v_1, v_2, ..., v_n) dos vectores en R^n.
    La suma se define componente a componente como:
        w_i = u_i + v_i,   para todo 1 <= i <= n.
        
    El vector resultante w pertenece a R^n (propiedad de cerradura bajo la adición).
    
    Parámetros:
        u_in: Primer vector sumando (lista de valores numéricos).
        v_in: Segundo vector sumando (lista de valores numéricos).
        
    Retorna:
        Vector resultante en R^n como lista de Fraction.
    """
    u = validar_vector_numerico(u_in)
    v = validar_vector_numerico(v_in)
    dim = validar_igualdad_dimension(u, v, operacion="Suma de Vectores")
    
    resultado: List[Fraction] = []
    # Bucle estándar para realizar la suma componente a componente
    for i in range(dim):
        suma_componente = u[i] + v[i]
        resultado.append(suma_componente)
        
    return resultado


def resta_vectores(u_in: Any, v_in: Any) -> List[Fraction]:
    """
    Calcula la resta algebraica de dos vectores en R^n: w = u - v.
    
    Procedimiento algebraico equivalente:
    La sustracción de vectores se define formalmente como la adición del inverso aditivo (-v):
        w = u + (-1) · v
    Componente a componente:
        w_i = u_i - v_i,   para todo 1 <= i <= n.
        
    Parámetros:
        u_in: Vector minuendo.
        v_in: Vector sustraendo.
        
    Retorna:
        Vector diferencia en R^n como lista de Fraction.
    """
    u = validar_vector_numerico(u_in)
    v = validar_vector_numerico(v_in)
    dim = validar_igualdad_dimension(u, v, operacion="Resta de Vectores")
    
    resultado: List[Fraction] = []
    # Bucle estándar para realizar la resta componente a componente
    for i in range(dim):
        diferencia_componente = u[i] - v[i]
        resultado.append(diferencia_componente)
        
    return resultado


def multiplicar_escalar_vector(c_in: Any, v_in: Any) -> List[Fraction]:
    """
    Calcula el producto de un escalar c en R por un vector v en R^n: w = c · v.
    
    Procedimiento algebraico equivalente:
    Dado el escalar c y el vector v = (v_1, v_2, ..., v_n), la multiplicación escalar
    dilata, contrae o invierte el vector distribuyendo el factor en cada componente:
        (c · v)_i = c · v_i,   para todo 1 <= i <= n.
        
    El vector resultante pertenece a R^n (propiedad de cerradura bajo el producto por escalar).
    
    Parámetros:
        c_in: Escalar (número entero, decimal o fracción).
        v_in: Vector en R^n.
        
    Retorna:
        Vector resultante en R^n como lista de Fraction.
    """
    c = parse_number(c_in)
    v = validar_vector_numerico(v_in)
    
    resultado: List[Fraction] = []
    # Bucle estándar para distribuir el escalar c sobre cada elemento v_i
    for i in range(len(v)):
        producto_componente = c * v[i]
        resultado.append(producto_componente)
        
    return resultado


def producto_punto(u_in: Any, v_in: Any) -> Fraction:
    """
    Calcula el producto punto (producto escalar euclídeo estándar) en R^n: <u, v> = u · v.
    
    Procedimiento algebraico equivalente:
    Sean u, v en R^n:
        u · v = u_1·v_1 + u_2·v_2 + ... + u_n·v_n = SUMATORIA_{i=1}^n (u_i · v_i)
        
    Retorna:
        Escalar en Q como Fraction.
    """
    u = validar_vector_numerico(u_in)
    v = validar_vector_numerico(v_in)
    dim = validar_igualdad_dimension(u, v, operacion="Producto Punto")
    
    acumulador = Fraction(0, 1)
    for i in range(dim):
        acumulador += u[i] * v[i]
        
    return acumulador


def norma_cuadrada(v_in: Any) -> Fraction:
    """
    Calcula la norma euclídea al cuadrado: ||v||^2 = v · v = SUMATORIA (v_i^2).
    Permite evaluar magnitudes de forma exacta en el cuerpo racional sin pérdida por raíz flotante.
    """
    v = validar_vector_numerico(v_in)
    return producto_punto(v, v)


def combinacion_lineal_directa(coeficientes_in: List[Any], lista_vectores_in: List[Any]) -> List[Fraction]:
    """
    Evalúa la combinación lineal directa dados los escalares c_1, ..., c_k y vectores v_1, ..., v_k:
        w = c_1·v_1 + c_2·v_2 + ... + c_k·v_k
        
    Procedimiento algebraico:
    Multiplica cada vector v_j por su respectivo escalar c_j y suma acumulativamente los vectores
    resultantes en R^n.
    """
    if len(coeficientes_in) != len(lista_vectores_in):
        raise ValueError(
            f"El número de escalares ({len(coeficientes_in)}) debe ser igual al "
            f"número de vectores ({len(lista_vectores_in)})."
        )
    if len(lista_vectores_in) == 0:
        raise ValueError("La lista de vectores para la combinación no puede estar vacía.")
        
    c_list = [parse_number(c) for c in coeficientes_in]
    v_list = [validar_vector_numerico(v) for v in lista_vectores_in]
    
    # Validar que todos los vectores tengan la misma dimensión n
    dim = len(v_list[0])
    for j, vec in enumerate(v_list):
        if len(vec) != dim:
            raise ValueError(f"Vector v_{j+1} tiene dimensión {len(vec)}, diferente a la dimensión base {dim}.")
            
    # Acumular la suma ponderada
    acumulador = [Fraction(0, 1)] * dim
    for j in range(len(v_list)):
        ponderado = multiplicar_escalar_vector(c_list[j], v_list[j])
        acumulador = suma_vectores(acumulador, ponderado)
        
    return acumulador
