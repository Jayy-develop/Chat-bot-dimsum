@echo off
chcp 65001 > nul
title Dimsum Mentai Oishi - WhatsApp Bot Launcher

echo.
echo ==============================================================
echo    DIMSUM MENTAI OISHI - WHATSAPP BOT LAUNCHER
echo ==============================================================
echo.

:: Cek keberadaan app.py
if not exist "app.py" (
  echo [ERROR] File app.py tidak ditemukan!
  echo Pastikan Anda menjalankan script ini dari folder project.
  pause
  exit /b
)

:: Pastikan node_modules wpp-server sudah ada
if not exist "wpp-server\node_modules" (
  echo [INFO] Menginstall paket WhatsApp Gateway...
  cd wpp-server
  call npm install
  cd ..
)

echo [1/2] Menjalankan Server Flask (port 5000)...
start "Flask Backend - Dimsum Mentai Oishi" cmd /k "python app.py"

timeout /t 2 /nobreak > nul

echo [2/2] Menjalankan WhatsApp Bot Gateway (port 3000)...
start "WhatsApp Bot Gateway - Scan QR Disini" cmd /k "cd wpp-server && node index.js"

echo.
echo ==============================================================
echo    Sistem Berhasil Dijalankan!
echo.
echo    Dashboard Admin & Scan QR:  http://127.0.0.1:5000/admin
echo    Chatbot Simulator:          http://127.0.0.1:5000/chat
echo    QR Web Viewer:              http://127.0.0.1:3000/qr
echo ==============================================================
echo.
echo    Scan QR Code di window WhatsApp Bot yang baru terbuka
echo    atau buka link Admin / QR di browser kamu!
echo.
pause
