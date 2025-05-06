@echo off
REM Script para instalar todos los requerimientos del proyecto

python -m pip install --upgrade pip
pip install -r requirements.txt

echo Instalación de requerimientos completada.
pause 