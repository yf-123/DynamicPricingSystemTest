import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Select,
  DatePicker,
  Table,
  Statistic,
  Alert,
  Tag,
  Tabs,
  Button
} from 'antd';
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
  Cell,
  ScatterChart,
  Scatter
} from 'recharts';
import {
  LineChartOutlined,
  BarChartOutlined,
  PieChartOutlined,
  RiseOutlined,
  FallOutlined,
  DollarOutlined,
  ShoppingCartOutlined,
  UserOutlined,
  ClockCircleOutlined,
  CalendarOutlined,
  DownloadOutlined,
  WarningOutlined,
  ShoppingOutlined
} from '@ant-design/icons';
import { analyticsAPI, apiUtils } from '../services/api';
import moment from 'moment';

const { Option } = Select;
const { RangePicker } = DatePicker;
const { TabPane } = Tabs;

const Analytics = () => {
  const [salesTrends, setSalesTrends] = useState([]);
  const [inventoryAnalysis, setInventoryAnalysis] = useState(null);
  const [pricingImpact, setPricingImpact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState(30);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

  useEffect(() => {
    loadAnalyticsData();
  }, [dateRange]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      const [trendsRes, inventoryRes, pricingRes] = await Promise.all([
        analyticsAPI.getSalesTrends({ days: dateRange }),
        analyticsAPI.getInventoryAnalysis(),
        analyticsAPI.getPricingImpact()
      ]);

      setSalesTrends(trendsRes.data.daily_sales || []);
      setInventoryAnalysis(inventoryRes.data);
      setPricingImpact(pricingRes.data);
    } catch (error) {
      console.error('Failed to load analytics data:', apiUtils.handleError(error).error);
    } finally {
      setLoading(false);
    }
  };

  const generateMonthlyReport = async () => {
    try {
      const currentDate = new Date();
      const response = await analyticsAPI.getMonthlyReport({
        year: currentDate.getFullYear(),
        month: currentDate.getMonth() + 1
      });
      
      // In a real app, you'd download or display this report
      console.log('Monthly Report:', response.data);
      // For demo, just show an alert
      alert('Monthly report generated! Check console for details.');
    } catch (error) {
      console.error('Failed to generate report:', error);
    }
  };

  const salesColumns = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      render: (date) => moment(date).format('MMM DD'),
    },
    {
      title: 'Units Sold',
      dataIndex: 'units_sold',
      key: 'units_sold',
      sorter: (a, b) => a.units_sold - b.units_sold,
    },
    {
      title: 'Revenue',
      dataIndex: 'revenue',
      key: 'revenue',
      render: (revenue) => `$${revenue?.toFixed(2)}`,
      sorter: (a, b) => a.revenue - b.revenue,
    },
  ];

  const inventoryColumns = [
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
      title: 'Inventory',
      dataIndex: 'inventory',
      key: 'inventory',
      render: (inventory) => (
        <span className={inventory <= 5 ? 'status-critical' : inventory <= 20 ? 'status-low' : 'status-normal'}>
          {inventory}
        </span>
      ),
    },
    {
      title: 'Sales (30d)',
      dataIndex: 'sales_last_30_days',
      key: 'sales',
    },
    {
      title: 'Status',
      key: 'status',
      render: (_, record) => {
        if (record.inventory <= 5) {
          return <Tag color="red">Critical</Tag>;
        }
        if (record.inventory <= 20) {
          return <Tag color="orange">Low</Tag>;
        }
        return <Tag color="green">Normal</Tag>;
      },
    },
  ];

  const pricingImpactColumns = [
    {
      title: 'Product',
      dataIndex: 'product_name',
      key: 'product_name',
      ellipsis: true,
    },
    {
      title: 'Price Change',
      key: 'price_change',
      render: (_, record) => {
        const change = record.price_change?.price_change_percent || 0;
        return (
          <span className={change > 0 ? 'price-increase' : change < 0 ? 'price-decrease' : 'price-stable'}>
            {change > 0 ? '+' : ''}{change?.toFixed(1)}%
          </span>
        );
      },
    },
    {
      title: 'Sales Before',
      dataIndex: 'sales_before',
      key: 'sales_before',
    },
    {
      title: 'Sales After',
      dataIndex: 'sales_after',
      key: 'sales_after',
    },
    {
      title: 'Impact',
      dataIndex: 'sales_impact_percent',
      key: 'impact',
      render: (impact) => (
        <span className={impact > 0 ? 'trend-up' : impact < 0 ? 'trend-down' : 'trend-stable'}>
          {impact > 0 ? '+' : ''}{impact?.toFixed(1)}%
        </span>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Row justify="space-between" align="middle">
          <Col>
            <h1>Analytics & Reports</h1>
            <p>Comprehensive insights into sales performance and pricing effectiveness</p>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={generateMonthlyReport}
            >
              Generate Monthly Report
            </Button>
          </Col>
        </Row>
      </div>

      <Tabs defaultActiveKey="sales" size="large">
        <TabPane tab="Sales Trends" key="sales">
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col span={12}>
              <Select
                value={dateRange}
                onChange={setDateRange}
                style={{ width: 200 }}
              >
                <Option value={7}>Last 7 days</Option>
                <Option value={30}>Last 30 days</Option>
                <Option value={90}>Last 90 days</Option>
              </Select>
            </Col>
          </Row>

          <Row gutter={[16, 16]}>
            <Col xs={24} lg={16}>
              <Card title="Revenue Trends" loading={loading}>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={salesTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tickFormatter={(date) => moment(date).format('MMM DD')}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(date) => moment(date).format('MMM DD, YYYY')}
                      formatter={(value, name) => [
                        name === 'revenue' ? `$${value?.toFixed(2)}` : value,
                        name === 'revenue' ? 'Revenue' : 'Units Sold'
                      ]}
                    />
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
              <Card title="Units Sold" loading={loading}>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={salesTrends.slice(-7)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tickFormatter={(date) => moment(date).format('MMM DD')}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(date) => moment(date).format('MMM DD, YYYY')}
                    />
                    <Bar dataKey="units_sold" fill="#52c41a" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          <Row style={{ marginTop: 24 }}>
            <Col span={24}>
              <Card title="Daily Sales Data">
                <Table
                  columns={salesColumns}
                  dataSource={salesTrends.slice(-10)}
                  rowKey="date"
                  pagination={false}
                  size="small"
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane tab="Inventory Analysis" key="inventory">
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={8}>
              <Card>
                <Statistic
                  title="Critical Inventory"
                  value={inventoryAnalysis?.inventory_status?.critical?.length || 0}
                  valueStyle={{ color: '#ff4d4f' }}
                  prefix={<WarningOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={8}>
              <Card>
                <Statistic
                  title="Low Inventory"
                  value={inventoryAnalysis?.inventory_status?.low?.length || 0}
                  valueStyle={{ color: '#fa8c16' }}
                  prefix={<ShoppingOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={8}>
              <Card>
                <Statistic
                  title="Normal Inventory"
                  value={inventoryAnalysis?.inventory_status?.normal_count || 0}
                  valueStyle={{ color: '#52c41a' }}
                  prefix={<RiseOutlined />}
                />
              </Card>
            </Col>
          </Row>

          {inventoryAnalysis?.inventory_status?.critical?.length > 0 && (
            <Alert
              message="Critical Inventory Alert"
              description={`${inventoryAnalysis.inventory_status.critical.length} products have critically low inventory (≤5 units).`}
              type="error"
              showIcon
              style={{ marginBottom: 24 }}
            />
          )}

          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title="Inventory Distribution by Category" loading={loading}>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={inventoryAnalysis?.category_inventory || []}
                      dataKey="total_inventory"
                      nameKey="category"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                    >
                      {(inventoryAnalysis?.category_inventory || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="High Turnover Products" loading={loading}>
                <Table
                  columns={inventoryColumns}
                  dataSource={inventoryAnalysis?.turnover_analysis?.high_turnover || []}
                  rowKey="id"
                  pagination={false}
                  size="small"
                />
              </Card>
            </Col>
          </Row>

          <Row style={{ marginTop: 24 }}>
            <Col span={24}>
              <Card title="Products Requiring Attention">
                <Table
                  columns={inventoryColumns}
                  dataSource={[
                    ...(inventoryAnalysis?.inventory_status?.critical || []),
                    ...(inventoryAnalysis?.inventory_status?.low || [])
                  ]}
                  rowKey="id"
                  pagination={{ pageSize: 10 }}
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane tab="Pricing Impact" key="pricing">
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col span={24}>
              <Alert
                message="Pricing Impact Analysis"
                description="Analysis of how recent price changes have affected sales performance"
                type="info"
                showIcon
              />
            </Col>
          </Row>

          <Row gutter={[16, 16]}>
            <Col xs={24} lg={16}>
              <Card title="Price vs Sales Impact" loading={loading}>
                <ResponsiveContainer width="100%" height={400}>
                  <ScatterChart data={pricingImpact?.pricing_impact || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="price_change.price_change_percent"
                      type="number"
                      domain={['dataMin - 5', 'dataMax + 5']}
                      name="Price Change %"
                    />
                    <YAxis 
                      dataKey="sales_impact_percent"
                      type="number"
                      domain={['dataMin - 10', 'dataMax + 10']}
                      name="Sales Impact %"
                    />
                    <Tooltip 
                      formatter={(value, name) => [
                        `${value?.toFixed(1)}%`,
                        name === 'sales_impact_percent' ? 'Sales Impact' : 'Price Change'
                      ]}
                    />
                    <Scatter dataKey="sales_impact_percent" fill="#1890ff" />
                  </ScatterChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col xs={24} lg={8}>
              <Card title="Price Elasticity" loading={loading}>
                <div style={{ padding: '20px 0' }}>
                  {(pricingImpact?.price_elasticity || []).slice(0, 5).map((item, index) => (
                    <div key={item.product_id} style={{ marginBottom: 16 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>{item.product_name}</span>
                        <Tag color={Math.abs(item.price_elasticity) > 1 ? 'red' : 'green'}>
                          {item.interpretation}
                        </Tag>
                      </div>
                      <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
                        Elasticity: {item.price_elasticity?.toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </Col>
          </Row>

          <Row style={{ marginTop: 24 }}>
            <Col span={24}>
              <Card title="Recent Pricing Changes Impact">
                <Table
                  columns={pricingImpactColumns}
                  dataSource={pricingImpact?.pricing_impact || []}
                  rowKey="product_id"
                  pagination={{ pageSize: 10 }}
                />
              </Card>
            </Col>
          </Row>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default Analytics; 