"""
================================================================================
UNIVERSIDAD AMERICANA (UAM)
Facultad de Ingeniería y Arquitectura (FIA)
Álgebra Lineal (MTM0120)
Módulo: Cálculo Computacional de Determinantes de Matrices Cuadradas
================================================================================
FUNDAMENTO MATEMÁTICO Y PROCEDIMIENTO ALGEBRAICO:

El determinante es una función escalar que asigna a cada matriz cuadrada A en M_(n x n)(R)
un único número real denotado como det(A) o |A|.

1. INTERPRETACIÓN GEOMÉTRICA Y ALGEBRAICA:
   - Para n = 1: det([a]) = a (longitud con signo en R).
   - Para n = 2: |det(A)| representa el área orientada del paralelogramo generado por
     los vectores fila (o columna) en R^2.
   - Para n = 3: |det(A)| representa el volumen orientado del paralelepípedo generado
     en R^3.
   - Para n >= 4: Hipervolumen n-dimensional en R^n.
   - Invertibilidad: Una matriz cuadrada A es invertible (no singular) si y solo si
     det(A) != 0. Si det(A) = 0, la matriz es singular (rango r < n, filas L.D.).

2. MÉTODOS DE CÁLCULO IMPLEMENTADOS:

   A) EXPANSIÓN POR COFACTORES (TEOREMA DE DESARROLLO DE LAPLACE):
      Dada A en M_(n x n)(R), para cualquier fila fija i (1 <= i <= n):
          det(A) = sum_{j=1}^n a_ij * C_ij
      donde:
          C_ij = (-1)^(i + j) * det(M_ij)
      y M_ij es la submatriz menor de orden (n - 1) x (n - 1) que resulta de suprimir
      la fila i y la columna j de A.
      
      Complejidad Computacional: O(n!) operaciones factoriales.
      - Para n = 1: 1 operación.
      - Para n = 2: 2 multiplicaciones (ad - bc).
      - Para n = 3: 6 multiplicaciones y sumas (regla de Sarrus).
      - Para n = 4: 24 evaluaciones de menores 3x3 (~40 operaciones).
      - Para n = 5: 120 evaluaciones de menores (~205 operaciones).
      - Para n = 8: 40,320 evaluaciones.
      Estrategia óptima: Selección de la fila o columna con mayor cantidad de ceros
      para anular términos a_ij * C_ij y minimizar la recursión.

   B) DESCOMPOSICIÓN LU CON PIVOTEO PARCIAL (PA = LU):
      Mediante eliminación gaussiana por renglones con pivoteo parcial, se obtienen:
      - P: Matriz de permutación que registra 's' intercambios de filas.
      - L: Matriz triangular inferior con unos en la diagonal principal y
           multiplicadores m_ik = a_ik / a_kk debajo de la diagonal.
      - U: Matriz triangular superior resultante de la reducción.
      
      Por propiedades del determinante:
          det(P * A) = det(L * U)
          det(P) * det(A) = det(L) * det(U)
          (-1)^s * det(A) = 1 * prod_{i=1}^n u_ii
          det(A) = (-1)^s * prod_{i=1}^n u_ii
          
      Complejidad Computacional: O(n^3) operaciones polinomiales (~ 2/3 * n^3 flops).
      - Para n = 2: ~2 operaciones.
      - Para n = 3: ~14 operaciones.
      - Para n = 4: ~36 operaciones.
      - Para n = 5: ~75 operaciones.
      - Para n = 8: ~320 operaciones.

3. RESTRICCIÓN DIDÁCTICA Y TÉCNICA:
   100% Python estándar con aritmética exacta fraccionaria (fractions.Fraction).
   Queda estrictamente prohibido el uso de NumPy, SciPy y funciones de álgebra lineal de math.
================================================================================
"""

from fractions import Fraction
from typing import List, Tuple, Dict, Any, Optional, Union

from src.core.arithmetic import (
    parse_number,
    format_number,
    validar_matriz_numerica,
    formatear_matriz,
)


# ==============================================================================
# BLOQUE 1: ESTRUCTURAS DE DATOS PARA RESULTADOS Y PASOS
# ==============================================================================

