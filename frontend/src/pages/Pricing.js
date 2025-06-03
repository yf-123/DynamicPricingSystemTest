import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  InputNumber,
  Input,
  message,
  Row,
  Col,
  Statistic,
  Alert,
  Tooltip,
  Progress
} from 'antd';
import {
  DollarOutlined,
  RiseOutlined,
  FallOutlined,
  ShoppingCartOutlined,
  UserOutlined,
  ClockCircleOutlined,
  CalendarOutlined,
  ExperimentOutlined,
  ReloadOutlined,
  HistoryOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import { productAPI, pricingAPI, apiUtils } from '../services/api';

const Pricing = () => {
  const [products, setProducts] = useState([]);
  const [competitorPrices, setCompetitorPrices] = useState([]);
  const [pricingAnalytics, setPricingAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [priceModalOpen, setPriceModalOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [pricingHistory, setPricingHistory] = useState([]);
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [productsRes, competitorRes, analyticsRes] = await Promise.all([
        productAPI.getProducts({ per_page: 100 }),
        pricingAPI.getCompetitorPrices(),
        pricingAPI.getPricingAnalytics()
      ]);

      setProducts(productsRes.data.products || []);
      setCompetitorPrices(competitorRes.data || []);
      setPricingAnalytics(analyticsRes.data || {});
    } catch (error) {
      message.error(apiUtils.handleError(error).error);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimizeAll = async () => {
    setOptimizing(true);
    try {
      const response = await pricingAPI.optimizeAllPricing();
      message.success(`Pricing optimization completed. ${response.data.successful} products optimized.`);
      loadData(); // Reload data to show updated prices
    } catch (error) {
      message.error(apiUtils.handleError(error).error);
    } finally {
      setOptimizing(false);
    }
  };

  const handleOptimizeSingle = async (productId) => {
    try {
      const response = await pricingAPI.optimizeSingleProduct(productId);
      if (response.data.success) {
        message.success(`Price optimized for product ${productId}`);
        loadData();
      } else {
        message.error(response.data.error || 'Optimization failed');
      }
    } catch (error) {
      message.error(apiUtils.handleError(error).error);
    }
  };

  const handleManualPriceUpdate = (product) => {
    setSelectedProduct(product);
    form.setFieldsValue({
      price: product.current_price,
      reason: ''
    });
    setPriceModalOpen(true);
  };

  const handlePriceModalOk = async () => {
    try {
      const values = await form.validateFields();
      await pricingAPI.updateProductPrice(selectedProduct.id, values);
      message.success('Price updated successfully');
      setPriceModalOpen(false);
      loadData();
    } catch (error) {
      if (error.errorFields) return;
      message.error(apiUtils.handleError(error).error);
    }
  };

  const handleViewHistory = async (product) => {
    setSelectedProduct(product);
    try {
      const response = await pricingAPI.getPricingHistory(product.id);
      setPricingHistory(response.data.history || []);
      setHistoryModalOpen(true);
    } catch (error) {
      message.error(apiUtils.handleError(error).error);
    }
  };

  const getCompetitorPrice = (productId) => {
    const competitor = competitorPrices.find(c => c.product_id === productId);
    return competitor?.competitor_price;
  };

  const getPriceComparison = (ourPrice, competitorPrice) => {
    if (!competitorPrice) return { status: 'default', text: 'No data' };
    
    const diff = ((ourPrice - competitorPrice) / competitorPrice) * 100;
    if (diff > 10) return { status: 'error', text: `+${diff.toFixed(1)}% vs competitor` };
    if (diff < -10) return { status: 'success', text: `${diff.toFixed(1)}% vs competitor` };
    return { status: 'warning', text: `${diff > 0 ? '+' : ''}${diff.toFixed(1)}% vs competitor` };
  };

  const columns = [
    {
      title: 'Product',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{record.id}</div>
          <div style={{ fontSize: '12px', color: '#8c8c8c' }}>{text}</div>
        </div>
      ),
    },
    {
      title: 'Current Price',
      dataIndex: 'current_price',
      key: 'current_price',
      width: 120,
      render: (price) => (
        <span className="price-tag">${price?.toFixed(2)}</span>
      ),
    },
    {
      title: 'Base Price',
      dataIndex: 'base_price',
      key: 'base_price',
      width: 100,
      render: (price) => `$${price?.toFixed(2)}`,
    },
    {
      title: 'Competitor',
      key: 'competitor',
      width: 120,
      render: (_, record) => {
        const competitorPrice = getCompetitorPrice(record.id);
        return competitorPrice ? `$${competitorPrice.toFixed(2)}` : 'N/A';
      },
    },
    {
      title: 'Comparison',
      key: 'comparison',
      width: 150,
      render: (_, record) => {
        const competitorPrice = getCompetitorPrice(record.id);
        const comparison = getPriceComparison(record.current_price, competitorPrice);
        return <Tag color={comparison.status}>{comparison.text}</Tag>;
      },
    },
    {
      title: 'Profit Margin',
      key: 'margin',
      width: 120,
      render: (_, record) => {
        const margin = ((record.current_price - record.cost_price) / record.cost_price) * 100;
        return (
          <span style={{ color: margin < 15 ? '#ff4d4f' : margin > 30 ? '#52c41a' : '#fa8c16' }}>
            {margin.toFixed(1)}%
          </span>
        );
      },
    },
    {
      title: 'Inventory',
      dataIndex: 'inventory',
      key: 'inventory',
      width: 100,
      render: (inventory) => (
        <span className={inventory <= 10 ? 'status-critical' : inventory <= 20 ? 'status-low' : 'status-normal'}>
          {inventory}
        </span>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="Optimize Price">
            <Button
              type="text"
              icon={<ThunderboltOutlined />}
              onClick={() => handleOptimizeSingle(record.id)}
              size="small"
            />
          </Tooltip>
          <Tooltip title="Manual Price Update">
            <Button
              type="text"
              icon={<DollarOutlined />}
              onClick={() => handleManualPriceUpdate(record)}
              size="small"
            />
          </Tooltip>
          <Tooltip title="Price History">
            <Button
              type="text"
              icon={<HistoryOutlined />}
              onClick={() => handleViewHistory(record)}
              size="small"
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const historyColumns = [
    {
      title: 'Date',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp) => new Date(timestamp).toLocaleDateString(),
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
      dataIndex: 'adjustment_reason',
      key: 'reason',
      ellipsis: true,
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Row justify="space-between" align="middle">
          <Col>
            <h1>Dynamic Pricing</h1>
            <p>AI-powered price optimization and competitor analysis</p>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={loadData}
                loading={loading}
              >
                Refresh Data
              </Button>
              <Button
                type="primary"
                icon={<RiseOutlined />}
                onClick={handleOptimizeAll}
                loading={optimizing}
                size="large"
              >
                Optimize All Prices
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* Analytics Summary */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Products"
              value={pricingAnalytics?.summary?.total_products || 0}
              prefix={<DollarOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Avg Profit Margin"
              value={pricingAnalytics?.summary?.average_profit_margin || 0}
              suffix="%"
              precision={1}
              valueStyle={{ 
                color: (pricingAnalytics?.summary?.average_profit_margin || 0) > 20 ? '#52c41a' : '#fa8c16' 
              }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Low Inventory"
              value={pricingAnalytics?.summary?.low_inventory_products || 0}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Pricing Recommendations */}
      {pricingAnalytics?.summary?.low_inventory_products > 0 && (
        <Alert
          message="Pricing Recommendations"
          description={`${pricingAnalytics.summary.low_inventory_products} products have low inventory and may benefit from price increases.`}
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
          action={
            <Button size="small" type="link" onClick={handleOptimizeAll}>
              Optimize Now
            </Button>
          }
        />
      )}

      {/* Main Pricing Table */}
      <Card title="Product Pricing Overview">
        <Table
          columns={columns}
          dataSource={products}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} products`,
          }}
          scroll={{ x: 1000 }}
        />
      </Card>

      {/* Manual Price Update Modal */}
      <Modal
        title={`Update Price - ${selectedProduct?.name}`}
        open={priceModalOpen}
        onOk={handlePriceModalOk}
        onCancel={() => setPriceModalOpen(false)}
        width={500}
      >
        {selectedProduct && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <Statistic
                  title="Current Price"
                  value={selectedProduct.current_price}
                  prefix="$"
                  precision={2}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="Min Price"
                  value={selectedProduct.cost_price * 1.1}
                  prefix="$"
                  precision={2}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="Max Price"
                  value={selectedProduct.base_price * 1.5}
                  prefix="$"
                  precision={2}
                />
              </Col>
            </Row>
            <Form form={form} layout="vertical">
              <Form.Item
                label="New Price"
                name="price"
                rules={[
                  { required: true, message: 'Price is required' },
                  {
                    validator: (_, value) => {
                      const min = selectedProduct.cost_price * 1.1;
                      const max = selectedProduct.base_price * 1.5;
                      if (value < min || value > max) {
                        return Promise.reject(new Error(`Price must be between $${min.toFixed(2)} and $${max.toFixed(2)}`));
                      }
                      return Promise.resolve();
                    }
                  }
                ]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  precision={2}
                  min={0}
                  formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={value => value.replace(/\$\s?|(,*)/g, '')}
                />
              </Form.Item>
              <Form.Item
                label="Reason for Change"
                name="reason"
              >
                <Input.TextArea
                  placeholder="Optional: Enter reason for price change"
                  rows={3}
                />
              </Form.Item>
            </Form>
          </div>
        )}
      </Modal>

      {/* Price History Modal */}
      <Modal
        title={`Pricing History - ${selectedProduct?.name}`}
        open={historyModalOpen}
        onCancel={() => setHistoryModalOpen(false)}
        footer={null}
        width={800}
      >
        <Table
          columns={historyColumns}
          dataSource={pricingHistory}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          size="small"
        />
      </Modal>
    </div>
  );
};

export default Pricing; 