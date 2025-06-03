import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Spin, Alert, Button } from 'antd';
import {
  ShoppingOutlined,
  DollarOutlined,
  WarningOutlined,
  RiseOutlined,
  ReloadOutlined,
  DashboardOutlined,
  FallOutlined,
  ShoppingCartOutlined,
  UserOutlined,
  ClockCircleOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { analyticsAPI, pricingAPI, apiUtils } from '../services/api';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [salesTrends, setSalesTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [dashboardResponse, trendsResponse] = await Promise.all([
        analyticsAPI.getDashboardData(),
        analyticsAPI.getSalesTrends({ days: 30 })
      ]);

      setDashboardData(dashboardResponse.data);
      setSalesTrends(trendsResponse.data.daily_sales || []);
    } catch (err) {
      setError(apiUtils.handleError(err).error);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimizeAllPricing = async () => {
    try {
      setLoading(true);
      await pricingAPI.optimizeAllPricing();
      // Reload dashboard data after optimization
      await loadDashboardData();
    } catch (err) {
      setError(apiUtils.handleError(err).error);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !dashboardData) {
    return (
      <div className="loading-container">
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Error loading dashboard"
        description={error}
        type="error"
        showIcon
        action={
          <Button size="small" onClick={loadDashboardData}>
            Retry
          </Button>
        }
      />
    );
  }

  const topProductColumns = [
    {
      title: 'Product ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: 'Sales (30d)',
      dataIndex: 'sales_last_30_days',
      key: 'sales',
      sorter: (a, b) => a.sales_last_30_days - b.sales_last_30_days,
    },
    {
      title: 'Current Price',
      dataIndex: 'current_price',
      key: 'price',
      render: (price) => `$${price?.toFixed(2)}`,
    },
    {
      title: 'Inventory',
      dataIndex: 'inventory',
      key: 'inventory',
      render: (inventory) => (
        <span className={inventory <= 10 ? 'status-critical' : inventory <= 20 ? 'status-low' : 'status-normal'}>
          {inventory}
        </span>
      ),
    },
  ];

  const recentPricingColumns = [
    {
      title: 'Product ID',
      dataIndex: 'product_id',
      key: 'product_id',
    },
    {
      title: 'Old Price',
      dataIndex: 'old_price',
      key: 'old_price',
      render: (price) => `$${price?.toFixed(2)}`,
    },
    {
      title: 'New Price',
      dataIndex: 'new_price',
      key: 'new_price',
      render: (price) => `$${price?.toFixed(2)}`,
    },
    {
      title: 'Change',
      dataIndex: 'price_change_percent',
      key: 'change',
      render: (change) => (
        <span className={change > 0 ? 'price-increase' : change < 0 ? 'price-decrease' : 'price-stable'}>
          {change > 0 ? '+' : ''}{change?.toFixed(1)}%
        </span>
      ),
    },
    {
      title: 'Reason',
      dataIndex: 'adjustment_type',
      key: 'reason',
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Row justify="space-between" align="middle">
          <Col>
            <h1>Dashboard</h1>
            <p>Overview of your dynamic pricing system performance</p>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<RiseOutlined />}
              onClick={handleOptimizeAllPricing}
              loading={loading}
            >
              Optimize All Pricing
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadDashboardData}
              style={{ marginLeft: 8 }}
            >
              Refresh
            </Button>
          </Col>
        </Row>
      </div>

      {/* Summary Cards */}
      <Row gutter={[16, 16]} className="dashboard-cards">
        <Col xs={24} sm={12} lg={6}>
          <Card className="card-hover">
            <Statistic
              title="Total Products"
              value={dashboardData?.summary?.total_products || 0}
              prefix={<ShoppingOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="card-hover">
            <Statistic
              title="Total Revenue"
              value={dashboardData?.summary?.total_revenue || 0}
              prefix={<DollarOutlined />}
              precision={2}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="card-hover">
            <Statistic
              title="Sales (7 days)"
              value={dashboardData?.summary?.recent_sales_7_days || 0}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="card-hover">
            <Statistic
              title="Low Inventory"
              value={dashboardData?.summary?.low_inventory_count || 0}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts Section */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="Sales Trends (Last 30 Days)" className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={salesTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#1890ff"
                  fill="#1890ff"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Category Performance" className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={dashboardData?.category_performance || []}
                  dataKey="total_sales"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                >
                  {(dashboardData?.category_performance || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Tables Section */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Top Performing Products">
            <Table
              dataSource={dashboardData?.top_products || []}
              columns={topProductColumns}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Recent Pricing Changes">
            <Table
              dataSource={dashboardData?.recent_pricing_changes || []}
              columns={recentPricingColumns}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 