class PasoDeterminante:
    """
    Representa un paso individual en el cálculo del determinante (Cofactores o LU).
    Permite registrar la justificación algebraica y el estado intermedio.
    """
    def __init__(
        self,
        numero: int,
        titulo: str,
        descripcion: str,
        matriz_estado: Optional[List[List[Fraction]]] = None,
        detalles: Optional[List[str]] = None,
    ):
        self.numero = numero
        self.titulo = titulo
        self.descripcion = descripcion
        self.matriz_estado = (
            [[Fraction(x.numerator, x.denominator) for x in fila] for fila in matriz_estado]
            if matriz_estado is not None
            else None
        )
        self.detalles = detalles or []


class AnalisisEficiencia:
    """
    Estructura que almacena la evaluación comparativa previa de eficiencia
    entre el Método de Cofactores y la Descomposición LU para una dimensión dada.
    """
    def __init__(self, n: int, ceros_totales: int = 0):
        self.orden_n = n
        self.ceros_totales = ceros_totales
        
        # Estimación de operaciones para Cofactores: O(n!)
        # n! evaluaciones de menores
        self.ops_cofactores = self._calcular_operaciones_cofactores(n)
        self.complejidad_cofactores = f"O(n!) = O({n}!)"
        
        # Estimación de operaciones para LU: O(n^3)
        # Aproximadamente 2/3 * n^3 + n multiplicaciones
        self.ops_lu = self._calcular_operaciones_lu(n)
        self.complejidad_lu = f"O(n³) = O({n}³)"
        
        # Determinación del método más eficiente
        if n <= 2:
            self.metodo_recomendado = "ambos"
            self.metodo_recomendado_nombre = "Cualquiera (Ambos óptimos para n ≤ 2)"
            self.justificacion = (
                f"Para orden n = {n}, el número de operaciones es casi idéntico. "
                "Cofactores aplica la fórmula analítica directa inmediata (ad - bc) "
                "y LU realiza una reducción elemental equivalente."
            )
            self.insignia_cofactores = "Óptimo y Directo"
            self.insignia_lu = "Óptimo"
        elif n == 3:
            self.metodo_recomendado = "lu"
            self.metodo_recomendado_nombre = "Descomposición LU (Leve ventaja)"
            self.justificacion = (
                f"Para n = 3, Cofactores requiere evaluar 3 menores de 2×2 (~{self.ops_cofactores} ops), "
                f"mientras que LU realiza la triangulación en ~{self.ops_lu} operaciones elementales. "
                "Ambos métodos son rápidos, pero LU escala mejor."
            )
            self.insignia_cofactores = "Didáctico (Sarrus / Menores)"
            self.insignia_lu = "Recomendado por Eficiencia"
        else:
            self.metodo_recomendado = "lu"
            self.metodo_recomendado_nombre = "Descomposición LU (Ampliamente Superior)"
            self.justificacion = (
                f"¡Para n = {n}, la Descomposición LU es drásticamente más eficiente! "
                f"Cofactores requiere un orden factorial de ~{self.ops_cofactores:,} operaciones, "
                f"mientras que LU resuelve la triangulación en únicamente ~{self.ops_lu:,} operaciones (O(n³)). "
                f"La diferencia de velocidad es de más de {max(1, self.ops_cofactores // max(1, self.ops_lu)):,} veces."
            )
            self.insignia_cofactores = "Inviable / Factorial O(n!)"
            self.insignia_lu = "ALTAMENTE RECOMENDADO (O(n³))"

    def _calcular_operaciones_cofactores(self, n: int) -> int:
        """Calcula el número aproximado de operaciones para la expansión de Laplace."""
        if n <= 1:
            return 1
        if n == 2:
            return 3  # 2 multiplicaciones + 1 resta (ad - bc)
        # Recursión: n * (ops(n - 1) + 2)
        total = 3
        for k in range(3, n + 1):
            total = k * (total + 2)
        return total

    def _calcular_operaciones_lu(self, n: int) -> int:
        """Calcula el número aproximado de operaciones (flops) para la descomposición LU."""
        if n <= 1:
            return 1
        # Suma de operaciones de eliminación: sum_{k=1}^{n-1} (n - k) * (2*(n - k) + 1) + (n - 1)
        ops = 0
        for k in range(n - 1):
            filas_restantes = n - 1 - k
            # Cálculo de multiplicador + actualización de fila + productos
            ops += filas_restantes * (2 * filas_restantes + 1)
        # Producto de la diagonal de U
        ops += (n - 1)
        return max(1, ops)


