import { Paper, Typography, Box } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const mockData = [
  { name: 'Low', value: 850, color: '#4caf50' },
  { name: 'Medium', value: 120, color: '#ff9800' },
  { name: 'High', value: 25, color: '#f44336' },
  { name: 'Critical', value: 5, color: '#9c27b0' },
];

export default function RiskDistributionChart() {
  return (
    <Paper sx={{ p: 3, height: '100%' }}>
      <Typography variant="h6" fontWeight={600} gutterBottom>
        Risk Distribution
      </Typography>
      <Box sx={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={mockData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {mockData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </Box>
      <Box mt={2} display="flex" flexWrap="wrap" gap={2}>
        {mockData.map((item) => (
          <Box key={item.name} display="flex" alignItems="center">
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: item.color,
                mr: 0.5,
              }}
            />
            <Typography variant="body2">
              {item.name}: <strong>{item.value}</strong>
            </Typography>
          </Box>
        ))}
      </Box>
    </Paper>
  );
}
