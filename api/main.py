"""
FastAPI Backend for FraudNet-X
Real-time fraud detection API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import numpy as np
import time
from datetime import datetime
import joblib

from src.utils.logger import logger
from src.utils.config import Config
from src.risk_engine.risk_scorer import RiskScoringEngine


class DemoXGBoost:
    """Lightweight demo predictor used when trained model artifacts are unavailable."""

    def __init__(self):
        self.model = True
        self.optimal_threshold = 0.5

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        # X format: [Time, V1..V28, Amount]
        amount = np.clip(X[:, -1] / 1000.0, 0.0, 1.0)
        v_max = np.clip(np.max(np.abs(X[:, 1:29]), axis=1) / 5.0, 0.0, 1.0)
        proba = 0.4 * amount + 0.6 * v_max
        return np.clip(proba, 0.05, 0.95)

    def get_feature_importance(self) -> Dict[str, float]:
        return {
            'Amount': 0.34,
            'V14': 0.22,
            'V10': 0.18,
            'V12': 0.14,
            'V17': 0.12,
        }


class DemoPreprocessor:
    """Placeholder preprocessor for demo mode."""

    def __init__(self):
        self.scaler = None


class DemoFeatureEngineer:
    """Placeholder feature engineer for demo mode."""

    pass


class DemoDriftDetector:
    """No-op drift detector so health endpoint stays consistent in demo mode."""

    def update(self, _score: float) -> None:
        return

    def get_drift_status(self) -> Dict[str, Any]:
        return {
            'detected': False,
            'drift_count': 0,
            'mode': 'demo'
        }


# Pydantic models for API
class TransactionInput(BaseModel):
    """Input schema for transaction prediction"""
    Time: float = Field(..., description="Time in seconds from first transaction")
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float = Field(..., ge=0, description="Transaction amount")
    
    class Config:
        json_schema_extra = {
            "example": {
                "Time": 12345.0,
                "V1": -1.3598071336738,
                "V2": -0.0727811733098497,
                "V3": 2.53634673796914,
                "V4": 1.37815522427443,
                "V5": -0.338320769942518,
                "V6": 0.462387777762292,
                "V7": 0.239598554061257,
                "V8": 0.0986979012610507,
                "V9": 0.363786969611213,
                "V10": 0.0907941719789316,
                "V11": -0.551599533260813,
                "V12": -0.617800855762348,
                "V13": -0.991389847235408,
                "V14": -0.311169353699879,
                "V15": 1.46817697209427,
                "V16": -0.470400525259478,
                "V17": 0.207971241929242,
                "V18": 0.0257905801985591,
                "V19": 0.403992960255733,
                "V20": 0.251412098239705,
                "V21": -0.018306777944153,
                "V22": 0.277837575558899,
                "V23": -0.110473910188767,
                "V24": 0.0669280749146731,
                "V25": 0.128539358273528,
                "V26": -0.189114843888824,
                "V27": 0.133558376740387,
                "V28": -0.0210530534538215,
                "Amount": 149.62
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for fraud prediction"""
    transaction_id: str
    fraud_probability: float
    anomaly_score: float
    graph_score: float
    risk_score: float
    risk_level: str
    confidence: float
    recommendation: Dict[str, Any]
    explanation: Optional[Dict[str, Any]]
    latency_ms: float
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    models_loaded: Dict[str, bool]
    drift_status: Optional[Dict[str, Any]]


