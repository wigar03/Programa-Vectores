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
Un vector $v \in \mathbb{R}^n$ es una $n$-tupla ordenada de escalares: $v = (v_1, v_2, \dots, v_n)$. El programa admite cualquier dimensión $n \ge 1$.
- **Suma Vectorial**: $u + v = (u_1 + v_1, u_2 + v_2, \dots, u_n + v_n)$. Requiere $\dim(u) = \dim(v) = n$.
- **Resta Vectorial**: $u - v = u + (-1)v = (u_1 - v_1, \dots, u_n - v_n)$.
- **Multiplicación por Escalar**: $c \cdot v = (c \cdot v_1, c \cdot v_2, \dots, c \cdot v_n)$, para $c \in \mathbb{R}$.
- **Producto Escalar Euclídeo (Producto Punto)**:

  $$
  \langle u, v \rangle = \sum_{i=1}^n u_i \cdot v_i
  $$

- **Norma al Cuadrado**:

  $$
  \|v\|^2 = \langle v, v \rangle = \sum_{i=1}^n v_i^2
  $$

### Módulo 2: Evaluación de Combinación Lineal
Dado un conjunto $S = \{v_1, v_2, \dots, v_k\} \subset \mathbb{R}^n$ y un vector $b \in \mathbb{R}^n$, $b$ es combinación lineal de $S$ si existen escalares $c_1, \dots, c_k$ tales que:

$$
c_1 v_1 + c_2 v_2 + \dots + c_k v_k = b
$$

Se construye la matriz aumentada $[V \mid b]$ donde la columna $j$ de $V$ es el vector $v_j$:

$$
\begin{pmatrix}
v_{11} & v_{12} & \cdots & v_{1k} & \bigm| & b_1 \\
v_{21} & v_{22} & \cdots & v_{2k} & \bigm| & b_2 \\
\vdots & \vdots & \ddots & \vdots & \bigm| & \vdots \\
v_{n1} & v_{n2} & \cdots & v_{nk} & \bigm| & b_n
\end{pmatrix}
$$

Mediante el **Teorema de Rouché-Capelli**:

1. **Sistema Compatible Determinado (SCD)**: combinación lineal única.

   $$
   \mathrm{rg}(V) = \mathrm{rg}(V \mid b) = k \implies b \in \mathrm{gen}(S)
   $$

2. **Sistema Compatible Indeterminado (SCI)**: infinitas combinaciones lineales.

   $$
   \mathrm{rg}(V) = \mathrm{rg}(V \mid b) < k \implies b \in \mathrm{gen}(S)
   $$

3. **Sistema Incompatible (SI)**: el vector $b$ no es combinación lineal.

   $$
   \mathrm{rg}(V) < \mathrm{rg}(V \mid b) \implies b \notin \mathrm{gen}(S)
   $$

### Módulo 3: Operaciones Matriciales Básicas
Para matrices $A, B \in \mathcal{M}_{m \times n}(\mathbb{R})$:

- **Adición y Sustracción** (válida si $\dim(A) = \dim(B)$):

  $$
  (A \pm B)_{ij} = a_{ij} \pm b_{ij}
  $$

- **Multiplicación por Escalar**:

  $$
  (k \cdot A)_{ij} = k \cdot a_{ij}
  $$

- **Multiplicación de Matrices**:

  $$
  C_{m \times p} = A_{m \times n} \cdot B_{n \times p}
  $$

  - Condición de existencia: $\mathrm{cols}(A) = \mathrm{filas}(B) = n$.
  - Desglose componente a componente:

    $$
    c_{ij} = \sum_{k=1}^n a_{ik} \cdot b_{kj}
    $$

### Módulo 4: Ecuaciones Matriciales $Ax = b$ y Enlace al Programa Anterior
- Planteamiento del sistema lineal en forma compacta:

  $$
  A \cdot x = b
  $$

- Construcción de la matriz aumentada $[A \mid b]$.
- **Llamada directa al programa elaborado en la Semana #3**: el motor de eliminación de renglones de Gauss y Gauss-Jordan se conecta para resolver el sistema y registrar las operaciones elementales de fila ($F_i \leftrightarrow F_j$, $F_i \leftarrow k F_i$, $F_i \leftarrow F_i + k F_j$).
- Comprobación computacional del vector residual:

  $$
  r = A \cdot x_{\mathrm{sol}} - b = 0
  $$

---

## 4. Estructura del Código

```text
Programa Vectores/
├── main.py                         # Punto de entrada principal con selector de GUI
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
│           ├── index.html
│           ├── styles.css
│           └── app.js
└── tests/                          # Suite completa de pruebas unitarias
    ├── test_vectores.py            # Tests de operaciones vectoriales
    ├── test_matrices.py            # Tests de álgebra de matrices
    ├── test_combinacion_lineal.py  # Tests de combinación lineal (SCD, SCI, SI)
    └── test_ecuaciones.py          # Tests de Ax = b y compatibilidad
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

### 3. Ejecutar las Pruebas Unitarias Automatizadas
El proyecto incluye una suite de 29 pruebas unitarias que validan la exactitud de cada algoritmo:
```bash
python -m unittest discover tests -v
```

---

## 6. Registro de Commits del Desarrollo

El desarrollo se organizó e integró cronológicamente en **10 commits** siguiendo la especificación *Conventional Commits*:

1. `chore: inicializar estructura del proyecto y configuración base`
2. `feat(core): implementar módulo aritmético exacto y validación de dimensiones`
3. `feat(vectores): implementar operaciones básicas en R^n (suma, resta y producto escalar)`
4. `feat(matrices): implementar operaciones matriciales básicas (suma, resta, escalar y producto A*B)`
5. `feat(solver): integrar motor Gauss-Jordan del programa anterior y mecanismo de llamada`
6. `feat(vectores): implementar evaluación rigurosa de combinación lineal en R^n`
7. `feat(ecuaciones): implementar resolución computacional de ecuaciones matriciales Ax = b`
8. `test: agregar suite completa de pruebas unitarias automatizadas`
9. `feat(ui): implementar interfaz gráfica moderna e interactiva para vectores y matrices`
10. `docs: actualizar README del proyecto con instrucciones de uso y teoría algebraica`
