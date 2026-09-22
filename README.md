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
3. **Operaciones matriciales fundamentales**: adición, sustracción, producto por escalar y multiplicación de matrices $A_{m \times n} \cdot B_{n \times p}$ con validación dimensional estricta.
4. **Resolución computacional de ecuaciones matriciales** de la forma $Ax = b$ con clasificación completa según el Teorema de Rouché-Capelli e integración directa con el programa de eliminación de renglones desarrollado en la **Semana #3**.

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
El vector $b$ **no es combinación lineal** ($b \notin \mathrm{gen}(S)$) si el rango de la matriz aumentada es estrictamente mayor al de la matriz de coeficientes:

$$
\mathrm{rg}(V) < \mathrm{rg}(V \mid b) \implies b \notin \mathrm{gen}(S)
$$

### Módulo 3: Operaciones Matriciales Básicas

Para matrices $A, B \in \mathcal{M}_{m \times n}(\mathbb{R})$ y un escalar $k \in \mathbb{R}$:

#### Adición y Sustracción
Válida únicamente si $\dim(A) = \dim(B)$ ($m \times n$):

$$
(A \pm B)_{ij} = a_{ij} \pm b_{ij}
$$

#### Multiplicación por Escalar
Para cualquier escalar real $k \in \mathbb{R}$:

$$
(k \cdot A)_{ij} = k \cdot a_{ij}
$$

#### Multiplicación de Matrices
Dadas $A \in \mathcal{M}_{m \times n}(\mathbb{R})$ y $B \in \mathcal{M}_{n \times p}(\mathbb{R})$, la multiplicación está definida si y solo si $\mathrm{cols}(A) = \mathrm{filas}(B) = n$:

$$
C_{m \times p} = A_{m \times n} \cdot B_{n \times p}
$$

Donde cada entrada de la matriz resultante se obtiene mediante la suma de productos de fila por columna:

$$
c_{ij} = \sum_{k=1}^n a_{ik} \cdot b_{kj}
$$

### Módulo 4: Ecuaciones Matriciales $Ax = b$ y Enlace al Programa Anterior

Dada una matriz de coeficientes $A \in \mathcal{M}_{m \times n}(\mathbb{R})$ y un vector de términos independientes $b \in \mathbb{R}^m$, el sistema lineal se expresa en forma matricial compacta:

$$
A \cdot x = b
$$

El proceso de análisis y resolución comprende:

1. **Matriz Aumentada**: Se construye $[A \mid b] \in \mathcal{M}_{m \times (n+1)}(\mathbb{R})$.
2. **Llamada Directa al Motor de la Semana #3**: Se invoca directamente el módulo de eliminación por renglones desarrollado en el proyecto anterior, obteniendo la matriz escalonada y reducida junto con el registro detallado de operaciones elementales de fila ($F_i \leftrightarrow F_j$, $F_i \leftarrow k F_i$, $F_i \leftarrow F_i + k F_j$).
3. **Clasificación y Solución**: Aplicación rigurosa del Teorema de Rouché-Capelli para determinar si el sistema es Compatible Determinado (solución única), Compatible Indeterminado (infinitas soluciones con parámetros libres) o Incompatible (sin solución).
4. **Comprobación Computacional del Residuo**: En sistemas consistentes con solución $x_{\mathrm{sol}}$, el programa comprueba computacionalmente que el vector residual sea exactamente cero:

$$
r = A \cdot x_{\mathrm{sol}} - b = 0
$$

---

## 4. Estructura del Código

```text
Programa Vectores/
├── main.py                         # Punto de entrada principal con selector y lanzador web
├── README.md                       # Documentación institucional completa
├── .gitignore                      # Exclusiones de control de versiones
├── src/
│   ├── core/                       # Núcleo aritmético y validaciones
│   │   ├── arithmetic.py           # Parser exacto de fracciones, validación y formateo
│   │   └── config.py               # Metadatos institucionales y constantes
│   ├── vectores/                   # Módulo 1 y evaluación de combinaciones lineales
│   │   ├── operaciones.py          # Suma, resta, escalar, producto punto y norma
│   │   └── combinacion_lineal.py   # Resolución de c_1*v_1 + ... + c_k*v_k = b
│   ├── matrices/                   # Módulo 2: Operaciones matriciales
│   │   └── operaciones.py          # Suma, resta, escalar y producto A * B
│   ├── solver/                     # Módulo del solucionador y enlace
│   │   ├── gauss_solver.py         # Motor Gauss / Gauss-Jordan paso a paso
│   │   └── anterior_programa.py    # Invocación del programa de la Semana #3
│   ├── ecuaciones/                 # Módulo 3: Ecuaciones matriciales
│   │   └── ecuacion_matricial.py   # Resolución computacional y residuo de Ax = b
│   └── ui/                         # Interfaz web de usuario de alta estética
│       ├── web_server.py           # Servidor local estándar en Python (cero dependencias)
│       └── web/                    # Frontend SPA moderno (HTML5, CSS, JS reactivo, Modo Claro/Oscuro)
│           ├── index.html          # Estructura semántica accesible con iconografía Lucide
│           ├── styles.css          # Paleta visual minimalista y diseño responsivo
│           ├── app.js              # Controlador cliente reactivo y renderizado KaTeX
│           └── lucide.min.js       # Librería de iconos minimalistas (offline, open source)
└── tests/                          # Suite completa de pruebas unitarias automatizadas
    ├── test_vectores.py            # Tests de operaciones vectoriales
    ├── test_matrices.py            # Tests de álgebra de matrices
    ├── test_combinacion_lineal.py  # Tests de combinación lineal (SCD, SCI, SI)
    ├── test_ecuaciones.py          # Tests de Ax = b y compatibilidad
    └── test_api_latex.py           # Tests de integración API y formateo matemático
```

---

## 5. Instrucciones de Instalación y Uso

### Prerrequisitos
- Python 3.8 o superior instalado en el sistema.
- **Sin necesidad de instalar paquetes externos vía `pip`**: el programa funciona 100% con la biblioteca estándar.

### 1. Ejecutar la Interfaz Web Interactiva
Inicia la aplicación moderna con tema claro por defecto (y selector a modo oscuro), tarjetas limpias, selectores simétricos y botones de reseteo:
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
El proyecto incluye una suite de **37 pruebas unitarias y de integración** que validan la exactitud de cada algoritmo y la fidelidad matemática de las respuestas:
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
