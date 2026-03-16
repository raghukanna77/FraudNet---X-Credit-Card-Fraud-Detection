# 🧪 FraudNet-X Testing Guide

Complete guide to testing your fraud detection system with various test cases.

---

## 🎯 Quick Test Methods

### Method 1: Web Interface (Easiest)
1. Open `simple-frontend.html` in your browser
2. Use the **Quick Test Samples** buttons
3. See instant results

### Method 2: API Documentation (Interactive)
1. Visit http://localhost:8000/docs
2. Try the `/predict` endpoint
3. Use the built-in test interface

### Method 3: PowerShell/Command Line
Use `Invoke-WebRequest` to test API endpoints directly

### Method 4: Python Scripts
Write custom test scripts with various scenarios

---

## 📊 Test Case Categories

### 1. LOW RISK Transactions (Should Pass ✅)
Normal, legitimate transactions

### 2. MEDIUM RISK Transactions (Should Review ⚠️)
Suspicious but could be legitimate

### 3. HIGH RISK Transactions (Should Block 🚫)
Likely fraudulent transactions

### 4. CRITICAL RISK Transactions (Definite Block 🔴)
Almost certainly fraudulent

---

## 🟢 LOW RISK TEST CASES

### Test Case 1.1: Small Normal Transaction
```json
{
  "Time": 500,
  "Amount": 10.50,
  "V1": 0.1, "V2": 0.15, "V3": 0.08, "V4": 0.12,
  "V5": 0.09, "V6": 0.11, "V7": 0.13, "V8": 0.07,
  "V9": 0.14, "V10": 0.06, "V11": 0.10, "V12": 0.08,
  "V13": 0.12, "V14": 0.09, "V15": 0.11, "V16": 0.07,
  "V17": 0.13, "V18": 0.08, "V19": 0.10, "V20": 0.12,
  "V21": 0.09, "V22": 0.11, "V23": 0.07, "V24": 0.13,
  "V25": 0.08, "V26": 0.10, "V27": 0.12, "V28": 0.09
}
```
**Expected Result:**
- Risk Score: 5-20
- Risk Level: Low
- Recommendation: Approve transaction

### Test Case 1.2: Medium Normal Transaction
```json
{
  "Time": 2500,
  "Amount": 45.99,
  "V1": 0.2, "V2": -0.1, "V3": 0.15, "V4": -0.08,
  "V5": 0.12, "V6": -0.15, "V7": 0.18, "V8": 0.10,
  "V9": -0.12, "V10": 0.14, "V11": 0.09, "V12": -0.11,
  "V13": 0.16, "V14": -0.13, "V15": 0.11, "V16": 0.08,
  "V17": -0.14, "V18": 0.12, "V19": 0.15, "V20": -0.09,
  "V21": 0.10, "V22": -0.12, "V23": 0.13, "V24": 0.11,
  "V25": -0.08, "V26": 0.14, "V27": 0.09, "V28": -0.10
}
```
**Expected Result:**
- Risk Score: 10-25
- Risk Level: Low
- Recommendation: Approve transaction

### Test Case 1.3: Grocery Shopping
```json
{
  "Time": 1200,
  "Amount": 67.23,
  "V1": -0.05, "V2": 0.08, "V3": -0.12, "V4": 0.15,
  "V5": 0.09, "V6": -0.11, "V7": 0.07, "V8": 0.13,
  "V9": -0.08, "V10": 0.10, "V11": 0.14, "V12": -0.09,
  "V13": 0.11, "V14": 0.06, "V15": -0.13, "V16": 0.08,
  "V17": 0.12, "V18": -0.07, "V19": 0.09, "V20": 0.14,
  "V21": -0.10, "V22": 0.11, "V23": 0.08, "V24": -0.12,
  "V25": 0.09, "V26": 0.13, "V27": -0.08, "V28": 0.10
}
```
**Expected Result:**
- Risk Score: 15-30
- Risk Level: Low
- Recommendation: Approve transaction

---

## 🟡 MEDIUM RISK TEST CASES

