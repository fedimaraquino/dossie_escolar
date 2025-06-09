@echo off
echo ========================================
echo Sistema de Controle de Dossie Escolar
echo Script de Instalacao para Windows
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python 3.7 ou superior.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python encontrado!
python --version

echo.
echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ERRO: Falha na instalacao das dependencias!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Instalacao concluida com sucesso!
echo ========================================
echo.
echo Para executar o sistema:
echo   1. Execute: python app.py
echo   2. Abra o navegador em: http://localhost:5000
echo   3. Login padrao: admin@escola.com / admin123
echo.
echo Ou execute o arquivo: executar.bat
echo.
pause
