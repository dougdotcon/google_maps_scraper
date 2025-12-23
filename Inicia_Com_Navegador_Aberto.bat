@echo off
setlocal
TITLE LAUNCHER DEBUG MODE (Brave/Edge/Chrome)

echo ================================================================
echo       MODO NAVEGADOR JA ABERTO (BYPASS DE ERROS)
echo ================================================================

:: ------------------------------------------------------------------
:: 1. LOCALIZAR A PASTA DO PROJETO
:: ------------------------------------------------------------------

:: Caso 1: Ja estamos na pasta certa
if exist "scraper.py" (
    echo [OK] Arquivo encontrado no diretorio atual.
    goto :FOUND
)

echo Procurando pasta 'google_maps_scraper' no Desktop...
set "TARGET=google_maps_scraper"

:: Caso 2: Desktop Padrao
if exist "%USERPROFILE%\Desktop\%TARGET%" (
    cd /d "%USERPROFILE%\Desktop\%TARGET%"
    goto :FOUND
)

:: Caso 3: OneDrive Desktop
if exist "%USERPROFILE%\OneDrive\Desktop\%TARGET%" (
    cd /d "%USERPROFILE%\OneDrive\Desktop\%TARGET%"
    goto :FOUND
)

:: Caso 4: OneDrive Desktop (PT-BR)
if exist "%USERPROFILE%\OneDrive\Área de Trabalho\%TARGET%" (
    cd /d "%USERPROFILE%\OneDrive\Área de Trabalho\%TARGET%"
    goto :FOUND
)

:: Se nao achou nada
echo.
echo [ERRO CRITICO] Nao encontrei a pasta '%TARGET%'!
echo.
echo Onde procurei:
echo 1. Diretorio atual
echo 2. %USERPROFILE%\Desktop\%TARGET%
echo 3. OneDrive...
echo.
echo Solucao: Coloque o arquivo .bat DENTRO da pasta do projeto,
echo ou certifique-se que a pasta esta na Area de Trabalho.
pause
exit /b

:FOUND
echo [OK] Pasta de execucao definida: %CD%

echo.
echo Este script vai:
echo 1. Fechar navegadores abertos (para evitar conflito).
echo 2. Abrir o seu navegador (Brave, Edge ou Chrome) em modo DEBUG.
echo 3. Iniciar o robo para usar esse navegador.
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

:: ------------------------------------------------------------------
:: 2. PREPARAR AMBIENTE E ABRIR NAVEGADOR
:: ------------------------------------------------------------------

:: Matar processos para liberar a porta 9222
taskkill /F /IM chrome.exe >nul 2>&1
taskkill /F /IM brave.exe >nul 2>&1
taskkill /F /IM msedge.exe >nul 2>&1

:: Pasta de perfil temporario
set "USER_DIR=%TEMP%\selenium_debug_profile"
rmdir /S /Q "%USER_DIR%" >nul 2>&1
mkdir "%USER_DIR%"

echo.
echo === TENTANDO ABRIR NAVEGADOR ===

:: Prioridade 1: Brave
if exist "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" (
    echo [Brave] Iniciando Brave...
    start "" "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222 --user-data-dir="%USER_DIR%"
    goto :LAUNCH_PYTHON
)

:: Prioridade 2: Edge (x86)
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo [Edge] Iniciando Edge...
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="%USER_DIR%"
    goto :LAUNCH_PYTHON
)

:: Prioridade 3: Edge (x64)
if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    echo [Edge] Iniciando Edge...
    start "" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="%USER_DIR%"
    goto :LAUNCH_PYTHON
)

:: Prioridade 4: Chrome
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo [Chrome] Iniciando Chrome...
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USER_DIR%"
    goto :LAUNCH_PYTHON
)

echo [ERRO] Nenhum executavel de navegador encontrado!
pause
exit /b

:LAUNCH_PYTHON
echo.
echo Navegador iniciado! Aguardando 5 segundos para carregar...
timeout /t 5 >nul

echo.
echo === INICIANDO ROBO ===
echo Executando de: %CD%

python scraper.py

if %errorlevel% neq 0 (
    echo.
    echo O programa fechou com erro ou foi cancelado.
)

echo.
echo Pressione qualquer tecla para sair.
pause
