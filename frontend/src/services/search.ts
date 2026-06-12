import { api } from './api';
import type { Product } from './product';

export interface SearchResponse {
  results: Product[];
  total: number;
  page: number;
  limit: number;
}

export interface FilterSearchPayload {
  query?: string;
  category?: string;
  brand?: string;
  min_price?: number;
  max_price?: number;
  min_rating?: number;
}

export const searchService = {
  async keywordSearch(query: string, page = 1, limit = 20): Promise<SearchResponse> {
    const res = await api.post<SearchResponse>('/api/search/', {
      query,
      page,
      limit
    });
    return res.data;
  },

  async semanticSearch(query: string, topK = 10): Promise<Product[]> {
    const res = await api.post<Product[]>('/api/search/semantic', {
      query,
      top_k: topK
    });
    return res.data;
  },

  async getAutocomplete(query: string): Promise<string[]> {
    const res = await api.get<string[]>('/api/search/autocomplete', {
      params: { query }
    });
    return res.data;
  },

  async getSuggestions(query: string): Promise<string[]> {
    const res = await api.get<string[]>('/api/search/suggestions', {
      params: { query }
    });
    return res.data;
  },

  async filterSearch(payload: FilterSearchPayload): Promise<Product[]> {
    const res = await api.post<Product[]>('/api/search/filter', payload);
    return res.data;
  },

  async categorySearch(category: string): Promise<Product[]> {
    const res = await api.get<Product[]>(`/api/search/category/${category}`);
    return res.data;
  },

  async getTrendingSearches(): Promise<string[]> {
    const res = await api.get<string[]>('/api/search/trending');
    return res.data;
  },

  async getRecentSearches(): Promise<string[]> {
    const res = await api.get<string[]>('/api/search/recent');
    return res.data;
  },

  async saveSearch(query: string): Promise<{ success: boolean; message: string }> {
    const res = await api.post<{ success: boolean; message: string }>('/api/search/save', null, {
      params: { query }
    });
    return res.data;
  },

  async aiSearch(query: string, topK = 10): Promise<Product[]> {
    const res = await api.post<Product[]>('/api/search/ai', {
      query,
      top_k: topK
    });
    return res.data;
  },

  async getSimilarProducts(productId: number): Promise<Product[]> {
    const res = await api.get<Product[]>(`/api/search/similar/${productId}`);
    return res.data;
  }
};
