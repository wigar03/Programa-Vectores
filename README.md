# Calculadora de Álgebra Lineal: Vectores, Matrices y Ecuaciones Matriciales

```text
================================================================================
                    UNIVERSIDAD AMERICANA (UAM)
               Facultad de Ingeniería y Arquitectura (FIA)
                    Álgebra Lineal (MTM0120)
                  Primer Corte Evaluativo (30 Puntos)
================================================================================
  Docente:     Carlos Iván Argüello
  Grupo:       Grupo 10
  Modalidad:   Grupal con defensa/exposición individual
  Proyecto:    PROGRAMA VECTORES: Operaciones Algebraicas en R^n,
               Combinación Lineal y Ecuaciones Matriciales
================================================================================
  Integrantes:
    • William Antonio García García
    • Caleb Jordan Tardencilla Alvarado
    • Rafael Hernández Sánchez
    • Andrés Sebastián González Maradiaga
================================================================================
```

---

## 1. Descripción de la Actividad y Objetivos

El presente proyecto integrador implementa un sistema computacional integral para la resolución y análisis algebraico de:
1. **Operaciones vectoriales en $\mathbb{R}^n$** de dimensión arbitraria desconocida a priori.
2. **Evaluación de combinación lineal** para determinar rigurosamente si un vector $b$ pertenece al subespacio generado por un conjunto de vectores $\{v_1, v_2, \dots, v_k\}$.
3. **Operaciones matriciales fundamentales**: adición, sustracción, producto por escalar, multiplicación de matrices $A_{m \times n} \cdot B_{n \times p}$ y transpuesta $A^T$ con análisis de simetría y propiedades.
4. **Cálculo de la inversa de una matriz $A^{-1}$**: siguiendo el procedimiento analítico formal (matriz aumentada $[A \mid I_n]$, fórmula $2 \times 2$, métodos de Gauss y Gauss-Jordan, detección de matrices singulares y doble verificación $A \cdot A^{-1} = I_n$ y $A^{-1} \cdot A = I_n$).
5. **Resolución computacional de ecuaciones matriciales** de la forma $Ax = b$ con clasificación completa según el Teorema de Rouché-Capelli e integración directa con el programa de eliminación de renglones desarrollado en la **Semana #3**.
6. **Cálculo del determinante de matrices cuadradas $|A|$ en la interfaz interactiva**: implementación 100% Python estándar (sin librerías externas) integrada en el servidor web, que permite seleccionar entre **Expansión por Cofactores (Laplace)** y **Descomposición LU ($PA = LU$)**, evaluando e indicando dinámicamente la eficiencia computacional ($O(n!)$ vs $O(n^3)$) antes de la selección.

---

## 2. Cumplimiento Estricto del Contrato Didáctico

> [!IMPORTANT]
> **Normas Técnicas y Restricciones:**
> - **Prohibición de librerías externas**: Queda estrictamente prohibido el uso de NumPy, SciPy o rutinas avanzadas de álgebra de `math`.
> - **100% Python Estándar**: Implementado utilizando únicamente listas, bucles `for` / `while`, condicionales `if` / `else` y funciones modulares.
> - **Aritmética Exacta en $\mathbb{Q}$**: Para prevenir imprecisiones por redondeo binario de coma flotante (IEEE-754) en el cálculo de rangos e independencia lineal, se utiliza la librería estándar `fractions.Fraction`.
> - **Comentarios en el Código**: Cada función cuenta con documentación teórica exhaustiva que explica el procedimiento algebraico equivalente.

---

## 3. Fundamentos Algebraicos por Módulo

### Módulo 1: Operaciones Vectoriales en $\mathbb{R}^n$

Un vector $v \in \mathbb{R}^n$ es una $n$-tupla ordenada de escalares: $v = (v_1, v_2, \dots, v_n)$. El programa admite cualquier dimensión $n \ge 1$:

- **Suma Vectorial**: $u + v = (u_1 + v_1, u_2 + v_2, \dots, u_n + v_n)$, requiriendo $\dim(u) = \dim(v) = n$.
- **Resta Vectorial**: $u - v = u + (-1)v = (u_1 - v_1, \dots, u_n - v_n)$.
- **Multiplicación por Escalar**: $c \cdot v = (c \cdot v_1, c \cdot v_2, \dots, c \cdot v_n)$, para $c \in \mathbb{R}$.
- **Producto Escalar Euclídeo (Producto Punto)**: $\langle u, v \rangle = \sum_{i=1}^n u_i \cdot v_i$.
- **Norma al Cuadrado**: $\|v\|^2 = \langle v, v \rangle = \sum_{i=1}^n v_i^2$.

