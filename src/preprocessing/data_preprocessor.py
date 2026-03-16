"""
Data preprocessing module with strict data leakage prevention
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from typing import Tuple, Dict, Any
import joblib

from ..utils.logger import logger
from ..utils.config import Config


class DataPreprocessor:
    """
    Handles data loading, cleaning, and preprocessing with leakage prevention
    
    Key principle: Split FIRST, then apply SMOTE and scaling ONLY on training data
    """
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.smote = SMOTE(
            sampling_strategy=config.SMOTE_SAMPLING_STRATEGY,
            random_state=config.RANDOM_STATE
        )
    
    def load_data(self, file_path: str = None) -> pd.DataFrame:
        """
        Load credit card transaction data
        
        Args:
            file_path: Path to CSV file. If None, uses config path
        
        Returns:
            DataFrame with transaction data
        """
        if file_path is None:
            file_path = self.config.RAW_DATA_PATH
        
        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)
        
        logger.info(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        logger.info(f"Fraud cases: {df['Class'].sum()} ({df['Class'].sum()/len(df)*100:.3f}%)")
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean data: remove duplicates, handle missing values
        
        Args:
            df: Raw DataFrame
        
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning data...")
        
        initial_shape = df.shape
        
        # Remove duplicates
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_shape[0] - df.shape[0]} duplicate rows")
        
        # Check for missing values
        missing = df.isnull().sum()
        if missing.any():
            logger.warning(f"Missing values found:\n{missing[missing > 0]}")
            df = df.dropna()
        
        # Reset index
        df = df.reset_index(drop=True)
        
        logger.info(f"Data after cleaning: {df.shape}")
        
        return df
    
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create temporal features from Time column
        
        Args:
            df: DataFrame with Time column
        
        Returns:
            DataFrame with additional temporal features
        """
        logger.info("Creating temporal features...")
        
        # Time is in seconds from first transaction
        # Convert to hours for more interpretable features
        df['Time_hours'] = df['Time'] / 3600
        
        # Create hour of day feature (assuming transactions span multiple days)
        # Modulo 24 to get hour in day
        df['Hour_of_day'] = (df['Time'] / 3600) % 24
        
        # Create day of week simulation (assuming 48 hours of data spans 2 days)
        df['Day_period'] = pd.cut(
            df['Time_hours'], 
            bins=[0, 12, 24, 36, 48], 
            labels=['morning', 'afternoon', 'evening', 'night'],
            include_lowest=True
        )
        
        # One-hot encode day period
        day_period_dummies = pd.get_dummies(df['Day_period'], prefix='period', drop_first=True)
        df = pd.concat([df, day_period_dummies], axis=1)
        
        # Drop the categorical column
        df = df.drop('Day_period', axis=1)
        
        logger.info(f"Temporal features created. New shape: {df.shape}")
        
        return df
    
    def split_data(
        self, 
        df: pd.DataFrame, 
        stratified: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data into train, validation, and test sets (BEFORE any oversampling)
        
        Args:
            df: Cleaned DataFrame
            stratified: Whether to use stratified splitting
        
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        logger.info("Splitting data (stratified)...")
        
        # First split: train+val vs test
        train_val, test = train_test_split(
            df,
            test_size=self.config.TEST_SIZE,
            random_state=self.config.RANDOM_STATE,
            stratify=df['Class'] if stratified else None
        )
        
        # Second split: train vs validation
        train, val = train_test_split(
            train_val,
            test_size=self.config.VALIDATION_SIZE,
            random_state=self.config.RANDOM_STATE,
            stratify=train_val['Class'] if stratified else None
        )
        
        logger.info(f"Train set: {len(train)} samples, Fraud: {train['Class'].sum()}")
        logger.info(f"Val set:   {len(val)} samples, Fraud: {val['Class'].sum()}")
        logger.info(f"Test set:  {len(test)} samples, Fraud: {test['Class'].sum()}")
        
        return train, val, test
    
    def scale_features(
        self, 
        train: pd.DataFrame, 
        val: pd.DataFrame, 
        test: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Scale Amount feature using StandardScaler fitted ONLY on training data
        
        Args:
            train, val, test: DataFrames
        
        Returns:
            Tuple of (X_train, y_train, X_val, y_val, X_test, y_test)
        """
        logger.info("Scaling features...")
        
        # Separate features and target
        X_train = train.drop('Class', axis=1)
        y_train = train['Class']
        
        X_val = val.drop('Class', axis=1)
        y_val = val['Class']
        
        X_test = test.drop('Class', axis=1)
        y_test = test['Class']
        
        # Store feature columns
        self.feature_columns = X_train.columns.tolist()
        
        # Identify columns to scale (Amount and any other non-V features)
        columns_to_scale = ['Amount', 'Time_hours', 'Hour_of_day']
        columns_to_scale = [col for col in columns_to_scale if col in X_train.columns]
        
        # Fit scaler ONLY on training data
        X_train_scaled = X_train.copy()
        X_train_scaled[columns_to_scale] = self.scaler.fit_transform(X_train[columns_to_scale])
        
        # Transform validation and test using the same scaler
        X_val_scaled = X_val.copy()
        X_val_scaled[columns_to_scale] = self.scaler.transform(X_val[columns_to_scale])
        
        X_test_scaled = X_test.copy()
        X_test_scaled[columns_to_scale] = self.scaler.transform(X_test[columns_to_scale])
        
        logger.info("Feature scaling complete")
        
        return (
            X_train_scaled.values, y_train.values,
            X_val_scaled.values, y_val.values,
            X_test_scaled.values, y_test.values
        )
    
    def apply_smote(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply SMOTE ONLY to training data to handle class imbalance
        
        Args:
            X_train: Training features
            y_train: Training labels
        
        Returns:
            Tuple of (X_train_resampled, y_train_resampled)
        """
        logger.info("Applying SMOTE to training data...")
        logger.info(f"Before SMOTE - Class 0: {np.sum(y_train==0)}, Class 1: {np.sum(y_train==1)}")
        
        X_train_resampled, y_train_resampled = self.smote.fit_resample(X_train, y_train)
        
        logger.info(f"After SMOTE - Class 0: {np.sum(y_train_resampled==0)}, Class 1: {np.sum(y_train_resampled==1)}")
        logger.info(f"Training set size increased from {len(y_train)} to {len(y_train_resampled)}")
        
        return X_train_resampled, y_train_resampled
    
    def preprocess_pipeline(
        self, 
        file_path: str = None,
        apply_smote: bool = True
    ) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline with data leakage prevention
        
        Pipeline:
        1. Load data
        2. Clean data
        3. Create temporal features
        4. Split into train/val/test
        5. Scale features (fit on train only)
        6. Apply SMOTE (on train only, optional)
        
        Args:
            file_path: Path to data file
            apply_smote: Whether to apply SMOTE oversampling
        
        Returns:
            Dictionary with all data splits and metadata
        """
        logger.info("Starting preprocessing pipeline...")
        
        # Load and clean
        df = self.load_data(file_path)
        df = self.clean_data(df)
        
        # Create temporal features
        df = self.create_temporal_features(df)
        
        # Split data FIRST
        train, val, test = self.split_data(df)
        
        # Scale features
        X_train, y_train, X_val, y_val, X_test, y_test = self.scale_features(train, val, test)
        
        # Apply SMOTE only on training data
        if apply_smote:
            X_train, y_train = self.apply_smote(X_train, y_train)
        
        # Prepare output
        data = {
            'X_train': X_train,
            'y_train': y_train,
            'X_val': X_val,
            'y_val': y_val,
            'X_test': X_test,
            'y_test': y_test,
            'feature_columns': self.feature_columns,
            'scaler': self.scaler
        }
        
        logger.info("Preprocessing pipeline complete!")
        logger.info(f"Feature columns: {len(self.feature_columns)}")
        
        return data
    
    def save_preprocessor(self, path: str = None):
        """Save scaler and feature columns"""
        if path is None:
            path = self.config.MODEL_DIR / "preprocessor.pkl"
        
        joblib.dump({
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }, path)
        logger.info(f"Preprocessor saved to {path}")
    
    def load_preprocessor(self, path: str = None):
        """Load saved scaler and feature columns"""
        if path is None:
            path = self.config.MODEL_DIR / "preprocessor.pkl"
        
        data = joblib.load(path)
        self.scaler = data['scaler']
        self.feature_columns = data['feature_columns']
        logger.info(f"Preprocessor loaded from {path}")
