"""
XGBoost model with cost-sensitive learning
"""

import numpy as np
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold
from typing import Dict, Any, Tuple
import joblib

from ..utils.logger import logger
from ..utils.config import Config
from ..utils.metrics import MetricsCalculator


class CostSensitiveXGBoost:
    """
    XGBoost classifier with cost-sensitive learning
    Uses custom weights and threshold optimization
    """
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.model = None
        self.optimal_threshold = 0.5
        self.metrics_calculator = MetricsCalculator(config.COST_MATRIX)
        self.cv_scores = []
    
    def calculate_sample_weights(self, y: np.ndarray) -> np.ndarray:
        """
        Calculate sample weights based on cost matrix
        
        Args:
            y: Target labels
        
        Returns:
            Array of sample weights
        """
        weights = np.ones(len(y))
        
        # Weight Class 1 (fraud) higher based on cost ratio
        cost_ratio = (
            self.config.COST_MATRIX['false_negative'] / 
            self.config.COST_MATRIX['false_positive']
        )
        
        weights[y == 1] = cost_ratio
        
        return weights
    
    def train(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None,
        use_cv: bool = False,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        Train XGBoost model with cost-sensitive learning
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
            use_cv: Whether to use cross-validation
            cv_folds: Number of cross-validation folds
        
        Returns:
            Dictionary with training metrics
        """
        logger.info("Training Cost-Sensitive XGBoost model...")
        
        # Calculate sample weights
        sample_weights = self.calculate_sample_weights(y_train)
        
        # Create DMatrix with weights
        dtrain = xgb.DMatrix(X_train, label=y_train, weight=sample_weights)
        
        # Prepare validation set if provided
        evals = []
        if X_val is not None and y_val is not None:
            dval = xgb.DMatrix(X_val, label=y_val)
            evals = [(dtrain, 'train'), (dval, 'val')]
        else:
            evals = [(dtrain, 'train')]
        
        # Train model
        self.model = xgb.train(
            self.config.XGBOOST_PARAMS,
            dtrain,
            num_boost_round=self.config.XGBOOST_PARAMS['n_estimators'],
            evals=evals,
            early_stopping_rounds=20,
            verbose_eval=50
        )
        
        logger.info("Model training complete")
        
        # Optimize threshold on validation set
        if X_val is not None and y_val is not None:
            y_val_proba = self.predict_proba(X_val)
            self.optimal_threshold, metrics = self.metrics_calculator.optimize_threshold(
                y_val, y_val_proba, metric='cost'
            )
            logger.info(f"Optimal threshold: {self.optimal_threshold:.4f}")
            return metrics
        
        # If using cross-validation
        if use_cv:
            return self.cross_validate(X_train, y_train, cv_folds)
        
        return {}
    
    def cross_validate(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        Perform stratified k-fold cross-validation
        
        Args:
            X: Features
            y: Labels
            cv_folds: Number of folds
        
        Returns:
            Dictionary with cross-validation metrics
        """
        logger.info(f"Performing {cv_folds}-fold cross-validation...")
        
        skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.config.RANDOM_STATE)
        
        cv_metrics = []
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
            logger.info(f"Training fold {fold}/{cv_folds}...")
            
            X_train_fold = X[train_idx]
            y_train_fold = y[train_idx]
            X_val_fold = X[val_idx]
            y_val_fold = y[val_idx]
            
            # Calculate sample weights
            sample_weights = self.calculate_sample_weights(y_train_fold)
            
            # Train on fold
            dtrain = xgb.DMatrix(X_train_fold, label=y_train_fold, weight=sample_weights)
            dval = xgb.DMatrix(X_val_fold, label=y_val_fold)
            
            model = xgb.train(
                self.config.XGBOOST_PARAMS,
                dtrain,
                num_boost_round=self.config.XGBOOST_PARAMS['n_estimators'],
                evals=[(dval, 'val')],
                early_stopping_rounds=20,
                verbose_eval=False
            )
            
            # Predict and evaluate
            y_val_proba = model.predict(dval)
            y_val_pred = (y_val_proba >= 0.5).astype(int)
            
            fold_metrics = self.metrics_calculator.calculate_all_metrics(
                y_val_fold, y_val_pred, y_val_proba
            )
            cv_metrics.append(fold_metrics)
            
            logger.info(f"Fold {fold} - AUC: {fold_metrics['roc_auc']:.4f}, "
                       f"F1: {fold_metrics['f1_score']:.4f}")
        
        # Calculate average metrics
        avg_metrics = {
            'cv_auc_mean': np.mean([m['roc_auc'] for m in cv_metrics]),
            'cv_auc_std': np.std([m['roc_auc'] for m in cv_metrics]),
            'cv_f1_mean': np.mean([m['f1_score'] for m in cv_metrics]),
            'cv_f1_std': np.std([m['f1_score'] for m in cv_metrics]),
            'cv_precision_mean': np.mean([m['precision'] for m in cv_metrics]),
            'cv_recall_mean': np.mean([m['recall'] for m in cv_metrics]),
        }
        
        self.cv_scores = cv_metrics
        
        logger.info(f"Cross-validation complete:")
        logger.info(f"  Mean AUC: {avg_metrics['cv_auc_mean']:.4f} ± {avg_metrics['cv_auc_std']:.4f}")
        logger.info(f"  Mean F1:  {avg_metrics['cv_f1_mean']:.4f} ± {avg_metrics['cv_f1_std']:.4f}")
        
        return avg_metrics
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict fraud probability
        
        Args:
            X: Features
        
        Returns:
            Array of fraud probabilities
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        dmatrix = xgb.DMatrix(X)
        return self.model.predict(dmatrix)
    
    def predict(self, X: np.ndarray, use_optimal_threshold: bool = True) -> np.ndarray:
        """
        Predict fraud labels
        
        Args:
            X: Features
            use_optimal_threshold: Whether to use optimized threshold
        
        Returns:
            Array of predictions (0 or 1)
        """
        proba = self.predict_proba(X)
        threshold = self.optimal_threshold if use_optimal_threshold else 0.5
        return (proba >= threshold).astype(int)
    
    def get_feature_importance(self, feature_names: list = None) -> Dict[str, float]:
        """
        Get feature importance scores
        
        Args:
            feature_names: List of feature names
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        importance = self.model.get_score(importance_type='gain')
        
        if feature_names:
            # Map f0, f1, ... to actual feature names
            importance_named = {}
            for key, value in importance.items():
                feature_idx = int(key.replace('f', ''))
                if feature_idx < len(feature_names):
                    importance_named[feature_names[feature_idx]] = value
            return importance_named
        
        return importance
    
    def save_model(self, path: str = None):
        """Save trained model"""
        if path is None:
            path = self.config.MODEL_DIR / "xgboost_model.pkl"
        
        joblib.dump({
            'model': self.model,
            'optimal_threshold': self.optimal_threshold,
            'cv_scores': self.cv_scores
        }, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str = None):
        """Load saved model"""
        if path is None:
            path = self.config.MODEL_DIR / "xgboost_model.pkl"
        
        data = joblib.load(path)
        self.model = data['model']
        self.optimal_threshold = data['optimal_threshold']
        self.cv_scores = data.get('cv_scores', [])
        logger.info(f"Model loaded from {path}")