### Módulo 2: Evaluación de Combinación Lineal

Dado un conjunto de vectores $S = \{v_1, v_2, \dots, v_k\} \subset \mathbb{R}^n$ y un vector objetivo $b \in \mathbb{R}^n$, $b$ es combinación lineal de $S$ si existen escalares $c_1, c_2, \dots, c_k \in \mathbb{R}$ tales que:

$$
c_1 v_1 + c_2 v_2 + \dots + c_k v_k = b
$$

Para resolverlo computacionalmente, se construye la matriz aumentada $[V \mid b]$ donde cada vector $v_j$ forma una columna de coeficientes:

$$
\left(\begin{array}{cccc|c}
v_{11} & v_{12} & \cdots & v_{1k} & b_1 \\
v_{21} & v_{22} & \cdots & v_{2k} & b_2 \\
\vdots & \vdots & \ddots & \vdots & \vdots \\
v_{n1} & v_{n2} & \cdots & v_{nk} & b_n
\end{array}\right)
$$

El sistema se resuelve y clasifica rigurosamente mediante el **Teorema de Rouché-Capelli**:

#### 1. Sistema Compatible Determinado (SCD)
Existe una **combinación lineal única** si y solo si el rango de la matriz de coeficientes coincide con el de la matriz aumentada y es igual al número de vectores:

$$
\mathrm{rg}(V) = \mathrm{rg}(V \mid b) = k \implies b \in \mathrm{gen}(S)
$$

#### 2. Sistema Compatible Indeterminado (SCI)
Existen **infinitas combinaciones lineales** si el rango coincide pero es estrictamente menor al número de vectores:

$$
\mathrm{rg}(V) = \mathrm{rg}(V \mid b) < k \implies b \in \mathrm{gen}(S)
$$

#### 3. Sistema Incompatible (SI)
El vector $b$ **no es combinación lineal** de los vectores de $S$ si el rango de la matriz aumentada es estrictamente mayor al de la matriz de coeficientes:

$$
\mathrm{rg}(V) < \mathrm{rg}(V \mid b) \implies b \notin \mathrm{gen}(S)
$$

### Módulo 3: Operaciones Matriciales Básicas

Para matrices $A, B \in \mathcal{M}_{m \times n}(\mathbb{R})$ y un escalar $k \in \mathbb{R}$:

#### Adición y Sustracción
Válida únicamente si ambas matrices tienen la misma dimensión:

$$
\dim(A) = \dim(B) = m \times n
$$

La suma y resta se calculan componente a componente:

$$
(A \pm B)_{ij} = a_{ij} \pm b_{ij}
$$

#### Multiplicación por Escalar
Para cualquier escalar real $k \in \mathbb{R}$:

$$
(k \cdot A)_{ij} = k \cdot a_{ij}
$$

#### Multiplicación de Matrices
Dadas una matriz $A$ de dimensión $m \times n$ y una matriz $B$ de dimensión $n \times p$, el producto está definido si y solo si el número de columnas de $A$ coincide con el número de filas de $B$:

$$
\mathrm{cols}(A) = \mathrm{filas}(B) = n
$$

La matriz resultante $C = A \cdot B$ tiene dimensión $m \times p$:

$$
C_{m \times p} = A_{m \times n} \cdot B_{n \times p}
$$

Donde cada entrada de la matriz resultante se obtiene mediante la suma de productos de fila por columna:

$$
c_{ij} = \sum_{k=1}^n a_{ik} \cdot b_{kj}
$$

#### Transpuesta de una Matriz $A^T$
Dada una matriz $A \in \mathcal{M}_{m \times n}(\mathbb{R})$, su transpuesta $A^T \in \mathcal{M}_{n \times m}(\mathbb{R})$ intercambia ordenadamente sus filas por columnas:

$$
(A^T)_{ji} = a_{ij}, \quad \forall \, 1 \le i \le m, \; 1 \le j \le n
$$

