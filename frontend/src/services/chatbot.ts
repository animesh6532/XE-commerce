import { api } from './api';

// --- TypeScript Interfaces ---

export interface Product {
  name: string;
  main_category: string;
  sub_category: string;
  image: string;
  link: string;
  ratings: string;
  no_of_ratings: string;
  discount_price: string;
  actual_price: string;
  clean_discount_price: number | null;
  clean_actual_price: number | null;
  clean_rating: number;
  clean_no_of_ratings: number;
  semantic_similarity: number;
  ranking_score: number;
}

export interface RAGData {
  query: string;
  routed_dataset: string;
  routing_similarity: number;
  top_5_datasets: Array<{ dataset: string; path: string; similarity: number }>;
  products: Product[];
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
  product_a: Product | null;
  product_b: Product | null;
  comparison: ComparisonDetails;
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


// --- API Services ---

export const chatbotService = {
  /**
   * Submits a search or recommend query to the assistant.
   */
  async queryChatbot(query: string, budget?: number, minRating?: number): Promise<ChatbotResponse> {
    const response = await api.post<ChatbotResponse>('/chatbot/query', {
      query,
      budget: budget || null,
      min_rating: minRating || null
    });
    return response.data;
  },

  /**
   * Compares two products or brands side-by-side.
   */
  async compareProducts(query: string): Promise<ComparisonResponse> {
    const response = await api.post<ComparisonResponse>('/chatbot/compare', { query });
    return response.data;
  },

  /**
   * Discovers products using the recommendation endpoints.
   */
  async recommendProducts(query: string, topK: number = 5): Promise<ChatbotResponse> {
    const response = await api.post<ChatbotResponse>('/chatbot/recommend', { query, top_k: topK });
    return response.data;
  },

  /**
   * Fetches the current session chatbot history.
   */
  async getChatHistory(): Promise<HistoryResponse> {
    const response = await api.get<HistoryResponse>('/chatbot/history');
    return response.data;
  },

  /**
   * Fetches all category datasets configured on the router.
   */
  async getCategories(): Promise<CategoriesResponse> {
    const response = await api.get<CategoriesResponse>('/chatbot/categories');
    return response.data;
  }
};
