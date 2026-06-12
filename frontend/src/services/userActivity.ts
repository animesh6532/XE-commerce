import { api } from './api';
import type { Product } from './product';

export interface BehaviorAnalytics {
  total_clicks: number;
  total_searches: number;
  total_views: number;
  most_viewed_category: string;
  average_session_duration: number;
}

export interface UserPreferences {
  top_categories: string[];
  top_brands: string[];
  preferred_price_range: { min: number; max: number };
}

export const userActivityService = {
  async trackView(productId: number): Promise<{ success: boolean }> {
    const res = await api.post<{ success: boolean }>('/api/user-activity/view', {
      product_id: productId
    });
    return res.data;
  },

  async trackSearch(query: string): Promise<{ success: boolean }> {
    const res = await api.post<{ success: boolean }>('/api/user-activity/search', {
      query
    });
    return res.data;
  },

  async trackClick(productId: number, source?: string): Promise<{ success: boolean }> {
    const res = await api.post<{ success: boolean }>('/api/user-activity/click', {
      product_id: productId,
      source: source || null
    });
    return res.data;
  },

  async getCartActivity(): Promise<any> {
    const res = await api.get('/api/user-activity/cart');
    return res.data;
  },

  async getWishlistActivity(): Promise<any> {
    const res = await api.get('/api/user-activity/wishlist');
    return res.data;
  },

  async getPurchaseHistory(): Promise<any> {
    const res = await api.get('/api/user-activity/purchases');
    return res.data;
  },

  async getRecentlyViewed(): Promise<Product[]> {
    const res = await api.get<Product[]>('/api/user-activity/recently-viewed');
    return res.data;
  },

  async getSessionAnalytics(): Promise<any> {
    const res = await api.get('/api/user-activity/session');
    return res.data;
  },

  async getBehaviorAnalytics(): Promise<BehaviorAnalytics> {
    const res = await api.get<BehaviorAnalytics>('/api/user-activity/behavior');
    return res.data;
  },

  async getUserPreferences(): Promise<UserPreferences> {
    const res = await api.get<UserPreferences>('/api/user-activity/preferences');
    return res.data;
  },

  async getActivitySummary(): Promise<any> {
    const res = await api.get('/api/user-activity/summary');
    return res.data;
  }
};
