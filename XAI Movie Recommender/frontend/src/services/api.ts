// API service layer for communicating with the FastAPI backend

import axios from 'axios';
import type { RecommendationResponse, UserRatingsResponse, HealthStatus } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data.detail || 'An error occurred');
    } else if (error.request) {
      // Request made but no response
      throw new Error('Unable to connect to the server. Please ensure the backend is running.');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
);

export const apiService = {
  /**
   * Check API health status
   */
  async getHealth(): Promise<HealthStatus> {
    const response = await api.get<HealthStatus>('/health');
    return response.data;
  },

  /**
   * Get movie recommendations for a user
   */
  async getRecommendations(userId: number, count: number = 5): Promise<RecommendationResponse> {
    const response = await api.get<RecommendationResponse>(`/recommend/${userId}`, {
      params: { n: count },
    });
    return response.data;
  },

  /**
   * Get user's rated movies
   */
  async getUserRatedMovies(userId: number, limit: number = 10): Promise<UserRatingsResponse> {
    const response = await api.get<UserRatingsResponse>(`/user/${userId}/rated`, {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Get root endpoint info
   */
  async getRootInfo(): Promise<any> {
    const response = await api.get('/');
    return response.data;
  },

  /**
   * Get graph path between two movies for visualization
   */
  async getGraphPath(sourceTitle: string, targetTitle: string): Promise<any> {
    const encodedSource = encodeURIComponent(sourceTitle);
    const encodedTarget = encodeURIComponent(targetTitle);
    const response = await api.get(`/graph/path/${encodedSource}/${encodedTarget}`);
    return response.data;
  },

  /**
   * Search for movies by title (guest mode)
   */
  async searchMovies(query: string, limit: number = 10): Promise<any> {
    const response = await api.get('/movies/search', {
      params: { q: query, limit },
    });
    return response.data;
  },

  /**
   * Get movie recommendations based on a movie title (guest mode)
   */
  async getRecommendationsByMovie(movieTitle: string, count: number = 5): Promise<RecommendationResponse> {
    const encodedTitle = encodeURIComponent(movieTitle);
    const response = await api.get<RecommendationResponse>(`/recommend/by-movie/${encodedTitle}`, {
      params: { n: count },
    });
    return response.data;
  },
};

export default apiService;
