"""
SHAP-based explainability module
Provides global and local explanations for fraud predictions
"""

import numpy as np
import pandas as pd
import shap
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import joblib

from ..utils.logger import logger
from ..utils.config import Config


class SHAPExplainer:
    """
    SHAP (SHapley Additive exPlanations) for model interpretability
    
    Provides:
    - Global feature importance
    - Local transaction-level explanations
    - Feature contribution analysis
    """
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.explainer = None
        self.expected_value = None
        self.feature_names = None
        self.global_shap_values = None
    
    def initialize_explainer(
        self,
        model_predict_fn,
        X_background: np.ndarray,
        feature_names: List[str],
        model_type: str = 'tree'
    ):
        """
        Initialize SHAP explainer with background data
        
        Args:
            model_predict_fn: Model's predict function
            X_background: Background dataset for SHAP (sample of training data)
            feature_names: List of feature names
            model_type: 'tree' for tree-based models, 'deep' for neural networks
        """
        logger.info(f"Initializing SHAP explainer (type: {model_type})...")
        
        self.feature_names = feature_names
        
        if model_type == 'tree':
            # TreeExplainer for XGBoost, Random Forest, etc.
            self.explainer = shap.TreeExplainer(model_predict_fn)
        else:
            # KernelExplainer for any model (slower but universal)
            # Use subset of background data for efficiency
            background_sample = shap.sample(X_background, min(100, len(X_background)))
            self.explainer = shap.KernelExplainer(model_predict_fn, background_sample)
        
        # Store expected value (baseline prediction)
        if hasattr(self.explainer, 'expected_value'):
            if isinstance(self.explainer.expected_value, np.ndarray):
                self.expected_value = self.explainer.expected_value[0]
            else:
                self.expected_value = self.explainer.expected_value
        
        logger.info("SHAP explainer initialized")
    
    def explain_prediction(
        self,
        X: np.ndarray,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Explain a single prediction
        
        Args:
            X: Single transaction features (1D array or 2D with 1 row)
            top_n: Number of top features to return
        
        Returns:
            Dictionary with explanation
        """
        if self.explainer is None:
            raise ValueError("Explainer not initialized")
        
        # Ensure 2D array
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X)
        
        # Handle different output formats
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Get positive class for binary classification
        
        # Get values for single prediction
        if shap_values.ndim > 1:
            shap_values = shap_values[0]
        
        # Get feature importance (absolute SHAP values)
        abs_shap_values = np.abs(shap_values)
        
        # Get top features
        top_indices = np.argsort(abs_shap_values)[-top_n:][::-1]
        
        top_features = []
        for idx in top_indices:
            top_features.append({
                'feature': self.feature_names[idx] if self.feature_names else f'feature_{idx}',
                'value': float(X[0, idx]),
                'shap_value': float(shap_values[idx]),
                'abs_shap_value': float(abs_shap_values[idx]),
                'impact': 'increases_risk' if shap_values[idx] > 0 else 'decreases_risk'
            })
        
        explanation = {
            'expected_value': float(self.expected_value) if self.expected_value is not None else 0.0,
            'prediction_value': float(self.expected_value + np.sum(shap_values)) if self.expected_value is not None else float(np.sum(shap_values)),
            'top_features': top_features,
            'all_shap_values': shap_values.tolist()
        }
        
        return explanation
    
    def explain_batch(
        self,
        X: np.ndarray,
        max_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Explain batch of predictions (for global analysis)
        
        Args:
            X: Feature matrix
            max_samples: Maximum samples to explain (for performance)
        
        Returns:
            Dictionary with batch explanations
        """
        if self.explainer is None:
            raise ValueError("Explainer not initialized")
        
        logger.info(f"Explaining batch of {min(len(X), max_samples)} predictions...")
        
        # Sample if too many
        if len(X) > max_samples:
            indices = np.random.choice(len(X), max_samples, replace=False)
            X_sample = X[indices]
        else:
            X_sample = X
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X_sample)
        
        # Handle different output formats
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Positive class
        
        # Store for visualization
        self.global_shap_values = shap_values
        
        # Calculate mean absolute SHAP values (global importance)
        mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
        
        # Create feature importance ranking
        feature_importance = []
        for idx in np.argsort(mean_abs_shap)[::-1]:
            feature_importance.append({
                'feature': self.feature_names[idx] if self.feature_names else f'feature_{idx}',
                'mean_abs_shap': float(mean_abs_shap[idx]),
                'mean_shap': float(np.mean(shap_values[:, idx]))
            })
        
        return {
            'feature_importance': feature_importance,
            'num_samples_explained': len(X_sample),
            'shap_values_shape': shap_values.shape
        }
    
    def get_global_importance(
        self,
        X: np.ndarray = None,
        top_n: int = 20
    ) -> Dict[str, float]:
        """
        Get global feature importance
        
        Args:
            X: Feature matrix (if None, use cached shap values)
            top_n: Number of top features to return
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if X is not None:
            self.explain_batch(X)
        
        if self.global_shap_values is None:
            raise ValueError("No SHAP values computed. Run explain_batch first.")
        
        # Calculate mean absolute SHAP values
        mean_abs_shap = np.mean(np.abs(self.global_shap_values), axis=0)
        
        # Get top features
        top_indices = np.argsort(mean_abs_shap)[-top_n:][::-1]
        
        importance = {}
        for idx in top_indices:
            feature_name = self.feature_names[idx] if self.feature_names else f'feature_{idx}'
            importance[feature_name] = float(mean_abs_shap[idx])
        
        return importance
    
    def create_explanation_text(
        self,
        explanation: Dict[str, Any],
        transaction_data: Optional[Dict] = None
    ) -> str:
        """
        Create human-readable explanation text
        
        Args:
            explanation: Explanation dictionary from explain_prediction
            transaction_data: Optional transaction data for context
        
        Returns:
            Human-readable explanation string
        """
        top_features = explanation['top_features'][:5]  # Top 5
        
        text = "🔍 Fraud Prediction Explanation:\n\n"
        
        if transaction_data:
            text += f"Transaction Amount: ${transaction_data.get('Amount', 'N/A')}\n"
            text += f"Risk Score: {transaction_data.get('risk_score', 'N/A'):.2f}/100\n\n"
        
        text += "Top Contributing Factors:\n"
        
        for i, feature in enumerate(top_features, 1):
            impact_emoji = "🔴" if feature['impact'] == 'increases_risk' else "🟢"
            impact_text = "increases" if feature['impact'] == 'increases_risk' else "decreases"
            
            text += f"{i}. {impact_emoji} {feature['feature']}: "
            text += f"Value={feature['value']:.4f}, "
            text += f"Impact={feature['abs_shap_value']:.4f} ({impact_text} fraud risk)\n"
        
        return text
    
    def plot_feature_importance(
        self,
        X: np.ndarray = None,
        save_path: str = None,
        top_n: int = 20
    ):
        """
        Plot global feature importance
        
        Args:
            X: Feature matrix
            save_path: Path to save plot
            top_n: Number of top features to plot
        """
        if X is not None:
            self.explain_batch(X)
        
        if self.global_shap_values is None:
            raise ValueError("No SHAP values computed")
        
        # Create summary plot
        plt.figure(figsize=(12, 8))
        shap.summary_plot(
            self.global_shap_values,
            features=X[:len(self.global_shap_values)] if X is not None else None,
            feature_names=self.feature_names,
            plot_type="bar",
            max_display=top_n,
            show=False
        )
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Feature importance plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def save_explainer(self, path: str = None):
        """Save explainer"""
        if path is None:
            path = self.config.MODEL_DIR / "shap_explainer.pkl"
        
        joblib.dump({
            'expected_value': self.expected_value,
            'feature_names': self.feature_names,
            'global_shap_values': self.global_shap_values
        }, path)
        
        logger.info(f"SHAP explainer saved to {path}")
    
    def load_explainer(self, path: str = None):
        """Load explainer (metadata only, explainer must be reinitialized)"""
        if path is None:
            path = self.config.MODEL_DIR / "shap_explainer.pkl"
        
        data = joblib.load(path)
        self.expected_value = data['expected_value']
        self.feature_names = data['feature_names']
        self.global_shap_values = data.get('global_shap_values')
        
        logger.info(f"SHAP explainer metadata loaded from {path}")
