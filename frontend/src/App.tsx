import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import PredictionPage from './components/PredictionPage';
import MonitoringPage from './components/MonitoringPage';
import BatchAnalysisPage from './components/BatchAnalysisPage';

function App() {
  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Box className="app-shell" sx={{ display: 'flex', minHeight: '100vh', width: '100%' }}>
        <Box className="bg-orb bg-orb-a" />
        <Box className="bg-orb bg-orb-b" />
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/predict" element={<PredictionPage />} />
            <Route path="/monitoring" element={<MonitoringPage />} />
            <Route path="/batch" element={<BatchAnalysisPage />} />
          </Routes>
        </Layout>
      </Box>
    </Router>
  );
}

export default App;
