import { api } from './api';

export interface ChatbotProduct {
  name: string;
  image?: string;
  link?: string;
  ratings?: string;
  discount_price?: string | number;
  actual_price?: string | number;
  clean_rating?: number | string;
  clean_no_of_ratings?: number | string;
}

export interface RAGData {
  query: string;
  routed_dataset: string;
  routing_similarity: number;
  top_5_datasets: Array<{ dataset: string; path: string; similarity: number }>;
  products: ChatbotProduct[];
  prompt: string;
  status: string;
}

export interface ChatbotResponse {
  status: string;
  response: string;
  rag_data: RAGData;
  source: string;
}

export interface ComparisonDetails {
  price: string;
  ratings: string;
  review_count: string;
  pros: { [brand: string]: string[] };
  cons: { [brand: string]: string[] };
  recommendation: string;
}

export interface ComparisonResponse {
  status: string;
  brand_a: string;
  brand_b: string;
  category: string | null;
  dataset: string;
  product_a: ChatbotProduct | null;
  product_b: ChatbotProduct | null;
  comparison: ComparisonDetails;
  message?: string;
}

export interface HistoryItem {
  query: string;
  response: string;
  source: string;
  routed_dataset: string;
}

export interface HistoryResponse {
  history: HistoryItem[];
}

export interface CategoriesResponse {
  categories: string[];
}

export const chatbotService = {
  async queryChatbot(query: string, budget?: number, minRating?: number): Promise<ChatbotResponse> {
    const response = await api.post<ChatbotResponse>('/api/chatbot/query', {
      query,
      budget: budget || null,
      min_rating: minRating || null
    });
    return response.data;
  },

  async compareProducts(query: string): Promise<ComparisonResponse> {
    const response = await api.post<ComparisonResponse>('/api/chatbot/compare', { query });
    return response.data;
  },

  async recommendProducts(query: string, topK = 5): Promise<ChatbotResponse> {
    const response = await api.post<ChatbotResponse>('/api/chatbot/recommend', { query, top_k: topK });
    return response.data;
  },

  async getChatHistory(): Promise<HistoryResponse> {
    const response = await api.get<HistoryResponse>('/api/chatbot/history');
    return response.data;
  },

  async getCategories(): Promise<CategoriesResponse> {
    const response = await api.get<CategoriesResponse>('/api/chatbot/categories');
    return response.data;
  }
};
