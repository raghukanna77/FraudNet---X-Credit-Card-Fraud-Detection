import {
  Paper,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import { format } from 'date-fns';

const mockPredictions = [
  {
    id: 'TXN001',
    timestamp: new Date(),
    amount: 149.62,
    risk_level: 'Low',
    fraud_probability: 0.05,
    action: 'APPROVE',
  },
  {
    id: 'TXN002',
    timestamp: new Date(Date.now() - 120000),
    amount: 2890.45,
    risk_level: 'High',
    fraud_probability: 0.87,
    action: 'BLOCK',
  },
  {
    id: 'TXN003',
    timestamp: new Date(Date.now() - 240000),
    amount: 545.23,
    risk_level: 'Medium',
    fraud_probability: 0.42,
    action: 'REVIEW',
  },
];

const getRiskColor = (level: string) => {
  const colors: Record<string, string> = {
    Low: 'success',
    Medium: 'warning',
    High: 'error',
    Critical: 'error',
  };
  return colors[level] || 'default';
};

const getActionColor = (action: string) => {
  const colors: Record<string, string> = {
    APPROVE: 'success',
    REVIEW: 'warning',
    CHALLENGE: 'warning',
    BLOCK: 'error',
  };
  return colors[action] || 'default';
};

export default function RecentPredictions() {
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" fontWeight={600} gutterBottom>
        Recent Predictions
      </Typography>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Transaction ID</strong></TableCell>
              <TableCell><strong>Time</strong></TableCell>
              <TableCell align="right"><strong>Amount</strong></TableCell>
              <TableCell align="center"><strong>Risk Level</strong></TableCell>
              <TableCell align="center"><strong>Fraud Prob.</strong></TableCell>
              <TableCell align="center"><strong>Action</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mockPredictions.map((pred) => (
              <TableRow key={pred.id} hover>
                <TableCell>
                  <Typography variant="body2" fontFamily="monospace">
                    {pred.id}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {format(pred.timestamp, 'MMM dd, HH:mm:ss')}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2" fontWeight={600}>
                    ${pred.amount.toFixed(2)}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Chip
                    label={pred.risk_level}
                    color={getRiskColor(pred.risk_level) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell align="center">
                  <Typography variant="body2">
                    {(pred.fraud_probability * 100).toFixed(1)}%
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Chip
                    label={pred.action}
                    color={getActionColor(pred.action) as any}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Box mt={2} display="flex" justifyContent="center">
        <Typography variant="body2" color="text.secondary">
          Showing last 3 transactions
        </Typography>
      </Box>
    </Paper>
  );
}
