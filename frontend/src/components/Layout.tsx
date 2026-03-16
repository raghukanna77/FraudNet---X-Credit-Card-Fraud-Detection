import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  AppBar,
  Avatar,
  Box,
  CssBaseline,
  Drawer,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  QueryStats as PredictIcon,
  MonitorHeart as MonitorIcon,
  BatchPrediction as BatchIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';

const drawerWidth = 260;

interface LayoutProps {
  children: React.ReactNode;
}

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Predict Transaction', icon: <PredictIcon />, path: '/predict' },
  { text: 'Batch Analysis', icon: <BatchIcon />, path: '/batch' },
  { text: 'Monitoring', icon: <MonitorIcon />, path: '/monitoring' },
];

export default function Layout({ children }: LayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar
        sx={{
            background: 'linear-gradient(135deg, #136f63 0%, #0d4f47 100%)',
            color: 'white',
            minHeight: '86px !important',
        }}
      >
          <Avatar
            sx={{
              mr: 1.4,
              width: 42,
              height: 42,
              bgcolor: 'rgba(255,255,255,0.18)',
              border: '1px solid rgba(255,255,255,0.28)',
            }}
          >
            <SecurityIcon sx={{ fontSize: 22 }} />
          </Avatar>
        <Box>
          <Typography variant="h6" noWrap component="div" fontWeight={700}>
            FraudNet-X
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.9 }}>
              Intelligent Risk Platform
          </Typography>
        </Box>
      </Toolbar>
        <Box sx={{ p: 1.5 }}>
          <Chip
            size="small"
            label="Live Monitoring"
            sx={{
              bgcolor: 'rgba(19, 111, 99, 0.12)',
              color: 'primary.dark',
              fontWeight: 700,
              borderRadius: '8px',
            }}
          />
        </Box>
        <Divider sx={{ mx: 1.5 }} />
        <List sx={{ mt: 1, px: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={Link}
              to={item.path}
              selected={location.pathname === item.path}
              sx={{
                mx: 1,
                mb: 0.75,
                borderRadius: 3,
                minHeight: 46,
                transition: 'all .24s ease',
                '&.Mui-selected': {
                  background: 'linear-gradient(135deg, #136f63 0%, #0d4f47 100%)',
                  color: 'white',
                  boxShadow: '0 10px 22px rgba(19, 111, 99, 0.32)',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
                '&:hover': {
                  transform: 'translateX(3px)',
                  backgroundColor: 'rgba(19, 111, 99, 0.08)',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: location.pathname === item.path ? 'white' : 'inherit',
                  minWidth: 40,
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Box sx={{ mt: 'auto', p: 2.2, color: 'text.secondary' }}>
        <Typography variant="caption">Realtime Security Insights</Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', width: '100%' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          background: 'linear-gradient(100deg, rgba(19,111,99,0.95) 0%, rgba(13,79,71,0.95) 100%)',
          backdropFilter: 'blur(8px)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {menuItems.find((item) => item.path === location.pathname)?.text ||
              'Dashboard'}
          </Typography>
          <Chip
            size="small"
            label="API Live"
            sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: '#fff', fontWeight: 700 }}
          />
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant={isMobile ? 'temporary' : 'permanent'}
          open={isMobile ? mobileOpen : true}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              borderRight: '1px solid rgba(8, 34, 31, 0.08)',
              background: 'linear-gradient(180deg, #f8fffd 0%, #f4f8f8 100%)',
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
          backgroundColor: 'transparent',
          minHeight: '100vh',
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
