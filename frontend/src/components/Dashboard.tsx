import { useQuery } from '@tanstack/react-query';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Warning,
  CheckCircle,
  Speed,
  SsidChart,
} from '@mui/icons-material';
import { fraudDetectionAPI } from '../services/api';
import RiskDistributionChart from './RiskDistributionChart';
import RecentPredictions from './RecentPredictions';

export default function Dashboard() {
  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: fraudDetectionAPI.getHealth,
    refetchInterval: 10000,
  });

  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: fraudDetectionAPI.getMetrics,
    refetchInterval: 5000,
  });

  if (healthLoading || metricsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  const StatCard = ({
    title,
    value,
    icon,
    color,
    subtitle,
  }: {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
    subtitle?: string;
  }) => (
    <Card
      elevation={0}
      sx={{
        height: '100%',
        border: '1px solid',
        borderColor: 'divider',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 3,
        },
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Typography color="text.secondary" variant="body2" fontWeight={500}>
            {title}
          </Typography>
          <Box
            sx={{
              backgroundColor: `${color}15`,
              color: color,
              borderRadius: '50%',
              p: 1,
              display: 'flex',
            }}
          >
            {icon}
          </Box>
        </Box>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="caption" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Dashboard Overview
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Real-time fraud detection system monitoring and metrics
      </Typography>

      {/* System Status Alert */}
      {health && !health.models_loaded.xgboost && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Models not loaded. Please train the models first.
        </Alert>
      )}

      {health?.drift_status?.detected && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          ⚠️ Concept drift detected! Model retraining recommended. Drift count:{' '}
          {health.drift_status?.drift_count}
        </Alert>
      )}

      {/* Key Metrics Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Predictions"
            value={metrics?.total_predictions?.toLocaleString() || '0'}
            icon={<SsidChart />}
            color="#1976d2"
            subtitle="Transactions processed"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Fraud Detected"
            value={metrics?.fraud_detected?.toLocaleString() || '0'}
            icon={<Warning />}
            color="#dc004e"
            subtitle={`${((metrics?.fraud_rate || 0) * 100).toFixed(2)}% fraud rate`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Risk Score"
            value={(metrics?.average_risk_score ?? 0).toFixed(1)}
            icon={<TrendingUp />}
            color="#ed6c02"
            subtitle="Out of 100"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Latency"
            value={`${(metrics?.average_latency_ms ?? 0).toFixed(1)}ms`}
            icon={<Speed />}
            color="#2e7d32"
            subtitle="Response time"
          />
        </Grid>
      </Grid>

      {/* Model Status */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Model Status
            </Typography>
            <Box mt={2}>
              {health &&
                Object.entries(health.models_loaded).map(([model, loaded]) => (
                  <Box
                    key={model}
                    display="flex"
                    alignItems="center"
                    justifyContent="space-between"
                    mb={1.5}
                    p={1.5}
                    sx={{
                      backgroundColor: loaded ? 'success.lighter' : 'error.lighter',
                      borderRadius: 1,
                    }}
                  >
                    <Typography
                      variant="body1"
                      fontWeight={500}
                      sx={{ textTransform: 'capitalize' }}
                    >
                      {model === 'xgboost' ? 'XGBoost' : model.toUpperCase()}
                    </Typography>
                    <Box display="flex" alignItems="center">
                      <CheckCircle
                        sx={{
                          color: loaded ? 'success.main' : 'error.main',
                          mr: 0.5,
                        }}
                      />
                      <Typography
                        variant="body2"
                        color={loaded ? 'success.main' : 'error.main'}
                        fontWeight={600}
                      >
                        {loaded ? 'Loaded' : 'Not Loaded'}
                      </Typography>
                    </Box>
                  </Box>
                ))}
            </Box>
            {metrics && (
              <Box mt={3} pt={2} borderTop="1px solid" borderColor="divider">
                <Typography variant="body2" color="text.secondary">
                  Model Accuracy: <strong>{((metrics.model_accuracy ?? 0) * 100).toFixed(2)}%</strong>
                </Typography>
                <Typography variant="body2" color="text.secondary" mt={0.5}>
                  Last Prediction: <strong>{metrics.last_prediction_time || 'N/A'}</strong>
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <RiskDistributionChart />
        </Grid>
      </Grid>

      {/* Recent Predictions */}
      <RecentPredictions />
    </Box>
  );
}
