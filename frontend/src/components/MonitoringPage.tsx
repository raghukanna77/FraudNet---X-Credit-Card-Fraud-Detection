import { useQuery } from '@tanstack/react-query';
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  LinearProgress,
  Paper,
  Typography,
} from '@mui/material';
import {
  CheckCircle,
  Memory,
  Speed,
  TrendingUp,
  Warning,
} from '@mui/icons-material';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { fraudDetectionAPI } from '../services/api';

const mockPerformanceData = [
  { time: '00:00', predictions: 42, latency: 36 },
  { time: '04:00', predictions: 28, latency: 39 },
  { time: '08:00', predictions: 74, latency: 41 },
  { time: '12:00', predictions: 101, latency: 47 },
  { time: '16:00', predictions: 127, latency: 44 },
  { time: '20:00', predictions: 90, latency: 40 },
];

export default function MonitoringPage() {
  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: fraudDetectionAPI.getHealth,
    refetchInterval: 5000,
  });

  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: fraudDetectionAPI.getMetrics,
    refetchInterval: 5000,
  });

  const { data: modelInfo } = useQuery({
    queryKey: ['model-info'],
    queryFn: fraudDetectionAPI.getModelInfo,
    refetchInterval: 30000,
  });

  if (healthLoading || metricsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={56} />
      </Box>
    );
  }

  const modelEntries = health ? Object.entries(health.models_loaded) : [];

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        System Monitoring
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Live health telemetry, model readiness, and response-time behavior.
      </Typography>

      <Alert
        severity={health?.status === 'healthy' ? 'success' : 'warning'}
        icon={health?.status === 'healthy' ? <CheckCircle /> : <Warning />}
        sx={{ mb: 3 }}
      >
        {health?.status === 'healthy'
          ? 'All core services are healthy and operating within expected thresholds.'
          : 'System is running in demo mode. Core APIs work, but trained models are not currently loaded.'}
      </Alert>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="text.secondary" variant="body2">
                  Model Accuracy
                </Typography>
                <TrendingUp sx={{ color: 'primary.main' }} />
              </Box>
              <Typography variant="h4" fontWeight={700} mt={1}>
                {((metrics?.model_accuracy || 0) * 100).toFixed(2)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(metrics?.model_accuracy || 0) * 100}
                sx={{ mt: 1.5, height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="text.secondary" variant="body2">
                  Avg Latency
                </Typography>
                <Speed sx={{ color: 'secondary.main' }} />
              </Box>
              <Typography variant="h4" fontWeight={700} mt={1}>
                {(metrics?.average_latency_ms ?? 0).toFixed(1)}ms
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Target under 100ms
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="text.secondary" variant="body2">
                  Total Predictions
                </Typography>
                <Memory sx={{ color: 'warning.main' }} />
              </Box>
              <Typography variant="h4" fontWeight={700} mt={1}>
                {metrics?.total_predictions?.toLocaleString() || '0'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Fraud detected: {metrics?.fraud_detected || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="text.secondary" variant="body2">
                  Drift Signals
                </Typography>
                <Warning sx={{ color: health?.drift_status?.detected ? 'error.main' : 'success.main' }} />
              </Box>
              <Typography variant="h4" fontWeight={700} mt={1}>
                {health?.drift_status?.drift_count || 0}
              </Typography>
              <Chip
                size="small"
                label={health?.drift_status?.detected ? 'Detected' : 'Stable'}
                color={health?.drift_status?.detected ? 'error' : 'success'}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Throughput vs Latency (24h)
            </Typography>
            <Box sx={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <LineChart data={mockPerformanceData}>
                  <CartesianGrid strokeDasharray="4 4" stroke="rgba(0,0,0,0.08)" />
                  <XAxis dataKey="time" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="predictions"
                    stroke="#136f63"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                    name="Predictions"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="latency"
                    stroke="#ff7f11"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    name="Latency (ms)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Model Readiness
            </Typography>
            {modelEntries.map(([model, loaded]) => (
              <Box key={model} mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.8}>
                  <Typography sx={{ textTransform: 'capitalize' }} fontWeight={600}>
                    {model === 'xgboost' ? 'XGBoost' : model}
                  </Typography>
                  <Chip
                    size="small"
                    label={loaded ? 'Loaded' : 'Unavailable'}
                    color={loaded ? 'success' : 'default'}
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={loaded ? 100 : 20}
                  color={loaded ? 'success' : 'inherit'}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            ))}

            {Array.isArray(modelInfo) && modelInfo.length > 0 && (
              <Box mt={3} pt={2} borderTop="1px solid" borderColor="divider">
                <Typography variant="body2" color="text.secondary" mb={1}>
                  Latest model package:
                </Typography>
                <Typography variant="body2" fontWeight={700}>
                  {modelInfo[0].model_name} v{modelInfo[0].version}
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
