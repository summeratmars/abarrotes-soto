@echo off
echo ===============================
echo   ⬆️ Subiendo cambios a GitHub...
echo ===============================
cd /d "%~dp0"

REM Opcional: actualizar repo
git pull origin main

set /p mensaje=📝 Escribe el mensaje del commit: 

git add .
git commit -m "%mensaje%"
git push origin main

echo.
echo ✅ Cambios subidos correctamente.
pause
