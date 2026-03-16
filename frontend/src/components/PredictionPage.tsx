import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Chip,
  Divider,
} from '@mui/material';
import { Send, Refresh } from '@mui/icons-material';
import toast from 'react-hot-toast';
import GaugeChart from 'react-gauge-chart';
import { fraudDetectionAPI } from '../services/api';
import type { TransactionInput, PredictionResponse } from '../types';

export default function PredictionPage() {
  const [formData, setFormData] = useState<TransactionInput>({
    Time: 0,
    Amount: 100,
    V1: 0, V2: 0, V3: 0, V4: 0, V5: 0, V6: 0, V7: 0,
    V8: 0, V9: 0, V10: 0, V11: 0, V12: 0, V13: 0, V14: 0,
    V15: 0, V16: 0, V17: 0, V18: 0, V19: 0, V20: 0, V21: 0,
    V22: 0, V23: 0, V24: 0, V25: 0, V26: 0, V27: 0, V28: 0,
  });

  const [result, setResult] = useState<PredictionResponse | null>(null);

  const mutation = useMutation({
    mutationFn: (data: TransactionInput) => fraudDetectionAPI.predictTransaction(data),
    onSuccess: (data) => {
      setResult(data);
      toast.success('Prediction completed successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Prediction failed');
      console.error('Prediction error:', error);
    },
  });

  const handleInputChange = (field: keyof TransactionInput, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: parseFloat(value) || 0,
    }));
  };

  const handleSubmit = () => {
    mutation.mutate(formData);
  };

  const handleReset = () => {
    setFormData({
      Time: 0,
      Amount: 100,
      V1: 0, V2: 0, V3: 0, V4: 0, V5: 0, V6: 0, V7: 0,
      V8: 0, V9: 0, V10: 0, V11: 0, V12: 0, V13: 0, V14: 0,
      V15: 0, V16: 0, V17: 0, V18: 0, V19: 0, V20: 0, V21: 0,
      V22: 0, V23: 0, V24: 0, V25: 0, V26: 0, V27: 0, V28: 0,
    });
    setResult(null);
  };

  const generateRandomTransaction = () => {
    const randomData: TransactionInput = {
      Time: Math.floor(Math.random() * 172800),
      Amount: parseFloat((Math.random() * 1000).toFixed(2)),
      V1: 0, V2: 0, V3: 0, V4: 0, V5: 0, V6: 0, V7: 0,
      V8: 0, V9: 0, V10: 0, V11: 0, V12: 0, V13: 0, V14: 0,
      V15: 0, V16: 0, V17: 0, V18: 0, V19: 0, V20: 0, V21: 0,
      V22: 0, V23: 0, V24: 0, V25: 0, V26: 0, V27: 0, V28: 0,
    };
    for (let i = 1; i <= 28; i++) {
      randomData[`V${i}` as keyof TransactionInput] = parseFloat(
        (Math.random() * 4 - 2).toFixed(4)
      );
    }
    setFormData(randomData);
  };

  const getRiskColor = (level: string) => {
    const colors: Record<string, string> = {
      Low: '#4caf50',
      Medium: '#ff9800',
      High: '#f44336',
      Critical: '#9c27b0',
    };
    return colors[level] || '#gray';
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Transaction Prediction
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Analyze individual transactions for fraud probability
      </Typography>

      <Grid container spacing={3}>
        {/* Input Form */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6" fontWeight={600}>
                Transaction Details
              </Typography>
              <Button
                size="small"
                variant="outlined"
                onClick={generateRandomTransaction}
                startIcon={<Refresh />}
              >
                Generate Sample
              </Button>
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Time (seconds)"
                  type="number"
                  value={formData.Time}
                  onChange={(e) => handleInputChange('Time', e.target.value)}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Amount ($)"
                  type="number"
                  value={formData.Amount}
                  onChange={(e) => handleInputChange('Amount', e.target.value)}
                  size="small"
                  inputProps={{ step: 0.01 }}
                />
              </Grid>

              {/* PCA Features V1-V28 */}
              {Array.from({ length: 28 }, (_, i) => i + 1).map((num) => (
                <Grid item xs={6} sm={4} md={3} key={`V${num}`}>
                  <TextField
                    fullWidth
                    label={`V${num}`}
                    type="number"
                    value={formData[`V${num}` as keyof TransactionInput]}
                    onChange={(e) =>
                      handleInputChange(`V${num}` as keyof TransactionInput, e.target.value)
                    }
                    size="small"
                    inputProps={{ step: 0.0001 }}
                  />
                </Grid>
              ))}
            </Grid>

            <Box mt={3} display="flex" gap={2}>
              <Button
                variant="contained"
                fullWidth
                onClick={handleSubmit}
                disabled={mutation.isPending}
                startIcon={mutation.isPending ? <CircularProgress size={20} /> : <Send />}
              >
                {mutation.isPending ? 'Analyzing...' : 'Predict'}
              </Button>
              <Button variant="outlined" onClick={handleReset}>
                Reset
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Results */}
        <Grid item xs={12} md={6}>
          {mutation.isError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Failed to get prediction. Make sure models are trained and API is running.
            </Alert>
          )}

          {result ? (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Prediction Results
              </Typography>

              {/* Risk Gauge */}
              <Box sx={{ my: 3 }}>
                <GaugeChart
                  id="risk-gauge"
                  nrOfLevels={4}
                  colors={['#4caf50', '#ff9800', '#f44336', '#9c27b0']}
                  arcWidth={0.3}
                  percent={result.risk_score / 100}
                  textColor="#000"
                  formatTextValue={() => `${result.risk_score.toFixed(1)}`}
                />
                <Typography variant="h5" align="center" fontWeight={700} mt={-2}>
                  Risk Score: {result.risk_score.toFixed(1)}/100
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* Key Metrics */}
              <Grid container spacing={2} mb={2}>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">
                        Fraud Probability
                      </Typography>
                      <Typography variant="h5" fontWeight={700}>
                        {(result.fraud_probability * 100).toFixed(2)}%
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">
                        Confidence
                      </Typography>
                      <Typography variant="h5" fontWeight={700}>
                        {(result.confidence * 100).toFixed(1)}%
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Risk Level & Recommendation */}
              <Box mb={2}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Risk Level
                </Typography>
                <Chip
                  label={result.risk_level}
                  sx={{
                    backgroundColor: getRiskColor(result.risk_level),
                    color: 'white',
                    fontWeight: 600,
                    fontSize: '1rem',
                    px: 2,
                    py: 2.5,
                  }}
                />
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Recommendation
                </Typography>
                {(() => {
                  const action = result.recommendation?.action || 'REVIEW';
                  const description =
                    result.recommendation?.description ||
                    (result.recommendation as any)?.reason ||
                    'Review transaction details before final decision.';

                  return (
                    <>
                      <Chip
                        label={action}
                        color={
                          action === 'APPROVE'
                            ? 'success'
                            : action === 'BLOCK'
                            ? 'error'
                            : 'warning'
                        }
                        sx={{ fontWeight: 600, mb: 1 }}
                      />
                      <Typography variant="body2">{description}</Typography>
                    </>
                  );
                })()}
              </Box>

              {/* Model Scores */}
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Model Scores
                </Typography>
                {Object.entries(
                  result.model_scores || {
                    xgboost: result.fraud_probability,
                    autoencoder: result.anomaly_score ?? result.fraud_probability,
                    graph: (result.graph_score ?? result.risk_score) / 100,
                  }
                ).map(([model, score]) => (
                  score !== undefined && (
                    <Box key={model} display="flex" justifyContent="space-between" mb={0.5}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {model === 'xgboost' ? 'XGBoost' : model}:
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {(score * 100).toFixed(2)}%
                      </Typography>
                    </Box>
                  )
                ))}
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="caption" color="text.secondary">
                Latency: {result.latency_ms.toFixed(2)}ms | ID: {result.transaction_id}
              </Typography>
            </Paper>
          ) : (
            <Paper
              sx={{
                p: 6,
                textAlign: 'center',
                backgroundColor: 'background.default',
                border: '2px dashed',
                borderColor: 'divider',
              }}
            >
              <Typography variant="h6" color="text.secondary">
                Fill in transaction details and click Predict
              </Typography>
              <Typography variant="body2" color="text.secondary" mt={1}>
                Results will appear here
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
