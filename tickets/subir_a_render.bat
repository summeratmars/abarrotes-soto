@echo off
cd /d %~dp0

echo --------------------------------------------
echo 🚀 SUBIENDO CAMBIOS A RENDER (GitHub + Render)
echo --------------------------------------------

git status

echo.
set /p mensaje=📝 Escribe el mensaje del commit: 
echo.
git add .
git commit -m "%mensaje%"
git push origin main

echo.
echo ✅ Cambios subidos correctamente a GitHub.
echo 🔁 Render iniciará el deploy automáticamente.
pause
