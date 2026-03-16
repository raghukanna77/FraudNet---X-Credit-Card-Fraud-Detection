"""
Quick inference script for testing trained models
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).parent))

from src.models.xgboost_model import CostSensitiveXGBoost
from src.risk_engine.risk_scorer import RiskScoringEngine
from src.utils.config import Config
from src.utils.logger import logger


def predict_sample_transaction():
    """Test prediction on a sample transaction"""
    
    logger.info("Loading trained models...")
    
    # Load XGBoost model
    xgboost_model = CostSensitiveXGBoost()
    try:
        xgboost_model.load_model()
        logger.info("✓ XGBoost model loaded")
    except:
        logger.error("✗ XGBoost model not found. Please train first.")
        return
    
    # Create sample transaction (random features)
    logger.info("\nGenerating sample transaction...")
    
    sample_transaction = {
        'Time': 12345.0,
        'Amount': 149.62
    }
    
    # Add V features (random for demo)
    for i in range(1, 29):
        sample_transaction[f'V{i}'] = np.random.randn()
    
    # Convert to array
    feature_order = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
    X = np.array([sample_transaction[f] for f in feature_order]).reshape(1, -1)
    
    # Predict
    logger.info("Making prediction...")
    fraud_probability = float(xgboost_model.predict_proba(X)[0])
    fraud_label = int(xgboost_model.predict(X, use_optimal_threshold=True)[0])
    
    # Calculate risk score
    risk_engine = RiskScoringEngine()
    risk_result = risk_engine.calculate_risk_score(fraud_probability)
    
    # Display results
    print("\n" + "="*60)
    print("PREDICTION RESULTS")
    print("="*60)
    print(f"\nTransaction Amount: ${sample_transaction['Amount']:.2f}")
    print(f"\nFraud Probability: {fraud_probability:.2%}")
    print(f"Fraud Prediction:  {'🔴 FRAUD' if fraud_label == 1 else '🟢 LEGITIMATE'}")
    print(f"\nRisk Score:        {risk_result['risk_score']:.2f}/100")
    print(f"Risk Level:        {risk_result['risk_level']}")
    print(f"Confidence:        {risk_result['confidence']:.2%}")
    
    recommendation = risk_engine.get_recommendation(
        risk_result['risk_score'],
        risk_result['risk_level']
    )
    
    print(f"\nRecommendation:    {recommendation['action']}")
    print(f"Description:       {recommendation['description']}")
    print("="*60)


if __name__ == "__main__":
    predict_sample_transaction()