### Test Case 2.1: Large Purchase
```json
{
  "Time": 5000,
  "Amount": 250.00,
  "V1": -1.2, "V2": 0.8, "V3": 1.5, "V4": -0.9,
  "V5": 0.6, "V6": -0.7, "V7": 0.5, "V8": -0.4,
  "V9": 0.9, "V10": -0.8, "V11": 0.7, "V12": -0.6,
  "V13": 0.5, "V14": -1.1, "V15": 0.9, "V16": -0.8,
  "V17": 0.7, "V18": -0.6, "V19": 0.8, "V20": -0.5,
  "V21": 0.4, "V22": -0.7, "V23": 0.6, "V24": -0.5,
  "V25": 0.4, "V26": -0.6, "V27": 0.5, "V28": -0.4
}
```
**Expected Result:**
- Risk Score: 35-55
- Risk Level: Medium
- Recommendation: Review recommended

### Test Case 2.2: Unusual Pattern
```json
{
  "Time": 8500,
  "Amount": 180.50,
  "V1": -1.5, "V2": 1.2, "V3": -1.1, "V4": 1.3,
  "V5": -0.9, "V6": 1.0, "V7": -0.8, "V8": 1.1,
  "V9": -1.2, "V10": 1.4, "V11": -1.0, "V12": 0.9,
  "V13": -1.1, "V14": 1.2, "V15": -0.9, "V16": 1.0,
  "V17": -1.3, "V18": 0.8, "V19": -1.0, "V20": 1.1,
  "V21": -0.9, "V22": 1.2, "V23": -0.8, "V24": 1.0,
  "V25": -1.1, "V26": 0.9, "V27": -1.0, "V28": 1.2
}
```
**Expected Result:**
- Risk Score: 40-60
- Risk Level: Medium
- Recommendation: Manual review

### Test Case 2.3: Late Night Purchase
```json
{
  "Time": 75600,
  "Amount": 199.99,
  "V1": -1.0, "V2": 0.9, "V3": -1.2, "V4": 1.1,
  "V5": -0.8, "V6": 0.7, "V7": -0.9, "V8": 1.0,
  "V9": -1.1, "V10": 0.8, "V11": -0.9, "V12": 1.2,
  "V13": -1.0, "V14": 0.9, "V15": -1.1, "V16": 0.8,
  "V17": -0.9, "V18": 1.0, "V19": -1.2, "V20": 0.9,
  "V21": -0.8, "V22": 1.1, "V23": -0.9, "V24": 1.0,
  "V25": -1.0, "V26": 0.8, "V27": -1.1, "V28": 0.9
}
```
**Expected Result:**
- Risk Score: 45-65
- Risk Level: Medium
- Recommendation: Additional verification

---

## 🟠 HIGH RISK TEST CASES

### Test Case 3.1: Large Unusual Transaction
```json
{
  "Time": 12345,
  "Amount": 850.00,
  "V1": -3.5, "V2": 2.8, "V3": -2.9, "V4": 3.1,
  "V5": -2.7, "V6": 2.6, "V7": -2.5, "V8": 2.4,
  "V9": -2.8, "V10": 2.9, "V11": -3.0, "V12": 2.7,
  "V13": -2.6, "V14": 3.2, "V15": -2.9, "V16": 2.8,
  "V17": -2.7, "V18": 2.5, "V19": -2.9, "V20": 2.8,
  "V21": -2.6, "V22": 2.7, "V23": -2.5, "V24": 2.4,
  "V25": -2.8, "V26": 2.6, "V27": -2.7, "V28": 2.5
}
```
**Expected Result:**
- Risk Score: 70-85
- Risk Level: High
- Recommendation: Block and investigate

### Test Case 3.2: Extreme V Values
```json
{
  "Time": 45000,
  "Amount": 650.00,
  "V1": -4.2, "V2": 3.8, "V3": -3.5, "V4": 4.1,
  "V5": -3.9, "V6": 3.2, "V7": -3.7, "V8": 3.4,
  "V9": -4.0, "V10": 3.6, "V11": -3.8, "V12": 3.9,
  "V13": -3.5, "V14": 4.2, "V15": -3.7, "V16": 3.4,
  "V17": -4.1, "V18": 3.3, "V19": -3.9, "V20": 3.5,
  "V21": -3.6, "V22": 4.0, "V23": -3.4, "V24": 3.8,
  "V25": -3.7, "V26": 3.9, "V27": -3.5, "V28": 4.1
}
```
**Expected Result:**
- Risk Score: 75-90
- Risk Level: High
- Recommendation: Block immediately

