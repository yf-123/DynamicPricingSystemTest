import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  ShoppingOutlined,
  BarChartOutlined,
  SettingOutlined,
  DollarOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

// Import pages
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Pricing from './pages/Pricing';
import Analytics from './pages/Analytics';
import ModelMonitoring from './pages/ModelMonitoring';

const { Header, Sider, Content } = Layout;

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/products',
      icon: <ShoppingOutlined />,
      label: 'Products',
    },
    {
      key: '/pricing',
      icon: <DollarOutlined />,
      label: 'Pricing',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: 'Analytics',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <Layout className="app-layout">
      <Sider
        theme="dark"
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div className="logo">
          DPS
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout style={{ marginLeft: 200 }}>
        <Header
          style={{
            padding: 0,
            background: '#fff',
            boxShadow: '0 1px 4px rgba(0,21,41,.08)',
          }}
        >
          <div style={{ 
            padding: '0 24px',
            fontSize: '18px',
            fontWeight: 'bold',
            color: '#1890ff'
          }}>
            Dynamic Pricing System
          </div>
        </Header>
        <Content className="site-layout-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/products" element={<Products />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/model-monitoring" element={<ModelMonitoring />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App; 