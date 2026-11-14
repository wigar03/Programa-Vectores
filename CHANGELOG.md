# Historial de versiones

## 1.0.0-rc.1

Primera candidata pública de la Calculadora de Álgebra Lineal.

### Incluido

- Diez módulos de álgebra lineal y métodos numéricos con procedimientos y verificación.
- Ventana de escritorio Windows que reutiliza el motor Python y la interfaz web.
- Instalador en español por usuario y paquete portable para Windows x64.
- KaTeX, fuentes y licencias distribuidos localmente para trabajar sin conexión.
- Cierre del servidor al cerrar la ventana y diagnóstico del ejecutable empaquetado.
- Pruebas automáticas de cálculos, API, recursos y ciclo de instalación.
- README orientado al usuario y guía matemática conservada por separado.

### Requisitos y límites

- Windows 10/11 x64 y Microsoft Edge WebView2 Runtime.
- Si falta WebView2, el setup requiere conexión para instalarlo; los cálculos son locales.
- Los instaladores de esta candidata no tienen firma digital del editor.
- Todavía no hay instaladores validados para macOS/Linux ni un sitio público alojado.
- No incluye guardado de cálculos, exportación ni actualizaciones automáticas.
- Las gráficas son orientativas; los métodos iterativos pueden no converger.

Esta publicación es una **prerelease**, no la declaración de estabilidad `1.0.0`.
Los problemas se pueden comunicar en los issues del repositorio indicando módulo,
entradas, resultado esperado, resultado obtenido y versión de Windows.
