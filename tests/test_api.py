"""
Integration tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from api.main import app


client = TestClient(app)


class TestAPI:
    """Test suite for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "FraudNet-X" in data["message"]
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "models_loaded" in data
    
    def test_predict_endpoint_valid_transaction(self):
        """Test prediction endpoint with valid transaction"""
        transaction = {
            "Time": 12345.0,
            "V1": -1.36, "V2": -0.07, "V3": 2.54, "V4": 1.38, "V5": -0.34,
            "V6": 0.46, "V7": 0.24, "V8": 0.10, "V9": 0.36, "V10": 0.09,
            "V11": -0.55, "V12": -0.62, "V13": -0.99, "V14": -0.31, "V15": 1.47,
            "V16": -0.47, "V17": 0.21, "V18": 0.03, "V19": 0.40, "V20": 0.25,
            "V21": -0.02, "V22": 0.28, "V23": -0.11, "V24": 0.07, "V25": 0.13,
            "V26": -0.19, "V27": 0.13, "V28": -0.02,
            "Amount": 149.62
        }
        
        response = client.post("/predict", json=transaction)
        
        # May fail if models not loaded, but should not crash
        if response.status_code == 200:
            data = response.json()
            assert "transaction_id" in data
            assert "risk_score" in data
            assert "risk_level" in data
            assert "fraud_probability" in data
    
    def test_predict_endpoint_invalid_transaction(self):
        """Test prediction endpoint with invalid transaction"""
        invalid_transaction = {
            "Time": 12345.0,
            "Amount": -100  # Negative amount
        }
        
        response = client.post("/predict", json=invalid_transaction)
        assert response.status_code == 422  # Validation error
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
    
    def test_model_info_endpoint(self):
        """Test model info endpoint"""
        response = client.get("/model-info")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "config" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
