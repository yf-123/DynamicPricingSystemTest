import React, { useState, useEffect } from 'react';
import {
  Table,
  Card,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  message,
  Popconfirm,
  Tooltip,
  Badge,
  Row,
  Col,
  Statistic
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  ShoppingOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { productAPI, apiUtils } from '../services/api';

const { Option } = Select;
const { Search } = Input;

const Products = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [filters, setFilters] = useState({
    search: '',
    category: '',
  });
  const [categories, setCategories] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadProducts();
    loadCategories();
  }, [pagination.current, pagination.pageSize, filters]);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.current,
        per_page: pagination.pageSize,
        ...filters,
      };
      
      const response = await productAPI.getProducts(params);
      const data = response.data;
      
      setProducts(data.products || []);
      setPagination(prev => ({
        ...prev,
        total: data.total || 0,
      }));
    } catch (error) {
      message.error(apiUtils.handleError(error).error);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await productAPI.getCategories();
      setCategories(response.data || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
  };

  const handleSearch = (value) => {
    setFilters(prev => ({ ...prev, search: value }));
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleCategoryFilter = (value) => {
    setFilters(prev => ({ ...prev, category: value }));
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleAdd = () => {
    setEditingProduct(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    form.setFieldsValue(product);
    setIsModalOpen(true);
  };

  const handleDelete = async (productId) => {
    try {
      await productAPI.deleteProduct(productId);
      message.success('Product deleted successfully');
      loadProducts();
    } catch (error) {
      message.error(apiUtils.handleError(error).error);
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingProduct) {
        await productAPI.updateProduct(editingProduct.id, values);
        message.success('Product updated successfully');
      } else {
        await productAPI.createProduct(values);
        message.success('Product created successfully');
      }
      
      setIsModalOpen(false);
      loadProducts();
    } catch (error) {
      if (error.errorFields) {
        return;
      }
      message.error(apiUtils.handleError(error).error);
    }
  };

  const getInventoryStatus = (inventory) => {
    if (inventory <= 5) return { status: 'error', text: 'Critical' };
    if (inventory <= 20) return { status: 'warning', text: 'Low' };
    return { status: 'success', text: 'Normal' };
  };

  const columns = [
    {
      title: 'Product ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
      fixed: 'left',
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
            {record.description}
          </div>
        </div>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category) => <Tag color="blue">{category}</Tag>,
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
      title: 'Cost Price',
      dataIndex: 'cost_price',
      key: 'cost_price',
      width: 100,
      render: (price) => `$${price?.toFixed(2)}`,
    },
    {
      title: 'Inventory',
      dataIndex: 'inventory',
      key: 'inventory',
      width: 100,
      render: (inventory) => {
        const status = getInventoryStatus(inventory);
        return (
          <Badge
            status={status.status}
            text={`${inventory} (${status.text})`}
          />
        );
      },
      sorter: (a, b) => a.inventory - b.inventory,
    },
    {
      title: 'Sales (30d)',
      dataIndex: 'sales_last_30_days',
      key: 'sales',
      width: 100,
      sorter: (a, b) => a.sales_last_30_days - b.sales_last_30_days,
    },
    {
      title: 'Rating',
      dataIndex: 'average_rating',
      key: 'rating',
      width: 80,
      render: (rating) => `${rating?.toFixed(1)}⭐`,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="Edit">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="Delete Product"
            description="Are you sure you want to delete this product?"
            onConfirm={() => handleDelete(record.id)}
            icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
          >
            <Tooltip title="Delete">
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const totalProducts = products.length;
  const lowInventoryCount = products.filter(p => p.inventory <= 10).length;
  const avgPrice = products.length > 0 
    ? products.reduce((sum, p) => sum + p.current_price, 0) / products.length 
    : 0;

  return (
    <div>
      <div className="page-header">
        <h1>Product Management</h1>
        <p>Manage your product catalog and inventory</p>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Total Products"
              value={totalProducts}
              prefix={<ShoppingOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Low Inventory"
              value={lowInventoryCount}
              valueStyle={{ color: lowInventoryCount > 0 ? '#ff4d4f' : '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Average Price"
              value={avgPrice}
              precision={2}
              prefix="$"
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row gutter={[16, 16]} justify="space-between">
            <Col xs={24} sm={12} lg={8}>
              <Search
                placeholder="Search products..."
                allowClear
                onSearch={handleSearch}
                style={{ width: '100%' }}
              />
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Select
                placeholder="Filter by category"
                allowClear
                onChange={handleCategoryFilter}
                style={{ width: '100%' }}
              >
                {categories.map(category => (
                  <Option key={category} value={category}>
                    {category}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col>
              <Space>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={loadProducts}
                />
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleAdd}
                >
                  Add Product
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        <Table
          columns={columns}
          dataSource={products}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} products`,
          }}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
        />
      </Card>

      <Modal
        title={editingProduct ? 'Edit Product' : 'Add Product'}
        open={isModalOpen}
        onOk={handleModalOk}
        onCancel={() => setIsModalOpen(false)}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          requiredMark={false}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Product ID"
                name="id"
                rules={[{ required: true, message: 'Product ID is required' }]}
              >
                <Input
                  placeholder="e.g., P001"
                  disabled={!!editingProduct}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Category"
                name="category"
                rules={[{ required: true, message: 'Category is required' }]}
              >
                <Select placeholder="Select category">
                  <Option value="Electronics">Electronics</Option>
                  <Option value="Apparel">Apparel</Option>
                  <Option value="Home">Home</Option>
                  <Option value="Books">Books</Option>
                  <Option value="Luxury">Luxury</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="Product Name"
            name="name"
            rules={[{ required: true, message: 'Product name is required' }]}
          >
            <Input placeholder="Enter product name" />
          </Form.Item>

          <Form.Item
            label="Description"
            name="description"
          >
            <Input.TextArea
              placeholder="Enter product description"
              rows={2}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="Base Price ($)"
                name="base_price"
                rules={[{ required: true, message: 'Base price is required' }]}
              >
                <InputNumber
                  min={0}
                  precision={2}
                  style={{ width: '100%' }}
                  placeholder="0.00"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="Cost Price ($)"
                name="cost_price"
                rules={[{ required: true, message: 'Cost price is required' }]}
              >
                <InputNumber
                  min={0}
                  precision={2}
                  style={{ width: '100%' }}
                  placeholder="0.00"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="Inventory"
                name="inventory"
                rules={[{ required: true, message: 'Inventory is required' }]}
              >
                <InputNumber
                  min={0}
                  style={{ width: '100%' }}
                  placeholder="0"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Sales (Last 30 days)"
                name="sales_last_30_days"
              >
                <InputNumber
                  min={0}
                  style={{ width: '100%' }}
                  placeholder="0"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Average Rating"
                name="average_rating"
              >
                <InputNumber
                  min={0}
                  max={5}
                  step={0.1}
                  precision={1}
                  style={{ width: '100%' }}
                  placeholder="0.0"
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default Products; 