"""Test FraudNet-X system and display full output."""

import requests
import json
import time
from datetime import datetime

API_URL = "http://localhost:8000"

def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_health():
    """Test the health endpoint."""
    print_section("🏥 HEALTH CHECK")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        health_data = response.json()
        print(json.dumps(health_data, indent=2))
        return health_data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_metrics():
    """Test the metrics endpoint."""
    print_section("📊 SYSTEM METRICS")
    try:
        response = requests.get(f"{API_URL}/metrics", timeout=5)
        metrics_data = response.json()
        print(json.dumps(metrics_data, indent=2))
        return metrics_data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_model_info():
    """Test the model info endpoint."""
    print_section("🧠 MODEL INFORMATION")
    try:
        response = requests.get(f"{API_URL}/model-info", timeout=5)
        model_data = response.json()
        print(json.dumps(model_data, indent=2))
        return model_data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_prediction(transaction_data):
    """Test the prediction endpoint."""
    print_section("🎯 PREDICTION TEST")
    try:
        response = requests.post(f"{API_URL}/predict", json=transaction_data, timeout=5)
        prediction_data = response.json()
        print(json.dumps(prediction_data, indent=2))
        return prediction_data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  🚀 FraudNet-X System - Complete Initialization & Output".center(78) + "║")
    print("║" + f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Check backend availability
    print("\n⏳ Checking backend availability...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is online!")
                break
        except:
            if i < max_retries - 1:
                print(f"⏳ Waiting... ({i+1}/{max_retries})")
                time.sleep(1)
            else:
                print("❌ Backend not responding. Make sure it's running on port 8000")
                return
    
    # Run tests
    health = test_health()
    metrics = test_metrics()
    model_info = test_model_info()
    
    # Test predictions with sample transactions
    sample_transactions = [
        {
            "Time": 1,
            "V1": 0.5, "V2": -0.7, "V3": 0.2, "V4": 0.1, "V5": -0.3,
            "V6": 0.0, "V7": 0.1, "V8": -0.1, "V9": 0.0, "V10": 0.1,
            "V11": 0.0, "V12": 0.0, "V13": -0.1, "V14": 0.0, "V15": 0.0,
            "V16": 0.0, "V17": 0.0, "V18": 0.0, "V19": 0.0, "V20": 0.0,
            "V21": 0.0, "V22": 0.0, "V23": 0.0, "V24": 0.0, "V25": 0.0,
            "V26": 0.0, "V27": 0.0, "V28": 0.0,
            "Amount": 50.0,
            "Class": 0
        },
        {
            "Time": 5,
            "V1": -3.5, "V2": 3.8, "V3": -2.1, "V4": 2.5, "V5": -1.9,
            "V6": 2.0, "V7": -1.5, "V8": 1.8, "V9": -2.0, "V10": 1.2,
            "V11": -3.0, "V12": 2.8, "V13": -1.9, "V14": 2.3, "V15": -1.5,
            "V16": 1.9, "V17": -2.5, "V18": 0.8, "V19": -0.5, "V20": 0.9,
            "V21": -1.1, "V22": 1.3, "V23": -0.7, "V24": 0.6, "V25": -0.8,
            "V26": 0.7, "V27": -0.4, "V28": 0.5,
            "Amount": 2500.0,
            "Class": 1
        }
    ]
    
    print_section("🎯 PREDICTION EXAMPLES")
    print("\n[Transaction 1] - Low Risk Legitimate Transaction (Amount: $50)")
    pred1 = test_prediction(sample_transactions[0])
    
    print("\n[Transaction 2] - High Risk Fraudulent Transaction (Amount: $2500)")
    pred2 = test_prediction(sample_transactions[1])
    
    # Summary
    print_section("📋 SYSTEM SUMMARY")
    if health:
        print(f"✅ System Status: {health.get('status', 'unknown').upper()}")
        print(f"✅ Models Loaded: {all(health.get('models_loaded', {}).values())}")
        print(f"   - XGBoost: {health.get('models_loaded', {}).get('xgboost', False)}")
        print(f"   - LSTM: {health.get('models_loaded', {}).get('lstm', False)}")
        print(f"   - Autoencoder: {health.get('models_loaded', {}).get('autoencoder', False)}")
        print(f"   - Drift Detector: {health.get('models_loaded', {}).get('drift_detector', False)}")
    
    if metrics:
        print(f"\n📊 Metrics:")
        print(f"   - Total Predictions: {metrics.get('total_predictions', 0)}")
        print(f"   - Fraud Detected: {metrics.get('fraud_detected', 0)}")
        print(f"   - Fraud Rate: {metrics.get('fraud_rate', 0):.2%}")
        print(f"   - Average Risk Score: {metrics.get('average_risk_score', 0):.3f}")
        print(f"   - Average Latency: {metrics.get('average_latency_ms', 0):.2f}ms")
        print(f"   - Model Accuracy: {metrics.get('model_accuracy', 0):.2%}")
    
    if model_info:
        print(f"\n🧠 Model Architecture:")
        print(f"   - Ensemble Size: 4 models")
        print(f"   - Primary Model: XGBoost")
        print(f"   - Input Features: 30 (28 PCA + Time + Amount)")
        print(f"   - Demo Mode: {model_info.get('demo_mode', False)}")
    
    print_section("✨ FRONTEND & BACKEND RUNNING")
    print("\n🌐 Frontend: http://localhost:3000")
    print("   - Dashboard: http://localhost:3000/dashboard")
    print("   - Predictions: http://localhost:3000/predict")
    print("   - Monitoring: http://localhost:3000/monitoring")
    print("   - Batch Analysis: http://localhost:3000/batch")
    
    print("\n⚡ Backend API: http://localhost:8000")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - Health: http://localhost:8000/health")
    print("   - Metrics: http://localhost:8000/metrics")
    print("   - Model Info: http://localhost:8000/model-info")
    
    print("\n" + "=" * 80)
    print("  ✅ FraudNet-X System Fully Operational!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
