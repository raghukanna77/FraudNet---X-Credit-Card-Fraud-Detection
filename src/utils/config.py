"""
Configuration management for FraudNet-X
"""

import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Central configuration for the fraud detection system"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    MODEL_DIR = BASE_DIR / "models"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Data paths
    RAW_DATA_PATH = DATA_DIR / "creditcard.csv"
    PROCESSED_DATA_PATH = DATA_DIR / "processed"
    
    # Model parameters
    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    VALIDATION_SIZE = 0.2
    
    # SMOTE parameters
    SMOTE_SAMPLING_STRATEGY = 0.5  # Minority to majority ratio
    
    # XGBoost parameters
    XGBOOST_PARAMS = {
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 200,
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'scale_pos_weight': 300,  # Address class imbalance
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': RANDOM_STATE
    }
    
    # LSTM parameters
    LSTM_PARAMS = {
        'sequence_length': 10,
        'lstm_units': 64,
        'dropout': 0.3,
        'epochs': 50,
        'batch_size': 128
    }
    
    # Autoencoder parameters
    AUTOENCODER_PARAMS = {
        'encoding_dim': 16,
        'hidden_layers': [28, 20],
        'epochs': 100,
        'batch_size': 256,
        'contamination': 0.001  # Expected fraud rate
    }
    
    # Graph parameters
    GRAPH_PARAMS = {
        'min_transactions': 2,
        'pagerank_alpha': 0.85,
        'community_resolution': 1.0
    }
    
    # Cost matrix (in dollars)
    COST_MATRIX = {
        'false_negative': 100000,  # Missing a fraud
        'false_positive': 500,      # Blocking legitimate transaction
        'true_positive': -500,      # Correctly catching fraud (saves money - investigation cost)
        'true_negative': 0          # Correctly approving legitimate
    }
    
    # Risk scoring thresholds
    RISK_THRESHOLDS = {
        'low': 30,
        'medium': 60,
        'high': 85,
        'critical': 95
    }
    
    # Drift detection parameters
    DRIFT_PARAMS = {
        'delta': 0.002,  # ADWIN confidence parameter
        'window_size': 1000
    }
    
    # API configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8000))
    API_WORKERS = int(os.getenv('API_WORKERS', 4))
    
    # Feature columns (will be updated after feature engineering)
    FEATURE_COLUMNS = []
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_model_path(cls, model_name: str) -> Path:
        """Get path for a specific model"""
        return cls.MODEL_DIR / f"{model_name}.pkl"
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'xgboost_params': cls.XGBOOST_PARAMS,
            'lstm_params': cls.LSTM_PARAMS,
            'autoencoder_params': cls.AUTOENCODER_PARAMS,
            'graph_params': cls.GRAPH_PARAMS,
            'cost_matrix': cls.COST_MATRIX,
            'risk_thresholds': cls.RISK_THRESHOLDS,
            'drift_params': cls.DRIFT_PARAMS
        }


# Create directories on import
Config.create_directories()
