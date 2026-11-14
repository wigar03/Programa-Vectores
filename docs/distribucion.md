# Desarrollo y distribución

## Arquitectura

`main.py` abre la interfaz en un navegador. `desktop.py` abre la misma página en
pywebview y mantiene el servidor restringido a `127.0.0.1`, con un puerto asignado
por Windows. El servidor se cierra al salir de la ventana.
Ambas entradas comparten los cálculos, las rutas `/api/` y `src/ui/web/`.

El modo navegador continúa usando exclusivamente la biblioteca estándar de Python.
El escritorio añade pywebview, Python.NET y WebView2. Los recursos de la interfaz
están en el repositorio y no requieren CDN.

## Ejecutar escritorio desde el código

En Windows x64, con Python 3.12 y WebView2 instalado:

```powershell
python -m venv .venv-release
.\.venv-release\Scripts\Activate.ps1
python -m pip install -r requirements-windows-lock.txt
python desktop.py
```

`requirements-desktop.txt` declara la dependencia principal de escritorio;
`requirements-build.txt` añade PyInstaller. El lock de Windows fija también las
dependencias transitivas que usa el proceso de distribución.

## Compilar

Instala Inno Setup 6.3 o posterior y ejecuta desde la raíz en el entorno anterior:

```powershell
.\scripts\build_windows.ps1
# Ruta alternativa del compilador:
.\scripts\build_windows.ps1 -Iscc 'C:\Herramientas\Inno Setup 6\ISCC.exe'
```

El build descarga el bootstrapper oficial de WebView2 y comprueba su firma de
Microsoft antes de incluirlo en el setup. Esa descarga requiere conexión.
El usuario final solo lo ejecuta si no tiene WebView2 instalado.

Los resultados aparecen en `dist/`:

- `CalculadoraAlgebraLineal/`: aplicación con todas sus dependencias.
- `CalculadoraAlgebraLineal-<version>-windows-x64-setup.exe`: instalador.
- `CalculadoraAlgebraLineal-<version>-windows-x64-portable.zip`: paquete portable.
- `SHA256SUMS.txt`: sumas de los archivos descargables.

La versión proviene de `src/core/version.py`. Para producir ejecutables de otro
sistema operativo se necesita compilar y validar en ese sistema; esta candidata
solo publica Windows x64.

## Validar el paquete

```powershell
python -m unittest discover tests -v
node --test (Get-ChildItem tests/test_*.cjs).FullName
.\scripts\test_windows_package.ps1
```

El último comando es para un entorno de pruebas: instala en una carpeta temporal,
reinstala y desinstala la calculadora. Puede reemplazar el registro de instalación
de una copia existente del mismo producto. GitHub Actions lo ejecuta en un runner
Windows desechable, después de comprobar cálculos y construir los binarios.

El diagnóstico del escritorio abre un WebView2 real oculto y comprueba diez módulos,
renderizado de fórmulas, ausencia de recursos externos y un cálculo mediante la API:

```powershell
.\dist\CalculadoraAlgebraLineal\CalculadoraAlgebraLineal.exe --diagnostico "$env:TEMP\calculadora.json"
Get-Content "$env:TEMP\calculadora.json"
```

El resultado es JSON y el proceso devuelve código 0 si todo está correcto.
El diagnóstico no sustituye una revisión manual de los módulos ni una prueba en
una computadora limpia. La rama de instalación de WebView2 debe probarse también
en una máquina que todavía no tenga ese componente.

## Publicar una candidata

1. Actualiza versión y changelog en commits pequeños.
2. Ejecuta las pruebas locales y revisa la interfaz en navegador y escritorio.
3. Sube los commits y espera a que `Windows release checks` termine correctamente.
4. Descarga sus artefactos y publica el tag correspondiente como **prerelease**,
   adjuntando setup, portable y sumas. Usa exactamente los artefactos validados.
5. Prueba la candidata con usuarios antes de promover una versión estable.

El workflow construye y valida; no publica releases automáticamente.

## Datos y diagnóstico de errores

En Windows se utiliza `%LOCALAPPDATA%\CalculadoraAlgebraLineal\` para el registro
`desktop.log` y el perfil de WebView2 (incluye preferencias como el tema).
La desinstalación conserva ese perfil. No se guardan historiales de cálculos.
No hay telemetría propia; el runtime Evergreen de Microsoft se mantiene por su
propio mecanismo de actualización.

Las licencias de fuentes, KaTeX y Lucide acompañan los archivos distribuidos.
El paquete incluye la licencia de Python y los metadatos de dependencias de
escritorio. No se ha escogido una nueva licencia para el código propio.