El programa analiza exhaustivamente sus propiedades teóricas:
- **Involución**: $(A^T)^T = A$.
- **Distributividad respecto a la suma**: $(A + B)^T = A^T + B^T$.
- **Homogeneidad con escalar**: $(k \cdot A)^T = k \cdot A^T$.
- **Propiedad multiplicativa (orden invertido)**: $(A \cdot B)^T = B^T \cdot A^T$.
- **Simetría y antisimetría**: si $A$ es cuadrada ($m = n$), se evalúa si es simétrica ($A^T = A$) o antisimétrica ($A^T = -A$).
- **Invarianza de la traza**: $\mathrm{tr}(A^T) = \mathrm{tr}(A) = \sum_{i=1}^n a_{ii}$.
- **Invertibilidad de la transpuesta (Teorema Unidad 2.2 c)**: $(A^T)^{-1} = (A^{-1})^T$.

### Módulo 4: Inversa de una Matriz $A^{-1}$

Este módulo implementa el cálculo y análisis formal de la inversa de una matriz:

#### 1. Definición Formal
Sea $A$ una matriz cuadrada de orden $n \times n$. Se dice que $A$ es **invertible** (o no singular) si existe una matriz $C$ de orden $n \times n$ tal que:

$$
C \cdot A = I_n \quad \text{y} \quad A \cdot C = I_n
$$

Donde $I_n$ es la matriz identidad de orden $n \times n$. Dicha matriz $C$ es única y se denota como $C = A^{-1}$. Una matriz que no posee inversa se denomina **matriz singular** ($\det(A) = 0$).

#### 2. Teorema de Inversión para Matrices $2 \times 2$
Sea $A = \begin{bmatrix} a & b \\ c & d \end{bmatrix}$. Si $ad - bc \neq 0$, entonces $A$ es invertible y:

$$
A^{-1} = \frac{1}{ad - bc} \begin{bmatrix} d & -b \\ -c & a \end{bmatrix}
$$

Si $ad - bc = 0$, entonces la matriz $A$ no es invertible.

#### 3. Algoritmo de Reducción por Renglones $[A \mid I_n] \sim [I_n \mid A^{-1}]$
Una matriz $A$ de $n \times n$ es invertible si y solo si es equivalente por filas a la matriz identidad $I_n$. Cualquier secuencia de operaciones elementales de renglón que transforme $A$ en $I_n$ transforma simultáneamente $I_n$ en $A^{-1}$:

$$
[A \mid I_n] \sim \dots \sim [I_n \mid A^{-1}]
$$

El programa ofrece dos métodos de cálculo:
- **Método Gauss-Jordan**: eliminación de renglones simultánea (hacia adelante y hacia atrás en cada columna pivote), normalizando cada renglón pivote $R_i \leftarrow \frac{1}{p} R_i$ y anulando todos los elementos restantes de la columna ($R_k \leftarrow R_k - c R_i$).
- **Método de Gauss**: eliminación gaussiana hacia adelante hasta obtener la matriz triangular superior $[U \mid B]$. Se comprueba que ningún pivote diagonal sea nulo ($\mathrm{rg}(A) = n$), y posteriormente se ejecuta la fase regresiva de normalización unitaria y anulación sobre la diagonal.

#### 4. Verificación Rigurosa Dual
Conforme a la exigencia didáctica del curso (*"No basta con obtener una matriz"*), el sistema comprueba automáticamente ambas identidades conmutativas en aritmética fraccionaria exacta:

$$
A \cdot A^{-1} = I_n \quad \text{y} \quad A^{-1} \cdot A = I_n
$$

Verificando además que el residuo matricial sea nulo:

$$
R = A \cdot A^{-1} - I_n = 0_{n \times n}
$$

#### 5. Propiedades Teóricas y Teorema de la Matriz Invertible
- $(A^{-1})^{-1} = A$
- $(A \cdot B)^{-1} = B^{-1} \cdot A^{-1}$
- $(A^T)^{-1} = (A^{-1})^T$
- Si $A$ es invertible, la ecuación matricial $Ax = b$ posee solución única $x = A^{-1}b$.
- Caracterizaciones equivalentes: $\mathrm{rg}(A) = n$, $n$ posiciones pivote, columnas linealmente independientes y núcleo trivial ($Ax = 0 \implies x = 0$).

### Módulo 5: Ecuaciones Matriciales $Ax = b$ y Enlace al Programa Anterior

Dada una matriz de coeficientes $A \in \mathcal{M}_{m \times n}(\mathbb{R})$ y un vector de términos independientes $b \in \mathbb{R}^m$, el sistema lineal se expresa en forma matricial compacta:

