# Script para iniciar API REST y ngrok en segundo plano sin ventanas

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Iniciar API REST en segundo plano
$apiProcess = Start-Process -FilePath "python" -ArgumentList "db_api_server.py" -WindowStyle Hidden -PassThru
Write-Host "✓ API REST iniciada (PID: $($apiProcess.Id))"

# Esperar 3 segundos
Start-Sleep -Seconds 3

# Iniciar ngrok en segundo plano
$ngrokProcess = Start-Process -FilePath "c:\Users\susu\Documents\ngrok\ngrok.exe" -ArgumentList "http 8001" -WindowStyle Hidden -PassThru
Write-Host "✓ ngrok iniciado (PID: $($ngrokProcess.Id))"

Write-Host ""
Write-Host "Servicios iniciados correctamente en segundo plano"
Write-Host "Para detenerlos, ejecuta: Stop-Process -Name python,ngrok -Force"