### Test Case 3.3: Very Large Amount
```json
{
  "Time": 30000,
  "Amount": 1250.00,
  "V1": -2.5, "V2": 2.2, "V3": -2.8, "V4": 2.6,
  "V5": -2.3, "V6": 2.1, "V7": -2.7, "V8": 2.4,
  "V9": -2.6, "V10": 2.5, "V11": -2.4, "V12": 2.3,
  "V13": -2.9, "V14": 2.7, "V15": -2.5, "V16": 2.2,
  "V17": -2.8, "V18": 2.4, "V19": -2.6, "V20": 2.5,
  "V21": -2.3, "V22": 2.8, "V23": -2.4, "V24": 2.6,
  "V25": -2.7, "V26": 2.3, "V27": -2.5, "V28": 2.4
}
```
**Expected Result:**
- Risk Score: 65-80
- Risk Level: High
- Recommendation: Block and verify

---

## 🔴 CRITICAL RISK TEST CASES

### Test Case 4.1: Maximum Risk Transaction
```json
{
  "Time": 60000,
  "Amount": 2500.00,
  "V1": -5.0, "V2": 4.8, "V3": -4.5, "V4": 5.2,
  "V5": -4.9, "V6": 4.3, "V7": -4.7, "V8": 4.6,
  "V9": -5.1, "V10": 4.9, "V11": -4.8, "V12": 5.0,
  "V13": -4.6, "V14": 5.3, "V15": -4.9, "V16": 4.7,
  "V17": -5.2, "V18": 4.5, "V19": -5.0, "V20": 4.8,
  "V21": -4.7, "V22": 5.1, "V23": -4.6, "V24": 4.9,
  "V25": -4.8, "V26": 5.0, "V27": -4.7, "V28": 5.2
}
```
**Expected Result:**
- Risk Score: 90-100
- Risk Level: Critical
- Recommendation: Block immediately, investigate fraud ring

### Test Case 4.2: Extreme Anomaly
```json
{
  "Time": 80000,
  "Amount": 3000.00,
  "V1": -6.5, "V2": 6.2, "V3": -5.8, "V4": 6.0,
  "V5": -5.5, "V6": 5.9, "V7": -6.1, "V8": 5.7,
  "V9": -5.9, "V10": 6.3, "V11": -6.0, "V12": 5.8,
  "V13": -5.7, "V14": 6.1, "V15": -6.2, "V16": 5.6,
  "V17": -5.8, "V18": 6.0, "V19": -6.4, "V20": 5.9,
  "V21": -5.6, "V22": 6.2, "V23": -5.9, "V24": 6.1,
  "V25": -6.0, "V26": 5.7, "V27": -6.3, "V28": 5.8
}
```
**Expected Result:**
- Risk Score: 95-100
- Risk Level: Critical
- Recommendation: Block and alert fraud team

---

## 🧪 PowerShell Test Commands