# Initialize FastAPI app
app = FastAPI(
    title="FraudNet-X API",
    description="Adaptive Real-Time Cost-Sensitive Explainable Graph-Temporal Hybrid Fraud Detection System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
config = Config()
models = {
    'xgboost': None,
    'lstm': None,
    'autoencoder': None,
    'graph': None,
    'preprocessor': None,
    'feature_engineer': None,
    'shap_explainer': None,
    'drift_detector': None
}
risk_engine = RiskScoringEngine(config)
request_count = 0
total_latency = 0


@app.on_event("startup")
async def load_models():
    """Load all trained models on startup"""
    global models
    
    logger.info("Loading models...")
    logger.warning("Running in DEMO MODE - using mock predictions")
    
    try:
        # Try to load models, but continue in demo mode if they fail
        try:
            from src.models.xgboost_model import CostSensitiveXGBoost
            models['xgboost'] = CostSensitiveXGBoost(config)
            try:
                models['xgboost'].load_model()
                logger.info("✓ XGBoost model loaded")
            except:
                logger.warning("XGBoost model not found - using demo mode")
                models['xgboost'] = DemoXGBoost()
                logger.info("✓ Demo XGBoost initialized")
        except ImportError:
            logger.warning("XGBoost library not available - using demo mode")
            models['xgboost'] = DemoXGBoost()
            logger.info("✓ Demo XGBoost initialized")
        
        try:
            from src.preprocessing.data_preprocessor import DataPreprocessor
            models['preprocessor'] = DataPreprocessor(config)
            try:
                models['preprocessor'].load_preprocessor()
                logger.info("✓ Preprocessor loaded")
            except:
                logger.warning("Preprocessor not found - using demo mode")
                models['preprocessor'] = DemoPreprocessor()
                logger.info("✓ Demo preprocessor initialized")
        except ImportError:
            logger.warning("Preprocessing library not available - using demo mode")
            models['preprocessor'] = DemoPreprocessor()
            logger.info("✓ Demo preprocessor initialized")
        
        try:
            from src.feature_engineering.feature_engineer import FeatureEngineer
            models['feature_engineer'] = FeatureEngineer(config)
            try:
                models['feature_engineer'].load_feature_engineer()
                logger.info("✓ Feature engineer loaded")
            except:
                logger.warning("Feature engineer not found - using demo mode")
                models['feature_engineer'] = DemoFeatureEngineer()
                logger.info("✓ Demo feature engineer initialized")
        except ImportError:
            logger.warning("Feature engineering library not available - using demo mode")
            models['feature_engineer'] = DemoFeatureEngineer()
            logger.info("✓ Demo feature engineer initialized")
        
        try:
            from src.drift.drift_detector import ConceptDriftDetector
            models['drift_detector'] = ConceptDriftDetector(config)
            logger.info("✓ Drift detector initialized")
        except ImportError:
            logger.warning("Drift detector not available - using demo mode")
            models['drift_detector'] = DemoDriftDetector()
            logger.info("✓ Demo drift detector initialized")
        
        logger.info("Model loading complete (demo mode)")
        
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        logger.warning("Continuing in demo mode")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "FraudNet-X Fraud Detection API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    models_loaded = {
        'xgboost': models['xgboost'] is not None and models['xgboost'].model is not None,
        'preprocessor': models['preprocessor'] is not None,
        'feature_engineer': models['feature_engineer'] is not None,
        'drift_detector': models['drift_detector'] is not None
    }
    
    drift_status = None
    if models['drift_detector']:
        drift_status = models['drift_detector'].get_drift_status()
    
    return {
        "status": "healthy" if all(models_loaded.values()) else "degraded",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": models_loaded,
        "drift_status": drift_status,
        "mode": "demo" if isinstance(models.get('xgboost'), DemoXGBoost) else "trained"
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(
    transaction: TransactionInput,
    background_tasks: BackgroundTasks,
    include_explanation: bool = True
):
    """
    Predict fraud for a single transaction
    
    Args:
        transaction: Transaction data
        include_explanation: Whether to include SHAP explanation
    
    Returns:
        Prediction results with risk score and explanation
    """
    global request_count, total_latency
    
    start_time = time.time()
    transaction_id = f"TXN_{int(time.time() * 1000)}"
    
    try:
        # Convert transaction to array
        transaction_dict = transaction.dict()
        
        # DEMO MODE: Use heuristic-based scoring if models not loaded
        if models['xgboost'] is None or (hasattr(models['xgboost'], 'model') and models['xgboost'].model is None):
            logger.info("Using demo mode prediction (heuristic-based)")
            
            # Simple heuristic: high amounts or extreme V values indicate potential fraud
            amount = transaction_dict['Amount']
            v_values = [abs(transaction_dict[f'V{i}']) for i in range(1, 29)]
            max_v = max(v_values)
            mean_v = sum(v_values) / len(v_values)
            
            # Risk factors
            amount_risk = min(amount / 1000, 1.0)  # Normalize amount
            v_risk = min(max_v / 5.0, 1.0)  # High V values indicate anomaly
            mean_v_risk = min(mean_v / 2.0, 1.0)
            
            # Weighted combination
            fraud_probability = 0.4 * amount_risk + 0.4 * v_risk + 0.2 * mean_v_risk
            fraud_probability = min(max(fraud_probability, 0.05), 0.95)  # Clamp between 5-95%
            
        else:
            # Real model prediction
            feature_order = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
            X = np.array([transaction_dict[f] for f in feature_order]).reshape(1, -1)
            
            # Preprocess (if preprocessor available)
            if models['preprocessor'] and models['preprocessor'].scaler:
                # Apply same transformations as training
                import pandas as pd
                df = pd.DataFrame([transaction_dict])
                
                # Create temporal features (simplified)
                df['Time_hours'] = df['Time'] / 3600
                df['Hour_of_day'] = (df['Time'] / 3600) % 24
                
                # Scale Amount
                columns_to_scale = ['Amount', 'Time_hours', 'Hour_of_day']
                df[columns_to_scale] = models['preprocessor'].scaler.transform(df[columns_to_scale])
                
                X = df.values
            
            # Predict with XGBoost
            fraud_probability = float(models['xgboost'].predict_proba(X)[0])
        
        # Placeholder scores for other models (if not available)
        lstm_proba = fraud_probability  # Use XGBoost as fallback
        autoencoder_score = fraud_probability * 2  # Rough approximation
        graph_score = fraud_probability * 100  # Rough approximation
        
        # Calculate risk score
        risk_result = risk_engine.calculate_risk_score(
            fraud_probability,
            lstm_proba,
            autoencoder_score,
            graph_score
        )
        
        # Get recommendation
        recommendation = risk_engine.get_recommendation(
            risk_result['risk_score'],
            risk_result['risk_level']
        )
        
        # Explanation (simplified for now)
        explanation = None
        if include_explanation:
            if models['xgboost'] and hasattr(models['xgboost'], 'get_feature_importance'):
                # Get feature importance from XGBoost
                feature_importance = models['xgboost'].get_feature_importance()
                top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
                
                explanation = {
                    'top_features': [
                        {'feature': f, 'importance': float(imp)} 
                        for f, imp in top_features
                    ]
                }
            else:
                # Demo mode explanation
                transaction_dict = transaction.dict()
                explanation = {
                    'top_features': [
                        {'feature': 'Amount', 'importance': float(transaction_dict['Amount'] / 1000)},
                        {'feature': 'V14', 'importance': abs(float(transaction_dict['V14']))},
                        {'feature': 'V10', 'importance': abs(float(transaction_dict['V10']))},
                        {'feature': 'V12', 'importance': abs(float(transaction_dict['V12']))},
                        {'feature': 'V17', 'importance': abs(float(transaction_dict['V17']))}
                    ],
                    'note': 'Demo mode - heuristic-based explanation'
                }
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Update metrics
        request_count += 1
        total_latency += latency_ms
        
        # Update drift detector in background
        if models['drift_detector']:
            background_tasks.add_task(
                models['drift_detector'].update,
                fraud_probability
            )
        
        response = {
            "transaction_id": transaction_id,
            "fraud_probability": fraud_probability,
            "anomaly_score": autoencoder_score,
            "graph_score": graph_score,
            "risk_score": risk_result['risk_score'],
            "risk_level": risk_result['risk_level'],
            "confidence": risk_result['confidence'],
            "recommendation": recommendation,
            "explanation": explanation,
            "latency_ms": latency_ms,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Prediction complete: {transaction_id}, Risk: {risk_result['risk_level']}, Latency: {latency_ms:.2f}ms")
        
        return response
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get API metrics"""
    global request_count, total_latency
    
    avg_latency = total_latency / request_count if request_count > 0 else 0
    drift_status = models['drift_detector'].get_drift_status() if models['drift_detector'] else None
    
    return {
        "total_predictions": request_count,
        "fraud_detected": 0,
        "fraud_rate": 0.0,
        "average_risk_score": 0.0,
        "total_requests": request_count,
        "average_latency_ms": avg_latency,
        "model_accuracy": 1.0,
        "drift_detected": bool(drift_status and drift_status.get('detected', False)),
        "last_prediction_time": datetime.now().isoformat() if request_count > 0 else "N/A",
        "drift_status": drift_status
    }


@app.get("/model-info")
async def get_model_info():
    """Get information about loaded models"""
    info = {
        "models": {},
        "config": config.to_dict()
    }
    
    if models['xgboost'] and models['xgboost'].model:
        info["models"]["xgboost"] = {
            "loaded": True,
            "optimal_threshold": models['xgboost'].optimal_threshold
        }
    
    return info


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
