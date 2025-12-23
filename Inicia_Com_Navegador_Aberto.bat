@echo off
TITLE LAUNCHER DEBUG MODE (Brave/Edge/Chrome)

echo ================================================================
echo       MODO NAVEGADOR JA ABERTO (BYPASS DE ERROS)
echo ================================================================

:: ------------------------------------------------------------------
:: 1. LOCALIZAR A PASTA DO PROJETO
:: ------------------------------------------------------------------
if exist "scraper.py" (
    echo [OK] Executando da pasta correta.
) else (
    echo Arquivo scraper.py nao encontrado aqui. Procurando pasta no Desktop...
    
    set "TARGET_FOLDER=google_maps_scraper"
    set "FOUND_PATH="

    :: Opcao A: Desktop Padrao
    if exist "%USERPROFILE%\Desktop\%TARGET_FOLDER%" set "FOUND_PATH=%USERPROFILE%\Desktop\%TARGET_FOLDER%"
    
    :: Opcao B: OneDrive Desktop
    if exist "%USERPROFILE%\OneDrive\Desktop\%TARGET_FOLDER%" set "FOUND_PATH=%USERPROFILE%\OneDrive\Desktop\%TARGET_FOLDER%"
    
    :: Opcao C: OneDrive Desktop (PT-BR)
    if exist "%USERPROFILE%\OneDrive\Área de Trabalho\%TARGET_FOLDER%" set "FOUND_PATH=%USERPROFILE%\OneDrive\Área de Trabalho\%TARGET_FOLDER%"

    if defined FOUND_PATH (
        echo [OK] Pasta encontrada em: "%FOUND_PATH%"
        cd /d "%FOUND_PATH%"
    ) else (
        echo.
        echo [ERRO CRITICO] Nao encontrei a pasta 'google_maps_scraper' e nem o arquivo scraper.py!
        echo Certifique-se de que a pasta do projeto esta na Area de Trabalho.
        pause
        exit /b
    )
)

echo.
echo Este script vai:
echo 1. Fechar navegadores abertos (para evitar conflito).
echo 2. Abrir o seu navegador (Brave, Edge ou Chrome) em modo DEBUG.
echo 3. Iniciar o robo para usar esse navegador.
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

:: ------------------------------------------------------------------
:: 2. PREPARAR AMBIENTE
:: ------------------------------------------------------------------

:: Matar processos existentes (Opcional, mas recomendado para liberar porta)
taskkill /F /IM chrome.exe >nul 2>&1
taskkill /F /IM brave.exe >nul 2>&1
taskkill /F /IM msedge.exe >nul 2>&1

:: Definir pasta de perfil temporario para nao bagunicar o seu pessoal
set "USER_DIR=%TEMP%\selenium_debug_profile"
rmdir /S /Q "%USER_DIR%" >nul 2>&1
mkdir "%USER_DIR%"

echo.
echo === TENTANDO ABRIR NAVEGADOR ===

:: Tenta achar Brave
if exist "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" (
    echo [Brave] Iniciando Brave...
    start "" "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222 --user-data-dir="%USER_DIR%"
    goto LAUNCH_PYTHON
)

:: Tenta achar Edge
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo [Edge] Iniciando Edge...
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="%USER_DIR%"
    goto LAUNCH_PYTHON
)
if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    echo [Edge] Iniciando Edge...
    start "" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="%USER_DIR%"
    goto LAUNCH_PYTHON
)

:: Tenta achar Chrome
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo [Chrome] Iniciando Chrome...
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USER_DIR%"
    goto LAUNCH_PYTHON
)

echo [ERRO] Nenhum navegador encontrado nas pastas padrao!
pause
exit /b

:LAUNCH_PYTHON
echo.
echo Navegador iniciado! Aguardando 5 segundos...
timeout /t 5 >nul

echo.
echo === INICIANDO ROBO ===
echo Diretorio atual: %CD%
python scraper.py

if %errorlevel% neq 0 (
    echo.
    echo Ocorreu um erro na execucao do Python.
)

echo.
echo Fim da execucao.
pause
