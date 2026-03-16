"""
LSTM model for temporal sequential fraud detection
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from typing import Dict, Any, Tuple
import joblib

from ..utils.logger import logger
from ..utils.config import Config


class LSTMFraudDetector:
    """
    LSTM-based model for capturing temporal patterns in user transaction sequences
    Learns sequential behavioral patterns to detect anomalous transaction sequences
    """
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.model = None
        self.input_shape = None
        self.history = None
    
    def build_model(self, input_shape: Tuple[int, int]) -> Model:
        """
        Build LSTM architecture for fraud detection
        
        Architecture:
        - LSTM layers to capture temporal dependencies
        - Dropout for regularization
        - Dense layers for classification
        
        Args:
            input_shape: (sequence_length, n_features)
        
        Returns:
            Compiled Keras model
        """
        logger.info(f"Building LSTM model with input shape: {input_shape}")
        
        self.input_shape = input_shape
        
        # Input layer
        inputs = keras.Input(shape=input_shape)
        
        # First LSTM layer (return sequences for stacking)
        x = layers.LSTM(
            self.config.LSTM_PARAMS['lstm_units'],
            return_sequences=True,
            name='lstm_1'
        )(inputs)
        x = layers.Dropout(self.config.LSTM_PARAMS['dropout'])(x)
        
        # Second LSTM layer
        x = layers.LSTM(
            self.config.LSTM_PARAMS['lstm_units'] // 2,
            return_sequences=False,
            name='lstm_2'
        )(x)
        x = layers.Dropout(self.config.LSTM_PARAMS['dropout'])(x)
        
        # Dense layers
        x = layers.Dense(32, activation='relu', name='dense_1')(x)
        x = layers.Dropout(0.2)(x)
        
        x = layers.Dense(16, activation='relu', name='dense_2')(x)
        
        # Output layer
        outputs = layers.Dense(1, activation='sigmoid', name='output')(x)
        
        # Create model
        model = Model(inputs=inputs, outputs=outputs, name='LSTM_Fraud_Detector')
        
        # Compile with class weights consideration
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=[
                'accuracy',
                keras.metrics.Precision(name='precision'),
                keras.metrics.Recall(name='recall'),
                keras.metrics.AUC(name='auc')
            ]
        )
        
        logger.info("Model architecture:")
        model.summary(print_fn=logger.info)
        
        return model
    
    def calculate_class_weights(self, y: np.ndarray) -> Dict[int, float]:
        """
        Calculate class weights to handle imbalance
        
        Args:
            y: Target labels
        
        Returns:
            Dictionary of class weights
        """
        n_samples = len(y)
        n_classes = 2
        
        # Count samples per class
        n_positive = np.sum(y == 1)
        n_negative = np.sum(y == 0)
        
        # Calculate weights
        weight_for_0 = n_samples / (n_classes * n_negative)
        weight_for_1 = n_samples / (n_classes * n_positive)
        
        # Apply cost-sensitive scaling
        cost_ratio = (
            self.config.COST_MATRIX['false_negative'] / 
            self.config.COST_MATRIX['false_positive']
        )
        weight_for_1 *= (cost_ratio / 100)  # Scale down for numerical stability
        
        class_weights = {0: weight_for_0, 1: weight_for_1}
        
        logger.info(f"Class weights: {class_weights}")
        
        return class_weights
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None
    ) -> Dict[str, Any]:
        """
        Train LSTM model
        
        Args:
            X_train: Training sequences (n_samples, sequence_length, n_features)
            y_train: Training labels
            X_val: Validation sequences (optional)
            y_val: Validation labels (optional)
        
        Returns:
            Dictionary with training history
        """
        logger.info("Training LSTM model...")
        logger.info(f"Training data shape: {X_train.shape}")
        logger.info(f"Fraud rate: {np.mean(y_train):.4f}")
        
        # Build model if not already built
        if self.model is None:
            input_shape = (X_train.shape[1], X_train.shape[2])
            self.model = self.build_model(input_shape)
        
        # Calculate class weights
        class_weights = self.calculate_class_weights(y_train)
        
        # Prepare validation data
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss' if validation_data else 'loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss' if validation_data else 'loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
                verbose=1
            )
        ]
        
        # Train model
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=self.config.LSTM_PARAMS['epochs'],
            batch_size=self.config.LSTM_PARAMS['batch_size'],
            class_weight=class_weights,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("LSTM training complete")
        
        # Return training history
        return {
            'history': self.history.history,
            'final_train_loss': self.history.history['loss'][-1],
            'final_train_auc': self.history.history['auc'][-1],
            'final_val_loss': self.history.history['val_loss'][-1] if validation_data else None,
            'final_val_auc': self.history.history['val_auc'][-1] if validation_data else None
        }
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict fraud probability for sequences
        
        Args:
            X: Input sequences
        
        Returns:
            Array of fraud probabilities
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        predictions = self.model.predict(X, verbose=0)
        return predictions.flatten()
    
    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """
        Predict fraud labels for sequences
        
        Args:
            X: Input sequences
            threshold: Classification threshold
        
        Returns:
            Array of predictions (0 or 1)
        """
        proba = self.predict_proba(X)
        return (proba >= threshold).astype(int)
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model on test data
        
        Args:
            X: Test sequences
            y: Test labels
        
        Returns:
            Dictionary with evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        logger.info("Evaluating LSTM model...")
        
        results = self.model.evaluate(X, y, verbose=0, return_dict=True)
        
        logger.info(f"Test Loss: {results['loss']:.4f}")
        logger.info(f"Test AUC: {results['auc']:.4f}")
        logger.info(f"Test Accuracy: {results['accuracy']:.4f}")
        
        return results
    
    def save_model(self, path: str = None):
        """Save trained model"""
        if path is None:
            path = self.config.MODEL_DIR / "lstm_model.h5"
        
        if self.model is not None:
            self.model.save(path)
            
            # Save history separately
            history_path = str(path).replace('.h5', '_history.pkl')
            joblib.dump(self.history.history if self.history else {}, history_path)
            
            logger.info(f"LSTM model saved to {path}")
    
    def load_model(self, path: str = None):
        """Load saved model"""
        if path is None:
            path = self.config.MODEL_DIR / "lstm_model.h5"
        
        self.model = keras.models.load_model(path)
        
        # Load history
        history_path = str(path).replace('.h5', '_history.pkl')
        try:
            history_dict = joblib.load(history_path)
            logger.info(f"LSTM model loaded from {path}")
        except:
            logger.warning("Could not load training history")
