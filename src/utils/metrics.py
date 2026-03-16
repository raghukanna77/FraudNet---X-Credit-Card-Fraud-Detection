"""
Metrics calculation utilities
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, matthews_corrcoef,
    confusion_matrix, classification_report
)
from typing import Dict, Tuple, Any
import time


class MetricsCalculator:
    """Calculate comprehensive evaluation metrics for fraud detection"""
    
    def __init__(self, cost_matrix: Dict[str, float]):
        """
        Initialize metrics calculator with cost matrix
        
        Args:
            cost_matrix: Dictionary with keys: false_negative, false_positive, 
                        true_positive, true_negative
        """
        self.cost_matrix = cost_matrix
    
    def calculate_all_metrics(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray, 
        y_proba: np.ndarray = None
    ) -> Dict[str, Any]:
        """
        Calculate all evaluation metrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (optional)
        
        Returns:
            Dictionary containing all metrics
        """
        metrics = {}
        
        # Basic classification metrics
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['precision'] = precision_score(y_true, y_pred, zero_division=0)
        metrics['recall'] = recall_score(y_true, y_pred, zero_division=0)
        metrics['f1_score'] = f1_score(y_true, y_pred, zero_division=0)
        metrics['mcc'] = matthews_corrcoef(y_true, y_pred)
        
        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        metrics['confusion_matrix'] = {
            'true_negative': int(tn),
            'false_positive': int(fp),
            'false_negative': int(fn),
            'true_positive': int(tp)
        }
        
        # ROC-AUC and PR-AUC (if probabilities provided)
        if y_proba is not None:
            metrics['roc_auc'] = roc_auc_score(y_true, y_proba)
            metrics['pr_auc'] = average_precision_score(y_true, y_proba)
        
        # Financial cost calculation
        financial_cost = self.calculate_financial_cost(tn, fp, fn, tp)
        metrics['financial_cost'] = financial_cost
        
        # Additional metrics
        metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
        metrics['false_positive_rate'] = fp / (fp + tn) if (fp + tn) > 0 else 0
        metrics['false_negative_rate'] = fn / (fn + tp) if (fn + tp) > 0 else 0
        
        return metrics
    
    def calculate_financial_cost(
        self, 
        tn: int, 
        fp: int, 
        fn: int, 
        tp: int
    ) -> Dict[str, float]:
        """
        Calculate financial cost based on confusion matrix
        
        Args:
            tn, fp, fn, tp: Confusion matrix values
        
        Returns:
            Dictionary with cost breakdown
        """
        cost_fn = fn * self.cost_matrix['false_negative']
        cost_fp = fp * self.cost_matrix['false_positive']
        cost_tp = tp * self.cost_matrix['true_positive']
        cost_tn = tn * self.cost_matrix['true_negative']
        
        total_cost = cost_fn + cost_fp + cost_tp + cost_tn
        
        return {
            'false_negative_cost': float(cost_fn),
            'false_positive_cost': float(cost_fp),
            'true_positive_cost': float(cost_tp),
            'true_negative_cost': float(cost_tn),
            'total_cost': float(total_cost),
            'cost_per_transaction': float(total_cost / (tn + fp + fn + tp))
        }
    
    def optimize_threshold(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        metric: str = 'cost'
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Find optimal threshold to minimize cost or maximize F1
        
        Args:
            y_true: True labels
            y_proba: Predicted probabilities
            metric: 'cost' for cost minimization, 'f1' for F1 maximization
        
        Returns:
            Tuple of (optimal_threshold, metrics_at_threshold)
        """
        thresholds = np.arange(0.1, 0.91, 0.01)
        best_threshold = 0.5
        best_value = float('inf') if metric == 'cost' else 0
        best_metrics = None
        
        for threshold in thresholds:
            y_pred = (y_proba >= threshold).astype(int)
            
            if metric == 'cost':
                tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
                cost = self.calculate_financial_cost(tn, fp, fn, tp)['total_cost']
                
                if cost < best_value:
                    best_value = cost
                    best_threshold = threshold
                    best_metrics = self.calculate_all_metrics(y_true, y_pred, y_proba)
            
            elif metric == 'f1':
                f1 = f1_score(y_true, y_pred, zero_division=0)
                
                if f1 > best_value:
                    best_value = f1
                    best_threshold = threshold
                    best_metrics = self.calculate_all_metrics(y_true, y_pred, y_proba)
        
        return best_threshold, best_metrics
    
    def print_metrics_report(self, metrics: Dict[str, Any], title: str = "Evaluation Report"):
        """
        Print formatted metrics report
        
        Args:
            metrics: Dictionary of metrics
            title: Report title
        """
        print(f"\n{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}\n")
        
        print("Classification Metrics:")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1 Score:  {metrics['f1_score']:.4f}")
        print(f"  MCC:       {metrics['mcc']:.4f}")
        
        if 'roc_auc' in metrics:
            print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
            print(f"  PR-AUC:    {metrics['pr_auc']:.4f}")
        
        cm = metrics['confusion_matrix']
        print(f"\nConfusion Matrix:")
        print(f"  TN: {cm['true_negative']:>6} | FP: {cm['false_positive']:>6}")
        print(f"  FN: {cm['false_negative']:>6} | TP: {cm['true_positive']:>6}")
        
        fc = metrics['financial_cost']
        print(f"\nFinancial Impact:")
        print(f"  False Negative Cost: ${fc['false_negative_cost']:>12,.2f}")
        print(f"  False Positive Cost: ${fc['false_positive_cost']:>12,.2f}")
        print(f"  Total Cost:          ${fc['total_cost']:>12,.2f}")
        print(f"  Cost per Transaction: ${fc['cost_per_transaction']:>11,.2f}")
        
        print(f"\n{'='*60}\n")


class LatencyTracker:
    """Track prediction latency"""
    
    def __init__(self):
        self.latencies = []
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.latencies.append(time.time() - self.start_time)
    
    def get_stats(self) -> Dict[str, float]:
        """Get latency statistics"""
        if not self.latencies:
            return {}
        
        return {
            'mean_ms': np.mean(self.latencies) * 1000,
            'median_ms': np.median(self.latencies) * 1000,
            'p95_ms': np.percentile(self.latencies, 95) * 1000,
            'p99_ms': np.percentile(self.latencies, 99) * 1000,
            'min_ms': np.min(self.latencies) * 1000,
            'max_ms': np.max(self.latencies) * 1000
        }
