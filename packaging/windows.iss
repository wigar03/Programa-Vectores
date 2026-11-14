#ifndef AppVersion
  #error AppVersion es obligatorio: use scripts/build_windows.ps1
#endif

[Setup]
AppId={{85D36068-9576-40B6-B3AC-556230ECA522}
AppName=Calculadora de Álgebra Lineal
AppVersion={#AppVersion}
AppPublisher=Equipo Calculadora de Álgebra Lineal
AppPublisherURL=https://github.com/wigar03/Calculadora-AlgebraLineal
DefaultDirName={localappdata}\Programs\CalculadoraAlgebraLineal
DefaultGroupName=Calculadora de Álgebra Lineal
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\dist
OutputBaseFilename=CalculadoraAlgebraLineal-{#AppVersion}-windows-x64-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\CalculadoraAlgebraLineal.exe
CloseApplications=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; Flags: unchecked

[Files]
Source: "..\dist\CalculadoraAlgebraLineal\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\build\MicrosoftEdgeWebview2Setup.exe"; Flags: dontcopy

[Icons]
Name: "{group}\Calculadora de Álgebra Lineal"; Filename: "{app}\CalculadoraAlgebraLineal.exe"
Name: "{autodesktop}\Calculadora de Álgebra Lineal"; Filename: "{app}\CalculadoraAlgebraLineal.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CalculadoraAlgebraLineal.exe"; Description: "Abrir la calculadora"; Flags: nowait postinstall skipifsilent

[Code]
function HasWebView2: Boolean;
var
  Version: String;
  Key: String;
begin
  Key := 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';
  Result := (RegQueryStringValue(HKLM32, Key, 'pv', Version) or
             RegQueryStringValue(HKCU, Key, 'pv', Version)) and
            (Version <> '') and (Version <> '0.0.0.0');
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ExitCode: Integer;
begin
  Result := '';
  if not HasWebView2 then begin
    ExtractTemporaryFile('MicrosoftEdgeWebview2Setup.exe');
    if not Exec(ExpandConstant('{tmp}\MicrosoftEdgeWebview2Setup.exe'),
                '/silent /install', '', SW_HIDE, ewWaitUntilTerminated, ExitCode) then
      Result := 'No se pudo iniciar la instalación de Microsoft WebView2.'
    else if not HasWebView2 then
      Result := 'Instale Microsoft Edge WebView2 Runtime y vuelva a ejecutar este setup. Su descarga requiere internet.';
  end;
end;
