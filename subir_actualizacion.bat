@echo off
cd /d %~dp0

echo ----------------------------------------
echo 🚀 Subiendo cambios a GitHub (Render)
echo ----------------------------------------

git pull origin main

echo.
set /p mensaje=📝 Escribe el mensaje del commit: 
git add .
git commit -m "%mensaje%"
git push origin main

echo.
echo ✅ Listo. Cambios subidos correctamente.
pause
