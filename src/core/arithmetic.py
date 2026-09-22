"""
Módulo de Aritmética Exacta y Validación Algebraica.
UAM - Álgebra Lineal (MTM0120)

FUNDAMENTO ALGEBRAICO:
En álgebra lineal computacional, el cuerpo base habitual es el conjunto de los números reales (R).
Sin embargo, las representaciones estándar en punto flotante binario (IEEE-754) introducen
errores por redondeo que pueden alterar propiedades fundamentales como el rango, la independencia
lineal y la compatibilidad de sistemas.

Para garantizar exactitud matemática absoluta sin recurrir a bibliotecas externas como NumPy o SciPy,
este módulo opera sobre el cuerpo de los números racionales (Q), donde:
    Q = { a / b : a, b en Z, b != 0 }
Las operaciones de suma, resta, multiplicación y división inversa son cerradas y exactas en Q.
"""

from fractions import Fraction
from typing import Any, List, Union, Tuple


def parse_number(val: Union[str, int, float, Fraction]) -> Fraction:
    """
    Convierte una representación numérica textual o numérica a un objeto Fraction exacto.
    
    Procedimiento algebraico:
    - Si la entrada es un entero 'k', se representa como k / 1.
    - Si la entrada es una fracción 'a/b', se extrae el numerador y denominador entero.
    - Si la entrada es un decimal 'd', se convierte a su forma fraccionaria irreducible irreducible a / 10^k.
    
    Parámetros:
        val: Cadena, entero, flotante o Fracción a normalizar.
        
    Retorna:
        Objeto Fraction en forma canónica irreducible.
        
    Lanza:
        ValueError: Si la cadena no puede ser interpretada como un número racional válido o si b == 0.
    """
    if isinstance(val, Fraction):
        return val
    if isinstance(val, int):
        return Fraction(val, 1)
    if isinstance(val, float):
        # Convertir float a string para evitar residuos binarios flotantes
        return Fraction(str(val))
    
    s = str(val).strip()
    if not s:
        return Fraction(0, 1)
    
    # Manejo de notación de división a/b
    if "/" in s:
        partes = s.split("/")
        if len(partes) != 2:
            raise ValueError(f"Formato de fracción inválido: '{s}'. Use 'a/b'.")
        try:
            num = int(partes[0].strip())
            den = int(partes[1].strip())
            if den == 0:
                raise ZeroDivisionError(f"División por cero en la fracción '{s}'.")
            return Fraction(num, den)
        except ValueError:
            raise ValueError(f"Numerador o denominador no entero en: '{s}'.")
            
    try:
        return Fraction(s)
    except Exception as exc:
        raise ValueError(f"No se pudo convertir '{s}' a un número racional válido.") from exc


def format_number(frac: Fraction, as_decimal: bool = False, decimal_places: int = 4) -> str:
    """
    Formatea un número racional para visualización limpia en interfaces y consolas.
    
    Procedimiento algebraico:
    - Si el denominador es 1, se muestra como entero: 'a/1' -> 'a'.
    - Si se solicita decimal, se evalúa a / b redondeado a 'decimal_places' dígitos.
    - En caso contrario, se muestra en su notación irreducible: 'a/b'.
    """
    if as_decimal:
        f_val = float(frac)
        if f_val.is_integer():
            return str(int(f_val))
        return f"{f_val:.{decimal_places}f}".rstrip("0").rstrip(".")
        
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def validar_vector_numerico(vector: Any) -> List[Fraction]:
    """
    Valida y convierte una lista o secuencia de valores a un vector algebraico en Q^n.
    
    Procedimiento algebraico:
    Un vector v en R^n es una n-tupla ordenada de escalares:
        v = (v_1, v_2, ..., v_n) donde cada v_i pertenece al cuerpo de escalares.
    
    Parámetros:
        vector: Lista o tupla de elementos convertibles a números racionales.
        
    Retorna:
        Lista de instancias de Fraction de longitud n >= 1.
        
    Lanza:
        ValueError: Si el vector está vacío o contiene elementos no numéricos.
    """
    if not isinstance(vector, (list, tuple)):
        raise TypeError(f"El vector debe ser una lista o tupla, recibido: {type(vector).__name__}")
    if len(vector) == 0:
        raise ValueError("El vector no puede ser vacío (la dimensión n debe ser mayor o igual a 1).")
        
    resultado: List[Fraction] = []
    for idx, item in enumerate(vector):
        try:
            resultado.append(parse_number(item))
        except Exception as e:
            raise ValueError(f"Componente {idx + 1} inválida en el vector ({item}): {e}") from e
            
    return resultado


def validar_matriz_numerica(matriz: Any) -> List[List[Fraction]]:
    """
    Valida y normaliza una matriz en R^(m x n).
    
    Procedimiento algebraico:
    Una matriz A de tamaño m x n es un arreglo bidimensional con m renglones y n columnas:
        A = [a_ij] para 1 <= i <= m, 1 <= j <= n.
    Todas las filas deben tener exactamente la misma cantidad de columnas n.
    
    Parámetros:
        matriz: Lista de filas (cada fila es una lista de elementos numéricos).
        
    Retorna:
        Matriz bidimensional (lista de listas de Fraction) de dimensión consistente m x n.
        
    Lanza:
        ValueError: Si la matriz no tiene filas, si alguna fila está vacía o si las filas tienen longitudes distintas.
    """
    if not isinstance(matriz, (list, tuple)):
        raise TypeError(f"La matriz debe ser una lista de listas, recibido: {type(matriz).__name__}")
    if len(matriz) == 0:
        raise ValueError("La matriz debe contener al menos una fila (m >= 1).")
        
    num_columnas: int = -1
    matriz_normalizada: List[List[Fraction]] = []
    
    for i, fila in enumerate(matriz):
        fila_norm = validar_vector_numerico(fila)
        if num_columnas == -1:
            num_columnas = len(fila_norm)
        elif len(fila_norm) != num_columnas:
            raise ValueError(
                f"Matriz inconsistente: la fila {i + 1} tiene {len(fila_norm)} columnas, "
                f"pero las filas anteriores tienen {num_columnas} columnas."
            )
        matriz_normalizada.append(fila_norm)
        
    return matriz_normalizada


def formatear_vector(vector: List[Fraction], as_decimal: bool = False) -> str:
    """
    Genera una representación textual legible de un vector en R^n: (v_1, v_2, ..., v_n).
    """
    elementos = [format_number(x, as_decimal=as_decimal) for x in vector]
    return f"({', '.join(elementos)})"


def formatear_matriz(matriz: List[List[Fraction]], as_decimal: bool = False) -> str:
    """
    Genera una representación tabular formateada con alineación de columnas.
    """
    if not matriz:
        return "[]"
    filas_str = [[format_number(val, as_decimal=as_decimal) for val in fila] for fila in matriz]
    num_cols = len(matriz[0])
    
    # Calcular el ancho máximo por columna para alineación estética
    anchos = [0] * num_cols
    for col in range(num_cols):
        anchos[col] = max(len(filas_str[row][col]) for row in range(len(matriz)))
        
    lineas = []
    for fila in filas_str:
        contenido = "  ".join(val.rjust(anchos[c]) for c, val in enumerate(fila))
        lineas.append(f"[ {contenido} ]")
        
    return "\n".join(lineas)