$$
A \cdot x = b
$$

El proceso de análisis y resolución comprende:

1. **Matriz Aumentada**: Se construye $[A \mid b] \in \mathcal{M}_{m \times (n+1)}(\mathbb{R})$.
2. **Llamada Directa al Motor de la Semana #3**: Se invoca directamente el módulo de eliminación por renglones desarrollado en el proyecto anterior, obteniendo la matriz escalonada y reducida junto con el registro detallado de las operaciones elementales de fila (intercambio de filas, multiplicación por escalar y adición de múltiplos de otra fila).
3. **Clasificación y Solución**: Aplicación rigurosa del Teorema de Rouché-Capelli para determinar si el sistema es Compatible Determinado (solución única), Compatible Indeterminado (infinitas soluciones con parámetros libres) o Incompatible (sin solución).
4. **Comprobación Computacional del Residuo**: En sistemas consistentes con solución $x_{\mathrm{sol}}$, el programa comprueba computacionalmente que el vector residual sea exactamente cero:

$$
r = A \cdot x_{\mathrm{sol}} - b = 0
$$

### Módulo 6: Determinante de Matrices Cuadradas $|A|$ (Cofactores vs Descomposición LU)

Este módulo implementa el cálculo exacto del determinante $|A|$ o $\det(A)$ para cualquier matriz cuadrada $A \in \mathcal{M}_{n \times n}(\mathbb{R})$ mediante una pestaña interactiva dedicada dentro del servidor web de la aplicación, desarrollada 100% en Python estándar (sin librerías prohibidas como NumPy, SciPy o rutinas de `math`):

#### 1. Definición Formal y Significado Geométrico
El determinante es un escalar único asociado a una matriz cuadrada que cuantifica el factor de dilatación o contracción del hipervolumen $n$-dimensional generado por los vectores fila o columna.
- Para $n = 1$: $\det([a]) = a$.
- Para $n = 2$: el valor absoluto $|\det(A)|$ representa el área orientada del paralelogramo en $\mathbb{R}^2$.
- Para $n = 3$: $|\det(A)|$ representa el volumen orientado del paralelepípedo en $\mathbb{R}^3$.
- Invertibilidad: $\det(A) \neq 0 \iff$ la matriz $A$ es no singular (invertible, rango completo $\mathrm{rg}(A) = n$). Si $\det(A) = 0$, la matriz es singular (filas linealmente dependientes, sin matriz inversa).

#### 2. Método de Expansión por Cofactores (Teorema de Laplace)
Para cualquier fila fija $i \in \{1, \dots, n\}$:

$$
\det(A) = \sum_{j=1}^n a_{ij} C_{ij} = \sum_{j=1}^n (-1)^{i+j} a_{ij} \det(M_{ij})
$$

Donde $C_{ij} = (-1)^{i+j} \det(M_{ij})$ es el cofactor del elemento $a_{ij}$, y $M_{ij}$ es la submatriz menor de orden $(n-1) \times (n-1)$ obtenida suprimiendo la fila $i$ y la columna $j$.

- **Estrategia Óptima**: El algoritmo inspecciona sistemáticamente filas y columnas para seleccionar aquella con mayor cantidad de ceros, anulando términos y reduciendo la recursión.
- **Complejidad Computacional**: $\mathcal{O}(n!)$ operaciones factoriales.
  - Para $n = 2$: 2 multiplicaciones ($ad - bc$).
  - Para $n = 3$: 6 multiplicaciones y sumas (regla de Sarrus).
  - Para $n = 4$: 24 evaluaciones de submatrices $3 \times 3$ ($\approx 40$ operaciones).
  - Para $n = 5$: 120 evaluaciones de submatrices ($\approx 205$ operaciones).
  - Para $n = 8$: 40,320 evaluaciones.

#### 3. Método de Descomposición LU con Pivoteo Parcial ($PA = LU$)
Mediante eliminación gaussiana por renglones con pivoteo parcial (para máxima estabilidad exacta):

$$
P \cdot A = L \cdot U
$$

Donde:
- $P$ es la matriz de permutación con $s$ intercambios de filas ($\det(P) = (-1)^s$).
- $L$ es triangular inferior unitaria con unos en la diagonal ($\det(L) = 1$) y multiplicadores $m_{ik} = \frac{u_{ik}}{u_{kk}}$ debajo de la diagonal.
- $U$ es la matriz triangular superior con los pivotes resultantes en su diagonal principal.

