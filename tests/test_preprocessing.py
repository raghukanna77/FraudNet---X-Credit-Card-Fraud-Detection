"""
Unit tests for preprocessing module
"""

import pytest
import numpy as np
import pandas as pd
from src.preprocessing.data_preprocessor import DataPreprocessor
from src.utils.config import Config


class TestDataPreprocessor:
    """Test suite for data preprocessing"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = Config()
        self.preprocessor = DataPreprocessor(self.config)
    
    def create_sample_data(self, n_samples=1000):
        """Create sample transaction data"""
        np.random.seed(42)
        
        data = {
            'Time': np.random.randint(0, 172800, n_samples),
            'Amount': np.random.exponential(50, n_samples),
            'Class': np.random.choice([0, 1], n_samples, p=[0.998, 0.002])
        }
        
        # Add V features
        for i in range(1, 29):
            data[f'V{i}'] = np.random.randn(n_samples)
        
        return pd.DataFrame(data)
    
    def test_clean_data(self):
        """Test data cleaning"""
        df = self.create_sample_data()
        # Add duplicate
        df = pd.concat([df, df.iloc[:5]], ignore_index=True)
        
        cleaned = self.preprocessor.clean_data(df)
        
        assert len(cleaned) < len(df)  # Duplicates removed
        assert cleaned.isnull().sum().sum() == 0  # No missing values
    
    def test_create_temporal_features(self):
        """Test temporal feature creation"""
        df = self.create_sample_data()
        
        df_with_features = self.preprocessor.create_temporal_features(df)
        
        assert 'Time_hours' in df_with_features.columns
        assert 'Hour_of_day' in df_with_features.columns
        assert df_with_features['Time_hours'].max() <= df['Time'].max() / 3600
    
    def test_split_data_stratified(self):
        """Test stratified data splitting"""
        df = self.create_sample_data()
        df = self.preprocessor.create_temporal_features(df)
        
        train, val, test = self.preprocessor.split_data(df, stratified=True)
        
        # Check sizes
        assert len(train) > len(val)
        assert len(train) > len(test)
        
        # Check fraud rates are similar (stratified)
        train_fraud_rate = train['Class'].mean()
        val_fraud_rate = val['Class'].mean()
        test_fraud_rate = test['Class'].mean()
        
        assert abs(train_fraud_rate - val_fraud_rate) < 0.01
        assert abs(train_fraud_rate - test_fraud_rate) < 0.01
    
    def test_scale_features(self):
        """Test feature scaling"""
        df = self.create_sample_data()
        df = self.preprocessor.create_temporal_features(df)
        
        train, val, test = self.preprocessor.split_data(df)
        
        X_train, y_train, X_val, y_val, X_test, y_test = \
            self.preprocessor.scale_features(train, val, test)
        
        assert X_train.shape[0] == len(train)
        assert X_val.shape[0] == len(val)
        assert X_test.shape[0] == len(test)
        assert len(y_train) == len(train)
    
    def test_apply_smote(self):
        """Test SMOTE application"""
        # Create imbalanced data
        X = np.random.randn(1000, 30)
        y = np.zeros(1000)
        y[:10] = 1  # Only 1% fraud
        
        X_resampled, y_resampled = self.preprocessor.apply_smote(X, y)
        
        # After SMOTE, minority class should increase
        assert np.sum(y_resampled == 1) > np.sum(y == 1)
        assert len(X_resampled) > len(X)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