class ResultadoDeterminante:
    """
    Estructura que encapsula el resultado completo del cálculo del determinante.
    """
    def __init__(self):
        self.metodo: str = ""  # "cofactores" o "lu"
        self.orden_n: int = 0
        self.matriz_original: List[List[Fraction]] = []
        self.determinante: Fraction = Fraction(0, 1)
        self.es_invertible: bool = False
        self.complejidad_teorica: str = ""
        self.operaciones_estimadas: int = 0
        self.pasos: List[PasoDeterminante] = []
        self.detalles_especificos: Dict[str, Any] = {}
        self.analisis_eficiencia: Optional[AnalisisEficiencia] = None


# ==============================================================================
# BLOQUE 2: FUNCIONES AUXILIARES DE COPIADO Y SUBMATRICES MENORES
# ==============================================================================

def clonar_matriz_fracciones(mat: List[List[Fraction]]) -> List[List[Fraction]]:
    """
    Genera una copia profunda exacta de una matriz bidimensional de fracciones.
    """
    return [[Fraction(val.numerator, val.denominator) for val in fila] for fila in mat]


def obtener_submatriz_menor(
    matriz: List[List[Fraction]],
    fila_eliminar: int,
    columna_eliminar: int
) -> List[List[Fraction]]:
    """
    Extrae la submatriz menor M_ij de orden (n - 1) x (n - 1) suprimiendo
    la fila 'fila_eliminar' y la columna 'columna_eliminar'.
    """
    n = len(matriz)
    submatriz: List[List[Fraction]] = []
    for i in range(n):
        if i == fila_eliminar:
            continue
        fila_nueva: List[Fraction] = []
        for j in range(n):
            if j == columna_eliminar:
                continue
            fila_nueva.append(Fraction(matriz[i][j].numerator, matriz[i][j].denominator))
        submatriz.append(fila_nueva)
    return submatriz


def analizar_eficiencia_determinante(
    matriz_o_n: Union[int, List[List[Any]]]
) -> AnalisisEficiencia:
    """
    Realiza una evaluación analítica previa de eficiencia entre Cofactores y LU.
    
    Parámetros:
        matriz_o_n: Entero n con la dimensión o matriz cuadrada a evaluar.
        
    Retorna:
        Instancia de AnalisisEficiencia con conteos y recomendaciones.
    """
    if isinstance(matriz_o_n, int):
        n = max(1, matriz_o_n)
        return AnalisisEficiencia(n=n, ceros_totales=0)
    
    matriz = validar_matriz_numerica(matriz_o_n)
    n = len(matriz)
    ceros = sum(1 for fila in matriz for val in fila if val == 0)
    return AnalisisEficiencia(n=n, ceros_totales=ceros)


# ==============================================================================
# BLOQUE 3: MÉTODO 1 - EXPANSIÓN POR COFACTORES (DESARROLLO DE LAPLACE)
# ==============================================================================

