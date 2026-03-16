"""
Feature engineering module for creating behavioral and temporal features
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import joblib

from ..utils.logger import logger
from ..utils.config import Config


class FeatureEngineer:
    """
    Creates advanced features including:
    - User behavioral features
    - Transaction velocity features
    - Deviation scores
    - Aggregation features
    """
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.user_stats = {}
        self.is_fitted = False
    
    def create_user_id(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create synthetic user ID based on transaction patterns
        (Since original dataset doesn't have user IDs)
        
        We'll use clustering of V1-V5 features which likely represent user identity
        """
        logger.info("Creating synthetic user identifiers...")
        
        # Use first few V features as proxy for user identity
        # In production, you would use actual card_id or user_id
        df['user_id'] = (df['V1'] * 1000 + df['V2'] * 100).astype(int)
        
        # Ensure unique but reasonable number of users
        df['user_id'] = df['user_id'] % 10000
        
        logger.info(f"Created user IDs: {df['user_id'].nunique()} unique users")
        
        return df
    
    def calculate_user_statistics(
        self, 
        df: pd.DataFrame, 
        fit_mode: bool = True
    ) -> pd.DataFrame:
        """
        Calculate per-user behavioral statistics
        
        Args:
            df: DataFrame with transactions
            fit_mode: If True, calculate and save user stats. If False, use saved stats
        
        Returns:
            DataFrame with user statistical features
        """
        logger.info("Calculating user behavioral statistics...")
        
        if 'user_id' not in df.columns:
            df = self.create_user_id(df)
        
        if fit_mode:
            # Calculate user statistics from training data
            user_stats = df.groupby('user_id').agg({
                'Amount': ['mean', 'std', 'median', 'min', 'max', 'count'],
                'Time': ['min', 'max']
            })
            
            user_stats.columns = ['_'.join(col).strip() for col in user_stats.columns.values]
            user_stats = user_stats.reset_index()
            
            # Calculate transaction frequency (transactions per hour)
            user_stats['time_span_hours'] = (
                user_stats['Time_max'] - user_stats['Time_min']
            ) / 3600
            user_stats['time_span_hours'] = user_stats['time_span_hours'].replace(0, 1)
            
            user_stats['transaction_frequency'] = (
                user_stats['Amount_count'] / user_stats['time_span_hours']
            )
            
            # Fill NaN std with 0 (users with single transaction)
            user_stats['Amount_std'] = user_stats['Amount_std'].fillna(0)
            
            # Store user stats
            self.user_stats = user_stats.set_index('user_id').to_dict('index')
            self.is_fitted = True
        
        # Merge user statistics with original dataframe
        user_stats_df = pd.DataFrame.from_dict(self.user_stats, orient='index')
        user_stats_df['user_id'] = user_stats_df.index
        
        df = df.merge(
            user_stats_df[['user_id', 'Amount_mean', 'Amount_std', 'Amount_median', 
                          'transaction_frequency', 'Amount_count']],
            on='user_id',
            how='left'
        )
        
        # Fill NaN for users not seen in training
        df['Amount_mean'] = df['Amount_mean'].fillna(df['Amount'].median())
        df['Amount_std'] = df['Amount_std'].fillna(0)
        df['Amount_median'] = df['Amount_median'].fillna(df['Amount'].median())
        df['transaction_frequency'] = df['transaction_frequency'].fillna(0.1)
        df['Amount_count'] = df['Amount_count'].fillna(1)
        
        logger.info(f"User statistics calculated. Shape: {df.shape}")
        
        return df
    
    def calculate_deviation_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate deviation of current transaction from user's normal behavior
        
        Args:
            df: DataFrame with user statistics
        
        Returns:
            DataFrame with deviation features
        """
        logger.info("Calculating deviation features...")
        
        # Deviation from user's average
        df['amount_deviation_from_mean'] = np.abs(df['Amount'] - df['Amount_mean'])
        
        # Z-score deviation (how many standard deviations away)
        df['amount_zscore'] = np.where(
            df['Amount_std'] > 0,
            (df['Amount'] - df['Amount_mean']) / df['Amount_std'],
            0
        )
        
        # Ratio to median
        df['amount_to_median_ratio'] = np.where(
            df['Amount_median'] > 0,
            df['Amount'] / df['Amount_median'],
            1
        )
        
        # Binary flag: is this transaction unusually large?
        df['is_amount_anomaly'] = (
            df['Amount'] > df['Amount_mean'] + 2 * df['Amount_std']
        ).astype(int)
        
        logger.info("Deviation features calculated")
        
        return df
    
    def calculate_velocity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate transaction velocity features (time-based patterns)
        
        Args:
            df: DataFrame with Time column
        
        Returns:
            DataFrame with velocity features
        """
        logger.info("Calculating velocity features...")
        
        if 'user_id' not in df.columns:
            df = self.create_user_id(df)
        
        # Sort by user and time
        df = df.sort_values(['user_id', 'Time'])
        
        # Time since last transaction for same user
        df['time_since_last_transaction'] = df.groupby('user_id')['Time'].diff()
        df['time_since_last_transaction'] = df['time_since_last_transaction'].fillna(0)
        
        # Rolling statistics (last 3 transactions)
        df['rolling_amount_mean_3'] = df.groupby('user_id')['Amount'].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )
        
        df['rolling_amount_std_3'] = df.groupby('user_id')['Amount'].transform(
            lambda x: x.rolling(window=3, min_periods=1).std()
        ).fillna(0)
        
        # Transaction count in last hour
        df['transactions_last_hour'] = 0  # Placeholder (requires more complex logic)
        
        logger.info("Velocity features calculated")
        
        return df
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create interaction features between existing features
        
        Args:
            df: DataFrame with engineered features
        
        Returns:
            DataFrame with interaction features
        """
        logger.info("Creating interaction features...")
        
        # Amount * Time interactions
        df['amount_time_interaction'] = df['Amount'] * df['Time_hours']
        
        # Amount * Frequency
        df['amount_frequency_interaction'] = df['Amount'] * df['transaction_frequency']
        
        # Hour-based amount patterns
        if 'Hour_of_day' in df.columns:
            df['amount_per_hour'] = df['Amount'] * df['Hour_of_day']
        
        logger.info("Interaction features created")
        
        return df
    
    def engineer_features(
        self, 
        df: pd.DataFrame, 
        fit_mode: bool = True
    ) -> pd.DataFrame:
        """
        Complete feature engineering pipeline
        
        Args:
            df: Input DataFrame
            fit_mode: If True, fit on this data. If False, use fitted parameters
        
        Returns:
            DataFrame with engineered features
        """
        logger.info("Starting feature engineering pipeline...")
        
        # Create user ID
        df = self.create_user_id(df)
        
        # Calculate user statistics
        df = self.calculate_user_statistics(df, fit_mode=fit_mode)
        
        # Calculate deviation features
        df = self.calculate_deviation_features(df)
        
        # Calculate velocity features
        df = self.calculate_velocity_features(df)
        
        # Create interaction features
        df = self.create_interaction_features(df)
        
        logger.info(f"Feature engineering complete. Final shape: {df.shape}")
        logger.info(f"Final feature count: {df.shape[1] - 1}")  # Excluding target
        
        return df
    
    def get_feature_names(self) -> List[str]:
        """Get list of all engineered feature names"""
        return [
            'Amount_mean', 'Amount_std', 'Amount_median', 
            'transaction_frequency', 'Amount_count',
            'amount_deviation_from_mean', 'amount_zscore', 
            'amount_to_median_ratio', 'is_amount_anomaly',
            'time_since_last_transaction', 'rolling_amount_mean_3', 
            'rolling_amount_std_3', 'transactions_last_hour',
            'amount_time_interaction', 'amount_frequency_interaction'
        ]
    
    def save_feature_engineer(self, path: str = None):
        """Save fitted feature engineer"""
        if path is None:
            path = self.config.MODEL_DIR / "feature_engineer.pkl"
        
        joblib.dump({
            'user_stats': self.user_stats,
            'is_fitted': self.is_fitted
        }, path)
        logger.info(f"Feature engineer saved to {path}")
    
    def load_feature_engineer(self, path: str = None):
        """Load fitted feature engineer"""
        if path is None:
            path = self.config.MODEL_DIR / "feature_engineer.pkl"
        
        data = joblib.load(path)
        self.user_stats = data['user_stats']
        self.is_fitted = data['is_fitted']
        logger.info(f"Feature engineer loaded from {path}")


class SequenceGenerator:
    """
    Generate sequences for LSTM model
    Groups transactions by user and creates sliding windows
    """
    
    def __init__(self, sequence_length: int = 10):
        self.sequence_length = sequence_length
    
    def create_sequences(
        self, 
        df: pd.DataFrame, 
        feature_columns: List[str]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM
        
        Args:
            df: DataFrame with user_id and features
            feature_columns: List of feature column names
        
        Returns:
            Tuple of (X_sequences, y_sequences)
        """
        logger.info(f"Creating sequences of length {self.sequence_length}...")
        
        if 'user_id' not in df.columns:
            raise ValueError("DataFrame must have 'user_id' column")
        
        # Sort by user and time
        df = df.sort_values(['user_id', 'Time'])
        
        sequences = []
        labels = []
        
        # Group by user
        for user_id, group in df.groupby('user_id'):
            if len(group) < self.sequence_length:
                # Pad short sequences
                padded = np.zeros((self.sequence_length, len(feature_columns)))
                padded[-len(group):] = group[feature_columns].values
                sequences.append(padded)
                labels.append(group['Class'].iloc[-1])
            else:
                # Create sliding windows
                for i in range(len(group) - self.sequence_length + 1):
                    seq = group[feature_columns].iloc[i:i+self.sequence_length].values
                    sequences.append(seq)
                    labels.append(group['Class'].iloc[i+self.sequence_length-1])
        
        X_sequences = np.array(sequences)
        y_sequences = np.array(labels)
        
        logger.info(f"Created {len(sequences)} sequences")
        logger.info(f"Sequence shape: {X_sequences.shape}")
        
        return X_sequences, y_sequences