Aplicando las propiedades del determinante:

$$
\det(P \cdot A) = \det(L \cdot U) \implies (-1)^s \det(A) = 1 \cdot \left(\prod_{i=1}^n u_{ii}\right)
$$

$$
\det(A) = (-1)^s \prod_{i=1}^n u_{ii}
$$

Si en alguna columna no existe ningún pivote no nulo disponible, la matriz tiene rango deficiente ($\mathrm{rg}(A) < n$) y se concluye inmediatamente que $\det(A) = 0$.

- **Complejidad Computacional**: $\mathcal{O}(n^3)$ operaciones polinomiales ($\approx \frac{2}{3}n^3$ flops).
  - Para $n = 2$: $\approx 2$ operaciones.
  - Para $n = 3$: $\approx 14$ operaciones.
  - Para $n = 4$: $\approx 36$ operaciones.
  - Para $n = 5$: $\approx 75$ operaciones.
  - Para $n = 8$: $\approx 320$ operaciones.

#### 4. Análisis Comparativo de Eficiencia Previo a la Selección
Cumpliendo la especificación requerida, la aplicación evalúa e informa **antes de que el usuario elija el método** cuál es el más eficiente según la dimensión $n$ actual:
- **Para $n \le 2$**: Ambos métodos presentan un costo computacional mínimo e idéntico. Cofactores ofrece la fórmula analítica directa inmediata ($ad - bc$).
- **Para $n = 3$**: Ambos métodos son rápidos y exactos. Cofactores es didáctico (desarrollo por Sarrus / Laplace) mientras que LU presenta una leve ventaja en operaciones elementales.
- **Para $n \ge 4$**: **La Descomposición LU es drásticamente más eficiente.** La complejidad polinomial $\mathcal{O}(n^3)$ supera exponencialmente a la complejidad factorial $\mathcal{O}(n!)$. Para $n = 5$, Cofactores requiere $\approx 120$ evaluaciones frente a solo $\approx 75$ operaciones elementales en LU; para $n = 8$, Cofactores exigiría más de 40,000 llamadas recursivas frente a solo 320 operaciones en LU.

---

## 4. Estructura del Código

```text
Programa Vectores/
├── main.py                         # Punto de entrada principal con selector (--gui o web)
├── README.md                       # Documentación institucional completa
├── .gitignore                      # Exclusiones de control de versiones
├── src/
│   ├── core/                       # Núcleo aritmético y validaciones
│   │   ├── arithmetic.py           # Parser exacto de fracciones, validación y formateo
│   │   └── config.py               # Metadatos institucionales y constantes
│   ├── vectores/                   # Módulo 1 y evaluación de combinaciones lineales
│   │   ├── operaciones.py          # Suma, resta, escalar, producto punto y norma
│   │   └── combinacion_lineal.py   # Resolución de c_1*v_1 + ... + c_k*v_k = b
│   ├── matrices/                   # Módulos 3, 4 y 6: Operaciones, inversa y determinantes
│   │   ├── operaciones.py          # Suma, resta, escalar, producto A * B y transpuesta A^T
│   │   ├── inversa.py              # Inversa A^(-1) por Gauss / Gauss-Jordan y verificación dual
│   │   └── determinante.py         # Determinantes exactos (Cofactores vs LU) y análisis de eficiencia
│   ├── solver/                     # Módulo del solucionador y enlace
│   │   ├── gauss_solver.py         # Motor Gauss / Gauss-Jordan paso a paso
│   │   └── anterior_programa.py    # Invocación del programa de la Semana #3
│   ├── ecuaciones/                 # Módulo 5: Ecuaciones matriciales
│   │   └── ecuacion_matricial.py   # Resolución computacional y residuo de Ax = b
│   └── ui/                         # Interfaz web de usuario de alta estética
│       ├── web_server.py           # Servidor local estándar en Python (cero dependencias externas)
│       └── web/                    # Frontend SPA moderno (HTML5, CSS, JS reactivo, Modo Claro/Oscuro)
│           ├── index.html          # Estructura semántica accesible con iconografía Lucide
│           ├── styles.css          # Paleta visual minimalista y diseño responsivo
│           ├── app.js              # Controlador cliente reactivo y renderizado KaTeX
│           └── lucide.min.js       # Librería de iconos minimalistas (offline, open source)
└── tests/                          # Suite completa de pruebas unitarias automatizadas
    ├── test_vectores.py            # Tests de operaciones vectoriales
    ├── test_matrices.py            # Tests de álgebra de matrices
    ├── test_inversa.py             # Tests de matriz inversa y transpuesta
    ├── test_determinante.py        # Tests de determinantes (1x1 a 4x4, singularidad y eficiencia)
    ├── test_combinacion_lineal.py  # Tests de combinación lineal (SCD, SCI, SI)
    ├── test_ecuaciones.py          # Tests de Ax = b y compatibilidad
    └── test_api_latex.py           # Tests de integración API y formateo matemático
```

