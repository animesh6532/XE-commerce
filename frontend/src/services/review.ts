import { api } from './api';

export interface Review {
  id: number;
  user_id: number;
  product_id: number;
  rating: number;
  comment: string;
  created_at: string;
  likes: number;
  dislikes: number;
  username?: string;
  sentiment?: 'Positive' | 'Negative' | 'Neutral' | string;
  is_fake?: boolean;
}

export interface ReviewCreatePayload {
  product_id: number;
  rating: number;
  comment: string;
}

export interface ReviewUpdatePayload {
  rating?: number;
  comment?: string;
}

export interface SentimentAnalysisResponse {
  sentiment: 'Positive' | 'Negative' | 'Neutral' | string;
  confidence: number;
}

export interface FakeReviewResponse {
  is_fake: boolean;
  prediction: 'CG' | 'OR' | string; // CG = Computer Generated, OR = Original
  probability: number;
}

export interface ReviewSummary {
  average_rating: number;
  total_reviews: number;
  rating_distribution: { [stars: number]: number };
  sentiment_summary: {
    positive: number;
    negative: number;
    neutral: number;
  };
  fake_review_percentage: number;
}

export const reviewService = {
  async addReview(payload: ReviewCreatePayload): Promise<Review> {
    const res = await api.post<Review>('/api/reviews/', payload);
    return res.data;
  },

  async updateReview(id: number, payload: ReviewUpdatePayload): Promise<Review> {
    const res = await api.put<Review>(`/api/reviews/${id}`, payload);
    return res.data;
  },

  async deleteReview(id: number): Promise<{ success: boolean; message: string }> {
    const res = await api.delete<{ success: boolean; message: string }>(`/api/reviews/${id}`);
    return res.data;
  },

  async getProductReviews(productId: number): Promise<Review[]> {
    const res = await api.get<Review[]>(`/api/reviews/product/${productId}`);
    return res.data;
  },

  async getUserReviews(): Promise<Review[]> {
    const res = await api.get<Review[]>('/api/reviews/my-reviews');
    return res.data;
  },

  async getReviewById(id: number): Promise<Review> {
    const res = await api.get<Review>(`/api/reviews/${id}`);
    return res.data;
  },

  async likeReview(id: number): Promise<{ success: boolean; likes: number }> {
    const res = await api.post<{ success: boolean; likes: number }>(`/api/reviews/${id}/like`);
    return res.data;
  },

  async dislikeReview(id: number): Promise<{ success: boolean; dislikes: number }> {
    const res = await api.post<{ success: boolean; dislikes: number }>(`/api/reviews/${id}/dislike`);
    return res.data;
  },

  async getSentiment(id: number): Promise<SentimentAnalysisResponse> {
    const res = await api.get<SentimentAnalysisResponse>(`/api/reviews/${id}/sentiment`);
    return res.data;
  },

  async getFakeReviewStatus(id: number): Promise<FakeReviewResponse> {
    const res = await api.get<FakeReviewResponse>(`/api/reviews/${id}/fake-review`);
    return res.data;
  },

  async getReviewSummary(productId: number): Promise<ReviewSummary> {
    const res = await api.get<ReviewSummary>(`/api/reviews/summary/${productId}`);
    return res.data;
  },

  async getTopReviews(productId: number): Promise<Review[]> {
    const res = await api.get<Review[]>(`/api/reviews/top/${productId}`);
    return res.data;
  },

  async verifyPurchase(productId: number): Promise<{ verified: boolean }> {
    const res = await api.get<{ verified: boolean }>(`/api/reviews/verify-purchase/${productId}`);
    return res.data;
  }
};
