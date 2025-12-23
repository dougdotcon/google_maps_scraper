@echo off
TITLE LAUNCHER DEBUG MODE (Brave/Edge/Chrome)

echo ================================================================
echo       MODO NAVEGADOR JA ABERTO (BYPASS DE ERROS)
echo ================================================================
echo.
echo Este script vai:
echo 1. Fechar navegadores abertos (para evitar conflito).
echo 2. Abrir o seu navegador (Brave, Edge ou Chrome) em modo DEBUG.
echo 3. Iniciar o robo para usar esse navegador.
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

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
python scraper.py

echo.
echo Fim da execucao.
pause
