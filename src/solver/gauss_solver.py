"""
Módulo de Solución de Sistemas de Ecuaciones Lineales y Matrices
mediante los Métodos de Eliminación de Gauss y Gauss-Jordan.

Basado en el motor de cálculo exacto desarrollado para la Semana #3 (UAM - Álgebra Lineal).
100% Python estándar (listas, bucles, condicionales, fractions.Fraction).
Sin dependencias de NumPy, SciPy o librerías de álgebra lineal externas.

FUNDAMENTO MATEMÁTICO:
Dado un sistema lineal de m ecuaciones con n incógnitas:
    A · x = b, donde A en M_(m x n)(R), x en R^n, b en R^m
Se construye la matriz aumentada [A | b] de orden m x (n + 1).

Operaciones Elementales por Fila:
1. Intercambio de filas: F_i <-> F_j
2. Multiplicación de una fila por un escalar no nulo: F_i <- c · F_i  (c != 0)
3. Adición de un múltiplo de una fila a otra: F_i <- F_i + c · F_j

Teorema de Rouché-Capelli:
- rg(A) < rg(A|b): Sistema Incompatible (SI) -> Sin solución.
- rg(A) = rg(A|b) = n: Sistema Compatible Determinado (SCD) -> Solución Única.
- rg(A) = rg(A|b) = r < n: Sistema Compatible Indeterminado (SCI) -> Infinitas Soluciones
  con (n - r) grados de libertad (variables libres).
"""

from fractions import Fraction
from typing import List, Tuple, Dict, Any, Optional, Union

from src.core.arithmetic import parse_number, format_number


class Step:
    """
    Representa un paso individual dentro del procedimiento de reducción por renglones.
    """
    def __init__(
        self,
        step_number: int,
        title: str,
        description: str,
        matrix_state: List[List[Fraction]],
        operation_code: str = "",
        highlight_rows: Optional[List[int]] = None,
        highlight_pivot: Optional[Tuple[int, int]] = None,
        calculation_details: Optional[List[str]] = None,
    ):
        self.step_number = step_number
        self.title = title
        self.description = description
        # Copia profunda del estado de la matriz en este paso
        self.matrix_state = [
            [Fraction(x.numerator, x.denominator) for x in row] for row in matrix_state
        ]
        self.operation_code = operation_code
        self.highlight_rows = highlight_rows or []
        self.highlight_pivot = highlight_pivot
        self.calculation_details = calculation_details or []


class GaussResult:
    """
    Estructura que encapsula el resultado completo de la reducción matricial.
    """
    def __init__(self):
        self.initial_matrix: List[List[Fraction]] = []
        self.final_matrix: List[List[Fraction]] = []
        self.steps: List[Step] = []
        self.num_equations: int = 0
        self.num_variables: int = 0
        self.rank_A: int = 0
        self.rank_Aug: int = 0
        self.system_type: str = ""  # "SCD", "SCI", "SI"
        self.system_type_desc: str = ""
        self.solution: Dict[str, Union[Fraction, str]] = {}
        self.solution_vector: List[Union[Fraction, str]] = []
        self.backward_substitution_steps: List[str] = []
        self.verification_steps: List[str] = []


def clonar_matriz(mat: List[List[Fraction]]) -> List[List[Fraction]]:
    """Genera una copia profunda de una matriz de fracciones."""
    return [[Fraction(x.numerator, x.denominator) for x in row] for row in mat]


