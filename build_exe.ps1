$ErrorActionPreference = "Stop"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$dotnetDir = Join-Path $root "bundled_dotnet"
$dotnetExe = Join-Path $dotnetDir "dotnet.exe"
if (-not (Test-Path $dotnetExe)) {
    Write-Host "Downloading portable .NET 8 SDK into bundled_dotnet (one-time, ~200 MB)..."
    $installer = Join-Path $env:TEMP "dotnet-install-meow.ps1"
    Invoke-WebRequest -Uri "https://dot.net/v1/dotnet-install.ps1" -OutFile $installer -UseBasicParsing
    New-Item -ItemType Directory -Force -Path $dotnetDir | Out-Null
    & $installer -Channel 8.0 -InstallDir $dotnetDir -Architecture x64 -Quality ga
    if (-not (Test-Path $dotnetExe)) {
        throw "dotnet-install did not create $dotnetExe"
    }
    Write-Host "bundled_dotnet ready."
}

python -m pip install -r requirements.txt
python -m pip install "pyinstaller>=6.0"

$syntaxProj = Join-Path $root "csharp_syntax_check\MeowSyntaxCheck.csproj"
$syntaxOut = Join-Path $root "csharp_syntax_check\bin\Release\net8.0"
if (Test-Path $syntaxProj) {
    Write-Host "Building MeowSyntaxCheck (fast Roslyn validation)..."
    & $dotnetExe build $syntaxProj -c Release --nologo -v q
    if ($LASTEXITCODE -ne 0) { throw "csharp_syntax_check build failed" }
}

if (-not (Test-Path (Join-Path $root "assets\paw_icon.ico"))) {
    Write-Host "Generating paw_icon.ico / paw_icon.png..."
    python (Join-Path $root "tools\generate_paw_icon.py")
}

# --collect-all: темы/ассеты CTk иначе onefile exe падает без исходников рядом
# bundled_dotnet: полный portable SDK — компиляция без установки .NET на ПК
# csharp_syntax_check и bundled_dotnet — только если папки есть (иначе PyInstaller упадёт)
$dotnetBundle = Join-Path $root "bundled_dotnet"
$common = @(
    "--noconfirm", "--onefile", "--windowed",
    "--name", "C# Meow Academy",
    "--icon", "assets\paw_icon.ico",
    "--add-data", "memes;memes",
    "--add-data", "assets;assets",
    "--add-data", "csharp_validator;csharp_validator",
    "--collect-all", "customtkinter",
    "--collect-all", "CTkMessagebox"
)
if (Test-Path $dotnetBundle) {
    $common += @("--add-data", "bundled_dotnet;bundled_dotnet")
} else {
    Write-Host "Note: bundled_dotnet not found - exe will not include embedded .NET SDK."
}
if (Test-Path $syntaxOut) {
    pyinstaller @common `
        --add-data "csharp_syntax_check\bin\Release\net8.0;csharp_syntax_check/bin/Release/net8.0" `
        main.py
} else {
    Write-Host "Skipping csharp_syntax_check in bundle (build output not found)."
    pyinstaller @common main.py
}

Write-Host "Build complete. Output: dist\C# Meow Academy.exe"
