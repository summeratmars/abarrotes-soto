@echo off
cd /d "%~dp0"

REM Crear VBS para ejecutar python sin ventana
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\run_api.vbs"
echo WshShell.Run "cmd /c cd /d ""%~dp0"" && python db_api_server.py", 0, False >> "%TEMP%\run_api.vbs"
echo Set WshShell = Nothing >> "%TEMP%\run_api.vbs"

REM Ejecutar API
cscript //nologo "%TEMP%\run_api.vbs"

REM Esperar 3 segundos
timeout /t 3 /nobreak >nul

REM Crear VBS para ejecutar ngrok sin ventana
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\run_ngrok.vbs"
echo WshShell.Run "c:\Users\susu\Documents\ngrok\ngrok.exe http 8001", 0, False >> "%TEMP%\run_ngrok.vbs"
echo Set WshShell = Nothing >> "%TEMP%\run_ngrok.vbs"

REM Ejecutar ngrok
cscript //nologo "%TEMP%\run_ngrok.vbs"

REM Limpiar archivos temporales
del "%TEMP%\run_api.vbs" >nul 2>&1
del "%TEMP%\run_ngrok.vbs" >nul 2>&1

exit
