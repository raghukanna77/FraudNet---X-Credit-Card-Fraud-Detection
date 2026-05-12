# FraudNet-X Deployment - Quick Start (5 Steps)

## 🚀 Deploy in 30 Minutes

```
┌─────────────────────────────────────────────────┐
│          FRAUDNET-X DEPLOYMENT FLOW             │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. GitHub Repository                          │
│         ↓                                       │
│  2. Render Backend (FastAPI)                   │
│         ↓                                       │
│  3. Vercel Frontend (React)                    │
│         ↓                                       │
│  4. Connect Both Services                      │
│         ↓                                       │
│  5. Test & Monitor                             │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## ✅ Step-by-Step

### Step 1️⃣: Push to GitHub (2 min)

```bash
# Your project root
git add .
git commit -m "Ready for deployment"
git push origin main
```

---

### Step 2️⃣: Deploy Backend to Render (10 min)

**What you're doing**: Uploading your FastAPI server to Render

1. Go to **https://render.com/dashboard**
2. Click **"New +"** → **"Web Service"**
3. Select your GitHub repository (`fraudnet-x`)
4. Fill in these settings:
   - **Name**: `fraudnet-x-backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: 
     ```
     gunicorn api.main:app --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:$PORT
     ```

5. Choose **free plan** (for testing) or **paid** (recommended)
6. Click **Deploy**
7. ⏳ Wait 3-5 minutes
8. 📌 Copy your URL: `https://fraudnet-x-backend.onrender.com` (example)

---

### Step 3️⃣: Deploy Frontend to Vercel (10 min)

**What you're doing**: Uploading your React app to Vercel

1. Go to **https://vercel.com/dashboard**
2. Click **"Add New"** → **"Project"**
3. Select your GitHub repository (`fraudnet-x`)
4. Configure:
   - **Framework**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. **Add Environment Variable**:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://fraudnet-x-backend.onrender.com` (from Step 2)

6. Click **Deploy**
7. ⏳ Wait 2-3 minutes
8. 📌 Copy your URL: `https://fraudnet-x.vercel.app` (example)

---

### Step 4️⃣: Update Backend CORS (5 min)

**What you're doing**: Allowing your frontend to talk to backend

Edit **`api/main.py`** and find the CORS middleware section. Update `allow_origins`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fraudnet-x.vercel.app",  # ← Add your Vercel URL here
        "https://fraudnet-x-backend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then push to GitHub:
```bash
git add api/main.py
git commit -m "Update CORS for production"
git push origin main
```

Render will auto-redeploy. ⏳ Wait 2 minutes.

---

### Step 5️⃣: Test Everything (3 min)

**Test Backend:**
```bash
# Open in browser or terminal
https://fraudnet-x-backend.onrender.com/health

# Should see:
# {"status":"healthy","timestamp":"...","service":"fraudnet-x-backend"}
```

**Test Frontend:**
1. Visit `https://fraudnet-x.vercel.app`
2. Open DevTools (F12 or Right-Click → Inspect)
3. Go to **Console** tab
4. Look for any errors (should be none!)
5. Try using the app (predictions, dashboard, etc)
6. Go to **Network** tab and confirm API calls reach your backend

---

## 📋 What Each File Does

| File | Purpose |
|------|---------|
| `runtime.txt` | Tells Render to use Python 3.11 |
| `.renderignore` | Files Render should skip (like node_modules) |
| `render.yaml` | Render deployment configuration |
| `requirements.txt` | Python dependencies + **gunicorn** |
| `frontend/.env.production` | Production API URL for React |
| `api/main.py` | Backend server (needs CORS update) |

---

## 🔗 Your Deployment URLs

```
Frontend: https://fraudnet-x.vercel.app
Backend:  https://fraudnet-x-backend.onrender.com
```

---

## ⚠️ Common Issues & Fixes

### Frontend Shows Blank Page?
```
→ Check DevTools Console (F12)
→ Verify VITE_API_URL in Vercel is correct
→ Trigger redeploy in Vercel dashboard
```

### API Calls Fail with CORS Error?
```
→ Edit api/main.py CORS settings
→ Add your Vercel URL to allow_origins
→ Push to GitHub and wait for auto-redeploy
```

### Backend Takes 30+ seconds to respond?
```
→ Normal on free tier (service "warms up")
→ Upgrade to paid plan to avoid cold starts
→ First request is always slow
```

### "Cannot find module" error on Vercel?
```
→ Ensure package.json exists in frontend/
→ Run: cd frontend && npm install
→ Push to GitHub
```

---

## 🎯 Deployment Checklist

```
GitHub:
☐ Repository created and pushed

Render Backend:
☐ Service deployed
☐ URL copied: https://_____.onrender.com
☐ Health check working

Vercel Frontend:
☐ Project deployed
☐ Environment variable set (VITE_API_URL)
☐ URL copied: https://_____.vercel.app

Integration:
☐ CORS updated in api/main.py
☐ Backend redeployed
☐ Frontend loads successfully
☐ API calls working
```

---

## 📚 Learn More

- **Full Guide**: Read [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/

---

## 💡 Pro Tips

✓ **Render + Vercel are free!** Generous free tiers perfect for learning/testing
✓ **Auto-deploys on git push** - no manual build steps needed
✓ **Automatic HTTPS** - both services provide free SSL certificates
✓ **Auto-scaling** - handles traffic spikes automatically
✓ **Environment variables** - keep secrets safe, not in code

---

## 🆘 Need Help?

If something goes wrong:

1. **Check the logs**:
   - Render: Dashboard → Your Service → Logs
   - Vercel: Dashboard → Your Project → Deployments

2. **Look at browser console** (F12 → Console tab)

3. **Read the full guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

4. **Common fixes**:
   - Clear browser cache (Ctrl+Shift+Delete)
   - Hard refresh (Ctrl+F5)
   - Trigger redeploy in dashboard

---

**Good luck! You've got this! 🚀**

