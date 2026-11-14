param([string]$Dist = 'dist')
$ErrorActionPreference = 'Stop'
$Dist = (Resolve-Path -LiteralPath $Dist).Path
$releaseVersion = (python -c "from src.core.version import VERSION; print(VERSION)").Trim()
if ($LASTEXITCODE -ne 0) { throw 'No se pudo leer la versión' }
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('calculadora-check-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $testRoot | Out-Null

function Run-Checked([string]$Executable, [string[]]$Arguments) {
    $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WindowStyle Hidden -PassThru
    if (-not $process.WaitForExit(60000)) {
        $process.Kill()
        throw "Tiempo agotado: $Executable"
    }
    if ($process.ExitCode -ne 0) { throw "Falló $Executable con código $($process.ExitCode)" }
}

function Test-Desktop([string]$Executable, [string]$Name) {
    $report = Join-Path $testRoot "$Name.json"
    Run-Checked $Executable @('--diagnostico', ('"' + $report + '"'))
    $result = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
    if (-not $result.ok -or $result.version -ne $releaseVersion) { throw "Diagnóstico inválido: $report" }
    Write-Output "$Name OK: $($result.interfaz.modulos) módulos, $($result.interfaz.formulas) fórmulas, sin recursos externos"
}

$portable = Join-Path $Dist 'CalculadoraAlgebraLineal\CalculadoraAlgebraLineal.exe'
Test-Desktop $portable 'portable'
$target = Join-Path $testRoot 'instalada'
$setup = Join-Path $Dist "CalculadoraAlgebraLineal-$releaseVersion-windows-x64-setup.exe"
$installArgs = @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/NOICONS', ('/DIR="' + $target + '"'))
Run-Checked $setup $installArgs
try {
    Test-Desktop (Join-Path $target 'CalculadoraAlgebraLineal.exe') 'instalada'
    Run-Checked $setup $installArgs
    Test-Desktop (Join-Path $target 'CalculadoraAlgebraLineal.exe') 'reinstalada'
} finally {
    Run-Checked (Join-Path $target 'unins000.exe') @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART')
}
if (Test-Path -LiteralPath (Join-Path $target 'CalculadoraAlgebraLineal.exe')) { throw 'Falló la desinstalación' }
Write-Output "Instalación, reinstalación y desinstalación OK. Informes: $testRoot"
