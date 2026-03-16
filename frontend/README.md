# FraudNet-X React Frontend

Modern, production-ready React frontend for the FraudNet-X Fraud Detection System.

## 🚀 Features

- **Real-time Dashboard**: Monitor system metrics, model status, and recent predictions
- **Transaction Prediction**: Interactive form for analyzing individual transactions
- **Batch Analysis**: Upload CSV files to process multiple transactions at once
- **System Monitoring**: Track model health, performance metrics, and drift detection
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Modern UI**: Built with Material-UI for a professional, polished interface

## 📋 Prerequisites

- Node.js 18+ and npm/yarn
- FraudNet-X API running on `http://localhost:8000`

## 🛠️ Installation

```bash
cd frontend
npm install
```

## 🏃 Running the Application

### Development Mode

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Production Build

```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Layout.tsx       # Main layout with sidebar
│   │   ├── Dashboard.tsx    # Dashboard overview
│   │   ├── PredictionPage.tsx      # Single prediction
│   │   ├── BatchAnalysisPage.tsx   # Batch processing
│   │   ├── MonitoringPage.tsx      # System monitoring
│   │   └── ...
│   ├── services/
│   │   └── api.ts           # API client with axios
│   ├── types/
│   │   └── index.ts         # TypeScript type definitions
│   ├── App.tsx              # Main app component
│   └── main.tsx             # Entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html
```

## 🎨 Key Components

### Dashboard
- **System Overview**: Key metrics and statistics
- **Model Status**: Real-time model loading status
- **Risk Distribution**: Visual pie chart of risk levels
- **Recent Predictions**: Latest transaction analyses

### Prediction Page
- **Transaction Form**: Input all 30 features (Time, V1-V28, Amount)
- **Sample Generator**: Quickly generate random test data
- **Risk Gauge**: Visual risk score display
- **Detailed Results**: Fraud probability, confidence, recommendations

### Batch Analysis
- **CSV Upload**: Process multiple transactions from file
- **Results Table**: View all predictions in a table
- **Download Results**: Export analysis results as CSV
- **Summary Stats**: Aggregate statistics

### Monitoring
- **API Health**: Real-time system status
- **Drift Detection**: Alerts for concept drift
- **Performance Metrics**: Accuracy, latency, throughput
- **Model Information**: Detailed model metadata

## 🔧 Configuration

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

## 🎯 API Integration

The frontend connects to these API endpoints:

- `GET /` - API info
- `GET /health` - System health check
- `POST /predict` - Single transaction prediction
- `GET /metrics` - System metrics
- `GET /model-info` - Model information

## 🧪 Development

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## 📦 Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Material-UI (MUI)** - Component library
- **React Router** - Navigation
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **React Gauge Chart** - Risk score gauge
- **React Hot Toast** - Notifications

## 🔐 Features Highlights

### Real-time Updates
- Automatic polling for health status (10s)
- Metrics refresh every 5 seconds
- Live drift detection alerts

### User Experience
- Loading states and error handling
- Toast notifications for actions
- Responsive design for all screen sizes
- Intuitive navigation with sidebar

### Data Visualization
- Risk distribution pie chart
- Risk gauge with color-coded levels
- Performance metrics cards
- Model status indicators

## 🚀 Deployment

### Docker Deployment

The frontend can be deployed with Docker:

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Build Command

```bash
docker build -t fraudnet-x-frontend .
docker run -p 80:80 fraudnet-x-frontend
```

## 📖 Usage Examples

### Single Transaction Prediction

1. Navigate to "Predict Transaction"
2. Fill in Time and Amount values
3. Click "Generate Sample" for random V1-V28 values (or enter manually)
4. Click "Predict"
5. View risk score, probability, and recommendations

### Batch Analysis

1. Navigate to "Batch Analysis"
2. Click "Select CSV File" and choose your file
3. Click "Process Batch"
4. Review results in the table
5. Click "Download Results" to export

### Monitoring

1. Navigate to "Monitoring"
2. View real-time system status
3. Check model loading status
4. Monitor performance metrics
5. Receive drift detection alerts

## 🤝 Contributing

1. Follow the existing code style
2. Use TypeScript for all new components
3. Add proper type definitions
4. Test on multiple screen sizes
5. Ensure accessibility best practices

## 📄 License

Part of the FraudNet-X project. See main project LICENSE for details.

## 🙏 Acknowledgments

- Material-UI for the excellent component library
- Recharts for beautiful data visualizations
- React Query for powerful data fetching
