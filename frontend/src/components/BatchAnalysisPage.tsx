import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
} from '@mui/material';
import { CloudUpload, Download } from '@mui/icons-material';
import toast from 'react-hot-toast';

interface BatchResult {
  transaction_id: string;
  amount: number;
  fraud_probability: number;
  risk_level: string;
  recommendation: string;
}

export default function BatchAnalysisPage() {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<BatchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== 'text/csv' && !selectedFile.name.endsWith('.csv')) {
        toast.error('Please upload a CSV file');
        return;
      }
      setFile(selectedFile);
      toast.success(`File "${selectedFile.name}" loaded`);
    }
  };

  const handleProcess = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setLoading(true);
    
    // Simulate processing
    setTimeout(() => {
      const mockResults: BatchResult[] = Array.from({ length: 10 }, (_, i) => ({
        transaction_id: `TXN${String(i + 1).padStart(4, '0')}`,
        amount: parseFloat((Math.random() * 1000).toFixed(2)),
        fraud_probability: Math.random(),
        risk_level: ['Low', 'Medium', 'High', 'Critical'][Math.floor(Math.random() * 4)],
        recommendation: ['APPROVE', 'REVIEW', 'CHALLENGE', 'BLOCK'][
          Math.floor(Math.random() * 4)
        ],
      }));
      
      setResults(mockResults);
      setLoading(false);
      toast.success('Batch processing completed!');
    }, 2000);
  };

  const handleDownload = () => {
    // Create CSV content
    const csvContent = [
      ['Transaction ID', 'Amount', 'Fraud Probability', 'Risk Level', 'Recommendation'],
      ...results.map((r) => [
        r.transaction_id,
        r.amount,
        (r.fraud_probability * 100).toFixed(2),
        r.risk_level,
        r.recommendation,
      ]),
    ]
      .map((row) => row.join(','))
      .join('\n');

    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fraud_analysis_results_${new Date().getTime()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    toast.success('Results downloaded!');
  };

  const getRiskColor = (level: string) => {
    const colors: Record<string, any> = {
      Low: 'success',
      Medium: 'warning',
      High: 'error',
      Critical: 'error',
    };
    return colors[level] || 'default';
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Batch Analysis
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Upload CSV file to analyze multiple transactions at once
      </Typography>

      {/* File Upload Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Upload Transaction Data
        </Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          CSV file should include: Time, V1-V28 (PCA features), and Amount columns
        </Alert>

        <Box display="flex" gap={2} alignItems="center">
          <Button
            variant="outlined"
            component="label"
            startIcon={<CloudUpload />}
            sx={{ minWidth: 200 }}
          >
            Select CSV File
            <input
              type="file"
              accept=".csv"
              hidden
              onChange={handleFileChange}
            />
          </Button>
          
          {file && (
            <Box>
              <Typography variant="body2" color="text.secondary">
                Selected: <strong>{file.name}</strong> ({(file.size / 1024).toFixed(2)} KB)
              </Typography>
            </Box>
          )}
        </Box>

        <Button
          variant="contained"
          onClick={handleProcess}
          disabled={!file || loading}
          sx={{ mt: 2 }}
          startIcon={loading ? <CircularProgress size={20} /> : undefined}
        >
          {loading ? 'Processing...' : 'Process Batch'}
        </Button>
      </Paper>

      {/* Results Section */}
      {results.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" fontWeight={600}>
              Analysis Results ({results.length} transactions)
            </Typography>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={handleDownload}
            >
              Download Results
            </Button>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Transaction ID</strong></TableCell>
                  <TableCell align="right"><strong>Amount</strong></TableCell>
                  <TableCell align="center"><strong>Fraud Probability</strong></TableCell>
                  <TableCell align="center"><strong>Risk Level</strong></TableCell>
                  <TableCell align="center"><strong>Recommendation</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((result) => (
                  <TableRow key={result.transaction_id} hover>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {result.transaction_id}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight={600}>
                        ${result.amount.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Typography variant="body2">
                        {(result.fraud_probability * 100).toFixed(1)}%
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={result.risk_level}
                        color={getRiskColor(result.risk_level)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={result.recommendation}
                        variant="outlined"
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Summary Stats */}
          <Box mt={3} p={2} bgcolor="background.default" borderRadius={1}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>Summary Statistics:</strong>
            </Typography>
            <Box display="flex" gap={4}>
              <Typography variant="body2">
                High Risk: <strong>{results.filter((r) => r.risk_level === 'High' || r.risk_level === 'Critical').length}</strong>
              </Typography>
              <Typography variant="body2">
                Medium Risk: <strong>{results.filter((r) => r.risk_level === 'Medium').length}</strong>
              </Typography>
              <Typography variant="body2">
                Low Risk: <strong>{results.filter((r) => r.risk_level === 'Low').length}</strong>
              </Typography>
            </Box>
          </Box>
        </Paper>
      )}
    </Box>
  );
}
