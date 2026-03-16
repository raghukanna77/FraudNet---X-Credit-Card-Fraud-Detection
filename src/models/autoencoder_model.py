"""
Autoencoder for anomaly detection
Trained only on legitimate transactions to detect anomalies
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import EarlyStopping
from typing import Dict, Any, Tuple
import joblib

from ..utils.logger import logger
from ..utils.config import Config


class AutoencoderAnomalyDetector:
    """
    Autoencoder trained on legitimate transactions only
    Uses reconstruction error as anomaly score
    
    Principle: Normal transactions should reconstruct well,
              Fraudulent transactions should have high reconstruction error
    """
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.model = None
        self.threshold = None
        self.history = None
    
    def build_model(self, input_dim: int) -> Model:
        """
        Build autoencoder architecture
        
        Architecture:
        - Encoder: progressively compress input
        - Bottleneck: compressed representation
        - Decoder: reconstruct input from bottleneck
        
        Args:
            input_dim: Number of input features
        
        Returns:
            Compiled Keras model
        """
        logger.info(f"Building Autoencoder with input dim: {input_dim}")
        
        encoding_dim = self.config.AUTOENCODER_PARAMS['encoding_dim']
        hidden_layers = self.config.AUTOENCODER_PARAMS['hidden_layers']
        
        # Input layer
        input_layer = keras.Input(shape=(input_dim,))
        
        # Encoder
        encoded = input_layer
        for i, units in enumerate(hidden_layers):
            encoded = layers.Dense(units, activation='relu', name=f'encoder_{i}')(encoded)
            encoded = layers.Dropout(0.2)(encoded)
        
        # Bottleneck
        encoded = layers.Dense(encoding_dim, activation='relu', name='bottleneck')(encoded)
        
        # Decoder (mirror of encoder)
        decoded = encoded
        for i, units in enumerate(reversed(hidden_layers)):
            decoded = layers.Dense(units, activation='relu', name=f'decoder_{i}')(decoded)
            decoded = layers.Dropout(0.2)(decoded)
        
        # Output layer (reconstruct input)
        decoded = layers.Dense(input_dim, activation='linear', name='output')(decoded)
        
        # Create autoencoder model
        autoencoder = Model(inputs=input_layer, outputs=decoded, name='Autoencoder')
        
        # Compile with MSE loss (reconstruction error)
        autoencoder.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        logger.info("Autoencoder architecture:")
        autoencoder.summary(print_fn=logger.info)
        
        return autoencoder
    
    def train(
        self,
        X_train_legitimate: np.ndarray,
        X_val_legitimate: np.ndarray = None,
        contamination: float = None
    ) -> Dict[str, Any]:
        """
        Train autoencoder ONLY on legitimate transactions
        
        Args:
            X_train_legitimate: Training data (legitimate transactions only)
            X_val_legitimate: Validation data (legitimate transactions only)
            contamination: Expected fraud rate for threshold setting
        
        Returns:
            Dictionary with training metrics
        """
        logger.info("Training Autoencoder on legitimate transactions only...")
        logger.info(f"Training samples: {X_train_legitimate.shape[0]}")
        
        # Build model if not already built
        if self.model is None:
            input_dim = X_train_legitimate.shape[1]
            self.model = self.build_model(input_dim)
        
        # Prepare validation data
        validation_data = None
        if X_val_legitimate is not None:
            validation_data = (X_val_legitimate, X_val_legitimate)
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss' if validation_data else 'loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            )
        ]
        
        # Train autoencoder (input = output for autoencoders)
        self.history = self.model.fit(
            X_train_legitimate, X_train_legitimate,
            validation_data=validation_data,
            epochs=self.config.AUTOENCODER_PARAMS['epochs'],
            batch_size=self.config.AUTOENCODER_PARAMS['batch_size'],
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("Autoencoder training complete")
        
        # Set anomaly threshold based on training reconstruction errors
        train_reconstruction_errors = self.get_reconstruction_error(X_train_legitimate)
        
        if contamination is None:
            contamination = self.config.AUTOENCODER_PARAMS['contamination']
        
        # Set threshold at percentile based on expected contamination
        percentile = 100 * (1 - contamination)
        self.threshold = np.percentile(train_reconstruction_errors, percentile)
        
        logger.info(f"Anomaly threshold set to: {self.threshold:.6f}")
        logger.info(f"Mean reconstruction error (legitimate): {np.mean(train_reconstruction_errors):.6f}")
        
        return {
            'history': self.history.history,
            'final_train_loss': self.history.history['loss'][-1],
            'final_val_loss': self.history.history['val_loss'][-1] if validation_data else None,
            'threshold': self.threshold,
            'mean_reconstruction_error': float(np.mean(train_reconstruction_errors)),
            'std_reconstruction_error': float(np.std(train_reconstruction_errors))
        }
    
    def get_reconstruction_error(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate reconstruction error (MSE) for each sample
        
        Args:
            X: Input features
        
        Returns:
            Array of reconstruction errors
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Reconstruct input
        X_reconstructed = self.model.predict(X, verbose=0)
        
        # Calculate MSE for each sample
        reconstruction_errors = np.mean(np.square(X - X_reconstructed), axis=1)
        
        return reconstruction_errors
    
    def get_anomaly_score(self, X: np.ndarray) -> np.ndarray:
        """
        Get normalized anomaly score (0-1 scale)
        
        Args:
            X: Input features
        
        Returns:
            Array of anomaly scores
        """
        reconstruction_errors = self.get_reconstruction_error(X)
        
        # Normalize to 0-1 scale using threshold
        # Score > 1.0 means highly anomalous
        anomaly_scores = reconstruction_errors / (self.threshold + 1e-10)
        
        # Clip to reasonable range
        anomaly_scores = np.clip(anomaly_scores, 0, 5)
        
        return anomaly_scores
    
    def predict(self, X: np.ndarray, threshold: float = None) -> np.ndarray:
        """
        Predict anomalies based on reconstruction error
        
        Args:
            X: Input features
            threshold: Custom threshold (if None, use fitted threshold)
        
        Returns:
            Array of predictions (0=legitimate, 1=anomaly)
        """
        if threshold is None:
            if self.threshold is None:
                raise ValueError("Threshold not set. Train the model first or provide threshold.")
            threshold = self.threshold
        
        reconstruction_errors = self.get_reconstruction_error(X)
        predictions = (reconstruction_errors > threshold).astype(int)
        
        return predictions
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, Any]:
        """
        Evaluate autoencoder's anomaly detection performance
        
        Args:
            X_test: Test features
            y_test: Test labels (0=legitimate, 1=fraud)
        
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Evaluating Autoencoder...")
        
        # Get reconstruction errors
        reconstruction_errors = self.get_reconstruction_error(X_test)
        
        # Separate by class
        legit_errors = reconstruction_errors[y_test == 0]
        fraud_errors = reconstruction_errors[y_test == 1]
        
        # Predict anomalies
        predictions = self.predict(X_test)
        
        # Calculate metrics
        from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
        
        metrics = {
            'mean_reconstruction_error_legitimate': float(np.mean(legit_errors)),
            'mean_reconstruction_error_fraud': float(np.mean(fraud_errors)),
            'std_reconstruction_error_legitimate': float(np.std(legit_errors)),
            'std_reconstruction_error_fraud': float(np.std(fraud_errors)),
            'threshold': float(self.threshold),
            'precision': float(precision_score(y_test, predictions, zero_division=0)),
            'recall': float(recall_score(y_test, predictions, zero_division=0)),
            'f1_score': float(f1_score(y_test, predictions, zero_division=0)),
            'roc_auc': float(roc_auc_score(y_test, reconstruction_errors))
        }
        
        logger.info(f"Reconstruction error (Legitimate): {metrics['mean_reconstruction_error_legitimate']:.6f}")
        logger.info(f"Reconstruction error (Fraud):      {metrics['mean_reconstruction_error_fraud']:.6f}")
        logger.info(f"AUC: {metrics['roc_auc']:.4f}")
        
        return metrics
    
    def save_model(self, path: str = None):
        """Save trained model"""
        if path is None:
            path = self.config.MODEL_DIR / "autoencoder_model.h5"
        
        if self.model is not None:
            self.model.save(path)
            
            # Save threshold and metadata
            metadata_path = str(path).replace('.h5', '_metadata.pkl')
            joblib.dump({
                'threshold': self.threshold,
                'history': self.history.history if self.history else {}
            }, metadata_path)
            
            logger.info(f"Autoencoder saved to {path}")
    
    def load_model(self, path: str = None):
        """Load saved model"""
        if path is None:
            path = self.config.MODEL_DIR / "autoencoder_model.h5"
        
        self.model = keras.models.load_model(path)
        
        # Load metadata
        metadata_path = str(path).replace('.h5', '_metadata.pkl')
        try:
            metadata = joblib.load(metadata_path)
            self.threshold = metadata['threshold']
            logger.info(f"Autoencoder loaded from {path}")
            logger.info(f"Threshold: {self.threshold}")
        except:
            logger.warning("Could not load metadata. Threshold not set.")
