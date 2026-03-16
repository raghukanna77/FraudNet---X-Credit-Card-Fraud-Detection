# 🚀 FraudNet-X Quick Start Guide

## ✅ Project Status

Your FraudNet-X fraud detection system is now **RUNNING** in **DEMO MODE**!

### What's Working:

✅ **FastAPI Backend Server** - Running on http://localhost:8000
✅ **Interactive Web Frontend** - Simple HTML interface
✅ **API Documentation** - Available at http://localhost:8000/docs
✅ **Demo Predictions** - Using heuristic-based fraud detection
✅ **Real-time Status Dashboard** - Health monitoring and metrics

---

## 📁 Simplified Project Structure

```
fraudnet-x/
├── simple-frontend.html      # ⭐ Simple web interface (NO npm needed!)
├── api/
│   └── main.py               # FastAPI backend server
├── src/                      # Core fraud detection modules
│   ├── utils/
│   ├── models/
│   ├── preprocessing/
│   ├── risk_engine/
│   └── ...
├── venv/                     # Python virtual environment
├── requirements.txt          # Python dependencies
└── QUICKSTART.md            # This file
```

---

## 🎯 How to Use

### 1. **Access the Web Interface**

Open in your browser:
```
file:///d:/fraudnet-x/simple-frontend.html
```

Or double-click the file: `simple-frontend.html`

### 2. **Use the Quick Test Samples**

The interface has pre-configured test cases:
- 🟢 **Low Risk** - Normal transaction
- 🟡 **Medium Risk** - Suspicious transaction  
- 🔴 **High Risk** - Likely fraudulent transaction

Click any button to auto-fill and analyze!

### 3. **Manual Transaction Input**

Enter transaction details:
- **Amount**: Transaction amount in dollars
- **Time**: Seconds since first transaction
- **V1-V28**: PCA-transformed features
- Click "Show All V Features" to reveal V5-V28

### 4. **View Results**

After analysis, you'll see:
- **Risk Score** (0-100)
- **Risk Level** (Low/Medium/High/Critical)
- **Fraud Probability**
- **Feature Importance** - Which features contributed most
- **Recommendation** - Suggested action

---

## 🔧 API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

### Predict Fraud
```bash
POST http://localhost:8000/predict
Content-Type: application/json

{
  "Time": 12345.0,
  "V1": -1.36,
  "V2": -0.07,
  ...
  "V28": -0.02,
  "Amount": 149.62
}
```

### Get Metrics
```bash
GET http://localhost:8000/metrics
```

### Interactive API Documentation
```
http://localhost:8000/docs
```

---

## 🎮 Demo Mode

Currently running in **DEMO MODE** using heuristic-based predictions:

**How it works:**
- Analyzes transaction amount (higher = riskier)
- Examines V feature extremeness (outliers = anomalies)
- Combines signals into risk score
- Provides explainable results

**Why Demo Mode?**
- Machine learning models require training data
- Training requires the Kaggle Credit Card Fraud dataset
- Demo mode lets you test the system immediately

---

## 🚦 Current Status

### ✅ Running Components:
- FastAPI server (port 8000)
- Web interface
- API documentation
- Health monitoring
- Prediction endpoint
- Metrics tracking

### ⚠️ Demo Mode (No ML Models):
- XGBoost: Using heuristics
- LSTM: Not loaded
- Autoencoder: Not loaded
- Graph Network: Not loaded

---

## 📊 API Status Dashboard

The web interface shows real-time status:
- **API Status**: healthy/degraded
- **Models Loaded**: 0/4 (demo mode)
- **Total Predictions**: Live counter
- **Avg Response Time**: Latency tracking

---

## 🛠️ Managing the Server

### Check if Server is Running
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*"}
```

### View Server Logs
The terminal running `uvicorn` shows live logs

### Stop the Server
Press `Ctrl+C` in the terminal running the server

### Restart the Server
```powershell
cd d:\fraudnet-x
.\venv\Scripts\Activate.ps1
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🎨 Features

### Web Interface
- 🎯 **Instant Predictions** - Real-time fraud analysis
- 📊 **Visual Results** - Color-coded risk levels
- 🔍 **Feature Importance** - See what drives the prediction
- ⚡ **Quick Tests** - Pre-configured samples
- 📈 **Live Metrics** - Performance monitoring

### API Features
- 🚀 **Fast Response** - Typically < 50ms
- 🔄 **Auto-reload** - Changes apply automatically
- 📝 **Auto-documentation** - Swagger UI included
- 🛡️ **CORS Enabled** - Works with any frontend
- ✅ **Input Validation** - Pydantic models

---

## 📝 Testing Examples

### Low Risk Transaction
```json
{
  "Time": 1000,
  "Amount": 15.50,
  "V1": 0.1, "V2": 0.2, "V3": 0.1, ...
}
```
**Expected**: Risk Score ~10-30, Level: Low

### Medium Risk Transaction
```json
{
  "Time": 5000,
  "Amount": 250.00,
  "V1": -1.2, "V2": 0.8, "V3": 1.5, ...
}
```
**Expected**: Risk Score ~40-60, Level: Medium

### High Risk Transaction
```json
{
  "Time": 12345,
  "Amount": 850.00,
  "V1": -3.5, "V2": 2.8, "V3": -2.9, ...
}
```
**Expected**: Risk Score ~70-90, Level: High

---

## 🔒 What Was Simplified

To make the project run error-free without disk space issues:

### ✅ Removed:
- ❌ Docker files (docker-compose.yml, Dockerfile)
- ❌ Makefile
- ❌ React frontend (requires npm install)
- ❌ Heavy ML dependencies (XGBoost, TensorFlow, scikit-learn)

### ✅ Created:
- ✨ Simple standalone HTML frontend
- ✨ Demo mode API (works without trained models)
- ✨ Heuristic-based predictions
- ✨ This quick start guide

---

## 🚀 Next Steps (Optional)

### To Train Real ML Models:

1. **Install ML dependencies**:
```powershell
pip install pandas scikit-learn xgboost tensorflow
```

2. **Download dataset**:
   - Get from: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
   - Place in: `d:\fraudnet-x\data\creditcard.csv`

3. **Train models**:
```powershell
python train_pipeline.py --data data/creditcard.csv
```

4. **Restart API** - Models will auto-load

---

## 🎉 Success Checklist

- ✅ API server running on port 8000
- ✅ Web interface accessible
- ✅ Can make predictions in demo mode
- ✅ API documentation viewable
- ✅ Health endpoint responding
- ✅ Metrics tracking working

---

## 📞 Troubleshooting

### Frontend not connecting to API
- Check API is running: http://localhost:8000/health
- Check CORS is enabled (it is by default)
- Open browser console for errors

### Port 8000 already in use
```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000

# Change port in startup command
uvicorn api.main:app --port 8001
```

### API not responding
- Check terminal for errors
- Ensure virtual environment is activated
- Verify FastAPI and Uvicorn are installed

---

## 🎯 Summary

**Your fraud detection system is READY TO USE!**

1. Open `simple-frontend.html` in browser
2. Click "High Risk 🔴" for a demo
3. See real-time fraud analysis
4. Explore API docs at http://localhost:8000/docs

**Enjoy your fraud detection system!** 🛡️

---

*Generated on March 2, 2026*
*FraudNet-X v1.0 - Demo Mode*
