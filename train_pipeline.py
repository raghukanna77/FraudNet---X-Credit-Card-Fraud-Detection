# Training pipeline script
# End-to-end model training

import sys
from pathlib import Path
import argparse

sys.path.append(str(Path(__file__).parent))

from src.preprocessing.data_preprocessor import DataPreprocessor
from src.feature_engineering.feature_engineer import FeatureEngineer, SequenceGenerator
from src.models.xgboost_model import CostSensitiveXGBoost
from src.models.lstm_model import LSTMFraudDetector
from src.models.autoencoder_model import AutoencoderAnomalyDetector
from src.graph.graph_detector import GraphFraudDetector
from src.explainability.shap_explainer import SHAPExplainer
from src.utils.config import Config
from src.utils.logger import logger
from src.utils.metrics import MetricsCalculator

import pandas as pd
import numpy as np


def train_pipeline(data_path: str, use_cv: bool = False):
    """
    Complete training pipeline
    
    Args:
        data_path: Path to credit card data CSV
        use_cv: Whether to use cross-validation
    """
    logger.info("="*60)
    logger.info("FraudNet-X Training Pipeline")
    logger.info("="*60)
    
    config = Config()
    
    # Step 1: Preprocessing
    logger.info("\n--- STEP 1: Data Preprocessing ---")
    preprocessor = DataPreprocessor(config)
    data = preprocessor.preprocess_pipeline(data_path, apply_smote=True)
    
    X_train = data['X_train']
    y_train = data['y_train']
    X_val = data['X_val']
    y_val = data['y_val']
    X_test = data['X_test']
    y_test = data['y_test']
    
    preprocessor.save_preprocessor()
    
    # Step 2: Feature Engineering
    logger.info("\n--- STEP 2: Feature Engineering ---")
    feature_engineer = FeatureEngineer(config)
    
    # Load original data for feature engineering
    df = preprocessor.load_data(data_path)
    df = preprocessor.clean_data(df)
    df = preprocessor.create_temporal_features(df)
    
    # Engineer features
    df_engineered = feature_engineer.engineer_features(df, fit_mode=True)
    feature_engineer.save_feature_engineer()
    
    # Step 3: Train XGBoost
    logger.info("\n--- STEP 3: Training XGBoost ---")
    xgboost_model = CostSensitiveXGBoost(config)
    xgb_metrics = xgboost_model.train(X_train, y_train, X_val, y_val, use_cv=use_cv)
    xgboost_model.save_model()
    
    # Evaluate XGBoost
    metrics_calc = MetricsCalculator(config.COST_MATRIX)
    y_pred = xgboost_model.predict(X_test, use_optimal_threshold=True)
    y_proba = xgboost_model.predict_proba(X_test)
    xgb_test_metrics = metrics_calc.calculate_all_metrics(y_test, y_pred, y_proba)
    metrics_calc.print_metrics_report(xgb_test_metrics, "XGBoost Test Results")
    
    # Step 4: Train LSTM (if enough sequences)
    logger.info("\n--- STEP 4: Training LSTM ---")
    try:
        sequence_gen = SequenceGenerator(config.LSTM_PARAMS['sequence_length'])
        
        # Create sequences from engineered data
        feature_cols = [col for col in df_engineered.columns if col not in ['Class', 'user_id']]
        
        # Split data back to train/val/test
        train_df, val_df, test_df = preprocessor.split_data(df_engineered)
        
        X_train_seq, y_train_seq = sequence_gen.create_sequences(train_df, feature_cols)
        X_val_seq, y_val_seq = sequence_gen.create_sequences(val_df, feature_cols)
        
        lstm_model = LSTMFraudDetector(config)
        lstm_metrics = lstm_model.train(X_train_seq, y_train_seq, X_val_seq, y_val_seq)
        lstm_model.save_model()
        
        logger.info("LSTM training complete")
    except Exception as e:
        logger.warning(f"LSTM training failed: {e}")
    
    # Step 5: Train Autoencoder
    logger.info("\n--- STEP 5: Training Autoencoder ---")
    autoencoder = AutoencoderAnomalyDetector(config)
    
    # Train only on legitimate transactions
    X_train_legit = X_train[y_train == 0]
    X_val_legit = X_val[y_val == 0]
    
    ae_metrics = autoencoder.train(X_train_legit, X_val_legit)
    autoencoder.save_model()
    
    # Evaluate autoencoder
    ae_test_metrics = autoencoder.evaluate(X_test, y_test)
    logger.info(f"Autoencoder Test AUC: {ae_test_metrics['roc_auc']:.4f}")
    
    # Step 6: Build Graph
    logger.info("\n--- STEP 6: Building Transaction Graph ---")
    graph_detector = GraphFraudDetector(config)
    graph_detector.fit(df_engineered)
    graph_detector.save_graph()
    
    graph_stats = graph_detector.get_graph_statistics()
    logger.info(f"Graph Statistics: {graph_stats}")
    
    # Step 7: SHAP Explainability
    logger.info("\n--- STEP 7: SHAP Explainability ---")
    shap_explainer = SHAPExplainer(config)
    
    # Initialize with XGBoost model
    def predict_fn(X):
        return xgboost_model.predict_proba(X)
    
    # Use sample of training data as background
    background_sample = X_train[:100]
    shap_explainer.initialize_explainer(
        xgboost_model.model,
        background_sample,
        data['feature_columns'],
        model_type='tree'
    )
    
    # Calculate global importance
    shap_explainer.explain_batch(X_test[:200])
    shap_explainer.save_explainer()
    
    importance = shap_explainer.get_global_importance(top_n=10)
    logger.info("Top 10 Features by SHAP:")
    for feature, score in list(importance.items())[:10]:
        logger.info(f"  {feature}: {score:.4f}")
    
    # Final Summary
    logger.info("\n" + "="*60)
    logger.info("Training Complete!")
    logger.info("="*60)
    logger.info(f"Test Accuracy:  {xgb_test_metrics['accuracy']:.4f}")
    logger.info(f"Test Precision: {xgb_test_metrics['precision']:.4f}")
    logger.info(f"Test Recall:    {xgb_test_metrics['recall']:.4f}")
    logger.info(f"Test F1:        {xgb_test_metrics['f1_score']:.4f}")
    logger.info(f"Test ROC-AUC:   {xgb_test_metrics['roc_auc']:.4f}")
    logger.info(f"Total Cost:     ${xgb_test_metrics['financial_cost']['total_cost']:,.2f}")
    logger.info("="*60)
    
    logger.info("\nAll models saved! Ready for inference.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train FraudNet-X models")
    parser.add_argument(
        "--data",
        type=str,
        default="data/creditcard.csv",
        help="Path to credit card data CSV"
    )
    parser.add_argument(
        "--cv",
        action="store_true",
        help="Use cross-validation"
    )
    
    args = parser.parse_args()
    
    train_pipeline(args.data, args.cv)
