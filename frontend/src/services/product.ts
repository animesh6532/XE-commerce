import { api } from './api';

export interface Product {
  id: number;
  name: string;
  description: string;
  category: string;
  brand: string;
  price: number;
  stock: number;
  rating: number;
  image_url?: string;
  is_featured?: boolean;
}

export interface ProductCreatePayload {
  name: string;
  description: string;
  category: string;
  brand: string;
  price: number;
  stock: number;
  image_url?: string;
}

export interface ProductUpdatePayload {
  name?: string;
  description?: string;
  category?: string;
  brand?: string;
  price?: number;
  stock?: number;
  image_url?: string;
}

export interface ProductStats {
  total_products: number;
  featured_products: number;
  low_stock_products: number;
}

export interface InventoryStatus {
  low_stock_count: number;
  low_stock_items: Array<{
    id: number;
    name: string;
    stock: number;
  }>;
}

export interface PaginatedProductResponse {
  products: Product[];
  total: number;
  page: number;
  limit: number;
}

export const productService = {
  async getProducts(page = 1, limit = 20): Promise<PaginatedProductResponse> {
    const res = await api.get<PaginatedProductResponse>('/api/products/', {
      params: { page, limit }
    });
    return res.data;
  },

  async getProduct(id: number): Promise<Product> {
    const res = await api.get<Product>(`/api/products/${id}`);
    return res.data;
  },

  async searchProducts(query: string): Promise<Product[]> {
    const res = await api.get<Product[]>('/api/products/search/', {
      params: { query }
    });
    return res.data;
  },

  async filterProducts(filters: {
    category?: string;
    min_price?: number;
    max_price?: number;
    min_rating?: number;
    brand?: string;
  }): Promise<Product[]> {
    const res = await api.get<Product[]>('/api/products/filter/', {
      params: filters
    });
    return res.data;
  },

  async getProductsByCategory(categoryName: string): Promise<Product[]> {
    const res = await api.get<Product[]>(`/api/products/category/${categoryName}`);
    return res.data;
  },

  async createProduct(payload: ProductCreatePayload): Promise<Product> {
    const res = await api.post<Product>('/api/products/', payload);
    return res.data;
  },

  async updateProduct(id: number, payload: ProductUpdatePayload): Promise<Product> {
    const res = await api.put<Product>(`/api/products/${id}`, payload);
    return res.data;
  },

  async deleteProduct(id: number): Promise<{ success: boolean; message: string }> {
    const res = await api.delete<{ success: boolean; message: string }>(`/api/products/${id}`);
    return res.data;
  },

  async getFeaturedProducts(): Promise<Product[]> {
    const res = await api.get<Product[]>('/api/products/featured/list');
    return res.data;
  },

  async getTrendingProducts(): Promise<Product[]> {
    const res = await api.get<Product[]>('/api/products/trending/list');
    return res.data;
  },

  async getDealProducts(): Promise<Product[]> {
    const res = await api.get<Product[]>('/api/products/deals/list');
    return res.data;
  },

  async getSimilarProducts(id: number): Promise<Product[]> {
    const res = await api.get<Product[]>(`/api/products/similar/${id}`);
    return res.data;
  },

  async getStats(): Promise<ProductStats> {
    const res = await api.get<ProductStats>('/api/products/stats/overview');
    return res.data;
  },

  async getInventoryStatus(): Promise<InventoryStatus> {
    const res = await api.get<InventoryStatus>('/api/products/inventory/status');
    return res.data;
  }
};
