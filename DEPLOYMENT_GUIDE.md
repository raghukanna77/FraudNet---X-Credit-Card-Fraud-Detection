# FraudNet-X Deployment Guide (Render + Vercel)

This guide provides step-by-step instructions to deploy the FraudNet-X project with:
- **Backend**: Python FastAPI → Render
- **Frontend**: React + Vite → Vercel

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Deployment (Render)](#backend-deployment-render)
3. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Create Accounts
1. **Render Account**: Visit https://render.com and create a free account
2. **Vercel Account**: Visit https://vercel.com and create a free account
3. **GitHub Account**: Both services require GitHub integration

### Prepare Your GitHub Repository
```bash
# If you haven't already, initialize git and push to GitHub
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fraudnet-x.git
git push -u origin main
```

---

## Backend Deployment (Render)

### Step 1: Prepare Backend Files

Create a `runtime.txt` file in the root directory:
```
python-3.11
```

Create a `.renderignore` file in the root directory (to exclude unnecessary files):
```
.git
.gitignore
__pycache__
*.pyc
.pytest_cache
node_modules
frontend/dist
frontend/node_modules
logs/
visualizations/
*.log
.env.local
```

Create a `build.sh` file in the root directory:
```bash
#!/bin/bash
pip install -r requirements.txt
```

Update `requirements.txt` to ensure all dependencies are production-ready. Add these if missing:
```
gunicorn==21.2.0
```

### Step 2: Update Main API for Production

Edit `api/main.py` and ensure CORS is properly configured:

```python
# At the top of your file, in the CORS configuration section:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://fraudnet-frontend.vercel.app",  # Update with your Vercel URL
        "*"  # Remove this in production for security
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Add this at the end of `api/main.py` to enable production server:
```python
if __name__ == "__main__":
    import uvicorn
    # For local testing
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 3: Create Render Configuration

Create a `render.yaml` file in the root directory:

```yaml
services:
  - type: web
    name: fraudnet-x-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn api.main:app --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: PORT
        value: 8000
```

### Step 4: Deploy to Render

1. Go to https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Select **Build and deploy from a Git repository**
4. Click **Connect GitHub**
5. Select your `fraudnet-x` repository
6. Configure the web service:
   - **Name**: `fraudnet-x-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: 
     ```
     gunicorn api.main:app --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:$PORT
     ```
   - **Plan**: Free tier (for testing) or paid for production
7. Click **Create Web Service**

### Step 5: Get Render Backend URL

Once deployed, you'll receive a URL like:
```
https://fraudnet-x-backend.onrender.com
```

**Save this URL** - you'll need it for frontend configuration.

---

## Frontend Deployment (Vercel)

### Step 1: Update API Configuration

Edit `frontend/src/services/api.ts` and update the base URL:

```typescript
// Instead of localhost, use the Render backend URL
const API_BASE_URL = process.env.VITE_API_URL || 'https://fraudnet-x-backend.onrender.com';

// Or configure via environment variables
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Step 2: Create Environment Configuration

Create `frontend/.env.production` file:
```
VITE_API_URL=https://fraudnet-x-backend.onrender.com
```

Create `frontend/.env.development` file:
```
VITE_API_URL=http://localhost:8000
```

### Step 3: Update Vite Config

Edit `frontend/vite.config.ts` to remove localhost proxy for production:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

### Step 4: Ensure Build Configuration

Verify `frontend/package.json` has correct build command:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  }
}
```

### Step 5: Deploy to Vercel

**Option A: Using Vercel Dashboard (Recommended)**

1. Go to https://vercel.com/dashboard
2. Click **Add New** → **Project**
3. Click **Import Git Repository**
4. Select your `fraudnet-x` repository
5. Configure project:
   - **Framework**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
6. Add Environment Variables:
   - Key: `VITE_API_URL`
   - Value: `https://fraudnet-x-backend.onrender.com`
7. Click **Deploy**

**Option B: Using Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Navigate to frontend directory
cd frontend

