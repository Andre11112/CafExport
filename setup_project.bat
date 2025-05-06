@echo off
echo Configurando el proyecto...

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no está instalado. Por favor, instala Python 3.x
    pause
    exit /b 1
)

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo ¡Configuración completada!
echo El entorno virtual está activado y las dependencias están instaladas.
echo.
echo Para activar el entorno virtual en el futuro, ejecuta: venv\Scripts\activate.bat
echo.

pause 