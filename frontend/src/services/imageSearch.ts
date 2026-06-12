import { api } from './api';
import type { Product } from './product';

export interface ImageSearchResponse {
  success: boolean;
  results: Product[];
}

export interface SimilarImageResponse {
  success: boolean;
  top_k: number;
  products: Product[];
}

export interface ReverseSearchResponse {
  success: boolean;
  matches: Array<{ product: Product; confidence: number }>;
}

export interface ImageRecommendResponse {
  success: boolean;
  recommendations: Product[];
}

export const imageSearchService = {
  async searchByImage(imageFile: File): Promise<ImageSearchResponse> {
    const formData = new FormData();
    formData.append('image', imageFile);
    const res = await api.post<ImageSearchResponse>('/api/image-search/search', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  async findSimilarProducts(imageFile: File, topK = 5): Promise<SimilarImageResponse> {
    const formData = new FormData();
    formData.append('image', imageFile);
    const res = await api.post<SimilarImageResponse>('/api/image-search/similar', formData, {
      params: { top_k: topK },
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  async reverseImageSearch(imageFile: File): Promise<ReverseSearchResponse> {
    const formData = new FormData();
    formData.append('image', imageFile);
    const res = await api.post<ReverseSearchResponse>('/api/image-search/reverse', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  async recommendByImage(imageFile: File, topK = 10): Promise<ImageRecommendResponse> {
    const formData = new FormData();
    formData.append('image', imageFile);
    const res = await api.post<ImageRecommendResponse>('/api/image-search/recommend', formData, {
      params: { top_k: topK },
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  }
};
