import { api } from './api';

export interface DashboardOverview {
  total_users: number;
  total_products: number;
  total_orders: number;
  total_revenue: number;
}

export interface MonthlySale {
  month: string;
  sales: number;
  revenue: number;
}

export interface CategoryAnalytic {
  category: string;
  total_sales: number;
  revenue: number;
}

export interface DemandForecastPoint {
  day: string;
  orders: number;
}

export const analyticsService = {
  async getDashboardOverview(): Promise<DashboardOverview> {
    const res = await api.get<DashboardOverview>('/api/analytics/dashboard');
    return res.data;
  },

  async getSalesAnalytics(): Promise<any> {
    const res = await api.get('/api/analytics/sales');
    return res.data;
  },

  async getRevenueAnalytics(): Promise<any> {
    const res = await api.get('/api/analytics/revenue');
    return res.data;
  },

  async getMonthlySales(): Promise<MonthlySale[]> {
    const res = await api.get<MonthlySale[]>('/api/analytics/monthly-sales');
    return res.data;
  },

  async getTopSellingProducts(limit = 10): Promise<any[]> {
    const res = await api.get<any[]>('/api/analytics/top-products', {
      params: { limit }
    });
    return res.data;
  },

  async getCategoryAnalytics(): Promise<CategoryAnalytic[]> {
    const res = await api.get<CategoryAnalytic[]>('/api/analytics/categories');
    return res.data;
  },

  async getUserAnalytics(): Promise<any> {
    const res = await api.get('/api/analytics/users');
    return res.data;
  },

  async getCustomerActivity(): Promise<any> {
    const res = await api.get('/api/analytics/customer-activity');
    return res.data;
  },

  async getOrderAnalytics(): Promise<any> {
    const res = await api.get('/api/analytics/orders');
    return res.data;
  },

  async getReviewAnalytics(): Promise<any> {
    const res = await api.get('/api/analytics/reviews');
    return res.data;
  },

  async getSentimentStatistics(): Promise<any> {
    const res = await api.get('/api/analytics/sentiment');
    return res.data;
  },

  async getFakeReviewStatistics(): Promise<any> {
    const res = await api.get('/api/analytics/fake-reviews');
    return res.data;
  },

  async getRecommendationAnalytics(): Promise<any> {
    const res = await api.get('/api/analytics/recommendations');
    return res.data;
  },

  async getModelPerformance(): Promise<any> {
    const res = await api.get('/api/analytics/model-performance');
    return res.data;
  },

  async getInventoryAnalytics(): Promise<any> {
    const res = await api.get('/api/analytics/inventory');
    return res.data;
  },

  async getDemandForecast(): Promise<DemandForecastPoint[]> {
    const res = await api.get<DemandForecastPoint[]>('/api/analytics/demand-forecast');
    return res.data;
  },

  async getPricePredictionAnalytics(): Promise<any> {
    const res = await api.get('/api/analytics/price-prediction');
    return res.data;
  },

  async getCompleteReport(): Promise<any> {
    const res = await api.get('/api/analytics/report');
    return res.data;
  }
};
