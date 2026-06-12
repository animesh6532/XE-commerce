import { api } from './api';
import type { Product } from './product';

export interface ExplanationResponse {
  product_id: number;
  name: string;
  rationale: string;
  score: number;
  factors: Array<{ factor: string; influence: number }>;
}

export interface BudgetRecommendationRequest {
  category: string;
  budget: number;
  top_k?: number;
}

export interface ComparisonResponse {
  product_a: Product;
  product_b: Product;
  comparison: {
    price_difference: number;
    rating_difference: number;
    better_value: string;
    metrics: Array<{ metric: string; val_a: any; val_b: any }>;
  };
}

export const recommendationService = {
  async getPersonalized(topK = 10): Promise<Product[]> {
    const res = await api.get<Product[]>('/api/recommendations/personalized', {
      params: { top_k: topK }
    });
    return res.data;
  },

  async getSimilar(productId: number, topK = 10): Promise<Product[]> {
    const res = await api.get<Product[]>(`/api/recommendations/similar/${productId}`, {
      params: { top_k: topK }
    });
    return res.data;
  },

  async getContentBased(userId: number, topK = 10): Promise<Product[]> {
    const res = await api.get<Product[]>(`/api/recommendations/content-based/${userId}`, {
      params: { top_k: topK }
    });
    return res.data;
  },

  async getCollaborative(userId: number, topK = 10): Promise<Product[]> {
    const res = await api.get<Product[]>(`/api/recommendations/collaborative/${userId}`, {
      params: { top_k: topK }
    });
    return res.data;
  },

  async getHybrid(userId: number, topK = 10): Promise<Product[]> {
    const res = await api.get<Product[]>(`/api/recommendations/hybrid/${userId}`, {
      params: { top_k: topK }
    });
    return res.data;
  },

  async explainRecommendation(productId: number): Promise<ExplanationResponse> {
    const res = await api.get<ExplanationResponse>(`/api/recommendations/explain/${productId}`);
    return res.data;
  },

  async getTrending(): Promise<Product[]> {
    const res = await api.get<Product[]>('/api/recommendations/trending');
    return res.data;
  },

  async getRecentlyViewed(): Promise<Product[]> {
    const res = await api.get<Product[]>('/api/recommendations/recently-viewed');
    return res.data;
  },

  async getCategoryRecommendations(category: string, topK = 10): Promise<Product[]> {
    const res = await api.get<Product[]>(`/api/recommendations/category/${category}`, {
      params: { top_k: topK }
    });
    return res.data;
  },

  async getBudgetRecommendations(payload: BudgetRecommendationRequest): Promise<Product[]> {
    const res = await api.post<Product[]>('/api/recommendations/budget', payload);
    return res.data;
  },

  async getBestDeals(): Promise<Product[]> {
    const res = await api.get<Product[]>('/api/recommendations/best-deals');
    return res.data;
  },

  async getDealFeed(): Promise<Product[]> {
    const res = await api.get<Product[]>('/api/recommendations/deal-feed');
    return res.data;
  },

  async compareProducts(p1: number, p2: number): Promise<ComparisonResponse> {
    const res = await api.get<ComparisonResponse>(`/api/recommendations/compare/${p1}/${p2}`);
    return res.data;
  }
};