def calcular_determinante_cofactores(matriz_in: Any) -> ResultadoDeterminante:
    """
    Calcula el determinante de una matriz cuadrada A de orden n x n
    mediante el Método de Expansión por Cofactores (Teorema de Laplace).
    
    Procedimiento algebraico:
    1. Valida que la matriz sea cuadrada (m = n >= 1).
    2. Para n = 1: det(A) = a_11.
    3. Para n = 2: det(A) = a_11 * a_22 - a_12 * a_21.
    4. Para n >= 3:
       - Identifica la fila o columna con mayor número de ceros para optimizar operaciones.
       - Desarrolla la sumatoria: det(A) = sum_{k} a_ik * (-1)^(i + k) * det(M_ik).
       - Registra recursivamente los menores y cofactores calculados.
    
    Parámetros:
        matriz_in: Matriz cuadrada numérica en R^(n x n).
        
    Retorna:
        Instancia de ResultadoDeterminante con valor exacto y registro paso a paso.
        
    Lanza:
        ValueError: Si la matriz no es cuadrada o está vacía.
    """
    matriz = validar_matriz_numerica(matriz_in)
    n = len(matriz)
    if len(matriz[0]) != n:
        raise ValueError(
            f"El cálculo del determinante exige una matriz estrictamente cuadrada. "
            f"Dimensiones recibidas: {n} filas x {len(matriz[0])} columnas."
        )

    res = ResultadoDeterminante()
    res.metodo = "cofactores"
    res.orden_n = n
    res.matriz_original = clonar_matriz_fracciones(matriz)
    res.analisis_eficiencia = analizar_eficiencia_determinante(matriz)
    res.complejidad_teorica = "O(n!) [Complejidad Factorial de Laplace]"
    res.operaciones_estimadas = res.analisis_eficiencia.ops_cofactores

    contador_pasos = 0

    # Función interna recursiva para registrar pasos detallados
    def resolver_recursivo(
        mat: List[List[Fraction]],
        nivel: int = 1,
        etiqueta_submatriz: str = "A"
    ) -> Tuple[Fraction, List[str]]:
        nonlocal contador_pasos
        orden_actual = len(mat)
        lineas_explicativas: List[str] = []

        # Caso base 1: Orden 1x1
        if orden_actual == 1:
            val = mat[0][0]
            lineas_explicativas.append(
                f"Matriz $1 \\times 1$ $[{format_number(val)}]$: $\\det(A) = {format_number(val)}$"
            )
            return val, lineas_explicativas

        # Caso base 2: Orden 2x2
        if orden_actual == 2:
            a, b = mat[0][0], mat[0][1]
            c, d = mat[1][0], mat[1][1]
            prod_diag_principal = a * d
            prod_diag_secundaria = b * c
            det_2x2 = prod_diag_principal - prod_diag_secundaria
            expr = (
                f"$\\det({etiqueta_submatriz}) = ({format_number(a)}) \\cdot ({format_number(d)}) - "
                f"({format_number(b)}) \\cdot ({format_number(c)}) = "
                f"{format_number(prod_diag_principal)} - ({format_number(prod_diag_secundaria)}) = "
                f"{format_number(det_2x2)}$"
            )
            lineas_explicativas.append(expr)
            return det_2x2, lineas_explicativas

        # Caso general: Orden n >= 3
        # Buscar la mejor línea (fila o columna) con mayor cantidad de ceros
        mejor_tipo = "fila"
        mejor_indice = 0
        max_ceros = -1

        # Evaluar filas
        for i in range(orden_actual):
            ceros_fila = sum(1 for c in range(orden_actual) if mat[i][c] == 0)
            if ceros_fila > max_ceros:
                max_ceros = ceros_fila
                mejor_tipo = "fila"
                mejor_indice = i

        # Evaluar columnas
        for j in range(orden_actual):
            ceros_col = sum(1 for r in range(orden_actual) if mat[r][j] == 0)
            if ceros_col > max_ceros:
                max_ceros = ceros_col
                mejor_tipo = "columna"
                mejor_indice = j

        lineas_explicativas.append(
            f"Desarrollo por {mejor_tipo} {mejor_indice + 1} (contiene {max_ceros} ceros para optimizar cómputo):"
        )

        suma_acumulada = Fraction(0, 1)
        terminos_suma_str: List[str] = []

        for k in range(orden_actual):
            if mejor_tipo == "fila":
                fila_idx = mejor_indice
                col_idx = k
            else:
                fila_idx = k
                col_idx = mejor_indice

            elemento = mat[fila_idx][col_idx]
            signo = 1 if ((fila_idx + col_idx) % 2 == 0) else -1
            signo_str = "+1" if signo == 1 else "-1"

            sub_m = obtener_submatriz_menor(mat, fila_idx, col_idx)
            nombre_menor = f"M_{{{fila_idx + 1},{col_idx + 1}}}"

            if elemento == 0:
                lineas_explicativas.append(
                    f"Elemento $a_{{{fila_idx + 1},{col_idx + 1}}} = 0$: "
                    f"Término nulo $0 \\cdot C_{{{fila_idx + 1},{col_idx + 1}}} = 0$ (se omite el cálculo del menor)."
                )
                terminos_suma_str.append("0")
                continue

            # Evaluar el menor recursivamente
            det_menor, pasos_menor = resolver_recursivo(
                sub_m, nivel=nivel + 1, etiqueta_submatriz=nombre_menor
            )
            cofactor = Fraction(signo, 1) * det_menor
            termino_valor = elemento * cofactor
            suma_acumulada += termino_valor

            lineas_explicativas.append(
                f"Elemento $a_{{{fila_idx + 1},{col_idx + 1}}} = {format_number(elemento)}$: "
                f"Signo $(-1)^{{{fila_idx + 1} + {col_idx + 1}}} = {signo_str}$, "
                f"$\\det({nombre_menor}) = {format_number(det_menor)}$, "
                f"Cofactor $C_{{{fila_idx + 1},{col_idx + 1}}} = {format_number(cofactor)}$. "
                f"Término: $({format_number(elemento)}) \\cdot ({format_number(cofactor)}) = {format_number(termino_valor)}$."
            )
            for pm in pasos_menor:
                lineas_explicativas.append(f"  $\\rightarrow$ {pm}")

            terminos_suma_str.append(format_number(termino_valor))

        total_str = " + ".join(terminos_suma_str)
        lineas_explicativas.append(
            f"Suma de cofactores: $\\det({etiqueta_submatriz}) = {total_str} = {format_number(suma_acumulada)}$"
        )
        return suma_acumulada, lineas_explicativas

    # Paso 0: Registro de la matriz inicial
    contador_pasos += 1
    res.pasos.append(
        PasoDeterminante(
            numero=contador_pasos,
            titulo=f"Matriz Cuadrada A de Orden ${n} \\times {n}$",
            descripcion="Se plantea la matriz cuadrada para expansión por cofactores (Laplace).",
            matriz_estado=matriz,
            detalles=[
                f"Dimensión: ${n} \\times {n}$ elementos.",
                f"Complejidad teórica: $\\mathcal{{O}}(n!) = \\mathcal{{O}}({n}!)$ operaciones factoriales.",
                f"Operaciones elementales estimadas: ~{res.operaciones_estimadas:,} cálculos.",
            ],
        )
    )

    # Ejecución del desarrollo recursivo
    det_final, detalles_desarrollo = resolver_recursivo(matriz, nivel=1, etiqueta_submatriz="A")
    res.determinante = det_final
    res.es_invertible = (det_final != 0)

    # Registrar el desarrollo completo como paso analítico
    contador_pasos += 1
    res.pasos.append(
        PasoDeterminante(
            numero=contador_pasos,
            titulo="Desarrollo de Expansión por Laplace",
            descripcion="Cálculo sistemático de cofactores, signos de posición y menores complementarios.",
            matriz_estado=matriz,
            detalles=detalles_desarrollo,
        )
    )

    # Registrar conclusión
    contador_pasos += 1
    res.pasos.append(
        PasoDeterminante(
            numero=contador_pasos,
            titulo="Conclusión e Invertibilidad",
            descripcion=(
                f"Determinante obtenido: $\\det(A) = {format_number(det_final)}$. "
                f"La matriz es {'INVERTIBLE (No Singular)' if res.es_invertible else 'SINGULAR (No Invertible)'}."
            ),
            matriz_estado=matriz,
            detalles=[
                f"Valor exacto fraccionario: ${format_number(det_final)}$",
                f"Valor decimal aproximado: $\\approx {format_number(det_final, as_decimal=True, decimal_places=6)}$",
                f"Criterio de Rango: {'Rango completo $\\operatorname{rg}(A) = n$' if res.es_invertible else 'Rango deficiente $\\operatorname{rg}(A) < n$'}.",
            ],
        )
    )

    res.detalles_especificos = {
        "metodo": "cofactores",
        "detalles_desarrollo": detalles_desarrollo,
    }
    return res


