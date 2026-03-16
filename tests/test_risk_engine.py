"""
Unit tests for Risk Scoring Engine
"""

import pytest
import numpy as np
from src.risk_engine.risk_scorer import RiskScoringEngine, RiskLevel
from src.utils.config import Config


class TestRiskScoringEngine:
    """Test suite for risk scoring engine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = Config()
        self.engine = RiskScoringEngine(self.config)
    
    def test_calculate_risk_score_all_models(self):
        """Test risk score calculation with all model inputs"""
        result = self.engine.calculate_risk_score(
            xgboost_proba=0.8,
            lstm_proba=0.75,
            autoencoder_score=1.5,
            graph_score=70
        )
        
        assert 'risk_score' in result
        assert 'risk_level' in result
        assert 'confidence' in result
        assert 0 <= result['risk_score'] <= 100
        assert result['risk_level'] in ['Low', 'Medium', 'High', 'Critical']
    
    def test_calculate_risk_score_xgboost_only(self):
        """Test risk score with only XGBoost input"""
        result = self.engine.calculate_risk_score(
            xgboost_proba=0.9
        )
        
        assert result['risk_score'] == 90.0
        assert result['risk_level'] == 'Critical'
    
    def test_get_risk_level_thresholds(self):
        """Test risk level classification"""
        assert self.engine.get_risk_level(10) == RiskLevel.LOW
        assert self.engine.get_risk_level(50) == RiskLevel.MEDIUM
        assert self.engine.get_risk_level(75) == RiskLevel.HIGH
        assert self.engine.get_risk_level(95) == RiskLevel.CRITICAL
    
    def test_confidence_calculation(self):
        """Test confidence based on model agreement"""
        # High agreement (all models agree)
        result1 = self.engine.calculate_risk_score(
            xgboost_proba=0.8,
            lstm_proba=0.8,
            autoencoder_score=1.6,  # Normalized to 0.8
            graph_score=80
        )
        assert result1['confidence'] > 0.8
        
        # Low agreement (models disagree)
        result2 = self.engine.calculate_risk_score(
            xgboost_proba=0.1,
            lstm_proba=0.9,
            autoencoder_score=0.2,
            graph_score=90
        )
        assert result2['confidence'] < 0.5
    
    def test_get_recommendation(self):
        """Test recommendation generation"""
        rec_critical = self.engine.get_recommendation(95, 'Critical')
        assert rec_critical['action'] == 'BLOCK'
        assert rec_critical['auto_block'] == True
        
        rec_low = self.engine.get_recommendation(20, 'Low')
        assert rec_low['action'] == 'APPROVE'
        assert rec_low['requires_review'] == False
    
    def test_batch_score(self):
        """Test batch scoring"""
        n_samples = 10
        xgboost_probas = np.random.rand(n_samples)
        
        result = self.engine.batch_score(xgboost_probas)
        
        assert len(result['risk_scores']) == n_samples
        assert len(result['risk_levels']) == n_samples
        assert len(result['confidences']) == n_samples
    
    def test_update_weights(self):
        """Test weight updating"""
        new_weights = {
            'xgboost': 0.5,
            'lstm': 0.3,
            'autoencoder': 0.1,
            'graph': 0.1
        }
        
        self.engine.update_weights(new_weights)
        assert self.engine.weights == new_weights
    
    def test_update_weights_invalid_sum(self):
        """Test that invalid weights raise error"""
        invalid_weights = {
            'xgboost': 0.5,
            'lstm': 0.3,
            'autoencoder': 0.1,
            'graph': 0.05  # Sum is 0.95, not 1.0
        }
        
        with pytest.raises(ValueError):
            self.engine.update_weights(invalid_weights)
    
    def test_get_risk_distribution(self):
        """Test risk distribution analysis"""
        risk_scores = np.array([10, 25, 45, 70, 90, 95, 15, 35, 65, 85])
        
        dist = self.engine.get_risk_distribution(risk_scores)
        
        assert dist['total_transactions'] == 10
        assert 'distribution' in dist
        assert 'percentage' in dist
        assert sum(dist['distribution'].values()) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
