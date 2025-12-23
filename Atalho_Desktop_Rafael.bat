@echo off
:: ==============================================================
:: LAUNCHER PARA AREA DE TRABALHO (PC DO RAFAEL)
:: Copie este arquivo para o Desktop. Ele vai buscar a pasta automaticamente.
:: ==============================================================

:: Caminho fixo onde a pasta do projeto esta salva na outra maquina
set "PROJECT_DIR=C:\Users\Rafae\Desktop\google_maps_scraper"

:: Verifica se a pasta existe
if not exist "%PROJECT_DIR%" (
    echo [ERRO] A pasta do projeto nao foi encontrada!
    echo.
    echo O sistema buscou em: "%PROJECT_DIR%"
    echo.
    echo Certifique-se de que a pasta 'google_maps_scraper' existe na Area de Trabalho e contem os arquivos.
    echo Se voce mudou o nome da pasta, edite este arquivo .bat (clique direito -> Editar) e ajuste o caminho.
    pause
    exit /b
)

:: Entra na pasta do projeto
cd /d "%PROJECT_DIR%"

echo ==========================================
echo      Iniciando Scraper (Modo Desktop)
echo ==========================================
echo Diretorio de execucao: %CD%
echo.

:: Verifica se o Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Instale o Python (marque 'Add to PATH' durante a instalacao).
    pause
    exit /b
)

:: (Opcional) Instala dependencias silenciosamente na primeira vez se falhar start
:: python -c "import selenium" >nul 2>&1
:: if %errorlevel% neq 0 (
::    echo Instalando dependencias iniciais...
::    pip install -r requirements.txt
:: )

:: Executa o script principal
python scraper.py

if %errorlevel% neq 0 (
    echo.
    echo Ocorreu um erro ao rodar o script.
)

pause