---

## 5. Instrucciones de Instalación y Uso

### Prerrequisitos
- Python 3.8 o superior instalado en el sistema (compatible con `python` o `py`).
- **Sin necesidad de instalar paquetes externos vía `pip`**: el programa funciona 100% con la biblioteca estándar (`fractions`, `http.server`, etc.).

### 1. Ejecutar la Aplicación Web Interactiva
Inicia la aplicación web SPA con tema claro por defecto (y selector a modo oscuro), tarjetas limpias, selectores simétricos y todos los 6 módulos integrados (Vectores, Combinación Lineal, Matrices, Inversa, Ax = b y Determinante):
```bash
python main.py
```
*Se iniciará un servidor local seguro y se abrirá automáticamente el navegador en `http://127.0.0.1:8080`.*

Opciones adicionales:
```bash
python main.py --port 9000      # Cambiar el puerto
python main.py --no-browser     # Iniciar servidor sin abrir navegador automáticamente
```

### 2. Ejecutar las Pruebas Unitarias Automatizadas
El proyecto incluye una suite completa de **60 pruebas unitarias y de integración** que validan la exactitud de cada algoritmo y la fidelidad matemática de las respuestas:
```bash
python -m unittest discover tests -v
```

---

## 6. Registro de Commits del Desarrollo

El desarrollo del proyecto se estructuró e integró cronológicamente mediante **commits semánticos** siguiendo el estándar *Conventional Commits*:

