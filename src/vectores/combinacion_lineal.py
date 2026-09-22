"""
Módulo de Evaluación y Resolución de Combinación Lineal en R^n.
UAM - Facultad de Ingeniería y Arquitectura (FIA)
Álgebra Lineal (MTM0120)

FUNDAMENTO ALGEBRAICO Y TEORÍA MATEMÁTICA:
Dado un conjunto no vacío de k vectores en R^n:
    S = { v_1, v_2, ..., v_k }, donde cada v_j = (v_1j, v_2j, ..., v_nj)^T en R^n
y un vector objetivo b = (b_1, b_2, ..., b_n)^T en R^n.

1. Definición Formal de Combinación Lineal:
   El vector b es una combinación lineal del conjunto S si y solo si existen escalares
   c_1, c_2, ..., c_k en el cuerpo R tales que:
       c_1 · v_1 + c_2 · v_2 + ... + c_k · v_k = b

2. Traducción a Sistema Matricial:
   Expandiendo componente a componente se obtiene un sistema lineal de n ecuaciones con k incógnitas:
       v_11 · c_1 + v_12 · c_2 + ... + v_1k · c_k = b_1
       v_21 · c_1 + v_22 · c_2 + ... + v_2k · c_k = b_2
       ...
       v_n1 · c_1 + v_n2 · c_2 + ... + v_nk · c_k = b_n

   En forma matricial compacta:
       V · c = b
   donde la matriz de coeficientes V en M_(n x k)(R) está formada colocando los vectores
   como columnas sucesivas: V = [ v_1 | v_2 | ... | v_k ], y c = [c_1, ..., c_k]^T.

3. Teorema de Rouché-Capelli aplicado al Subespacio Generado:
   La matriz aumentada del sistema es [ V | b ] de orden n x (k + 1).
   - CASO 1: rg(V) = rg(V|b) = k
     El sistema es Compatible Determinado (SCD). El vector b PERTENECE a gen(S) y se
     expresa de forma ÚNICA mediante los escalares calculados: c_1, c_2, ..., c_k.
   - CASO 2: rg(V) = rg(V|b) < k
     El sistema es Compatible Indeterminado (SCI). El vector b PERTENECE a gen(S), pero
     existen INFINITAS maneras de expresarlo como combinación lineal debido a que los
     vectores del conjunto son linealmente dependientes (LD).
   - CASO 3: rg(V) < rg(V|b)
     El sistema es Incompatible (SI). El vector b NO ES COMBINACIÓN LINEAL de S;
     b no pertenece al espacio generado gen{v_1, ..., v_k}.

RESTRICCIÓN DIDÁCTICA:
100% Python estándar sin NumPy ni SciPy, con aritmética exacta de fracciones y
resolución computacional mediante el motor de eliminación de renglones.
"""

from fractions import Fraction
from typing import Any, List, Dict, Optional, Union

from src.core.arithmetic import (
    parse_number,
    format_number,
    validar_vector_numerico,
    formatear_vector,
)
from src.solver.gauss_solver import solve_gaussian_elimination, GaussResult, Step
from src.vectores.operaciones import suma_vectores, multiplicar_escalar_vector


class ResultadoCombinacionLineal:
    """
    Estructura exhaustiva que documenta el análisis algebraico de combinación lineal.
    """
    def __init__(self):
        self.es_combinacion: bool = False
        self.tipo_solucion: str = ""  # "UNICA", "INFINITAS", "NO_COMBINACION"
        self.dimension_n: int = 0
        self.cantidad_vectores_k: int = 0
        self.vectores_conjunto: List[List[Fraction]] = []
        self.vector_objetivo: List[Fraction] = []
        self.matriz_aumentada_inicial: List[List[Fraction]] = []
        self.matriz_aumentada_final: List[List[Fraction]] = []
        self.escalares: Dict[str, Union[Fraction, str]] = {}
        self.escalares_vector: List[Union[Fraction, str]] = []
        self.escalares_particulares: Optional[List[Fraction]] = None
        self.expresion_algebraica: str = ""
        self.justificacion_teorica: str = ""
        self.pasos_reduccion: List[Step] = []
        self.comprobacion_sustitucion: List[str] = []