def solve_gaussian_elimination(
    augmented_matrix: List[List[Union[str, int, float, Fraction]]],
    variable_names: Optional[List[str]] = None,
    use_gauss_jordan: bool = True,
) -> GaussResult:
    """
    Resuelve el sistema aumentado [A | b] paso a paso mediante Gauss o Gauss-Jordan.
    """
    result = GaussResult()
    num_rows = len(augmented_matrix)
    if num_rows == 0:
        raise ValueError("La matriz aumentada no puede estar vacía.")
    num_cols = len(augmented_matrix[0])
    if num_cols < 2:
        raise ValueError("La matriz aumentada debe tener al menos una columna de variables y una columna de términos independientes.")
        
    num_vars = num_cols - 1
    result.num_equations = num_rows
    result.num_variables = num_vars
    
    if variable_names is None or len(variable_names) != num_vars:
        variable_names = [f"x_{i+1}" for i in range(num_vars)]
        
    # Convertir todas las entradas a Fraction exacto
    mat: List[List[Fraction]] = []
    for r in range(num_rows):
        row_fracs = [parse_number(augmented_matrix[r][c]) for c in range(num_cols)]
        mat.append(row_fracs)
        
    result.initial_matrix = clonar_matriz(mat)
    
    # Paso 0: Estado Inicial
    step_count = 0
    step_count += 1
    result.steps.append(
        Step(
            step_number=step_count,
            title="Matriz Aumentada Inicial [A | b]",
            description="Se plantea el sistema en su forma matricial aumentada [A | b].",
            matrix_state=mat,
            operation_code="Inicio",
        )
    )
    
    # 1. Eliminación hacia adelante (Forward Elimination)
    pivot_row = 0
    pivot_positions: List[Tuple[int, int]] = []
    
    for col in range(num_vars):
        if pivot_row >= num_rows:
            break
            
        # Buscar pivote con mayor magnitud (Pivoteo Parcial)
        best_row = pivot_row
        max_val = abs(mat[pivot_row][col])
        for r in range(pivot_row + 1, num_rows):
            if abs(mat[r][col]) > max_val:
                max_val = abs(mat[r][col])
                best_row = r
                
        # Si la columna es completamente ceros en las filas restantes, continuar a la siguiente columna
        if max_val == 0:
            continue
            
        # Intercambiar filas si es necesario (F_i <-> F_j)
        if best_row != pivot_row:
            mat[pivot_row], mat[best_row] = mat[best_row], mat[pivot_row]
            step_count += 1
            result.steps.append(
                Step(
                    step_number=step_count,
                    title=f"Pivoteo: Intercambio Fila {pivot_row + 1} ↔ Fila {best_row + 1}",
                    description=(
                        f"Se intercambia la fila {pivot_row + 1} con la fila {best_row + 1} "
                        f"para colocar el pivote de mayor magnitud ({format_number(mat[pivot_row][col])}) en la diagonal."
                    ),
                    matrix_state=mat,
                    operation_code=f"F_{pivot_row+1} <-> F_{best_row+1}",
                    highlight_rows=[pivot_row, best_row],
                )
            )
            
        current_pivot = mat[pivot_row][col]
        
        # En Gauss-Jordan, normalizar el pivote a 1
        if use_gauss_jordan and current_pivot != 1:
            inv_pivot = Fraction(1, 1) / current_pivot
            calc_details = []
            for c in range(col, num_cols):
                orig_val = mat[pivot_row][c]
                mat[pivot_row][c] *= inv_pivot
                calc_details.append(
                    f"F_{pivot_row+1}[{c+1}]: {format_number(orig_val)} · ({format_number(inv_pivot)}) = {format_number(mat[pivot_row][c])}"
                )
            step_count += 1
            result.steps.append(
                Step(
                    step_number=step_count,
                    title=f"Normalización del Pivote: Fila {pivot_row + 1} ← (1 / {format_number(current_pivot)}) · Fila {pivot_row + 1}",
                    description=f"Se divide la fila {pivot_row + 1} entre el pivote {format_number(current_pivot)} para hacerlo unitario.",
                    matrix_state=mat,
                    operation_code=f"F_{pivot_row+1} <- ({format_number(inv_pivot)}) · F_{pivot_row+1}",
                    highlight_rows=[pivot_row],
                    highlight_pivot=(pivot_row, col),
                    calculation_details=calc_details,
                )
            )
            current_pivot = mat[pivot_row][col]
            
        pivot_positions.append((pivot_row, col))
        
        # Eliminación de filas: en Gauss estándar se eliminan solo las de abajo; en Gauss-Jordan todas excepto el pivote
        target_rows = range(num_rows) if use_gauss_jordan else range(pivot_row + 1, num_rows)
        for r in target_rows:
            if r == pivot_row:
                continue
            factor = mat[r][col] if use_gauss_jordan else (mat[r][col] / current_pivot)
            if factor != 0:
                calc_details = []
                for c in range(num_cols):
                    orig_target = mat[r][c]
                    sub_val = factor * mat[pivot_row][c]
                    mat[r][c] -= sub_val
                    calc_details.append(
                        f"Col {c+1}: {format_number(orig_target)} - ({format_number(factor)})·({format_number(mat[pivot_row][c])}) = {format_number(mat[r][c])}"
                    )
                op_sign = "-" if factor > 0 else "+"
                factor_disp = format_number(abs(factor))
                step_count += 1
                result.steps.append(
                    Step(
                        step_number=step_count,
                        title=f"Eliminación: Fila {r + 1} ← Fila {r + 1} {op_sign} {factor_disp} · Fila {pivot_row + 1}",
                        description=f"Se hace cero el elemento de la fila {r + 1}, columna {col + 1} usando la fila pivote.",
                        matrix_state=mat,
                        operation_code=f"F_{r+1} <- F_{r+1} {op_sign} ({factor_disp})·F_{pivot_row+1}",
                        highlight_rows=[r, pivot_row],
                        calculation_details=calc_details,
                    )
                )
                
        pivot_row += 1
        
    result.final_matrix = clonar_matriz(mat)
    
    # 2. Análisis de Rangos (Teorema de Rouché-Capelli)
    rank_A = 0
    rank_Aug = 0
    inconsistent_row = -1
    
    for r in range(num_rows):
        is_row_A_zero = all(mat[r][c] == 0 for c in range(num_vars))
        is_row_Aug_zero = is_row_A_zero and (mat[r][num_cols - 1] == 0)
        
        if not is_row_A_zero:
            rank_A += 1
        if not is_row_Aug_zero:
            rank_Aug += 1
        else:
            if not is_row_A_zero and mat[r][num_cols - 1] != 0:
                pass
        if is_row_A_zero and mat[r][num_cols - 1] != 0:
            if inconsistent_row == -1:
                inconsistent_row = r
                
    result.rank_A = rank_A
    result.rank_Aug = rank_Aug
    
    # 3. Clasificación
    if rank_A < rank_Aug:
        # Sistema Incompatible (Sin solución)
        result.system_type = "SI"
        b_val = format_number(mat[inconsistent_row][num_cols - 1])
        result.system_type_desc = (
            f"SISTEMA INCOMPATIBLE (Sin Solución).\n"
            f"Rango(A) = {rank_A} ≠ Rango(A|B) = {rank_Aug}.\n"
            f"En la fila {inconsistent_row + 1} se tiene la contradicción: 0 = {b_val} (Imposible)."
        )
        for var in variable_names:
            result.solution[var] = "Sin solución"
        result.solution_vector = ["Sin solución"] * num_vars
        
    elif rank_A == rank_Aug and rank_A < num_vars:
        # Sistema Compatible Indeterminado (Infinitas soluciones)
        result.system_type = "SCI"
        num_free_vars = num_vars - rank_A
        result.system_type_desc = (
            f"SISTEMA COMPATIBLE INDETERMINADO (Infinitas Soluciones).\n"
            f"Rango(A) = Rango(A|B) = {rank_A} < Número de incógnitas ({num_vars}).\n"
            f"El sistema posee {num_free_vars} grado(s) de libertad (variable(s) libre(s))."
        )
        
        pivot_col_indices: Dict[int, int] = {}
        for r in range(num_rows):
            for c in range(num_vars):
                if mat[r][c] != 0:
                    pivot_col_indices[r] = c
                    break
                    
        pivots = set(pivot_col_indices.values())
        free_vars = [c for c in range(num_vars) if c not in pivots]
        
        param_names: Dict[int, str] = {}
        param_letters = ["t", "s", "r", "u", "v"]
        for idx, f_col in enumerate(free_vars):
            p_name = param_letters[idx % len(param_letters)] if idx < len(param_letters) else f"t_{idx+1}"
            param_names[f_col] = p_name
            result.solution[variable_names[f_col]] = p_name
            
        for r in reversed(range(num_rows)):
            if r in pivot_col_indices:
                p_col = pivot_col_indices[r]
                p_coeff = mat[r][p_col]
                rhs = mat[r][num_cols - 1]
                terms = []
                const_term = rhs / p_coeff
                
                for c in range(p_col + 1, num_vars):
                    coeff = mat[r][c]
                    if coeff != 0:
                        norm_coeff = -coeff / p_coeff
                        var_rep = param_names.get(c, variable_names[c])
                        if norm_coeff == 1:
                            terms.append(f"+ {var_rep}")
                        elif norm_coeff == -1:
                            terms.append(f"- {var_rep}")
                        elif norm_coeff > 0:
                            terms.append(f"+ {format_number(norm_coeff)}{var_rep}")
                        else:
                            terms.append(f"- {format_number(abs(norm_coeff))}{var_rep}")
                            
                expr_str = ""
                if const_term != 0 or not terms:
                    expr_str = format_number(const_term)
                if terms:
                    if expr_str:
                        expr_str += " " + " ".join(terms)
                    else:
                        expr_str = terms[0].lstrip("+ ") + (" " + " ".join(terms[1:]) if len(terms) > 1 else "")
                        
                result.solution[variable_names[p_col]] = expr_str or "0"
                result.backward_substitution_steps.append(
                    f"Fila {r + 1}: {variable_names[p_col]} = {expr_str}"
                )
                
        result.solution_vector = [result.solution[var] for var in variable_names]
        
    else:
        # Sistema Compatible Determinado (Solución Única)
        result.system_type = "SCD"
        result.system_type_desc = (
            f"SISTEMA COMPATIBLE DETERMINADO (Solución Única).\n"
            f"Rango(A) = Rango(A|B) = {rank_A} = Número de incógnitas ({num_vars})."
        )
        
        sol_dict: Dict[int, Fraction] = {}
        for r in range(num_vars):
            val = mat[r][num_cols - 1]
            sol_dict[r] = val
            result.solution[variable_names[r]] = val
            result.backward_substitution_steps.append(
                f"Fila {r + 1} de la matriz reducida: {variable_names[r]} = {format_number(val)}"
            )
            
        result.solution_vector = [result.solution[var] for var in variable_names]
        
        # Comprobación de la solución en el sistema original
        for r in range(result.num_equations):
            lhs_eval = Fraction(0, 1)
            eq_terms = []
            for c in range(num_vars):
                coeff = result.initial_matrix[r][c]
                var_val = sol_dict[c]
                lhs_eval += coeff * var_val
                eq_terms.append(f"({format_number(coeff)})·({format_number(var_val)})")
                
            orig_b = result.initial_matrix[r][num_cols - 1]
            check_str = " + ".join(eq_terms) + f" = {format_number(lhs_eval)}"
            is_valid = (lhs_eval == orig_b)
            status_sym = "✓ Correcto" if is_valid else "✗ Error"
            result.verification_steps.append(
                f"Ecuación {r + 1}: {check_str} (Esperado: {format_number(orig_b)}) → {status_sym}"
            )
            
    return result