# Deploy
vercel --prod
```

### Step 6: Get Vercel Frontend URL

Once deployed, Vercel will provide a URL like:
```
https://fraudnet-x.vercel.app
```

---

## Post-Deployment Configuration

### Update Backend CORS

After getting your Vercel URL, update `api/main.py` CORS settings:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fraudnet-x.vercel.app",  # Your Vercel URL
        "https://fraudnet-x-backend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Update Render Environment Variables (Optional)

If you have any sensitive configuration:

1. Go to Render Dashboard → Your service
2. Click **Environment** tab
3. Add variables (don't hardcode secrets):
   ```
   FRONTEND_URL=https://fraudnet-x.vercel.app
   ```

### Enable Health Checks

Add a health check endpoint to `api/main.py`:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "fraudnet-x-backend"
    }
```

---

## Testing Deployment

### Test Backend (Render)

```bash
# Check if backend is running
curl https://fraudnet-x-backend.onrender.com/health

# Expected response:
# {"status":"healthy","timestamp":"2024-...","service":"fraudnet-x-backend"}
```

### Test Frontend (Vercel)

1. Visit `https://fraudnet-x.vercel.app`
2. Check browser console for any API errors
3. Verify API calls reach your Render backend

### Test API Endpoints

```bash
# Test prediction endpoint
curl -X POST https://fraudnet-x-backend.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{"transaction_data": [...]}'
```

---

## Local Testing Before Deployment

### Test Backend Locally with Production Settings

```bash
# Install production server
pip install gunicorn

# Run with gunicorn (as it will run on Render)
gunicorn api.main:app --worker-class uvicorn.workers.UvicornWorker --workers 1 --bind 0.0.0.0:8000
```

### Test Frontend with Production API

```bash
cd frontend

# Build for production
npm run build

# Preview production build
npm run preview

# Then update VITE_API_URL to point to your actual endpoints
```

---

## Troubleshooting

### Backend Issues

**Problem: "ModuleNotFoundError" on Render**
- Solution: Ensure all imports in `api/main.py` use correct paths
- Check `requirements.txt` includes all dependencies

**Problem: API returns 500 errors**
- Solution: Check Render logs: Dashboard → Service → Logs
- Verify Python version matches `runtime.txt`

**Problem: CORS errors in frontend**
- Solution: Update `allow_origins` in `api/main.py` with correct Vercel URL

### Frontend Issues

**Problem: "Cannot find module" errors during build**
- Solution: Ensure all dependencies in `package.json` are installed
- Run `npm install` locally before pushing

**Problem: API calls return 404**
- Solution: Verify `VITE_API_URL` is correctly set in `.env.production`
- Check Render backend is running (visit health check endpoint)

**Problem: Environment variables not loading**
- Solution: In Vercel dashboard, ensure variables are set and redeploy
- Prefix must be `VITE_` for Vite to make them available in frontend

### General Issues

**Slow Cold Starts on Free Tier**
- Render free tier services spin down after 15 minutes of inactivity
- First request may take 30+ seconds
- Solution: Upgrade to paid plan or use cron jobs to keep alive

**Database/Model Loading Issues**
- Preload models in startup events
- Cache results appropriately

---

## Performance Optimization

### For Render Backend
```python
# Add to api/main.py
from fastapi import FastAPI

app = FastAPI(title="FraudNet-X", description="Real-time Fraud Detection")

@app.on_event("startup")
async def startup_event():
    # Preload models here to reduce first request latency
    logger.info("Loading models...")
    # Initialize your models
    logger.info("Models loaded successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down gracefully")
```

### For Vercel Frontend
- Images are automatically optimized
- Use `npm run build` to generate minified production build
- Vercel automatically caches assets

---

## Next Steps

1. **Monitor**: Set up Render/Vercel monitoring and alerts
2. **Security**: Update `allow_origins` to be specific (not "*")
3. **CI/CD**: Both services auto-deploy on git push
4. **Scaling**: Upgrade plans as traffic increases
5. **Database**: If needed, integrate MongoDB or PostgreSQL

---

## Useful Links

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
- Vite Deployment: https://vitejs.dev/guide/static-deploy.html

---

## Support

For issues:
- Check service logs in dashboards
- Review this guide's troubleshooting section
- Consult official documentation

