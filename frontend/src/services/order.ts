import { api } from './api';
import type { Product } from './product';

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  quantity: number;
  price: number;
  product?: Product;
}

export interface Order {
  id: number;
  user_id: number;
  shipping_address: string;
  payment_method: string;
  status: string;
  total_amount: number;
  discount: number;
  shipping_fee: number;
  final_amount: number;
  created_at: string;
  items: OrderItem[];
}

export interface OrderCreatePayload {
  shipping_address: string;
  payment_method: string;
}

export interface TrackingStep {
  status: string;
  timestamp: string;
  description: string;
  completed: boolean;
}

export interface OrderSummary {
  total_orders: number;
  total_spent: number;
  average_order_value: number;
}

export const orderService = {
  async placeOrder(payload: OrderCreatePayload): Promise<Order> {
    const res = await api.post<Order>('/api/orders/place', payload);
    return res.data;
  },

  async getOrders(): Promise<Order[]> {
    const res = await api.get<Order[]>('/api/orders/');
    return res.data;
  },

  async getOrderById(id: number): Promise<Order> {
    const res = await api.get<Order>(`/api/orders/${id}`);
    return res.data;
  },

  async trackOrder(id: number): Promise<{ order_id: number; current_status: string; tracking_history: TrackingStep[] }> {
    const res = await api.get<{ order_id: number; current_status: string; tracking_history: TrackingStep[] }>(`/api/orders/track/${id}`);
    return res.data;
  },

  async cancelOrder(id: number): Promise<{ success: boolean; message: string; order: Order }> {
    const res = await api.put<{ success: boolean; message: string; order: Order }>(`/api/orders/cancel/${id}`);
    return res.data;
  },

  async returnOrder(id: number, reason: string): Promise<{ success: boolean; message: string }> {
    const res = await api.post<{ success: boolean; message: string }>(`/api/orders/return/${id}`, {
      reason
    });
    return res.data;
  },

  async updateOrderStatus(id: number, status: string): Promise<{ success: boolean; message: string; order: Order }> {
    const res = await api.put<{ success: boolean; message: string; order: Order }>(`/api/orders/status/${id}`, {
      status
    });
    return res.data;
  },

  async getOrderSummary(): Promise<OrderSummary> {
    const res = await api.get<OrderSummary>('/api/orders/summary');
    return res.data;
  },

  async getRecentOrders(): Promise<Order[]> {
    const res = await api.get<Order[]>('/api/orders/recent');
    return res.data;
  },

  async getAllOrders(): Promise<Order[]> {
    const res = await api.get<Order[]>('/api/orders/admin/all');
    return res.data;
  }
};
