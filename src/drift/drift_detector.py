"""
Concept drift detection using ADWIN algorithm
"""

import numpy as np
from river import drift
from typing import List, Dict, Any, Optional
import joblib
from datetime import datetime
from collections import deque

from ..utils.logger import logger
from ..utils.config import Config


class ConceptDriftDetector:
    """
    Monitor concept drift in fraud patterns using ADWIN
    
    ADWIN (Adaptive Windowing) automatically detects distribution changes
    in streaming data without prior knowledge of distribution
    """
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.adwin = drift.ADWIN(delta=config.DRIFT_PARAMS['delta'])
        self.drift_detected_count = 0
        self.drift_history = []
        self.prediction_window = deque(maxlen=config.DRIFT_PARAMS['window_size'])
        self.is_monitoring = False
    
    def update(self, fraud_probability: float) -> bool:
        """
        Update drift detector with new prediction
        
        Args:
            fraud_probability: Predicted fraud probability (0-1)
        
        Returns:
            True if drift detected, False otherwise
        """
        # Add to window
        self.prediction_window.append(fraud_probability)
        
        # Update ADWIN
        self.adwin.update(fraud_probability)
        
        # Check if drift detected
        if self.adwin.drift_detected:
            self.drift_detected_count += 1
            drift_info = {
                'timestamp': datetime.now().isoformat(),
                'drift_count': self.drift_detected_count,
                'window_size': len(self.prediction_window),
                'mean_probability': float(np.mean(self.prediction_window)),
                'std_probability': float(np.std(self.prediction_window))
            }
            self.drift_history.append(drift_info)
            
            logger.warning(f"⚠️  Concept drift detected! Count: {self.drift_detected_count}")
            logger.info(f"Drift info: {drift_info}")
            
            return True
        
        return False
    
    def batch_update(self, fraud_probabilities: np.ndarray) -> Dict[str, Any]:
        """
        Update drift detector with batch of predictions
        
        Args:
            fraud_probabilities: Array of fraud probabilities
        
        Returns:
            Dictionary with drift detection results
        """
        logger.info(f"Batch updating drift detector with {len(fraud_probabilities)} predictions...")
        
        drift_detected_positions = []
        
        for i, prob in enumerate(fraud_probabilities):
            if self.update(prob):
                drift_detected_positions.append(i)
        
        results = {
            'total_predictions': len(fraud_probabilities),
            'drift_detected_count': len(drift_detected_positions),
            'drift_positions': drift_detected_positions,
            'total_drifts_overall': self.drift_detected_count
        }
        
        logger.info(f"Drift detection results: {results['drift_detected_count']} drifts in batch")
        
        return results
    
    def get_drift_status(self) -> Dict[str, Any]:
        """
        Get current drift monitoring status
        
        Returns:
            Dictionary with drift status information
        """
        return {
            'is_monitoring': self.is_monitoring,
            'total_drifts_detected': self.drift_detected_count,
            'window_size': len(self.prediction_window),
            'current_mean': float(np.mean(self.prediction_window)) if self.prediction_window else 0,
            'current_std': float(np.std(self.prediction_window)) if self.prediction_window else 0,
            'recent_drifts': self.drift_history[-5:] if self.drift_history else []
        }
    
    def should_retrain(self, threshold: int = 3) -> bool:
        """
        Check if model should be retrained based on drift count
        
        Args:
            threshold: Number of drifts before recommending retrain
        
        Returns:
            True if retraining recommended
        """
        return self.drift_detected_count >= threshold
    
    def reset(self):
        """Reset drift detector"""
        self.adwin = drift.ADWIN(delta=self.config.DRIFT_PARAMS['delta'])
        self.drift_detected_count = 0
        self.drift_history = []
        self.prediction_window.clear()
        logger.info("Drift detector reset")
    
    def save_detector(self, path: str = None):
        """Save drift detector state"""
        if path is None:
            path = self.config.MODEL_DIR / "drift_detector.pkl"
        
        joblib.dump({
            'drift_detected_count': self.drift_detected_count,
            'drift_history': self.drift_history,
            'prediction_window': list(self.prediction_window)
        }, path)
        
        logger.info(f"Drift detector saved to {path}")
    
    def load_detector(self, path: str = None):
        """Load drift detector state"""
        if path is None:
            path = self.config.MODEL_DIR / "drift_detector.pkl"
        
        data = joblib.load(path)
        self.drift_detected_count = data['drift_detected_count']
        self.drift_history = data['drift_history']
        self.prediction_window = deque(data['prediction_window'], 
                                      maxlen=self.config.DRIFT_PARAMS['window_size'])
        
        logger.info(f"Drift detector loaded from {path}")


class PerformanceMonitor:
    """
    Monitor model performance over time
    Track metrics to detect performance degradation
    """
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.predictions = deque(maxlen=window_size)
        self.actuals = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
        self.performance_history = []
    
    def update(self, y_true: int, y_pred: int, y_proba: float):
        """
        Add new prediction result
        
        Args:
            y_true: Actual label
            y_pred: Predicted label
            y_proba: Predicted probability
        """
        self.predictions.append((y_pred, y_proba))
        self.actuals.append(y_true)
        self.timestamps.append(datetime.now())
    
    def get_current_performance(self) -> Dict[str, float]:
        """
        Calculate performance metrics on current window
        
        Returns:
            Dictionary with current performance metrics
        """
        if len(self.actuals) < 10:
            return {}
        
        y_true = np.array(self.actuals)
        y_pred = np.array([p[0] for p in self.predictions])
        y_proba = np.array([p[1] for p in self.predictions])
        
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        metrics = {
            'window_size': len(self.actuals),
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_true, y_pred, zero_division=0)),
            'roc_auc': float(roc_auc_score(y_true, y_proba)) if len(np.unique(y_true)) > 1 else 0
        }
        
        return metrics
    
    def detect_performance_degradation(
        self, 
        baseline_metrics: Dict[str, float],
        threshold: float = 0.1
    ) -> bool:
        """
        Detect if performance has degraded significantly
        
        Args:
            baseline_metrics: Original performance metrics
            threshold: Degradation threshold (e.g., 0.1 = 10% drop)
        
        Returns:
            True if significant degradation detected
        """
        current_metrics = self.get_current_performance()
        
        if not current_metrics:
            return False
        
        # Check key metrics
        key_metrics = ['accuracy', 'f1_score', 'roc_auc']
        
        for metric in key_metrics:
            if metric in baseline_metrics and metric in current_metrics:
                baseline = baseline_metrics[metric]
                current = current_metrics[metric]
                
                if baseline > 0:
                    degradation = (baseline - current) / baseline
                    
                    if degradation > threshold:
                        logger.warning(
                            f"Performance degradation detected in {metric}: "
                            f"{baseline:.4f} → {current:.4f} ({degradation*100:.1f}% drop)"
                        )
                        return True
        
        return False