1. `46b076b` - `first commit`: Inicialización del repositorio Git.
2. `caea445` - `chore: inicializar estructura del proyecto y configuración base`: Estructuración de directorios modulares `src/`, `tests/` y archivos de configuración base.
3. `428ed00` - `feat(core): implementar módulo aritmético exacto y validación de dimensiones`: Manejo exacto en $\mathbb{Q}$ mediante `fractions.Fraction` y validación dimensional.
4. `f70d01a` - `feat(vectores): implementar operaciones básicas en R^n (suma, resta y producto escalar)`: Algoritmos de suma, resta, producto escalar euclídeo y norma al cuadrado.
5. `d92feee` - `feat(matrices): implementar operaciones matriciales básicas (suma, resta, escalar y producto A*B)`: Operaciones matriciales con verificación dimensional estricta.
6. `25ecffb` - `feat(solver): integrar motor Gauss-Jordan del programa anterior y mecanismo de llamada`: Conexión directa y resolución paso a paso basada en el algoritmo de eliminación de la Semana #3.
7. `9c06188` - `feat(vectores): implementar evaluación rigurosa de combinación lineal en R^n`: Construcción de matriz aumentada y clasificación SCD, SCI y SI con Teorema de Rouché-Capelli.
8. `d0def47` - `feat(ecuaciones): implementar resolución computacional de ecuaciones matriciales Ax = b`: Solución computacional completa y comprobación del vector residual.
9. `3ab8aa2` - `test: agregar suite completa de pruebas unitarias automatizadas`: Batería inicial de 29 pruebas unitarias automatizadas.
10. `88fb5ed` - `feat(ui): implementar interfaz gráfica moderna e interactiva para vectores y matrices`: Creación de la interfaz web SPA interactiva con servidor HTTP nativo de Python.
11. `8801309` - `docs: actualizar README del proyecto con instrucciones de uso y teoría algebraica`: Documentación formal institucional y fundamentos matemáticos.
12. `f0b4b0b` - `refactor(ui): implementar modo claro por defecto, boton limpiar, remover tkinter y enlace previo`: Rediseño UI con modo claro por defecto, botón de limpieza, selectores simétricos y eliminación de dependencias GUI heredadas.
13. `1d94f3a` - `feat(ui): agregar renderizado formal de ecuaciones en LaTeX y optimizacion responsiva para dimension 20`: Integración de KaTeX para notación matemática formal y optimización de rejillas para dimensiones hasta $n = 20$.
14. `e67e1a8` - `feat(ui): implementar formato multilineal y notacion transpuesta para evitar scroll horizontal`: Notación transpuesta $v^T$ y saltos de renglón adaptativos en visualización de vectores.
15. `fe6ff2a` - `feat(ui): fijar formato columna en vectores, transpuesta en combinacion lineal y remover menciones de LaTeX`: Presentación en columnas simétricas y limpieza de textos de interfaz.
16. `9487ebe` - `fix(math): renderizar con KaTeX explicaciones teoricas, desgloses y comprobaciones paso a paso`: Desglose formal matemático en todas las tarjetas de procedimiento y comprobación de residuales.
17. `7996e98` - `feat(ui): sustituir emojis por iconografia minimalista Lucide y refinar paleta visual`: Incorporación de iconos SVG minimalistas Lucide offline y armonización cromática.
18. `aafdbc4` - `docs: corregir compatibilidad de formulas matematicas con MathJax en GitHub`: Sustitución de macros no permitidas (`\operatorname` $\to$ `\mathrm`) para el motor de GitHub.
19. `0f83efc` - `docs(readme): separar bloques matematicos en lineas dedicadas para renderizado MathJax en GitHub`: Ajuste inicial de saltos de línea para visualización de ecuaciones.
20. `cdc1dbd` - `docs(readme): estructurar bloques matematicos de nivel superior y sincronizar historial completo de commits`: Desacoplamiento de bloques matemáticos fuera de listas para renderizado nativo en GitHub y actualización del árbol de archivos.
21. `506703e` - `docs(readme): registrar commit 20 en la relacion de cambios del desarrollo`: Sincronización del commit 20 en el registro histórico de desarrollo.
22. `ed97434` - `docs(readme): eliminar colisiones de cursiva y parentesis en formulas inline de modulos 2 y 3`: Corrección tipográfica en fórmulas inline.
23. `19c726a` - `feat(matrices): implementar calculo de matriz inversa por metodos Gauss-Jordan y Gauss`: Algoritmo formal de matriz inversa con reducción por renglones $[A \mid I_n]$, fórmula $2 \times 2$ y doble verificación $A \cdot A^{-1} = I_n$ y $A^{-1} \cdot A = I_n$.
24. `2e816d8` - `feat(matrices): enriquecer calculo y analisis de transpuesta con propiedades algebraicas`: Mapeo explícito fila a columna, simetría, antisimetría, traza y teorema $(A^T)^{-1} = (A^{-1})^T$.
25. `924dda2` - `feat(server): agregar endpoints de API para matriz inversa y transpuesta detallada`: Endpoints `/api/matrices/inversa` y `/api/matrices/operar` enriquecidos con serialización JSON exacta.
26. `c9bfd0c` - `feat(ui): integrar interfaz interactiva para matriz inversa, transpuesta y verificacion KaTeX`: Nueva pestaña SPA para cálculo de inversa $A^{-1}$, selección de métodos (Gauss / Gauss-Jordan), presets interactivos y renderizado matemático formal.
27. `f85d734` - `test: añadir suite exhaustiva de pruebas unitarias para inversa y transpuesta`: Suite de 49 pruebas unitarias herméticas incluyendo servidor de pruebas en proceso.
28. `b9e7ea7` - `docs(readme): documentar teoria de matriz inversa, transpuesta y actualizar historial`: Documentación detallada de matriz inversa, transpuesta, actualización de árbol de archivos y registro histórico de 28 commits.
29. `4f2699a` - `fix(latex): corregir formato latex en verificacion y propiedades, y suprimir referencias externas`: Delimitación estricta de expresiones matemáticas en KaTeX `$ ... $` para comprobación dual $A \cdot A^{-1} = I_n$, propiedades de transpuesta y supresión total de menciones a documentos de referencia.
30. `feat(determinantes)` - `feat(determinantes): integrar modulo web interactivo de determinantes por cofactores y LU`: Motor de determinantes 100% Python estándar en $\mathbb{Q}$ (sin librerías prohibidas), panel interactivo de evaluación previa de eficiencia ($O(n!)$ vs $O(n^3)$), nueva pestaña SPA en servidor web con renderizado KaTeX y 11 nuevas pruebas unitarias (60 tests totales).
