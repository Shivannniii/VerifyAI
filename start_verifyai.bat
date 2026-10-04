@echo off
title VerifyAI

echo Starting VerifyAI Backend...
start "VerifyAI Backend" "%~dp0start_backend.bat"

timeout /t 5 /nobreak >nul

echo Starting VerifyAI Frontend...
start "VerifyAI Frontend" "%~dp0start_frontend.bat"

timeout /t 5 /nobreak >nul

echo Opening VerifyAI...
start http://localhost:5173

echo.
echo VerifyAI is starting...
echo Keep the backend and frontend windows open.