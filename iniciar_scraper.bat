@echo off
:: Muda para o diretorio onde este arquivo esta salvo
cd /d "%~dp0"

echo ==========================================
echo      Google Maps Scraper - Launcher
echo ==========================================

:: Verifica se python esta acessivel
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python em python.org e marque a opcao "Add to PATH" durante a instalacao.
    pause
    exit /b
)

:: Pergunta rapida para instalar dependencias (util para primeira vez em novo PC)
echo.
echo Para pular a instalacao de requisitos, aguarde 3 segundos ou pressione qualquer tecla...
timeout /t 3 >nul
echo.
echo Deseja verificar e instalar as dependencias (requirements.txt)? (S/N)
set /p INSTALL_DEPS="> "

if /i "%INSTALL_DEPS%"=="S" (
    echo Instalando/Verificando bibliotecas necessarias...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Falha ao instalar dependencias. Verifique sua internet ou instalacao do Python.
        pause
    )
    echo Dependencias ok!
    echo.
)

:: Inicia o script python
echo Iniciando o programa...
python scraper.py

if %errorlevel% neq 0 (
    echo.
    echo O programa fechou com um erro. Veja a mensagem acima.
)

pause
