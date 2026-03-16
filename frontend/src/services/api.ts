import axios from 'axios';
import type {
  TransactionInput,
  PredictionResponse,
  HealthResponse,
  MetricsResponse,
  ModelInfo,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.url} - ${response.status}`);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const fraudDetectionAPI = {
  // Health check
  getHealth: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  // Predict transaction
  predictTransaction: async (
    transaction: TransactionInput
  ): Promise<PredictionResponse> => {
    const response = await apiClient.post<PredictionResponse>(
      '/predict',
      transaction
    );
    return response.data;
  },

  // Get metrics
  getMetrics: async (): Promise<MetricsResponse> => {
    const response = await apiClient.get('/metrics');
    const raw = response.data ?? {};

    // Normalize demo-mode backend fields to frontend metric contract
    const totalPredictions = Number(raw.total_predictions ?? raw.total_requests ?? 0);
    const fraudDetected = Number(raw.fraud_detected ?? 0);
    const averageLatency = Number(raw.average_latency_ms ?? 0);

    return {
      total_predictions: totalPredictions,
      fraud_detected: fraudDetected,
      fraud_rate:
        raw.fraud_rate !== undefined
          ? Number(raw.fraud_rate)
          : totalPredictions > 0
          ? fraudDetected / totalPredictions
          : 0,
      average_risk_score: Number(raw.average_risk_score ?? 0),
      average_latency_ms: averageLatency,
      model_accuracy: Number(raw.model_accuracy ?? 0),
      drift_detected: Boolean(raw.drift_detected ?? raw.drift_status?.detected ?? false),
      last_prediction_time: String(raw.last_prediction_time ?? ''),
    };
  },

  // Get model info
  getModelInfo: async (): Promise<ModelInfo[]> => {
    const response = await apiClient.get<ModelInfo[]>('/model-info');
    return response.data;
  },

  // Root endpoint
  getRoot: async (): Promise<{ message: string; version: string }> => {
    const response = await apiClient.get('/');
    return response.data;
  },
};

export default apiClient;