def evaluar_combinacion_lineal(
    vectores_conjunto_in: List[Any],
    vector_objetivo_in: Any
) -> ResultadoCombinacionLineal:
    """
    Determina computacional y algebraicamente si un vector b es combinación lineal de {v_1, ..., v_k}.
    
    Procedimiento algebraico:
    1. Valida que todos los vectores v_j y el vector b tengan la misma dimensión n (desconocida a priori).
    2. Construye la matriz aumentada [V | b] donde la j-ésima columna de V es el vector v_j.
    3. Aplica el método de Gauss-Jordan para obtener la matriz escalonada reducida.
    4. Analiza los rangos de la matriz de coeficientes y de la matriz aumentada.
    5. Deduce los escalares c_j y verifica la igualdad w = SUM(c_j · v_j) = b.
    
    Parámetros:
        vectores_conjunto_in: Lista de vectores [v_1, v_2, ..., v_k].
        vector_objetivo_in: Vector objetivo b.
        
    Retorna:
        Instancia de ResultadoCombinacionLineal con el dictamen y pasos.
    """
    if not isinstance(vectores_conjunto_in, (list, tuple)) or len(vectores_conjunto_in) == 0:
        raise ValueError("El conjunto de vectores debe contener al menos un vector (k >= 1).")
        
    # Validar y normalizar vectores
    vectores: List[List[Fraction]] = [validar_vector_numerico(v) for v in vectores_conjunto_in]
    b = validar_vector_numerico(vector_objetivo_in)
    
    k = len(vectores)
    n = len(vectores[0])
    
    # Validar que todos los vectores del conjunto tengan la misma dimensión n
    for idx, v in enumerate(vectores):
        if len(v) != n:
            raise ValueError(
                f"Inconsistencia de dimensión: El vector v_{idx + 1} tiene dimensión {len(v)}, "
                f"mientras que v_1 tiene dimensión {n}. Todos los vectores deben estar en R^{n}."
            )
            
    # Validar que el vector objetivo b tenga la misma dimensión n
    if len(b) != n:
        raise ValueError(
            f"El vector objetivo b tiene dimensión {len(b)}, pero los vectores dados están en R^{n}. "
            f"No puede existir combinación lineal entre espacios de dimensiones distintas."
        )
        
    resultado = ResultadoCombinacionLineal()
    resultado.dimension_n = n
    resultado.cantidad_vectores_k = k
    resultado.vectores_conjunto = vectores
    resultado.vector_objetivo = b
    
    # Construcción de la matriz aumentada [ V | b ] de orden n x (k + 1)
    # Renglón i: [ v_1[i], v_2[i], ..., v_k[i] | b[i] ]
    matriz_aumentada: List[List[Fraction]] = []
    for i in range(n):
        fila = [vectores[j][i] for j in range(k)] + [b[i]]
        matriz_aumentada.append(fila)
        
    resultado.matriz_aumentada_inicial = matriz_aumentada
    
    # Nombres de variables para los escalares c_1, c_2, ..., c_k
    nombres_escalares = [f"c_{j + 1}" for j in range(k)]
    
    # Resolver el sistema mediante Gauss-Jordan
    gauss_res = solve_gaussian_elimination(
        matriz_aumentada,
        variable_names=nombres_escalares,
        use_gauss_jordan=True
    )
    
    resultado.pasos_reduccion = gauss_res.steps
    resultado.matriz_aumentada_final = gauss_res.final_matrix
    resultado.escalares = gauss_res.solution
    resultado.escalares_vector = gauss_res.solution_vector
    
    # Clasificación algebraica
    if gauss_res.system_type == "SI":
        resultado.es_combinacion = False
        resultado.tipo_solucion = "NO_COMBINACION"
        resultado.justificacion_teorica = (
            rf"El vector $\vec{{b}}$ NO es combinación lineal del conjunto de vectores." "\n"
            rf"Justificación: $\operatorname{{rg}}(V) = {gauss_res.rank_A} < \operatorname{{rg}}(V|b) = {gauss_res.rank_Aug}$." "\n"
            rf"El sistema lineal $V \cdot \vec{{c}} = \vec{{b}}$ es INCOMPATIBLE (carece de solución). "
            rf"Por ende, el vector $\vec{{b}} \notin \operatorname{{gen}}\{{\vec{{v}}_1, \dots, \vec{{v}}_{{{k}}}\}}$."
        )
        resultado.expresion_algebraica = (
            f"b = {formatear_vector(b)} ∉ gen{{ v_1, ..., v_{k} }}"
        )
        
    elif gauss_res.system_type == "SCI":
        resultado.es_combinacion = True
        resultado.tipo_solucion = "INFINITAS"
        resultado.justificacion_teorica = (
            rf"El vector $\vec{{b}}$ SÍ es combinación lineal del conjunto de vectores (con INFINITAS soluciones)." "\n"
            rf"Justificación: $\operatorname{{rg}}(V) = \operatorname{{rg}}(V|b) = {gauss_res.rank_A} < k = {k}$ (número de vectores)." "\n"
            rf"El conjunto $\{{\vec{{v}}_1, \dots, \vec{{v}}_{{{k}}}\}}$ es Linealmente Dependiente (LD), por lo que existen "
            rf"infinitas combinaciones de escalares que reproducen exactamente el vector $\vec{{b}}$."
        )
        
        # Construir una solución particular asignando 0 a los parámetros libres
        escalares_particulares: List[Fraction] = []
        for j in range(k):
            var_val = gauss_res.solution_vector[j]
            if isinstance(var_val, Fraction):
                escalares_particulares.append(var_val)
            else:
                # Si contiene parámetros como 't', 's', evaluar caso particular con parámetro = 0
                val_str = str(var_val)
                # Extraer el término independiente si existe
                partes = val_str.split()
                try:
                    primer_elem = partes[0]
                    escalares_particulares.append(parse_number(primer_elem))
                except Exception:
                    escalares_particulares.append(Fraction(0, 1))
                    
        resultado.escalares_particulares = escalares_particulares
        
        # Formular expresión con escalares paramétricos
        terminos = [f"({gauss_res.solution_vector[j]})·v_{j+1}" for j in range(k)]
        resultado.expresion_algebraica = f"b = {' + '.join(terminos)}"
        
        # Comprobar la solución particular
        _comprobar_solucion(resultado, escalares_particulares)
        
    else:
        # SCD: Solución Única
        resultado.es_combinacion = True
        resultado.tipo_solucion = "UNICA"
        resultado.justificacion_teorica = (
            rf"El vector $\vec{{b}}$ SÍ es combinación lineal del conjunto de vectores de forma ÚNICA." "\n"
            rf"Justificación: $\operatorname{{rg}}(V) = \operatorname{{rg}}(V|b) = {gauss_res.rank_A} = k = {k}$ (número de vectores)." "\n"
            rf"Existe una única combinación de escalares $(c_1, \dots, c_{{{k}}})$ tal que $c_1\vec{{v}}_1 + \dots + c_{{{k}}}\vec{{v}}_{{{k}}} = \vec{{b}}$."
        )
        
        c_valores = [gauss_res.solution_vector[j] for j in range(k)]  # Todos son Fraction
        resultado.escalares_particulares = [parse_number(val) for val in c_valores]
        
        # Construir expresión algebraica limpia: b = c_1·v_1 + ... + c_k·v_k
        terminos = []
        for j in range(k):
            val_frac = parse_number(c_valores[j])
            terminos.append(f"({format_number(val_frac)})·v_{j+1}")
        resultado.expresion_algebraica = f"b = {' + '.join(terminos)}"
        
        _comprobar_solucion(resultado, resultado.escalares_particulares)
        
    return resultado


def _comprobar_solucion(resultado: ResultadoCombinacionLineal, c_vals: List[Fraction]):
    """Verifica que c_1·v_1 + ... + c_k·v_k == b componente por componente."""
    n = resultado.dimension_n
    k = resultado.cantidad_vectores_k
    
    # Calcular combinación componente por componente
    for i in range(n):
        terminos_str = []
        suma_i = Fraction(0, 1)
        for j in range(k):
            c_j = c_vals[j]
            v_ji = resultado.vectores_conjunto[j][i]
            producto = c_j * v_ji
            suma_i += producto
            terminos_str.append(f"({format_number(c_j)}) \\cdot ({format_number(v_ji)})")
            
        b_i = resultado.vector_objetivo[i]
        es_valido = (suma_i == b_i)
        simbolo = "✓ Satisface" if es_valido else "✗ Falla"
        
        desglose = " + ".join(terminos_str)
        resultado.comprobacion_sustitucion.append(
            f"Componente {i + 1}: ${desglose} = {format_number(suma_i)}$ [Esperado: ${format_number(b_i)}$] $\\rightarrow$ {simbolo}"
        )
