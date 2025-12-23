@echo off
TITLE Google Maps Scraper Launcher
:: ==============================================================
:: LAUNCHER UNIVERSAL (FUNCIONA EM QUALQUER USUARIO)
:: ==============================================================

echo Iniciando diagnostic...
echo Usuario atual: %USERNAME%
echo.

:: 1. Tenta descobrir o caminho do Desktop automaticamente
set "TARGET_FOLDER=google_maps_scraper"

:: Opcao A: Desktop Padrao
set "PATH_A=%USERPROFILE%\Desktop\%TARGET_FOLDER%"

:: Opcao B: Desktop OneDrive (Comum no Windows 11)
set "PATH_B=%USERPROFILE%\OneDrive\Desktop\%TARGET_FOLDER%"

:: Opcao C: Desktop OneDrive (Pt-Br)
set "PATH_C=%USERPROFILE%\OneDrive\Área de Trabalho\%TARGET_FOLDER%"

:: Tenta localizar
if exist "%PATH_A%" (
    set "FINAL_PATH=%PATH_A%"
    echo [OK] Pasta encontrada no Desktop padrao.
) else if exist "%PATH_B%" (
    set "FINAL_PATH=%PATH_B%"
    echo [OK] Pasta encontrada no OneDrive Desktop.
) else if exist "%PATH_C%" (
    set "FINAL_PATH=%PATH_C%"
    echo [OK] Pasta encontrada no OneDrive Desktop (PT-BR).
) else (
    echo [ERRO CRITICO] Nao consegui encontrar a pasta '%TARGET_FOLDER%'.
    echo.
    echo Procuramos em:
    echo 1. %PATH_A%
    echo 2. %PATH_B%
    echo 3. %PATH_C%
    echo.
    echo Por favor, certifique-se de que a pasta se chama EXATAMENTE 'google_maps_scraper'
    echo e esta na Area de Trabalho.
    echo.
    pause
    exit /b
)

:: 2. Entra na pasta
cd /d "%FINAL_PATH%"

:: 3. Verifica Python
echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 'python' comando nao encontrado. Tentando 'py'...
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERRO] Python nao instalado ou nao esta no PATH.
        echo Baixe em python.org
        pause
        exit /b
    ) else (
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)

:: 4. Executa
echo.
echo === Executando Scraper em: %FINAL_PATH% ===
echo.

%PYTHON_CMD% scraper.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] O programa fechou com erro.
)

echo.
echo Pressione qualquer tecla para sair...
pause
