#!/bin/bash
# Prerequisites Verification Script for FraudNet-X Deployment
# Run this to verify all requirements are met

echo ""
echo "========================================"
echo "FraudNet-X Prerequisites Verification"
echo "========================================"
echo ""

# Check Git
echo "Checking Git..."
if command -v git &> /dev/null; then
    echo "[OK] Git is installed"
    git --version
else
    echo "[ERROR] Git is not installed"
    echo "Please install Git: https://git-scm.com/download/linux"
    exit 1
fi
echo ""

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    echo "[OK] Python is installed"
    python3 --version
else
    echo "[ERROR] Python is not installed"
    echo "Please install Python: https://www.python.org/downloads/"
    exit 1
fi
echo ""

# Check Node.js
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    echo "[OK] Node.js is installed"
    node --version
else
    echo "[ERROR] Node.js is not installed"
    echo "Please install Node.js: https://nodejs.org/"
    exit 1
fi
echo ""

# Check npm
echo "Checking npm..."
if command -v npm &> /dev/null; then
    echo "[OK] npm is installed"
    npm --version
else
    echo "[ERROR] npm is not installed"
    echo "npm should be included with Node.js"
    exit 1
fi
echo ""

# Check virtual environment
echo "Checking Python virtual environment..."
if [ -d "venv" ]; then
    echo "[OK] Virtual environment exists"
else
    echo "[WARNING] Virtual environment not found"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "[OK] Virtual environment created and activated"
fi
echo ""

# Check requirements
echo "Checking Python requirements..."
if pip list | grep -q "fastapi"; then
    echo "[OK] FastAPI is installed"
else
    echo "[WARNING] Installing Python requirements..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "[OK] Requirements installed"
fi
echo ""

# Check frontend dependencies
echo "Checking frontend npm packages..."
if [ -d "frontend/node_modules" ]; then
    echo "[OK] Frontend dependencies installed"
else
    echo "[WARNING] Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "[OK] Frontend dependencies installed"
fi
echo ""

# Check git status
echo "Checking Git repository..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "[OK] Git repository initialized"
    echo "Current branch:"
    git rev-parse --abbrev-ref HEAD
else
    echo "[ERROR] Git repository not initialized"
    exit 1
fi
echo ""

# Check deployment files
echo "Checking deployment configuration files..."
missing=0

if [ ! -f "runtime.txt" ]; then
    echo "[ERROR] Missing: runtime.txt"
    missing=1
fi
if [ ! -f "render.yaml" ]; then
    echo "[ERROR] Missing: render.yaml"
    missing=1
fi
if [ ! -f ".renderignore" ]; then
    echo "[ERROR] Missing: .renderignore"
    missing=1
fi
if [ ! -f ".env.example" ]; then
    echo "[ERROR] Missing: .env.example"
    missing=1
fi

if [ $missing -eq 0 ]; then
    echo "[OK] All deployment files present"
else
    echo "[WARNING] Some deployment files are missing"
fi
echo ""

# Check .env file
echo "Checking environment variables..."
if [ -f ".env" ]; then
    echo "[OK] .env file exists (not shown for security)"
else
    echo "[WARNING] .env file not found"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "[OK] .env created (please edit with your values)"
fi
echo ""

echo "========================================"
echo "Verification Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: npm run dev (to test frontend)"
echo "3. In another terminal: python -m uvicorn api.main:app --reload"
echo "4. Test at: http://localhost:5173"
echo ""
echo "See PREREQUISITES_GITHUB_SETUP.md for detailed setup instructions."
echo ""
