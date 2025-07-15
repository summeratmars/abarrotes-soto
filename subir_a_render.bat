@echo off
title === Subiendo a GitHub para Render ===
echo ================================
echo 🚀 Subiendo cambios a GitHub...
echo ================================
echo.

REM Establecer mensaje de commit automático con fecha y hora
set FECHA=%date:~6,4%-%date:~3,2%-%date:~0,2%
set HORA=%time:~0,2%-%time:~3,2%-%time:~6,2%
set MSG=Actualizacion_%FECHA%_%HORA%

echo 🔁 Commit: %MSG%
git add .
git commit -m "%MSG%"
git push origin main

echo.
echo ✅ Cambios subidos correctamente. Recuerda hacer Manual Deploy en Render.
pause
