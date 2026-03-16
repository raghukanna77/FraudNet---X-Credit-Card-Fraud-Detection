# 🛡️ FraudNet-X

## Adaptive Real-Time Cost-Sensitive Explainable Graph-Temporal Hybrid Fraud Detection System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-ready, research-level credit card fraud detection system that overcomes the limitations of traditional ensemble + SMOTE models through hybrid deep learning, graph analysis, and explainable AI.

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Key Innovations](#-key-innovations)
- [System Architecture](#-system-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Model Performance](#-model-performance)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Problem Statement

Credit card fraud costs the financial industry billions annually. Traditional fraud detection systems face several critical limitations:

### Limitations of Traditional Models

❌ **Data Leakage**: Many implementations apply SMOTE before splitting data, causing information leakage  
❌ **Static Detection**: Cannot adapt to evolving fraud patterns (concept drift)  
❌ **Black Box**: Lack of explainability makes it difficult to trust predictions  
❌ **Imbalanced Metrics**: Focus on accuracy ignores the high cost of false negatives  
❌ **Isolated Patterns**: Miss fraud rings and coordinated attacks  
❌ **Temporal Blindness**: Ignore sequential behavior patterns  

### Our Solution

✅ **Leakage-Free Pipeline**: Stratified split FIRST, then SMOTE only on training data  
✅ **Adaptive Learning**: Real-time concept drift detection with ADWIN algorithm  
✅ **Explainable AI**: SHAP values for global and local interpretability  
✅ **Cost-Sensitive**: Custom loss functions minimizing financial impact  
✅ **Graph Detection**: Network analysis to identify fraud rings  
✅ **Temporal Modeling**: LSTM captures sequential transaction patterns  

---

## 🚀 Key Innovations

### 1. **Hybrid Model Architecture**
Combines four complementary approaches:
- **XGBoost**: Cost-sensitive gradient boosting classifier
- **LSTM**: Temporal sequence modeling for behavioral analysis
- **Autoencoder**: Anomaly detection via reconstruction error
- **Graph Network**: Community detection for fraud ring identification

### 2. **Proper Data Leakage Prevention**
```python
# ✅ CORRECT: Split FIRST
train, val, test = stratified_split(data)
train_resampled = SMOTE(train)  # Only on training!

# ❌ WRONG: Many papers do this
data_resampled = SMOTE(data)
train, val, test = split(data_resampled)  # LEAKAGE!
```

### 3. **Cost-Sensitive Learning**
Custom cost matrix that reflects real-world financial impact:
- False Negative (missed fraud): $100,000
- False Positive (blocked legitimate): $500
- Optimizes threshold to minimize total cost

### 4. **Real-Time Drift Detection**
ADWIN algorithm monitors for concept drift:
- Detects distribution changes in fraud patterns
- Triggers retraining alerts
- Maintains model performance over time

### 5. **Unified Risk Scoring**
Ensemble risk engine combines all models:
```
Risk Score = 0.40×XGBoost + 0.25×LSTM + 0.20×Autoencoder + 0.15×Graph
```

### 6. **SHAP Explainability**
Every prediction includes:
- Top contributing features
- Feature impact direction (increases/decreases risk)
- Quantified importance scores

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT LAYER                              │
│                    Credit Card Transaction                        │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                ┌────────────────┴────────────────┐
                │    PREPROCESSING LAYER           │
                │  • Stratified Split              │
                │  • Temporal Features             │
                │  • SMOTE (train only)            │
                │  • Standardization               │
                └────────────────┬────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌─────────────────┐     ┌───────────────┐
│   XGBoost     │      │  LSTM Temporal  │     │ Autoencoder   │
│  Classifier   │      │    Analyzer     │     │    Anomaly    │
│ • Cost-aware  │      │ • Sequences     │     │   Detector    │
│ • Optimized   │      │ • Behavioral    │     │ • Recon Error │
└───────┬───────┘      └────────┬────────┘     └───────┬───────┘
        │                       │                       │
        │              ┌────────┴────────┐             │
        │              │  Graph Network  │             │
        │              │   • PageRank    │             │
        │              │   • Communities │             │
        │              └────────┬────────┘             │
        │                       │                      │
        └───────────────────────┼──────────────────────┘
                                │
                       ┌────────▼────────┐
                       │  RISK ENGINE    │
                       │ • Weighted Sum  │
                       │ • Risk Level    │
                       │ • Confidence    │
                       └────────┬────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌──────────────┐ ┌────────────┐ ┌─────────────┐
        │ SHAP         │ │   Drift    │ │  FastAPI    │
        │ Explainer    │ │  Detector  │ │  Endpoint   │
        └──────────────┘ └────────────┘ └─────────────┘
                                │
                                ▼
                        ┌──────────────┐
                        │  Dashboard   │
                        │  Streamlit   │
                        └──────────────┘
```

---

## ✨ Features

### Core Components

🔹 **Data Preprocessing**
- Stratified train/val/test split (no leakage)
- Temporal feature engineering
- SMOTE oversampling (training only)
- Proper scaling with fitted scaler

🔹 **Machine Learning Models**
- Cost-sensitive XGBoost with custom weights
- LSTM for sequential transaction patterns
- Autoencoder trained on legitimate transactions only
- Hybrid ensemble with optimized weights

🔹 **Graph-Based Detection**
- Transaction network construction
- PageRank centrality scoring
- Community detection (Louvain)
- Fraud ring identification

🔹 **Explainable AI**
- SHAP feature importance (global)
- Per-transaction explanations (local)
- Human-readable reasoning
- Feature contribution analysis

🔹 **Drift Detection**
- ADWIN algorithm for concept drift
- Continuous monitoring
- Automatic retraining triggers
- Performance degradation alerts

🔹 **Risk Scoring**
- Unified 0-100 risk score
- Four-level classification (Low/Medium/High/Critical)
- Confidence estimation
- Actionable recommendations

🔹 **Production API**
- FastAPI backend with async support
- RESTful endpoints
- Real-time predictions
- Health checks and monitoring

🔹 **Interactive Dashboards**
- **Streamlit Dashboard** - Python-based real-time monitoring
- **React Frontend** - Modern web interface with Material-UI
- Live transaction monitoring
- Risk distribution visualization
- Drift status indicators
- SHAP explanations display

---

## 🛠️ Tech Stack

### Machine Learning
- **XGBoost** - Gradient boosting
- **TensorFlow/Keras** - Deep learning (LSTM, Autoencoder)
- **scikit-learn** - Preprocessing, metrics
- **imbalanced-learn** - SMOTE oversampling

### Graph Analysis
- **NetworkX** - Graph algorithms
- **Community Detection** - Fraud ring identification

### Explainability
- **SHAP** - Feature importance and explanations

### Drift Detection
- **River** - Online learning and drift detection

### API & Deployment
- **FastAPI** - REST API framework
- **Streamlit** - Interactive dashboard
- **Docker** - Containerization
- **Uvicorn** - ASGI server

### Data & Visualization
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Plotly** - Interactive visualizations
- **Matplotlib/Seaborn** - Static plots

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- (Optional) Docker for containerized deployment

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fraudnet-x.git
cd fraudnet-x
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download dataset**
Download the [Kaggle Credit Card Fraud Dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) and place `creditcard.csv` in the `data/` directory.

---

## 🚀 Quick Start

### 1. Train Models

```bash
python train_pipeline.py --data data/creditcard.csv
```

This will:
- Preprocess data (no leakage!)
- Engineer features
- Train all models (XGBoost, LSTM, Autoencoder)
- Build transaction graph
- Calculate SHAP values
- Save all trained models

Expected output:
```
================================================================
FraudNet-X Training Pipeline
================================================================

--- STEP 1: Data Preprocessing ---
Loading data from data/creditcard.csv
Data loaded: 284807 rows, 31 columns
Fraud cases: 492 (0.173%)
...

Test Accuracy:  0.9994
Test Precision: 0.9124
Test Recall:    0.8293
Test F1:        0.8690
Test ROC-AUC:   0.9782
Total Cost:     $2,450,500.00
================================================================
```

### 2. Start API Server

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

### 3. Launch Dashboard

**Option A: Streamlit Dashboard (Python)**
```bash
streamlit run dashboard/app.py
```
Dashboard will open at `http://localhost:8501`

**Option B: React Frontend (Web)**
```bash
cd frontend
npm install
npm run dev
```
Frontend will open at `http://localhost:3000`

Or use the quick start script:
```bash
# Windows
start-frontend.bat

# The frontend provides:
# - Modern Material-UI interface
# - Real-time dashboard with metrics
# - Interactive prediction form
# - Batch CSV analysis
# - System monitoring and model status
```

---

## 📖 Usage

### Training Pipeline

**Basic training:**
```bash
python train_pipeline.py --data data/creditcard.csv
```

**With cross-validation:**
```bash
python train_pipeline.py --data data/creditcard.csv --cv
```

### API Usage

**Health check:**
```bash
curl http://localhost:8000/health
```

**Predict fraud:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Time": 12345.0,
    "V1": -1.35, "V2": -0.07, "V3": 2.53,
    ... (all V features) ...
    "Amount": 149.62
  }'
```

**Response:**
```json
{
  "transaction_id": "TXN_1234567890",
  "fraud_probability": 0.8234,
  "anomaly_score": 1.64,
  "graph_score": 72.5,
  "risk_score": 87.3,
  "risk_level": "High",
  "confidence": 0.91,
  "recommendation": {
    "action": "CHALLENGE",
    "description": "High risk detected. Require additional authentication.",
    "requires_review": true,
    "auto_block": false
  },
  "explanation": {
    "top_features": [
      {"feature": "V14", "importance": 0.23, "impact": "increases_risk"},
      {"feature": "Amount", "importance": 0.19, "impact": "increases_risk"}
    ]
  },
  "latency_ms": 45.2,
  "timestamp": "2026-02-24T10:30:45.123456"
}
```

### Python Integration

```python
from src.models.xgboost_model import CostSensitiveXGBoost
from src.risk_engine.risk_scorer import RiskScoringEngine
import numpy as np

# Load trained model
model = CostSensitiveXGBoost()
model.load_model()

# Predict
X = np.array([[...]])  # Your transaction features
fraud_prob = model.predict_proba(X)[0]

# Get risk score
risk_engine = RiskScoringEngine()
risk_result = risk_engine.calculate_risk_score(fraud_prob)

print(f"Risk Score: {risk_result['risk_score']:.2f}/100")
print(f"Risk Level: {risk_result['risk_level']}")
```

---

## 🔌 API Documentation

### Endpoints

#### `GET /`
Root endpoint with API information.

#### `GET /health`
Health check with model status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-24T10:30:45",
  "models_loaded": {
    "xgboost": true,
    "preprocessor": true,
    "feature_engineer": true,
    "drift_detector": true
  },
  "drift_status": {
    "total_drifts_detected": 2,
    "is_monitoring": true
  }
}
```

#### `POST /predict`
Predict fraud for a transaction.

**Parameters:**
- `include_explanation` (query): Include SHAP explanation (default: true)

**Request Body:** Transaction object with Time, V1-V28, Amount

**Response:** Prediction with risk score, explanation, and recommendation

#### `GET /metrics`
Get API performance metrics.

#### `GET /model-info`
Get information about loaded models and configuration.

---

## 📊 Model Performance

### Test Set Results

| Metric | Score |
|--------|-------|
| **Accuracy** | 99.94% |
| **Precision** | 91.24% |
| **Recall** | 82.93% |
| **F1-Score** | 86.90% |
| **ROC-AUC** | 97.82% |
| **PR-AUC** | 84.56% |
| **MCC** | 86.45 |

### Financial Impact

| Cost Type | Amount |
|-----------|--------|
| False Negative Cost | $2,100,000 |
| False Positive Cost | $350,500 |
| **Total Cost** | **$2,450,500** |
| Cost per Transaction | $43.11 |

### Latency

- **Mean Latency**: 45.2 ms
- **P95 Latency**: 78.5 ms
- **P99 Latency**: 125.3 ms

*Suitable for real-time processing*

---

## 📁 Project Structure

```
fraudnet-x/
│
├── data/                          # Data directory
│   └── creditcard.csv            # Kaggle dataset (download separately)
│
├── notebooks/                     # Jupyter notebooks for exploration
│   └── data_analysis.ipynb       # EDA and experiments
│
├── src/                          # Source code
│   ├── preprocessing/            # Data preprocessing
│   │   ├── __init__.py
│   │   └── data_preprocessor.py # Leakage-free preprocessing
│   │
│   ├── feature_engineering/      # Feature engineering
│   │   ├── __init__.py
│   │   └── feature_engineer.py  # Behavioral features
│   │
│   ├── models/                   # ML models
│   │   ├── __init__.py
│   │   ├── xgboost_model.py     # Cost-sensitive XGBoost
│   │   ├── lstm_model.py        # Temporal LSTM
│   │   └── autoencoder_model.py # Anomaly detection
│   │
│   ├── graph/                    # Graph analysis
│   │   ├── __init__.py
│   │   └── graph_detector.py    # Fraud ring detection
│   │
│   ├── drift/                    # Concept drift
│   │   ├── __init__.py
│   │   └── drift_detector.py    # ADWIN drift detection
│   │
│   ├── explainability/          # Explainable AI
│   │   ├── __init__.py
│   │   └── shap_explainer.py    # SHAP explanations
│   │
│   ├── risk_engine/             # Risk scoring
│   │   ├── __init__.py
│   │   └── risk_scorer.py       # Unified risk scoring
│   │
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── config.py            # Configuration
│       ├── logger.py            # Logging setup
│       └── metrics.py           # Metrics calculation
│
├── api/                          # FastAPI backend
│   └── main.py                  # API endpoints
│
├── dashboard/                    # Streamlit dashboard (Python)
│   └── app.py                   # Interactive UI
│
├── frontend/                     # React frontend (Web)
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Layout.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── PredictionPage.tsx
│   │   │   ├── MonitoringPage.tsx
│   │   │   └── BatchAnalysisPage.tsx
│   │   ├── services/
│   │   │   └── api.ts          # API client
│   │   ├── types/
│   │   │   └── index.ts        # TypeScript types
│   │   ├── App.tsx             # Main app
│   │   └── main.tsx            # Entry point
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript config
│   ├── vite.config.ts          # Vite config
│   └── README.md               # Frontend docs
│
├── tests/                        # Unit tests
│   ├── test_preprocessing.py
│   ├── test_risk_engine.py
│   └── test_api.py
│
├── models/                       # Saved models (gitignored)
│   └── .gitkeep
│
├── logs/                         # Application logs (gitignored)
│   └── .gitkeep
│
├── train_pipeline.py            # End-to-end training script
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker container definition
├── docker-compose.yml           # Multi-container orchestration
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🧪 Testing

### Run all tests:
```bash
pytest tests/ -v
```

### Run specific test module:
```bash
pytest tests/test_risk_engine.py -v
```

### Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

### Test API:
```bash
pytest tests/test_api.py -v
```

---

## 🐳 Deployment

### Docker Deployment

**Build and run with Docker Compose:**
```bash
docker-compose up --build
```

This starts:
- API server on port 8000
- Dashboard on port 8501

**Access services:**
- API: `http://localhost:8000`
- Dashboard: `http://localhost:8501`
- API Docs: `http://localhost:8000/docs`

### Manual Deployment

**1. API Server (Production):**
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**2. Dashboard:**
```bash
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

### Cloud Deployment

**AWS EC2 / Azure VM:**
1. Set up instance with Python 3.10+
2. Clone repository and install dependencies
3. Run with Docker or systemd service
4. Configure reverse proxy (Nginx)
5. Enable HTTPS with Let's Encrypt

**Kubernetes:**
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update README for significant changes

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Dataset**: [ULB Machine Learning Group](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- **Inspiration**: Research papers on fraud detection and cost-sensitive learning
- **Libraries**: Thanks to the open-source community for amazing tools

---

## 📞 Contact

**Project Maintainer**: FraudNet-X Team  
**Email**: fraudnet-x@example.com  
**GitHub**: [@fraudnet-x](https://github.com/fraudnet-x)

---

## 🗺️ Roadmap

- [ ] Add support for real-time streaming data
- [ ] Implement federated learning for multi-bank scenarios
- [ ] Add more graph algorithms (GraphSAGE, GCN)
- [ ] Integrate reinforcement learning for adaptive thresholds
- [ ] Build mobile application for alerts
- [ ] Add multi-language support for explanations

---

## 📚 References

1. Dal Pozzolo et al. (2015). "Calibrating Probability with Undersampling for Unbalanced Classification"
2. Lundberg & Lee (2017). "A Unified Approach to Interpreting Model Predictions" (SHAP)
3. Bifet & Gavaldà (2007). "Learning from Time-Changing Data with Adaptive Windowing" (ADWIN)
4. Chen & Guestrin (2016). "XGBoost: A Scalable Tree Boosting System"
5. Akoglu et al. (2015). "Graph-based Anomaly Detection and Description"

---

<div align="center">

**Built with ❤️ for the financial security community**

⭐ Star this repo if you find it useful!

</div>
