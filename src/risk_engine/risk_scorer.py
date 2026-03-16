"""
Risk Scoring Engine
Combines outputs from multiple models into unified risk score
"""

import numpy as np
from typing import Dict, Any, Tuple
from enum import Enum

from ..utils.logger import logger
from ..utils.config import Config


class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RiskScoringEngine:
    """
    Unified risk scoring engine that combines:
    - XGBoost fraud probability
    - LSTM temporal risk
    - Autoencoder anomaly score
    - Graph network risk
    
    Produces:
    - Overall risk score (0-100)
    - Risk level classification
    - Component score breakdown
    """
    
    def __init__(self, config: Config = Config):
        self.config = config
        
        # Weights for ensemble (sum to 1.0)
        self.weights = {
            'xgboost': 0.40,      # Primary classifier
            'lstm': 0.25,          # Temporal patterns
            'autoencoder': 0.20,   # Anomaly detection
            'graph': 0.15          # Network analysis
        }
    
    def calculate_risk_score(
        self,
        xgboost_proba: float,
        lstm_proba: float = None,
        autoencoder_score: float = None,
        graph_score: float = None
    ) -> Dict[str, Any]:
        """
        Calculate unified risk score from component scores
        
        Args:
            xgboost_proba: XGBoost fraud probability (0-1)
            lstm_proba: LSTM fraud probability (0-1, optional)
            autoencoder_score: Autoencoder anomaly score (0-5+, optional)
            graph_score: Graph risk score (0-100, optional)
        
        Returns:
            Dictionary with risk score and breakdown
        """
        # Normalize all scores to 0-1 scale
        xgboost_normalized = xgboost_proba
        
        lstm_normalized = lstm_proba if lstm_proba is not None else xgboost_proba
        
        # Autoencoder: normalize to 0-1 (scores > 1.0 indicate anomaly)
        if autoencoder_score is not None:
            autoencoder_normalized = min(autoencoder_score / 2.0, 1.0)
        else:
            autoencoder_normalized = xgboost_proba
        
        # Graph: already 0-100, normalize to 0-1
        graph_normalized = (graph_score / 100.0) if graph_score is not None else xgboost_proba
        
        # Weighted ensemble
        risk_score_normalized = (
            self.weights['xgboost'] * xgboost_normalized +
            self.weights['lstm'] * lstm_normalized +
            self.weights['autoencoder'] * autoencoder_normalized +
            self.weights['graph'] * graph_normalized
        )
        
        # Convert to 0-100 scale
        risk_score = risk_score_normalized * 100
        
        # Determine risk level
        risk_level = self.get_risk_level(risk_score)
        
        # Confidence score (based on agreement between models)
        confidence = self._calculate_confidence(
            xgboost_normalized,
            lstm_normalized,
            autoencoder_normalized,
            graph_normalized
        )
        
        return {
            'risk_score': float(risk_score),
            'risk_level': risk_level.value,
            'confidence': float(confidence),
            'component_scores': {
                'xgboost_probability': float(xgboost_normalized),
                'lstm_probability': float(lstm_normalized),
                'autoencoder_score': float(autoencoder_normalized),
                'graph_score': float(graph_normalized)
            },
            'weights': self.weights
        }
    
    def get_risk_level(self, risk_score: float) -> RiskLevel:
        """
        Classify risk score into risk level
        
        Args:
            risk_score: Risk score (0-100)
        
        Returns:
            RiskLevel enum
        """
        thresholds = self.config.RISK_THRESHOLDS
        
        if risk_score >= thresholds['critical']:
            return RiskLevel.CRITICAL
        elif risk_score >= thresholds['high']:
            return RiskLevel.HIGH
        elif risk_score >= thresholds['medium']:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _calculate_confidence(
        self,
        xgboost_score: float,
        lstm_score: float,
        autoencoder_score: float,
        graph_score: float
    ) -> float:
        """
        Calculate confidence based on model agreement
        
        High confidence when models agree, low when they disagree
        
        Args:
            Normalized scores from each model (0-1)
        
        Returns:
            Confidence score (0-1)
        """
        scores = [xgboost_score, lstm_score, autoencoder_score, graph_score]
        
        # Calculate standard deviation (low = high agreement)
        std = np.std(scores)
        
        # Convert to confidence (inverse relationship)
        # std = 0 → confidence = 1.0 (perfect agreement)
        # std = 0.5 → confidence = 0.0 (maximum disagreement)
        confidence = max(0, 1.0 - (std * 2))
        
        return confidence
    
    def get_recommendation(
        self,
        risk_score: float,
        risk_level: str
    ) -> Dict[str, Any]:
        """
        Get action recommendation based on risk level
        
        Args:
            risk_score: Risk score (0-100)
            risk_level: Risk level string
        
        Returns:
            Dictionary with recommendations
        """
        recommendations = {
            'Low': {
                'action': 'APPROVE',
                'description': 'Transaction appears legitimate. Process normally.',
                'requires_review': False,
                'auto_block': False
            },
            'Medium': {
                'action': 'REVIEW',
                'description': 'Elevated risk detected. Flag for manual review.',
                'requires_review': True,
                'auto_block': False
            },
            'High': {
                'action': 'CHALLENGE',
                'description': 'High risk detected. Require additional authentication.',
                'requires_review': True,
                'auto_block': False
            },
            'Critical': {
                'action': 'BLOCK',
                'description': 'Critical risk detected. Block transaction immediately.',
                'requires_review': True,
                'auto_block': True
            }
        }
        
        return recommendations.get(risk_level, recommendations['Medium'])
    
    def batch_score(
        self,
        xgboost_probas: np.ndarray,
        lstm_probas: np.ndarray = None,
        autoencoder_scores: np.ndarray = None,
        graph_scores: np.ndarray = None
    ) -> Dict[str, np.ndarray]:
        """
        Calculate risk scores for batch of transactions
        
        Args:
            xgboost_probas: Array of XGBoost probabilities
            lstm_probas: Array of LSTM probabilities (optional)
            autoencoder_scores: Array of autoencoder scores (optional)
            graph_scores: Array of graph scores (optional)
        
        Returns:
            Dictionary with arrays of risk scores and levels
        """
        n_samples = len(xgboost_probas)
        
        # Use XGBoost as fallback for missing models
        if lstm_probas is None:
            lstm_probas = xgboost_probas
        if autoencoder_scores is None:
            autoencoder_scores = xgboost_probas
        if graph_scores is None:
            graph_scores = xgboost_probas * 100
        
        risk_scores = []
        risk_levels = []
        confidences = []
        
        for i in range(n_samples):
            result = self.calculate_risk_score(
                xgboost_probas[i],
                lstm_probas[i],
                autoencoder_scores[i],
                graph_scores[i]
            )
            
            risk_scores.append(result['risk_score'])
            risk_levels.append(result['risk_level'])
            confidences.append(result['confidence'])
        
        return {
            'risk_scores': np.array(risk_scores),
            'risk_levels': np.array(risk_levels),
            'confidences': np.array(confidences)
        }
    
    def update_weights(self, new_weights: Dict[str, float]):
        """
        Update ensemble weights
        
        Args:
            new_weights: Dictionary with new weights (must sum to 1.0)
        """
        if not np.isclose(sum(new_weights.values()), 1.0):
            raise ValueError("Weights must sum to 1.0")
        
        self.weights = new_weights
        logger.info(f"Updated weights: {self.weights}")
    
    def get_risk_distribution(
        self,
        risk_scores: np.ndarray
    ) -> Dict[str, Any]:
        """
        Analyze distribution of risk scores
        
        Args:
            risk_scores: Array of risk scores
        
        Returns:
            Dictionary with distribution statistics
        """
        risk_levels = [self.get_risk_level(score).value for score in risk_scores]
        
        from collections import Counter
        level_counts = Counter(risk_levels)
        
        return {
            'total_transactions': len(risk_scores),
            'mean_risk_score': float(np.mean(risk_scores)),
            'median_risk_score': float(np.median(risk_scores)),
            'std_risk_score': float(np.std(risk_scores)),
            'distribution': {
                'low': level_counts.get('Low', 0),
                'medium': level_counts.get('Medium', 0),
                'high': level_counts.get('High', 0),
                'critical': level_counts.get('Critical', 0)
            },
            'percentage': {
                'low': level_counts.get('Low', 0) / len(risk_scores) * 100,
                'medium': level_counts.get('Medium', 0) / len(risk_scores) * 100,
                'high': level_counts.get('High', 0) / len(risk_scores) * 100,
                'critical': level_counts.get('Critical', 0) / len(risk_scores) * 100
            }
        }
