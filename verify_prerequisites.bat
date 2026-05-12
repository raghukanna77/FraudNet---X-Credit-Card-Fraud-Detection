@echo off
REM Prerequisites Verification Script for FraudNet-X Deployment
REM Run this to verify all requirements are met

echo.
echo ========================================
echo FraudNet-X Prerequisites Verification
echo ========================================
echo.

REM Check Git
echo Checking Git...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Git is installed
    git --version
) else (
    echo [ERROR] Git is not installed
    echo Please download from: https://git-scm.com/download/win
    exit /b 1
)
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python is installed
    python --version
) else (
    echo [ERROR] Python is not installed
    echo Please download from: https://www.python.org/downloads/
    exit /b 1
)
echo.

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Node.js is installed
    node --version
) else (
    echo [ERROR] Node.js is not installed
    echo Please download from: https://nodejs.org/
    exit /b 1
)
echo.

REM Check npm
echo Checking npm...
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] npm is installed
    npm --version
) else (
    echo [ERROR] npm is not installed
    echo npm should be included with Node.js
    exit /b 1
)
echo.

REM Check virtual environment
echo Checking Python virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo [OK] Virtual environment exists
) else (
    echo [WARNING] Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment created and activated
)
echo.

REM Check requirements
echo Checking Python requirements...
pip list | find "fastapi" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] FastAPI is installed
) else (
    echo [WARNING] Installing Python requirements...
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
    echo [OK] Requirements installed
)
echo.

REM Check frontend dependencies
echo Checking frontend npm packages...
if exist "frontend\node_modules" (
    echo [OK] Frontend dependencies installed
) else (
    echo [WARNING] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
    echo [OK] Frontend dependencies installed
)
echo.

REM Check git status
echo Checking Git repository...
git status >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Git repository initialized
    echo Current branch:
    git rev-parse --abbrev-ref HEAD
) else (
    echo [ERROR] Git repository not initialized
    exit /b 1
)
echo.

REM Check deployment files
echo Checking deployment configuration files...
set missing=0

if not exist "runtime.txt" (
    echo [ERROR] Missing: runtime.txt
    set missing=1
)
if not exist "render.yaml" (
    echo [ERROR] Missing: render.yaml
    set missing=1
)
if not exist ".renderignore" (
    echo [ERROR] Missing: .renderignore
    set missing=1
)
if not exist ".env.example" (
    echo [ERROR] Missing: .env.example
    set missing=1
)

if %missing% equ 0 (
    echo [OK] All deployment files present
) else (
    echo [WARNING] Some deployment files are missing
)
echo.

REM Check .env file
echo Checking environment variables...
if exist ".env" (
    echo [OK] .env file exists (not shown for security)
) else (
    echo [WARNING] .env file not found
    echo Creating .env from .env.example...
    copy .env.example .env
    echo [OK] .env created (please edit with your values)
)
echo.

echo ========================================
echo Verification Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Run: npm run dev (to test frontend)
echo 3. In another terminal: python -m uvicorn api.main:app --reload
echo 4. Test at: http://localhost:5173
echo.
echo See PREREQUISITES_GITHUB_SETUP.md for detailed setup instructions.
echo.