### Test 1: Health Check
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test 2: Root Endpoint
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test 3: Low Risk Prediction
```powershell
$body = @{
    Time = 500
    Amount = 10.50
    V1 = 0.1; V2 = 0.15; V3 = 0.08; V4 = 0.12
    V5 = 0.09; V6 = 0.11; V7 = 0.13; V8 = 0.07
    V9 = 0.14; V10 = 0.06; V11 = 0.10; V12 = 0.08
    V13 = 0.12; V14 = 0.09; V15 = 0.11; V16 = 0.07
    V17 = 0.13; V18 = 0.08; V19 = 0.10; V20 = 0.12
    V21 = 0.09; V22 = 0.11; V23 = 0.07; V24 = 0.13
    V25 = 0.08; V26 = 0.10; V27 = 0.12; V28 = 0.09
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test 4: High Risk Prediction
```powershell
$body = @{
    Time = 12345
    Amount = 850.00
    V1 = -3.5; V2 = 2.8; V3 = -2.9; V4 = 3.1
    V5 = -2.7; V6 = 2.6; V7 = -2.5; V8 = 2.4
    V9 = -2.8; V10 = 2.9; V11 = -3.0; V12 = 2.7
    V13 = -2.6; V14 = 3.2; V15 = -2.9; V16 = 2.8
    V17 = -2.7; V18 = 2.5; V19 = -2.9; V20 = 2.8
    V21 = -2.6; V22 = 2.7; V23 = -2.5; V24 = 2.4
    V25 = -2.8; V26 = 2.6; V27 = -2.7; V28 = 2.5
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test 5: Get Metrics
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/metrics" -UseBasicParsing | Select-Object -ExpandProperty Content
```

---

## 🐍 Python Test Script

Create a file `test_fraud_detection.py`:

```python
import requests
import json

API_URL = "http://localhost:8000"

def test_prediction(name, data, expected_risk_level):
    """Test a prediction and verify result"""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"{'='*60}")
    
    response = requests.post(f"{API_URL}/predict", json=data)
    result = response.json()
    
    print(f"Amount: ${data['Amount']}")
    print(f"Risk Score: {result['risk_score']:.1f}/100")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Fraud Probability: {result['fraud_probability']*100:.1f}%")
    print(f"Recommendation: {result['recommendation']['action']}")
    
    # Verify result
    if result['risk_level'].lower() == expected_risk_level.lower():
        print(f"✅ PASS - Got expected risk level: {expected_risk_level}")
    else:
        print(f"❌ FAIL - Expected: {expected_risk_level}, Got: {result['risk_level']}")
    
    return result

# Test Cases
print("Starting FraudNet-X Test Suite...")

# Low Risk
test_prediction("Small Normal Transaction", {
    "Time": 500, "Amount": 10.50,
    "V1": 0.1, "V2": 0.15, "V3": 0.08, "V4": 0.12,
    "V5": 0.09, "V6": 0.11, "V7": 0.13, "V8": 0.07,
    "V9": 0.14, "V10": 0.06, "V11": 0.10, "V12": 0.08,
    "V13": 0.12, "V14": 0.09, "V15": 0.11, "V16": 0.07,
    "V17": 0.13, "V18": 0.08, "V19": 0.10, "V20": 0.12,
    "V21": 0.09, "V22": 0.11, "V23": 0.07, "V24": 0.13,
    "V25": 0.08, "V26": 0.10, "V27": 0.12, "V28": 0.09
}, "Low")

# Medium Risk
test_prediction("Large Purchase", {
    "Time": 5000, "Amount": 250.00,
    "V1": -1.2, "V2": 0.8, "V3": 1.5, "V4": -0.9,
    "V5": 0.6, "V6": -0.7, "V7": 0.5, "V8": -0.4,
    "V9": 0.9, "V10": -0.8, "V11": 0.7, "V12": -0.6,
    "V13": 0.5, "V14": -1.1, "V15": 0.9, "V16": -0.8,
    "V17": 0.7, "V18": -0.6, "V19": 0.8, "V20": -0.5,
    "V21": 0.4, "V22": -0.7, "V23": 0.6, "V24": -0.5,
    "V25": 0.4, "V26": -0.6, "V27": 0.5, "V28": -0.4
}, "Medium")

# High Risk
test_prediction("Large Unusual Transaction", {
    "Time": 12345, "Amount": 850.00,
    "V1": -3.5, "V2": 2.8, "V3": -2.9, "V4": 3.1,
    "V5": -2.7, "V6": 2.6, "V7": -2.5, "V8": 2.4,
    "V9": -2.8, "V10": 2.9, "V11": -3.0, "V12": 2.7,
    "V13": -2.6, "V14": 3.2, "V15": -2.9, "V16": 2.8,
    "V17": -2.7, "V18": 2.5, "V19": -2.9, "V20": 2.8,
    "V21": -2.6, "V22": 2.7, "V23": -2.5, "V24": 2.4,
    "V25": -2.8, "V26": 2.6, "V27": -2.7, "V28": 2.5
}, "High")

