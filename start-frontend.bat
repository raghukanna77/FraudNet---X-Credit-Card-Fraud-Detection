@echo off
echo ========================================
echo FraudNet-X Frontend Quick Start
echo ========================================
echo.

cd frontend

if not exist "node_modules" (
    echo [1/3] Installing dependencies...
    call npm install
) else (
    echo [1/3] Dependencies already installed
)

echo.
echo [2/3] Creating .env file...
if not exist ".env" (
    copy .env.example .env
    echo .env file created from .env.example
) else (
    echo .env file already exists
)

echo.
echo [3/3] Starting development server...
echo.
echo Frontend will be available at: http://localhost:3000
echo Make sure the API is running on: http://localhost:8000
echo.
call npm run dev
