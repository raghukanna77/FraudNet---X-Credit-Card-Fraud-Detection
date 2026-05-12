# Prerequisites & GitHub Setup Guide for FraudNet-X Deployment

Complete this checklist before deploying to Render and Vercel.

---

## Table of Contents
1. [Account Setup](#account-setup)
2. [Local Environment Setup](#local-environment-setup)
3. [Project Configuration](#project-configuration)
4. [GitHub Repository Setup](#github-repository-setup)
5. [Local Testing](#local-testing)
6. [Final Verification](#final-verification)

---

## Account Setup

### ☐ 1. Create Required Accounts

#### GitHub Account
- [ ] Go to https://github.com/signup
- [ ] Create account with email
- [ ] Verify email
- [ ] Set up SSH keys (optional but recommended)
  ```bash
  # Generate SSH key
  ssh-keygen -t ed25519 -C "your-email@example.com"
  
  # Copy public key and add to GitHub
  # Settings → SSH and GPG keys → New SSH key
  ```

#### Render Account
- [ ] Go to https://render.com
- [ ] Click "Sign Up"
- [ ] Choose "Sign up with GitHub" (easier)
- [ ] Authorize GitHub access
- [ ] Verify email

#### Vercel Account
- [ ] Go to https://vercel.com/signup
- [ ] Click "Continue with GitHub"
- [ ] Authorize GitHub access
- [ ] Verify email

### ☐ 2. Connect GitHub to Deployment Platforms

#### Render GitHub Integration
1. [ ] Go to https://dashboard.render.com
2. [ ] Click your profile → Settings
3. [ ] Go to "Integrations"
4. [ ] Click "Connect GitHub"
5. [ ] Choose "All repositories" or select `fraudnet-x` repo
6. [ ] Authorize on GitHub

#### Vercel GitHub Integration
1. [ ] Go to https://vercel.com/account
2. [ ] Go to "Integrations"
3. [ ] Search for "GitHub"
4. [ ] Click "Add"
5. [ ] Choose "All repositories" or select `fraudnet-x` repo
6. [ ] Authorize on GitHub

---

## Local Environment Setup

### ☐ 3. Install Required Software

#### Git
```bash
# Windows - Check if already installed
git --version

# If not installed, download from https://git-scm.com/download/win
# Or use: choco install git
```

#### Python 3.11+
```bash
# Windows - Check version
python --version

# If Python not installed or wrong version, download from https://www.python.org/downloads/
# Or use: choco install python@3.11
```

#### Node.js & npm
```bash
# Windows - Check version
node --version
npm --version

# If not installed, download from https://nodejs.org/
# Or use: choco install nodejs
```

### ☐ 4. Set Up Python Virtual Environment

Navigate to project root:
```bash
cd d:\fraudnet-x
```

Create virtual environment:
```bash
# Windows
python -m venv venv

# Or using virtualenv
virtualenv venv
```

Activate virtual environment:
```bash
# Windows - PowerShell
.\venv\Scripts\Activate.ps1

# Windows - Command Prompt
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Verify installation:
```bash
pip list | find "fastapi"  # Windows
pip list | grep "fastapi"   # Linux/Mac
# Should show: fastapi, uvicorn, gunicorn
```

### ☐ 5. Set Up Frontend Dependencies

Navigate to frontend:
```bash
cd frontend
```

Install npm packages:
```bash
npm install
```

Verify installation:
```bash
npm list react vite
# Should show versions without errors
```

Return to root:
```bash
cd ..
```

---

## Project Configuration

### ☐ 6. Configure Environment Variables

Create `.env` file in project root:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` with your values:
```
DEBUG=False
ENVIRONMENT=production
REACT_APP_API_URL=http://localhost:8000
VITE_API_URL=http://localhost:8000
```

**Do NOT commit .env file** (it's in .gitignore)

### ☐ 7. Verify Backend Configuration

Check `api/main.py` has:

1. **CORS Middleware** (line ~173):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Health Endpoint** (line ~279):
```python
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy", ...}
```

3. **Main Entry Point** (line ~493):
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

✅ **All present? Proceed to next step.**

### ☐ 8. Verify Frontend Configuration

Check `frontend/src/services/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

✅ **Looks good? Proceed to next step.**

### ☐ 9. Verify Deployment Configuration Files

Ensure these files exist in project root:

```bash
# Windows
Get-ChildItem -Path "d:\fraudnet-x" -Include runtime.txt, render.yaml, build.sh, .renderignore, .env.example -ErrorAction SilentlyContinue

# Linux/Mac
ls -la | grep -E "runtime.txt|render.yaml|build.sh|.renderignore"
```

Should see:
- [ ] `runtime.txt` - Contains: `python-3.11`
- [ ] `render.yaml` - Render deployment config
- [ ] `build.sh` - Build script
- [ ] `.renderignore` - Files to exclude
- [ ] `.env.example` - Environment template
- [ ] `requirements.txt` - Contains `gunicorn==21.2.0`

Also verify frontend env files:
```bash
# Windows
Get-ChildItem -Path "frontend" -Include .env.development, .env.production

# Linux/Mac
ls -la frontend/.env.*
```

Should see:
- [ ] `frontend/.env.development` - Local API URL
- [ ] `frontend/.env.production` - Production API URL

---

## GitHub Repository Setup

### ☐ 10. Initialize/Verify Git Repository

Check git status:
```bash
cd d:\fraudnet-x
git status
```

If not a git repo:
```bash
git init
git config user.email "your-email@example.com"
git config user.name "Your Name"
```

### ☐ 11. Create GitHub Repository

#### Option A: Via GitHub Web Interface
1. [ ] Go to https://github.com/new
2. [ ] **Repository name**: `fraudnet-x`
3. [ ] **Description**: "Adaptive Real-Time Fraud Detection System"
4. [ ] **Public** (for Render/Vercel to access)
5. [ ] **Do NOT initialize** with README/gitignore (you already have them)
6. [ ] Click **Create repository**
7. [ ] Copy repository URL (HTTPS or SSH)

#### Option B: Via GitHub CLI
```bash
gh repo create fraudnet-x --public --source=. --remote=origin --push
```

### ☐ 12. Connect Local Repo to GitHub

Get your repository URL from GitHub:
```bash
# HTTPS (easier if you haven't set up SSH)
https://github.com/YOUR-USERNAME/fraudnet-x.git

# SSH (if you've set up SSH keys)
git@github.com:YOUR-USERNAME/fraudnet-x.git
```

Add remote:
```bash
git remote add origin https://github.com/YOUR-USERNAME/fraudnet-x.git

# Or if already exists, update it
git remote set-url origin https://github.com/YOUR-USERNAME/fraudnet-x.git
```

Verify connection:
```bash
git remote -v
# Should show:
# origin  https://github.com/YOUR-USERNAME/fraudnet-x.git (fetch)
# origin  https://github.com/YOUR-USERNAME/fraudnet-x.git (push)
```

### ☐ 13. Stage and Commit Files

Check what's staged for commit:
```bash
git status
```

Add all files:
```bash
git add .
```

**Verify no secrets are included:**
```bash
# Check if .env (with secrets) is being staged
git status | find ".env"  # Windows
git status | grep ".env"   # Linux/Mac

# Should only see: .env.example and .env.*.local
# Should NOT see: .env (without extension)
```

Commit with meaningful message:
```bash
git commit -m "Prepare for deployment to Render and Vercel

- Add deployment configuration files
- Update CORS and API configuration
- Add environment variable templates
- Configure frontend API client
- Add .renderignore and runtime.txt
- Update requirements.txt with gunicorn"
```

### ☐ 14. Push to GitHub

Set upstream branch:
```bash
git branch -M main
git push -u origin main
```

For subsequent pushes:
```bash
git push
```

Verify on GitHub:
1. [ ] Go to https://github.com/YOUR-USERNAME/fraudnet-x
2. [ ] Check files are visible
3. [ ] Check commit message in commit history

---

## Local Testing

### ☐ 15. Test Backend Locally

Start backend:
```bash
# Activate venv if not already
.\venv\Scripts\Activate.ps1

# Navigate to project root
cd d:\fraudnet-x

# Run backend
python -m uvicorn api.main:app --reload --port 8000
```

Expected output:
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

In another terminal, test health endpoint:
```bash
curl http://localhost:8000/health

# Or in PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/health" | ConvertTo-Json
```

Should see:
```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "service": "fraudnet-x-backend"
}
```

### ☐ 16. Test Frontend Locally

In a new terminal, navigate to frontend:
```bash
cd d:\fraudnet-x\frontend
```

Start dev server:
```bash
npm run dev
```

Expected output:
```
VITE v5.0.0  ready in 234 ms

➜  Local:   http://localhost:5173/
```

Open browser to http://localhost:5173:
- [ ] App loads without blank/white page
- [ ] No console errors (F12 → Console tab)
- [ ] NavBar and layout visible
- [ ] Can navigate to different pages

### ☐ 17. Test Backend → Frontend Communication

With both running (backend on 8000, frontend on 5173):

1. [ ] Open frontend in browser
2. [ ] Open DevTools (F12)
3. [ ] Go to Network tab
4. [ ] Interact with app (e.g., go to Predictions page)
5. [ ] Check that API requests appear in Network tab
6. [ ] Verify requests show:
   - [ ] URL: `http://localhost:8000/...`
   - [ ] Status: `200` (not 404 or CORS errors)
7. [ ] Verify Response tab shows expected data

---

## Final Verification

### ☐ 18. Verify All Prerequisites Complete

**Accounts:**
- [ ] GitHub account created and verified
- [ ] Render account created and verified
- [ ] Vercel account created and verified
- [ ] Render/Vercel authorized with GitHub

**Local Setup:**
- [ ] Git installed and configured
- [ ] Python 3.11+ installed
- [ ] Node.js/npm installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (pip & npm)

**Configuration:**
- [ ] `.env` file created (not committed)
- [ ] All deployment config files exist
- [ ] API configuration verified
- [ ] Frontend API client configured

**GitHub:**
- [ ] Local repo connected to GitHub
- [ ] All files committed
- [ ] `.env` NOT committed (only `.env.example`)
- [ ] Push to main branch successful
- [ ] Files visible on GitHub

**Testing:**
- [ ] Backend runs locally without errors
- [ ] Frontend runs locally without errors
- [ ] Health endpoint responds correctly
- [ ] Frontend can communicate with backend

### ☐ 19. Fix Any Issues

**If backend won't start:**
```bash
# Check for port conflicts
netstat -ano | find ":8000"  # Windows

# Try different port
python -m uvicorn api.main:app --port 8001
```

**If frontend shows blank page:**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -r node_modules package-lock.json
npm install

# Restart dev server
npm run dev
```

**If git push fails:**
```bash
# Check SSH/HTTPS connection
git remote -v

# Verify credentials
git config --list | grep user

# Try again with verbose output
git push -v
```

---

## ✅ You're Ready to Deploy!

If all checkboxes are complete, proceed to:

**→ [DEPLOYMENT_QUICKSTART.md](./DEPLOYMENT_QUICKSTART.md)**

---

## Troubleshooting Reference

| Issue | Solution |
|-------|----------|
| Python not found | Add Python to PATH or reinstall |
| npm not found | Install Node.js from nodejs.org |
| Port 8000 already in use | Change port: `--port 8001` |
| .env file errors | Copy from `.env.example` and fill values |
| Git remote error | Verify URL: `git remote -v` |
| Frontend blank page | Check console (F12), verify VITE_API_URL |
| CORS error | Check api/main.py CORS allow_origins |
| Module not found | Run `pip install -r requirements.txt` |
| npm ERR! | Try `npm cache clean --force` then `npm install` |

---

## Useful Commands Reference

```bash
# Git
git status              # Check status
git add .              # Stage all files
git commit -m "msg"    # Commit
git push               # Push to GitHub
git log                # View commit history

# Python
python --version       # Check version
pip install -r requirements.txt  # Install dependencies
pip list               # List packages
python -m venv venv    # Create virtual env
.\venv\Scripts\Activate.ps1  # Activate venv (Windows)

# Backend
python -m uvicorn api.main:app --reload  # Run backend
curl http://localhost:8000/health        # Test endpoint

# Frontend
npm install            # Install dependencies
npm run dev           # Start dev server
npm run build         # Build for production
npm run preview       # Preview production build

# General
cd d:\fraudnet-x      # Navigate to project
pwd                   # Current directory
ls -la               # List files (Linux/Mac)
dir                  # List files (Windows)
```

---

**Next Step:** Once all prerequisites are complete, head to [DEPLOYMENT_QUICKSTART.md](./DEPLOYMENT_QUICKSTART.md) for deployment!

