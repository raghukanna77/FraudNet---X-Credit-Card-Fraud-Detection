// API Response Types
export interface TransactionInput {
  Time: number;
  V1: number;
  V2: number;
  V3: number;
  V4: number;
  V5: number;
  V6: number;
  V7: number;
  V8: number;
  V9: number;
  V10: number;
  V11: number;
  V12: number;
  V13: number;
  V14: number;
  V15: number;
  V16: number;
  V17: number;
  V18: number;
  V19: number;
  V20: number;
  V21: number;
  V22: number;
  V23: number;
  V24: number;
  V25: number;
  V26: number;
  V27: number;
  V28: number;
  Amount: number;
}

export interface PredictionResponse {
  transaction_id: string;
  fraud_probability: number;
  is_fraud: boolean;
  anomaly_score?: number;
  graph_score?: number;
  risk_score: number;
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
  confidence: number;
  recommendation: {
    action: 'APPROVE' | 'REVIEW' | 'CHALLENGE' | 'BLOCK';
    description: string;
    flags: string[];
  };
  model_scores: {
    xgboost: number;
    lstm?: number;
    autoencoder?: number;
    graph?: number;
  };
  explanation?: {
    top_features: Array<{
      feature: string;
      importance: number;
      impact: string;
    }>;
    explanation_text: string;
  };
  latency_ms: number;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  models_loaded: Record<string, boolean>;
  drift_status: {
    detected: boolean;
    drift_count: number;
  } | null;
}

export interface MetricsResponse {
  total_predictions: number;
  fraud_detected: number;
  fraud_rate: number;
  average_risk_score: number;
  average_latency_ms: number;
  model_accuracy: number;
  drift_detected: boolean;
  last_prediction_time: string;
}

export interface ModelInfo {
  model_name: string;
  version: string;
  last_trained: string;
  features_count: number;
  status: string;
}

// UI State Types
export interface DriftStatus {
  detected: boolean;
  drift_count: number;
  last_check: string;
}

export interface RiskDistribution {
  Low: number;
  Medium: number;
  High: number;
  Critical: number;
}
