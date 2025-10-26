// Type definitions for Lumiere

export interface Recommendation {
  movie_title: string;
  movie_id: number;
  explanation: string;
  similarity: number;
}

export interface RecommendationResponse {
  source_movie: string | null;
  source_movie_id?: number;
  recommendations: Recommendation[];
  message?: string;
}

export interface RatedMovie {
  movie_id: number;
  title: string;
  rating: number;
}

export interface UserRatingsResponse {
  user_id: number;
  rated_movies: RatedMovie[];
  count: number;
}

export interface HealthStatus {
  status: string;
  model_loaded: boolean;
  neo4j_connected: boolean;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'Movie' | 'Actor' | 'Director' | 'Genre';
  x?: number;
  y?: number;
}

export interface GraphLink {
  source: string;
  target: string;
  type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface Movie {
  movieId: number;
  title: string;
}

export interface MovieSearchResponse {
  query: string;
  results: Movie[];
  count: number;
}
