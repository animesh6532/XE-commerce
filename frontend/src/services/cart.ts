import { api } from './api';
import type { Product } from './product';

export interface CartItem {
  id: number;
  user_id: number;
  product_id: number;
  quantity: number;
  saved_for_later: boolean;
  product?: Product;
}

export interface CartSummary {
  subtotal: number;
  discount: number;
  tax: number;
  shipping: number;
  total: number;
  coupon_code: string | null;
  item_count: number;
}

export interface CheckoutPreview {
  items: CartItem[];
  summary: CartSummary;
}

export const cartService = {
  async getCart(): Promise<CartItem[]> {
    const res = await api.get<CartItem[]>('/api/cart/');
    return res.data;
  },

  async addToCart(productId: number, quantity = 1): Promise<CartItem> {
    const res = await api.post<CartItem>('/api/cart/add', {
      product_id: productId,
      quantity
    });
    return res.data;
  },

  async updateQuantity(productId: number, quantity: number): Promise<CartItem> {
    const res = await api.put<CartItem>(`/api/cart/update/${productId}`, {
      quantity
    });
    return res.data;
  },

  async removeFromCart(productId: number): Promise<{ success: boolean; message: string }> {
    const res = await api.delete<{ success: boolean; message: string }>(`/api/cart/remove/${productId}`);
    return res.data;
  },

  async clearCart(): Promise<{ success: boolean; message: string }> {
    const res = await api.delete<{ success: boolean; message: string }>('/api/cart/clear');
    return res.data;
  },

  async getSummary(): Promise<CartSummary> {
    const res = await api.get<CartSummary>('/api/cart/summary');
    return res.data;
  },

  async applyCoupon(code: string): Promise<{ success: boolean; message: string; summary: CartSummary }> {
    const res = await api.post<{ success: boolean; message: string; summary: CartSummary }>('/api/cart/apply-coupon', {
      code
    });
    return res.data;
  },

  async saveForLater(productId: number): Promise<{ success: boolean; message: string }> {
    const res = await api.post<{ success: boolean; message: string }>(`/api/cart/save-for-later/${productId}`);
    return res.data;
  },

  async moveToWishlist(productId: number): Promise<{ success: boolean; message: string }> {
    const res = await api.post<{ success: boolean; message: string }>(`/api/cart/move-to-wishlist/${productId}`);
    return res.data;
  },

  async getCheckoutPreview(): Promise<CheckoutPreview> {
    const res = await api.get<CheckoutPreview>('/api/cart/checkout-preview');
    return res.data;
  }
};
