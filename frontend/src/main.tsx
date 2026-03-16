import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createTheme, ThemeProvider, CssBaseline } from '@mui/material';
import { Toaster } from 'react-hot-toast';
import App from './App';
import './styles.css';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

// Create MUI theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#136f63',
      light: '#2f8d80',
      dark: '#0d4f47',
    },
    secondary: {
      main: '#ff7f11',
      light: '#ffa34c',
      dark: '#d96400',
    },
    success: {
      main: '#15803d',
    },
    warning: {
      main: '#eab308',
    },
    error: {
      main: '#dc2626',
    },
    background: {
      default: '#f6f8f7',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Manrope", "Segoe UI", sans-serif',
    h1: {
      fontWeight: 800,
    },
    h2: {
      fontWeight: 800,
    },
    h3: {
      fontWeight: 700,
    },
    h4: {
      fontFamily: '"Space Grotesk", "Manrope", sans-serif',
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h5: {
      fontFamily: '"Space Grotesk", "Manrope", sans-serif',
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
  },
  shape: {
    borderRadius: 14,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 12,
          fontWeight: 700,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 16px 40px rgba(7, 23, 21, 0.08)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 14px 36px rgba(11, 21, 20, 0.06)',
        },
      },
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#4caf50',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#f44336',
                secondary: '#fff',
              },
            },
          }}
        />
      </ThemeProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
