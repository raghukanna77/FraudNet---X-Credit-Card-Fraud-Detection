# Quick Deployment Checklist

## Pre-Deployment (5 minutes)

### Accounts & Setup
- [ ] Create Render account (https://render.com)
- [ ] Create Vercel account (https://vercel.com)
- [ ] Create GitHub account or use existing
- [ ] Push FraudNet-X code to GitHub repository

### Configuration Files (✓ Already Created)
- [ ] `runtime.txt` - Python version
- [ ] `.renderignore` - Files to exclude
- [ ] `render.yaml` - Render configuration
- [ ] `frontend/.env.development` - Local API URL
- [ ] `frontend/.env.production` - Production API URL

---

## Backend Deployment on Render (10-15 minutes)

### Step 1: Prepare Backend
```bash
# Ensure gunicorn is in requirements.txt
pip list | grep gunicorn  # Should show: gunicorn==21.2.0
```

### Step 2: Update CORS in api/main.py
- [ ] Find CORS middleware configuration
- [ ] Add your Vercel URL to `allow_origins`
- [ ] For now, you can use `"*"` temporarily (change later for security)

### Step 3: Deploy to Render
1. [ ] Go to https://dashboard.render.com
2. [ ] Click "New +" → "Web Service"
3. [ ] Connect GitHub repository
4. [ ] Fill in:
   - Name: `fraudnet-x-backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: 
     ```
     gunicorn api.main:app --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:$PORT
     ```
5. [ ] Click "Create Web Service"
6. [ ] Wait for deployment (2-5 minutes)
7. [ ] **Copy your Render URL** (e.g., https://fraudnet-x-backend.onrender.com)

### Step 4: Test Backend
```bash
# Test health check
curl https://YOUR-RENDER-URL/health

# Should return: {"status":"healthy","timestamp":"...","service":"fraudnet-x-backend"}
```

---

## Frontend Deployment on Vercel (10-15 minutes)

### Step 1: Update Frontend Configuration
- [ ] Edit `frontend/src/services/api.ts`
- [ ] Change API URL to use Render backend (not localhost)
- [ ] Or ensure it reads from `VITE_API_URL` environment variable

### Step 2: Update .env.production
```
VITE_API_URL=https://your-render-url.onrender.com
```

### Step 3: Deploy to Vercel

**Option A: Via Dashboard (Easier)**

1. [ ] Go to https://vercel.com/dashboard
2. [ ] Click "Add New" → "Project"
3. [ ] Select GitHub repository
4. [ ] Configure:
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. [ ] Add Environment Variable:
   - Name: `VITE_API_URL`
   - Value: `https://your-render-url.onrender.com`
6. [ ] Click "Deploy"
7. [ ] Wait for deployment (2-5 minutes)
8. [ ] **Copy your Vercel URL** (e.g., https://fraudnet-x.vercel.app)

**Option B: Via CLI**
```bash
npm install -g vercel
vercel login
cd frontend
vercel --prod
```

### Step 4: Test Frontend
1. [ ] Visit your Vercel URL
2. [ ] Open browser DevTools → Console
3. [ ] Check for any errors
4. [ ] Test an API call to verify it reaches Render backend

---

## Post-Deployment Updates (5 minutes)

### Update Backend CORS (Security)
- [ ] Go to Render Dashboard → Your Service → Environment tab
- [ ] Add your Vercel URL to backend CORS settings
- [ ] Redeploy backend

### Verify Both Services
- [ ] Backend health check: `curl https://your-render-url/health`
- [ ] Frontend loads without errors
- [ ] API calls work (check Network tab in DevTools)

---

## Environment Variables Reference

### Backend (Render Dashboard → Environment tab)
```
PYTHON_VERSION=3.11
```

### Frontend (Vercel Dashboard → Settings → Environment Variables)
```
VITE_API_URL=https://your-render-url.onrender.com
```

---

## Deployment URLs

After successful deployment, save these:

```
Frontend URL: https://_____________________.vercel.app
Backend URL:  https://_____________________.onrender.com
```

---

## Troubleshooting Quick Fixes

### Backend not responding
- [ ] Check Render logs (Dashboard → Service → Logs)
- [ ] Verify Python version (should be 3.11)
- [ ] Check all required packages in `requirements.txt`

### Frontend shows blank page
- [ ] Check browser console (F12)
- [ ] Verify `VITE_API_URL` is set in Vercel environment
- [ ] Trigger redeploy in Vercel

### API calls failing (CORS error)
- [ ] Verify Vercel URL is in backend's CORS `allow_origins`
- [ ] Check CORS middleware is correctly configured

### 404 on API endpoints
- [ ] Verify `VITE_API_URL` has no trailing slash
- [ ] Check endpoint paths match backend implementation
- [ ] Render backend might be spinning up (free tier cold start)

---

## Important Notes

### Free Tier Limitations
- **Render Free**: Services spin down after 15 min inactivity (cold start ~30 sec)
- **Vercel Free**: 12 deployments/month, bandwidth limits
- **Solution**: Upgrade plans for production or keep service awake with cron

### Security Best Practices
- Don't use `"*"` for CORS in production
- Use environment variables for sensitive data
- Enable HTTPS (automatic on both platforms)
- Keep secrets out of git (use `.env` files)

### Performance Tips
- Render: Use paid plan to avoid cold starts
- Frontend: Use Vercel Analytics to monitor performance
- Backend: Implement caching and rate limiting

---

## Need More Help?

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions.

