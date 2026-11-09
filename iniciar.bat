@echo off
setlocal
title TechHelp IA - Servidor
cd /d "%~dp0"

echo ========================================================
echo               INICIANDO TECHHELP IA
echo ========================================================
echo.

set "PY_CMD=python"
python --version >nul 2>&1
if not errorlevel 1 goto RUN_APP

py --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=py"
    goto RUN_APP
)

goto NO_PYTHON

:RUN_APP
echo [*] Python detectado correctamente (%PY_CMD%).
echo [*] Instalando dependencias necesarias (Flask, etc.)...
%PY_CMD% -m pip install -r requirements.txt

if not exist ".env" (
    echo [*] Creando archivo de configuracion .env...
    copy .env.example .env >nul
)

echo.
echo ========================================================
echo   SERVIDOR INICIADO CORRECTAMENTE
echo ========================================================
echo   URL de la aplicacion:  http://localhost:5000
echo   Usuario Administrador: admin@techhelp.ia
echo   Clave Administrador:   Admin123456!
echo ========================================================
echo.
echo Abriendo navegador en http://localhost:5000 ...
echo.
echo IMPORTANTE: NO CIERRES ESTA VENTANA mientras uses la web.
echo.

start "" "http://localhost:5000"

%PY_CMD% app.py
goto END

:NO_PYTHON
echo.
echo ========================================================
echo  ERROR: Python no esta instalado en tu ordenador.
echo ========================================================
echo.
echo Windows necesita que descargues el instalador de Python:
echo.
echo 1. Abre este enlace: https://www.python.org/downloads/
echo 2. Descarga y ejecuta el boton amarillo "Download Python".
echo 3. MUY IMPORTANTE: En la primera pantalla, MARCA la casilla:
echo    [X] "Add python.exe to PATH"
echo 4. Haz clic en "Install Now".
echo 5. Al terminar, vuelve a hacer doble clic en iniciar.bat.
echo ========================================================
echo.

:END
pause