print("\n" + "="*60)
print("Test Suite Complete!")
print("="*60)
```

Run with:
```powershell
python test_fraud_detection.py
```

---

## 🎯 Testing Scenarios

### Scenario 1: Normal Shopping Day
Test a sequence of normal transactions:
1. Coffee shop: $5.50 (Low Risk)
2. Lunch: $15.30 (Low Risk)
3. Gas station: $45.00 (Low Risk)
4. Grocery: $87.50 (Low-Medium Risk)

### Scenario 2: Unusual Activity
Test escalating risk:
1. Normal purchase: $25.00 (Low Risk)
2. Larger purchase: $150.00 (Medium Risk)
3. Very large: $500.00 (High Risk)
4. Suspicious: $1000.00 (Critical Risk)

### Scenario 3: Time-Based Testing
Test different times of day:
1. Morning (9 AM): Normal risk
2. Afternoon (2 PM): Normal risk
3. Late night (2 AM): Higher risk
4. Very late (4 AM): Highest risk

### Scenario 4: Amount-Based Testing
Test different amounts:
1. Micro: $1.00 - $10.00
2. Small: $10.00 - $50.00
3. Medium: $50.00 - $200.00
4. Large: $200.00 - $500.00
5. Very Large: $500.00 - $1000.00
6. Extreme: $1000.00+

---

## ✅ Expected Behavior

### Low Risk (0-30)
- ✅ Small amounts (< $100)
- ✅ Low V values (< 0.5)
- ✅ Normal patterns
- **Action:** Approve immediately

### Medium Risk (30-60)
- ⚠️ Medium amounts ($100-$300)
- ⚠️ Moderate V values (0.5-2.0)
- ⚠️ Unusual but possible
- **Action:** Review or approve with caution

### High Risk (60-85)
- 🚫 Large amounts ($300-$1000)
- 🚫 High V values (2.0-4.0)
- 🚫 Suspicious patterns
- **Action:** Block and investigate

### Critical Risk (85-100)
- 🔴 Very large amounts (> $1000)
- 🔴 Extreme V values (> 4.0)
- 🔴 Clear fraud indicators
- **Action:** Block immediately, alert fraud team

---

## 📊 Performance Testing

### Load Test
Test multiple predictions in sequence:

```powershell
for ($i=1; $i -le 10; $i++) {
    Write-Host "Test $i of 10"
    Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Start-Sleep -Milliseconds 100
}
```

### Response Time Test
Measure API latency:

```python
import requests
import time

times = []
for i in range(100):
    start = time.time()
    requests.get("http://localhost:8000/health")
    elapsed = (time.time() - start) * 1000
    times.append(elapsed)

print(f"Average: {sum(times)/len(times):.2f}ms")
print(f"Min: {min(times):.2f}ms")
print(f"Max: {max(times):.2f}ms")
```

---

## 🔍 Debugging Failed Tests

### If predictions are all Low Risk:
- Check V values are properly set
- Increase V values to > 2.0 for higher risk
- Increase Amount to > $500

### If predictions are all High Risk:
- Reduce V values to < 1.0
- Reduce Amount to < $100
- Check for typos in JSON

### If API returns errors:
1. Check server is running: `http://localhost:8000/health`
2. Verify JSON format is correct
3. Check all 30 fields are present (Time, V1-V28, Amount)
4. View server logs in PowerShell terminal

---

## 📝 Test Results Checklist

Test each category and check off:

- [ ] Low Risk - Small normal transaction
- [ ] Low Risk - Medium normal transaction
- [ ] Low Risk - Grocery shopping
- [ ] Medium Risk - Large purchase
- [ ] Medium Risk - Unusual pattern
- [ ] Medium Risk - Late night purchase
- [ ] High Risk - Large unusual transaction
- [ ] High Risk - Extreme V values
- [ ] High Risk - Very large amount
- [ ] Critical Risk - Maximum risk transaction
- [ ] Critical Risk - Extreme anomaly
- [ ] Health endpoint working
- [ ] Metrics endpoint working
- [ ] API documentation accessible
- [ ] Web interface functional
- [ ] Quick test buttons working

---

## 🎉 Success Criteria

Your system is working correctly if:

✅ Low risk transactions score < 30
✅ Medium risk transactions score 30-60
✅ High risk transactions score 60-85
✅ Critical risk transactions score > 85
✅ API responds in < 100ms
✅ All endpoints return valid JSON
✅ Web interface displays results correctly
✅ Feature importance shows top contributors
✅ Recommendations are appropriate for risk level

---

*Happy Testing! 🧪*
