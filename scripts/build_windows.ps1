param([string]$Iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe")
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path -LiteralPath $Iscc)) { throw "No se encontró Inno Setup: $Iscc" }
$releaseVersion = (python -c "from src.core.version import VERSION; print(VERSION)").Trim()
if ($LASTEXITCODE -ne 0) { throw 'No se pudo leer la versión' }
python -m PyInstaller --noconfirm --clean packaging/calculadora.spec
if ($LASTEXITCODE -ne 0) { throw 'Falló PyInstaller' }
$bootstrapper = Join-Path (Get-Location) 'build\MicrosoftEdgeWebview2Setup.exe'
Invoke-WebRequest 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile $bootstrapper
$signature = Get-AuthenticodeSignature -LiteralPath $bootstrapper
if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'O=Microsoft Corporation') {
    throw 'El instalador de WebView2 no tiene una firma válida de Microsoft'
}
& $Iscc "/DAppVersion=$releaseVersion" packaging/windows.iss
if ($LASTEXITCODE -ne 0) { throw 'Falló Inno Setup' }
Compress-Archive -Path dist/CalculadoraAlgebraLineal -DestinationPath "dist/CalculadoraAlgebraLineal-$releaseVersion-windows-x64-portable.zip" -Force
$artifacts = Get-ChildItem dist -File | Where-Object { $_.Extension -in '.exe', '.zip' }
$sums = $artifacts | ForEach-Object { (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower() + '  ' + $_.Name }
[IO.File]::WriteAllLines((Join-Path (Get-Location) 'dist\SHA256SUMS.txt'), [string[]]$sums)
