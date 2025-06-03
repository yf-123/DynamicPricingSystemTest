import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 1000000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Product API
export const productAPI = {
  // Get all products with pagination and filtering
  getProducts: (params = {}) => api.get('/products', { params }),
  
  // Get single product
  getProduct: (id) => api.get(`/products/${id}`),
  
  // Create new product
  createProduct: (data) => api.post('/products', data),
  
  // Update product
  updateProduct: (id, data) => api.put(`/products/${id}`, data),
  
  // Delete product
  deleteProduct: (id) => api.delete(`/products/${id}`),
  
  // Get product sales history
  getProductSales: (id) => api.get(`/products/${id}/sales`),
  
  // Get product categories
  getCategories: () => api.get('/products/categories'),
};

// Pricing API
export const pricingAPI = {
  // Optimize pricing for all products
  optimizeAllPricing: (data = {}) => api.post('/pricing/optimize', data),
  
  // Optimize pricing for single product
  optimizeSingleProduct: (productId) => api.post(`/pricing/product/${productId}/optimize`),
  
  // Update product price manually
  updateProductPrice: (productId, data) => api.put(`/pricing/product/${productId}/price`, data),
  
  // Get pricing history for product
  getPricingHistory: (productId, params = {}) => api.get(`/pricing/product/${productId}/history`, { params }),
  
  // Get competitor prices
  getCompetitorPrices: () => api.get('/pricing/competitor-prices'),
  
  // Get pricing analytics
  getPricingAnalytics: () => api.get('/pricing/analytics'),
};

// Analytics API
export const analyticsAPI = {
  // Get dashboard data
  getDashboardData: () => api.get('/analytics/dashboard'),
  
  // Get sales trends
  getSalesTrends: (params = {}) => api.get('/analytics/sales-trends', { params }),
  
  // Get inventory analysis
  getInventoryAnalysis: () => api.get('/analytics/inventory-analysis'),
  
  // Get pricing impact analysis
  getPricingImpact: () => api.get('/analytics/pricing-impact'),
  
  // Generate monthly report
  getMonthlyReport: (params = {}) => api.get('/analytics/reports/monthly', { params }),
};

// Utility functions
export const apiUtils = {
  // Handle API errors consistently
  handleError: (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.error || error.response.data?.message || 'Server error';
      return { success: false, error: message };
    } else if (error.request) {
      // Request made but no response
      return { success: false, error: 'Network error - please check your connection' };
    } else {
      // Something else happened
      return { success: false, error: error.message || 'Unknown error occurred' };
    }
  },
  
  // Format API response consistently
  formatResponse: (response) => {
    return {
      success: true,
      data: response.data,
      status: response.status,
    };
  },
};

export default api; 