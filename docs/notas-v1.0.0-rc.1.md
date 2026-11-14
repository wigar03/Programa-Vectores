Primera candidata pública de la Calculadora de Álgebra Lineal.

Incluye los diez módulos actuales, ventana de escritorio, instalador en español por usuario y versión portable para Windows 10/11 x64. Los cálculos, las fórmulas y las fuentes se ejecutan localmente sin conexión.

### Descargas

- **setup.exe**: instalación recomendada, con accesos directos y desinstalación.
- **portable.zip**: extraer toda la carpeta y abrir CalculadoraAlgebraLineal.exe.
- **SHA256SUMS.txt**: sumas para verificar las descargas.

No se necesita Python ni Node.js. Se requiere Microsoft Edge WebView2 Runtime; si falta, el setup intentará instalarlo y necesitará internet durante esa descarga inicial. El portable requiere WebView2 ya instalado.

### Validación

167 pruebas de Python y 30 de JavaScript. GitHub Actions compila los archivos y comprueba el ZIP extraído, el renderizado con WebView2, un cálculo real y la instalación, reinstalación y desinstalación en Windows.

### Límites de la candidata

Esta publicación es una prerelease para recibir comentarios antes de v1.0.0. Los ejecutables no tienen firma digital del editor y Windows puede mostrar una advertencia. La instalación de WebView2 en una máquina que aún no lo tenga requiere validación adicional. No se incluyen instaladores macOS/Linux, sitio web público, guardado de cálculos, exportación ni actualización automática.

Reporta problemas indicando módulo, entradas, resultado esperado y versión de Windows. Los créditos académicos y la guía matemática se conservan en el repositorio.
