# Compilar desde la raíz: python -m PyInstaller packaging/calculadora.spec
from pathlib import Path
import sys
from PyInstaller.utils.hooks import copy_metadata

root = Path(SPECPATH).parent
datas = [(str(root / 'src/ui/web'), 'src/ui/web')]
datas += [(str(Path(sys.base_prefix) / 'LICENSE.txt'), 'licenses/python')]
for package in ('pywebview', 'pythonnet', 'clr_loader', 'cffi', 'bottle', 'proxy_tools', 'typing_extensions'):
    datas += copy_metadata(package)

a = Analysis(
    [str(root / 'desktop.py')], pathex=[str(root)], datas=datas,
    hiddenimports=['webview.platforms.edgechromium'],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'tkinter'],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name='CalculadoraAlgebraLineal',
    console=False, debug=False, upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,
               name='CalculadoraAlgebraLineal')