# ==============================================================================
# BLOQUE 4: MÉTODO 2 - DESCOMPOSICIÓN LU / TRIANGULACIÓN CON PIVOTEO (PA = LU)
# ==============================================================================

def calcular_determinante_lu(matriz_in: Any) -> ResultadoDeterminante:
    """
    Calcula el determinante de una matriz cuadrada A de orden n x n
    mediante Descomposición LU con Pivoteo Parcial (PA = LU).
    
    Procedimiento algebraico:
    1. Valida que la matriz sea cuadrada (m = n >= 1).
    2. Inicializa L = I_n, U = A, P = I_n y contador de intercambios de fila s = 0.
    3. Para cada columna k (0 <= k < n):
       a) Pivoteo Parcial: Selecciona la fila p >= k con pivote no nulo de mayor magnitud.
       b) Si todos los candidatos a pivote son cero: det(A) = 0 (matriz singular).
       c) Si p != k: Intercambia filas k y p en U, en L (columnas previas) y suma 1 a s.
          Cada intercambio multiplica el determinante por -1.
       d) Eliminación por renglones: Para cada fila i > k, calcula el multiplicador
          m_ik = U[i][k] / U[k][k], lo almacena en L[i][k] y realiza F_i <- F_i - m_ik * F_k en U.
    4. El determinante final es:
          det(A) = (-1)^s * prod_{i=1}^n U[i][i]
    
    Complejidad Computacional: O(n^3) operaciones polinomiales.
    
    Parámetros:
        matriz_in: Matriz cuadrada numérica en R^(n x n).
        
    Retorna:
        Instancia de ResultadoDeterminante con valor exacto y registro paso a paso.
        
    Lanza:
        ValueError: Si la matriz no es cuadrada o está vacía.
    """
    matriz = validar_matriz_numerica(matriz_in)
    n = len(matriz)
    if len(matriz[0]) != n:
        raise ValueError(
            f"El cálculo del determinante exige una matriz estrictamente cuadrada. "
            f"Dimensiones recibidas: {n} filas x {len(matriz[0])} columnas."
        )

    res = ResultadoDeterminante()
    res.metodo = "lu"
    res.orden_n = n
    res.matriz_original = clonar_matriz_fracciones(matriz)
    res.analisis_eficiencia = analizar_eficiencia_determinante(matriz)
    res.complejidad_teorica = "O(n³) [Complejidad Polinomial de Eliminación Gaussiana]"
    res.operaciones_estimadas = res.analisis_eficiencia.ops_lu

    contador_pasos = 0

    # Inicializar matrices U = copia de A, L = I_n, permutaciones P
    U = clonar_matriz_fracciones(matriz)
    L = [[Fraction(1, 1) if i == j else Fraction(0, 1) for j in range(n)] for i in range(n)]
    permutaciones: List[int] = list(range(n))
    intercambios_filas: int = 0
    matriz_es_singular: bool = False

    # Paso 0: Estado Inicial
    contador_pasos += 1
    res.pasos.append(
        PasoDeterminante(
            numero=contador_pasos,
            titulo=f"Matriz Cuadrada Inicial A ({n}×{n})",
            descripcion="Se inicializa el procedimiento de Descomposición LU con pivoteo parcial ($P \\cdot A = L \\cdot U$).",
            matriz_estado=U,
            detalles=[
                f"Dimensión: ${n} \\times {n}$ elementos.",
                f"Complejidad teórica: $\\mathcal{{O}}(n^3) = \\mathcal{{O}}({n}^3)$ operaciones polinomiales.",
                f"Operaciones elementales estimadas: ~{res.operaciones_estimadas:,} flops.",
                "Fórmula fundamental: $\\det(A) = (-1)^s \\cdot \\det(L) \\cdot \\det(U) = (-1)^s \\cdot \\prod_{i=1}^n u_{ii}$.",
            ],
        )
    )

    # Proceso de Triangulación y Eliminación hacia adelante
    for k in range(n):
        # 1. Pivoteo Parcial: Buscar fila p >= k con pivote no nulo de mayor magnitud
        mejor_fila = k
        max_valor = abs(U[k][k])
        for p in range(k + 1, n):
            val_abs = abs(U[p][k])
            if val_abs > max_valor:
                max_valor = val_abs
                mejor_fila = p

        # Si el pivote máximo es cero, toda la subcolumna es cero -> Singular
        if U[mejor_fila][k] == 0:
            matriz_es_singular = True
            contador_pasos += 1
            res.pasos.append(
                PasoDeterminante(
                    numero=contador_pasos,
                    titulo=f"Columna {k + 1} sin Pivote No Nulo (Matriz Singular)",
                    descripcion=(
                        f"Todos los elementos de la columna {k + 1} desde la fila {k + 1} son cero. "
                        f"La matriz tiene rango deficiente $\\operatorname{{rg}}(A) < {n}$, por tanto $\\det(A) = 0$."
                    ),
                    matriz_estado=U,
                    detalles=[
                        f"Pivote en entrada $({k + 1}, {k + 1})$ nulo y sin fila candidata no nula.",
                        "Por el Teorema del Determinante y Rango, $|A| = 0$ idénticamente.",
                    ],
                )
            )
            break

        # 2. Intercambio de Filas si es necesario (p > k)
        if mejor_fila != k:
            intercambios_filas += 1
            # Intercambiar en U
            U[k], U[mejor_fila] = U[mejor_fila], U[k]
            # Intercambiar en L para columnas previas ya calculadas (0 a k-1)
            for col_prev in range(k):
                L[k][col_prev], L[mejor_fila][col_prev] = L[mejor_fila][col_prev], L[k][col_prev]
            # Intercambiar en vector de permutación P
            permutaciones[k], permutaciones[mejor_fila] = permutaciones[mejor_fila], permutaciones[k]

            contador_pasos += 1
            res.pasos.append(
                PasoDeterminante(
                    numero=contador_pasos,
                    titulo=f"Pivoteo Parcial: Intercambio $F_{{{k + 1}}} \\leftrightarrow F_{{{mejor_fila + 1}}}$",
                    descripcion=(
                        f"Se intercambian las filas {k + 1} y {mejor_fila + 1} para ubicar el pivote de mayor "
                        f"magnitud (${format_number(U[k][k])}$). Cada intercambio multiplica el determinante por $(-1)$. "
                        f"Total de intercambios acumulados: $s = {intercambios_filas}$."
                    ),
                    matriz_estado=U,
                    detalles=[
                        f"Operación de permutación: $F_{{{k + 1}}} \\leftrightarrow F_{{{mejor_fila + 1}}}$.",
                        f"Signo de paridad acumulado: $(-1)^{{{intercambios_filas}}} = {(-1)**intercambios_filas:+d}$.",
                    ],
                )
            )

        pivote = U[k][k]

        # 3. Eliminación por filas para anular elementos debajo del pivote
        detalles_eliminacion: List[str] = []
        hubo_eliminacion = False

        for i in range(k + 1, n):
            if U[i][k] != 0:
                hubo_eliminacion = True
                multiplicador = U[i][k] / pivote
                L[i][k] = multiplicador

                detalles_eliminacion.append(
                    f"Fila {i + 1}: Multiplicador $m_{{{i + 1},{k + 1}}} = \\frac{{{format_number(U[i][k])}}}{{{format_number(pivote)}}} = "
                    f"{format_number(multiplicador)}$. Operación: $F_{{{i + 1}}} \\leftarrow F_{{{i + 1}}} - ({format_number(multiplicador)}) \\cdot F_{{{k + 1}}}$"
                )

                # Aplicar eliminación en la fila i de U
                for j in range(k, n):
                    U[i][j] = U[i][j] - multiplicador * U[k][j]
                U[i][k] = Fraction(0, 1)  # Garantizar cero exacto

        if hubo_eliminacion:
            contador_pasos += 1
            res.pasos.append(
                PasoDeterminante(
                    numero=contador_pasos,
                    titulo=f"Eliminación Gaussiana en Columna {k + 1}",
                    descripcion=f"Se anulan los elementos bajo el pivote $u_{{{k + 1},{k + 1}}} = {format_number(pivote)}$.",
                    matriz_estado=U,
                    detalles=detalles_eliminacion,
                )
            )

    # 4. Cálculo final del determinante
    if matriz_es_singular:
        det_final = Fraction(0, 1)
        res.determinante = det_final
        res.es_invertible = False
    else:
        # Multiplicación de la diagonal de U
        elementos_diagonal: List[Fraction] = [U[i][i] for i in range(n)]
        producto_diagonal = Fraction(1, 1)
        detalles_prod_diag: List[str] = []

        for idx, diag_val in enumerate(elementos_diagonal):
            producto_diagonal *= diag_val
            detalles_prod_diag.append(f"$u_{{{idx + 1},{idx + 1}}} = {format_number(diag_val)}$")

        # Factor de signo por permutaciones de filas
        factor_signo = 1 if (intercambios_filas % 2 == 0) else -1
        det_final = Fraction(factor_signo, 1) * producto_diagonal

        res.determinante = det_final
        res.es_invertible = (det_final != 0)

        # Paso de producto de la diagonal
        contador_pasos += 1
        res.pasos.append(
            PasoDeterminante(
                numero=contador_pasos,
                titulo="Cálculo Final por Producto de la Diagonal de U",
                descripcion=(
                    f"Al ser $U$ triangular superior, $\\det(U) = \\prod_{{i=1}}^{{n}} u_{{ii}}$. "
                    f"Se multiplica por $(-1)^s$ donde $s = {intercambios_filas}$ intercambios."
                ),
                matriz_estado=U,
                detalles=[
                    f"Elementos diagonales de $U$: {', '.join(detalles_prod_diag)}.",
                    f"Producto de la diagonal: $\\det(U) = {format_number(producto_diagonal)}$.",
                    f"Intercambios de filas: $s = {intercambios_filas} \\implies (-1)^{{{intercambios_filas}}} = {factor_signo:+d}$.",
                    f"Fórmula final: $\\det(A) = ({factor_signo:+d}) \\cdot ({format_number(producto_diagonal)}) = {format_number(det_final)}$.",
                ],
            )
        )

    # Registrar conclusión
    contador_pasos += 1
    res.pasos.append(
        PasoDeterminante(
            numero=contador_pasos,
            titulo="Conclusión e Invertibilidad",
            descripcion=(
                f"Determinante obtenido: $\\det(A) = {format_number(det_final)}$. "
                f"La matriz es {'INVERTIBLE (No Singular)' if res.es_invertible else 'SINGULAR (No Invertible)'}."
            ),
            matriz_estado=U,
            detalles=[
                f"Valor exacto fraccionario: ${format_number(det_final)}$",
                f"Valor decimal aproximado: $\\approx {format_number(det_final, as_decimal=True, decimal_places=6)}$",
                f"Criterio de Rango: {'Rango completo $\\operatorname{rg}(A) = n$' if res.es_invertible else 'Rango deficiente $\\operatorname{rg}(A) < n$'}.",
            ],
        )
    )

    res.detalles_especificos = {
        "metodo": "lu",
        "matriz_L": L,
        "matriz_U": U,
        "intercambios_filas": intercambios_filas,
        "permutaciones": permutaciones,
        "es_singular": matriz_es_singular,
    }
    return res


# ==============================================================================
# BLOQUE 5: FUNCIÓN DESPACHADORA PRINCIPAL
# ==============================================================================

def calcular_determinante(
    matriz_in: Any,
    metodo: str = "lu"
) -> ResultadoDeterminante:
    """
    Función de entrada principal para el cálculo del determinante.
    Permite seleccionar entre Expansión por Cofactores ("cofactores") o Descomposición LU ("lu").
    
    Parámetros:
        matriz_in: Matriz cuadrada de orden n x n.
        metodo: "cofactores" o "lu" (por defecto "lu").
        
    Retorna:
        Instancia de ResultadoDeterminante con el análisis completo.
    """
    metodo_normalizado = str(metodo).strip().lower()
    if metodo_normalizado in ("cofactores", "laplace", "cofactor"):
        return calcular_determinante_cofactores(matriz_in)
    elif metodo_normalizado in ("lu", "triangulacion", "gauss", "eliminacion"):
        return calcular_determinante_lu(matriz_in)
    else:
        raise ValueError(
            f"Método de cálculo no reconocido: '{metodo}'. "
            f"Opciones válidas: 'cofactores' (Laplace) o 'lu' (Descomposición LU)."
        )
