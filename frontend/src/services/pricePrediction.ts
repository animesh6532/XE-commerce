import { api } from './api';

export interface PricePrediction {
  predicted_price: number;
  confidence_lower: number;
  confidence_upper: number;
  optimal_price: number;
  discount_recommendation: number;
}

export interface TrendPoint {
  date: string;
  price: number;
}

export interface PriceHistory {
  product_id: number;
  historical_prices: TrendPoint[];
}

export interface BestTimeToBuyResponse {
  product_id: number;
  current_price: number;
  action: 'BUY' | 'WAIT' | 'HOLD' | string;
  message: string;
  expected_price_change_percentage: number;
  optimal_buy_date?: string;
}

export interface DealScoreResponse {
  product_id: number;
  deal_score: number; // 0 to 100
  rating: 'POOR' | 'FAIR' | 'GOOD' | 'EXCELLENT' | string;
  savings_value: number;
}

export interface PriceComparisonResponse {
  cheapest_product_id: number;
  price_spread: { [productId: number]: number };
  comparison_details: Array<{
    product_id: number;
    name: string;
    current_price: number;
    rating: number;
  }>;
}

export const pricePredictionService = {
  async predictPrice(productId: number): Promise<{ success: boolean; prediction: PricePrediction }> {
    const res = await api.post<{ success: boolean; prediction: PricePrediction }>('/api/price-prediction/predict', {
      product_id: productId
    });
    return res.data;
  },

  async getPriceTrend(productId: number): Promise<{ product_id: number; trend: TrendPoint[] }> {
    const res = await api.get<{ product_id: number; trend: TrendPoint[] }>(`/api/price-prediction/trend/${productId}`);
    return res.data;
  },

  async getPriceHistory(productId: number): Promise<PriceHistory> {
    const res = await api.get<PriceHistory>(`/api/price-prediction/history/${productId}`);
    return res.data;
  },

  async getBestTimeToBuy(productId: number): Promise<BestTimeToBuyResponse> {
    const res = await api.get<BestTimeToBuyResponse>(`/api/price-prediction/best-time/${productId}`);
    return res.data;
  },

  async getDealScore(productId: number): Promise<DealScoreResponse> {
    const res = await api.get<DealScoreResponse>(`/api/price-prediction/deal-score/${productId}`);
    return res.data;
  },

  async comparePrices(productIds: number[]): Promise<PriceComparisonResponse> {
    const res = await api.post<PriceComparisonResponse>('/api/price-prediction/compare', {
      product_ids: productIds
    });
    return res.data;
  },

  async bulkPredict(productIds: number[]): Promise<{ [productId: number]: PricePrediction }> {
    const res = await api.post<{ [productId: number]: PricePrediction }>('/api/price-prediction/bulk-predict', {
      product_ids: productIds
    });
    return res.data;
  },

  async getModelMetrics(): Promise<{ accuracy: number; mean_absolute_error: number; r2_score: number }> {
    const res = await api.get<{ accuracy: number; mean_absolute_error: number; r2_score: number }>('/api/price-prediction/metrics');
    return res.data;
  }
};
