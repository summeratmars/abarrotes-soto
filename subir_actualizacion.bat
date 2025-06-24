@echo off
echo ===========================================
echo 🔄 Subiendo cambios a GitHub...
echo ===========================================

REM Paso 1: Agregar todos los cambios
git add .

REM Paso 2: Pedir mensaje de commit
set /p MSG=📝 Escribe el mensaje del commit:

REM Paso 3: Hacer commit
git commit -m "%MSG%"

REM Paso 4: Subir a GitHub
git push origin main

echo.
echo ✅ Cambios subidos correctamente.
pause
