import { api } from './api';
import type { Product } from './product';

export interface VoiceCommandResponse {
  command: string;
  action: string;
  parameters: { [key: string]: any };
  message: string;
}

export const voiceSearchService = {
  async speechToText(audioBlob: Blob): Promise<{ text: string }> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice.wav');
    const res = await api.post<{ text: string }>('/api/voice-search/speech-to-text', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  async voiceSearch(audioBlob: Blob): Promise<Product[]> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice.wav');
    const res = await api.post<Product[]>('/api/voice-search/search', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  async textSearch(text: string): Promise<Product[]> {
    const res = await api.post<Product[]>('/api/voice-search/text-search', { text });
    return res.data;
  },

  async voiceRecommend(audioBlob: Blob): Promise<Product[]> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice.wav');
    const res = await api.post<Product[]>('/api/voice-search/recommend', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  async categorySearch(audioBlob: Blob): Promise<{ category: string; products: Product[] }> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice.wav');
    const res = await api.post<{ category: string; products: Product[] }>('/api/voice-search/category', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  async runVoiceCommand(text: string): Promise<VoiceCommandResponse> {
    const res = await api.post<VoiceCommandResponse>('/api/voice-search/command', { text });
    return res.data;
  },

  async getVoiceHistory(): Promise<Array<{ id: number; query: string; created_at: string }>> {
    const res = await api.get<Array<{ id: number; query: string; created_at: string }>>('/api/voice-search/history');
    return res.data;
  },

  async getTrendingQueries(): Promise<string[]> {
    const res = await api.get<string[]>('/api/voice-search/trending');
    return res.data;
  },

  async askVoiceAssistant(text: string): Promise<{ reply: string; data?: any }> {
    const res = await api.post<{ reply: string; data?: any }>('/api/voice-search/assistant', { text });
    return res.data;
  }
};
