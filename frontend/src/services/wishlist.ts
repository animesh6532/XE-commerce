import { api } from './api';
import type { Product } from './product';

export interface WishlistItem {
  id: number;
  user_id: number;
  product_id: number;
  created_at: string;
  product?: Product;
}

export interface WishlistDeal {
  product_id: number;
  name: string;
  original_price: number;
  current_price: number;
  discount_percentage: number;
  deal_score: number;
}

export interface WishlistPriceAlert {
  product_id: number;
  name: string;
  old_price: number;
  new_price: number;
  price_drop: number;
  timestamp: string;
}

export interface WishlistAnalytics {
  total_items: number;
  category_distribution: { [category: string]: number };
  average_price: number;
  total_value: number;
  potential_savings: number;
}

export const wishlistService = {
  async getWishlist(): Promise<WishlistItem[]> {
    const res = await api.get<any>('/api/wishlist/');
    return res.data.items || [];
  },

  async addToWishlist(productId: number): Promise<WishlistItem> {
    const res = await api.post<WishlistItem>('/api/wishlist/add', {
      product_id: productId
    });
    return res.data;
  },

  async removeFromWishlist(productId: number): Promise<{ success: boolean; message: string }> {
    const res = await api.delete<{ success: boolean; message: string }>(`/api/wishlist/remove/${productId}`);
    return res.data;
  },

  async clearWishlist(): Promise<{ success: boolean; message: string }> {
    const res = await api.delete<{ success: boolean; message: string }>('/api/wishlist/clear');
    return res.data;
  },

  async moveToCart(productId: number): Promise<{ success: boolean; message: string }> {
    const res = await api.post<{ success: boolean; message: string }>(`/api/wishlist/move-to-cart/${productId}`);
    return res.data;
  },

  async saveForLater(productId: number): Promise<{ success: boolean; message: string }> {
    const res = await api.post<{ success: boolean; message: string }>(`/api/wishlist/save-for-later/${productId}`);
    return res.data;
  },

  async getDealTracking(): Promise<WishlistDeal[]> {
    const res = await api.get<any>('/api/wishlist/deal-tracking');
    return res.data.deals || [];
  },

  async getPriceAlerts(): Promise<WishlistPriceAlert[]> {
    const res = await api.get<any>('/api/wishlist/price-alerts');
    return res.data.alerts || [];
  },

  async getWishlistRecommendations(): Promise<Product[]> {
    const res = await api.get<any>('/api/wishlist/recommendations');
    return res.data.recommendations || [];
  },

  async getWishlistAnalytics(): Promise<WishlistAnalytics> {
    const res = await api.get<WishlistAnalytics>('/api/wishlist/analytics');
    return res.data;
  }
};
