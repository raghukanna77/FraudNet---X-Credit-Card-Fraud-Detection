"""
FraudNet-X Quick Test Script
Run various test cases to verify fraud detection system
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def print_header(text, color_code="95"):
    """Print colored header"""
    print(f"\n\033[{color_code}m{'='*70}\033[0m")
    print(f"\033[{color_code}m{text.center(70)}\033[0m")
    print(f"\033[{color_code}m{'='*70}\033[0m")

def print_result(label, value, color="0"):
    """Print colored result"""
    print(f"\033[{color}m{label}: {value}\033[0m")

def test_prediction(name, data, expected_risk):
    """Test a fraud prediction"""
    print_header(f"TEST: {name}", "96")
    
    try:
        response = requests.post(f"{API_URL}/predict", json=data)
        response.raise_for_status()
        result = response.json()
        
        # Display results
        print_result("Amount", f"${data['Amount']:.2f}", "96")
        print_result("Risk Score", f"{result['risk_score']:.1f}/100", "93")
        
        # Color code based on risk level
        risk_colors = {
            "Low": "92",      # Green
            "Medium": "93",   # Yellow
            "High": "91",     # Red
            "Critical": "91"  # Red
        }
        color = risk_colors.get(result['risk_level'], "0")
        print_result("Risk Level", result['risk_level'], color)
        print_result("Fraud Probability", f"{result['fraud_probability']*100:.1f}%", color)
        print_result("Confidence", f"{result['confidence']*100:.1f}%", "94")
        print_result("Recommendation", result['recommendation']['action'], "95")
        print_result("Response Time", f"{result['latency_ms']:.2f}ms", "90")
        
        # Show top contributing features
        if result.get('explanation') and result['explanation'].get('top_features'):
            print("\n📊 Top Contributing Features:")
            for feature in result['explanation']['top_features'][:3]:
                bar_length = int(feature['importance'] * 20)
                bar = "█" * bar_length
                print(f"  {feature['feature']:8s} {bar} {feature['importance']:.3f}")
        
        # Check if result matches expectation
        if expected_risk.lower() in result['risk_level'].lower():
            print_result("\n✅ TEST STATUS", "PASS", "92")
        else:
            print_result("\n⚠️  TEST STATUS", f"UNEXPECTED (Expected: {expected_risk})", "93")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print_result("❌ ERROR", str(e), "91")
        return None

def test_health():
    """Test health endpoint"""
    print_header("HEALTH CHECK", "94")
    try:
        response = requests.get(f"{API_URL}/health")
        health = response.json()
        
        status_colors = {"healthy": "92", "degraded": "93"}
        color = status_colors.get(health['status'], "91")
        print_result("Status", health['status'].upper(), color)
        print_result("Timestamp", health['timestamp'], "90")
        
        print("\n📦 Models Loaded:")
        for model, loaded in health['models_loaded'].items():
            status = "✅ Loaded" if loaded else "⚠️  Not loaded (Demo mode)"
            print(f"  {model:20s} {status}")
        
    except Exception as e:
        print_result("❌ ERROR", str(e), "91")

def test_metrics():
    """Test metrics endpoint"""
    print_header("API METRICS", "94")
    try:
        response = requests.get(f"{API_URL}/metrics")
        metrics = response.json()
        
        print_result("Total Predictions", metrics['total_requests'], "96")
        print_result("Average Latency", f"{metrics['average_latency_ms']:.2f}ms", "93")
        
    except Exception as e:
        print_result("❌ ERROR", str(e), "91")

# =============================================================================
# MAIN TEST SUITE
# =============================================================================

if __name__ == "__main__":
    print_header("🛡️  FRAUDNET-X TEST SUITE", "95")
    print(f"\033[90mStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
    print(f"\033[90mAPI URL: {API_URL}\033[0m")
    
    # Health check first
    test_health()
    
    # Test Case 1: Low Risk - Small normal transaction
    test_prediction(
        "Low Risk - Small Normal Transaction",
        {
            "Time": 500, "Amount": 10.50,
            "V1": 0.1, "V2": 0.15, "V3": 0.08, "V4": 0.12,
            "V5": 0.09, "V6": 0.11, "V7": 0.13, "V8": 0.07,
            "V9": 0.14, "V10": 0.06, "V11": 0.10, "V12": 0.08,
            "V13": 0.12, "V14": 0.09, "V15": 0.11, "V16": 0.07,
            "V17": 0.13, "V18": 0.08, "V19": 0.10, "V20": 0.12,
            "V21": 0.09, "V22": 0.11, "V23": 0.07, "V24": 0.13,
            "V25": 0.08, "V26": 0.10, "V27": 0.12, "V28": 0.09
        },
        expected_risk="Low"
    )
    
    # Test Case 2: Low Risk - Grocery shopping
    test_prediction(
        "Low Risk - Grocery Shopping",
        {
            "Time": 1200, "Amount": 67.23,
            "V1": -0.05, "V2": 0.08, "V3": -0.12, "V4": 0.15,
            "V5": 0.09, "V6": -0.11, "V7": 0.07, "V8": 0.13,
            "V9": -0.08, "V10": 0.10, "V11": 0.14, "V12": -0.09,
            "V13": 0.11, "V14": 0.06, "V15": -0.13, "V16": 0.08,
            "V17": 0.12, "V18": -0.07, "V19": 0.09, "V20": 0.14,
            "V21": -0.10, "V22": 0.11, "V23": 0.08, "V24": -0.12,
            "V25": 0.09, "V26": 0.13, "V27": -0.08, "V28": 0.10
        },
        expected_risk="Low"
    )
    
    # Test Case 3: Medium Risk - Large purchase
    test_prediction(
        "Medium Risk - Large Purchase",
        {
            "Time": 5000, "Amount": 250.00,
            "V1": -1.2, "V2": 0.8, "V3": 1.5, "V4": -0.9,
            "V5": 0.6, "V6": -0.7, "V7": 0.5, "V8": -0.4,
            "V9": 0.9, "V10": -0.8, "V11": 0.7, "V12": -0.6,
            "V13": 0.5, "V14": -1.1, "V15": 0.9, "V16": -0.8,
            "V17": 0.7, "V18": -0.6, "V19": 0.8, "V20": -0.5,
            "V21": 0.4, "V22": -0.7, "V23": 0.6, "V24": -0.5,
            "V25": 0.4, "V26": -0.6, "V27": 0.5, "V28": -0.4
        },
        expected_risk="Medium"
    )
    
    # Test Case 4: Medium Risk - Unusual pattern
    test_prediction(
        "Medium Risk - Unusual Pattern",
        {
            "Time": 8500, "Amount": 180.50,
            "V1": -1.5, "V2": 1.2, "V3": -1.1, "V4": 1.3,
            "V5": -0.9, "V6": 1.0, "V7": -0.8, "V8": 1.1,
            "V9": -1.2, "V10": 1.4, "V11": -1.0, "V12": 0.9,
            "V13": -1.1, "V14": 1.2, "V15": -0.9, "V16": 1.0,
            "V17": -1.3, "V18": 0.8, "V19": -1.0, "V20": 1.1,
            "V21": -0.9, "V22": 1.2, "V23": -0.8, "V24": 1.0,
            "V25": -1.1, "V26": 0.9, "V27": -1.0, "V28": 1.2
        },
        expected_risk="Medium"
    )
    
    # Test Case 5: High Risk - Large unusual transaction
    test_prediction(
        "High Risk - Large Unusual Transaction",
        {
            "Time": 12345, "Amount": 850.00,
            "V1": -3.5, "V2": 2.8, "V3": -2.9, "V4": 3.1,
            "V5": -2.7, "V6": 2.6, "V7": -2.5, "V8": 2.4,
            "V9": -2.8, "V10": 2.9, "V11": -3.0, "V12": 2.7,
            "V13": -2.6, "V14": 3.2, "V15": -2.9, "V16": 2.8,
            "V17": -2.7, "V18": 2.5, "V19": -2.9, "V20": 2.8,
            "V21": -2.6, "V22": 2.7, "V23": -2.5, "V24": 2.4,
            "V25": -2.8, "V26": 2.6, "V27": -2.7, "V28": 2.5
        },
        expected_risk="High"
    )
    
    # Test Case 6: High Risk - Very large amount
    test_prediction(
        "High Risk - Very Large Amount",
        {
            "Time": 30000, "Amount": 1250.00,
            "V1": -2.5, "V2": 2.2, "V3": -2.8, "V4": 2.6,
            "V5": -2.3, "V6": 2.1, "V7": -2.7, "V8": 2.4,
            "V9": -2.6, "V10": 2.5, "V11": -2.4, "V12": 2.3,
            "V13": -2.9, "V14": 2.7, "V15": -2.5, "V16": 2.2,
            "V17": -2.8, "V18": 2.4, "V19": -2.6, "V20": 2.5,
            "V21": -2.3, "V22": 2.8, "V23": -2.4, "V24": 2.6,
            "V25": -2.7, "V26": 2.3, "V27": -2.5, "V28": 2.4
        },
        expected_risk="High"
    )
    
    # Test Case 7: Critical Risk - Maximum risk
    test_prediction(
        "Critical Risk - Maximum Risk Transaction",
        {
            "Time": 60000, "Amount": 2500.00,
            "V1": -5.0, "V2": 4.8, "V3": -4.5, "V4": 5.2,
            "V5": -4.9, "V6": 4.3, "V7": -4.7, "V8": 4.6,
            "V9": -5.1, "V10": 4.9, "V11": -4.8, "V12": 5.0,
            "V13": -4.6, "V14": 5.3, "V15": -4.9, "V16": 4.7,
            "V17": -5.2, "V18": 4.5, "V19": -5.0, "V20": 4.8,
            "V21": -4.7, "V22": 5.1, "V23": -4.6, "V24": 4.9,
            "V25": -4.8, "V26": 5.0, "V27": -4.7, "V28": 5.2
        },
        expected_risk="Critical"
    )
    
    # Test Case 8: Critical Risk - Extreme anomaly
    test_prediction(
        "Critical Risk - Extreme Anomaly",
        {
            "Time": 80000, "Amount": 3000.00,
            "V1": -6.5, "V2": 6.2, "V3": -5.8, "V4": 6.0,
            "V5": -5.5, "V6": 5.9, "V7": -6.1, "V8": 5.7,
            "V9": -5.9, "V10": 6.3, "V11": -6.0, "V12": 5.8,
            "V13": -5.7, "V14": 6.1, "V15": -6.2, "V16": 5.6,
            "V17": -5.8, "V18": 6.0, "V19": -6.4, "V20": 5.9,
            "V21": -5.6, "V22": 6.2, "V23": -5.9, "V24": 6.1,
            "V25": -6.0, "V26": 5.7, "V27": -6.3, "V28": 5.8
        },
        expected_risk="Critical"
    )
    
    # Final metrics
    test_metrics()
    
    # Summary
    print_header("🎉 TEST SUITE COMPLETE", "92")
    print(f"\033[90mCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
    print(f"\n\033[96mAll test cases have been executed!\033[0m")
    print(f"\033[90mCheck results above to verify fraud detection accuracy.\033[0m\n")
