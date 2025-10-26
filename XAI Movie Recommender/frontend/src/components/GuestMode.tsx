import React, { useState, useEffect } from 'react';
import { FaSearch, FaFilm } from 'react-icons/fa';
import RecommendationCard from './RecommendationCard';
import LoadingSpinner from './LoadingSpinner';
import ErrorAlert from './ErrorAlert';
import apiService from '../services/api';
import type { RecommendationResponse, Movie } from '../types';

interface GuestModeProps {
  recommendationCount: number;
  showGraphs: boolean;
  healthStatus: string | undefined;
}

const GuestMode: React.FC<GuestModeProps> = ({
  recommendationCount,
  showGraphs,
  healthStatus,
}) => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<Movie[]>([]);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [searchLoading, setSearchLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);

  // Debounced search
  useEffect(() => {
    if (searchQuery.length >= 2) {
      const timeoutId = setTimeout(() => {
        handleSearch();
      }, 300);

      return () => clearTimeout(timeoutId);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const handleSearch = async () => {
    if (searchQuery.length < 2) return;

    setSearchLoading(true);
    try {
      const data = await apiService.searchMovies(searchQuery, 10);
      setSearchResults(data.results || []);
    } catch (err) {
      console.error('Search failed:', err);
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleMovieSelect = (movie: Movie) => {
    setSelectedMovie(movie);
    setSearchQuery(movie.title);
    setSearchResults([]);
    setRecommendations(null);
    setError(null);
  };

  const handleGetRecommendations = async () => {
    if (!selectedMovie) {
      setError('Please select a movie first');
      return;
    }

    setError(null);
    setRecommendations(null);
    setLoading(true);

    try {
      const data = await apiService.getRecommendationsByMovie(
        selectedMovie.title,
        recommendationCount
      );
      setRecommendations(data);

      if (data.message && data.recommendations.length === 0) {
        setError(data.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Search Section */}
      <div className="card max-w-2xl mx-auto">
        <div className="space-y-6">
          <div>
            <label htmlFor="movieSearch" className="block text-sm font-medium text-gray-700 mb-2">
              Search for a Movie
            </label>
            <div className="relative">
              <input
                type="text"
                id="movieSearch"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setSelectedMovie(null);
                }}
                className="input-field pr-10"
                placeholder="e.g., Toy Story, Matrix, Inception..."
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                {searchLoading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
                ) : (
                  <FaSearch className="text-gray-400" />
                )}
              </div>
            </div>
            <p className="mt-2 text-sm text-gray-500">
              Type at least 2 characters to search for movies
            </p>
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">Found {searchResults.length} movies:</p>
              <div className="max-h-60 overflow-y-auto space-y-1 border border-gray-200 rounded-lg p-2">
                {searchResults.map((movie) => (
                  <button
                    key={movie.movieId}
                    onClick={() => handleMovieSelect(movie)}
                    className="w-full text-left px-4 py-3 hover:bg-primary-50 rounded-lg transition-colors flex items-center space-x-3"
                  >
                    <FaFilm className="text-primary-600 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-gray-900">{movie.title}</p>
                      <p className="text-xs text-gray-500">Movie ID: {movie.movieId}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Selected Movie Display */}
          {selectedMovie && (
            <div className="bg-gradient-to-r from-primary-500 to-primary-600 text-white p-4 rounded-lg">
              <p className="text-sm font-medium mb-1">Selected Movie:</p>
              <p className="text-xl font-bold">{selectedMovie.title}</p>
            </div>
          )}

          {/* Get Recommendations Button */}
          <button
            onClick={handleGetRecommendations}
            disabled={!selectedMovie || loading || healthStatus !== 'healthy'}
            className="btn-primary w-full flex items-center justify-center space-x-2"
          >
            <FaSearch />
            <span>{loading ? 'Finding Similar Movies...' : 'Get Similar Movies'}</span>
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="max-w-2xl mx-auto">
          <ErrorAlert message={error} onClose={() => setError(null)} />
        </div>
      )}

      {/* Loading State */}
      {loading && <LoadingSpinner message="Finding movies similar to your selection..." />}

      {/* Results */}
      {!loading && recommendations && recommendations.recommendations.length > 0 && (
        <div className="animate-fade-in">
          {/* Source Movie */}
          {recommendations.source_movie && (
            <div className="max-w-2xl mx-auto mb-8">
              <div className="bg-gradient-to-r from-primary-500 to-primary-600 text-white p-6 rounded-xl shadow-lg">
                <div className="flex items-center space-x-3 mb-2">
                  <FaFilm className="text-2xl" />
                  <h3 className="text-lg font-semibold">Because you like:</h3>
                </div>
                <p className="text-2xl font-bold">{recommendations.source_movie}</p>
              </div>
            </div>
          )}

          {/* Recommendations Grid */}
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
              You Might Also Enjoy
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {recommendations.recommendations.map((rec, index) => (
                <RecommendationCard
                  key={rec.movie_id}
                  recommendation={rec}
                  index={index + 1}
                  sourceMovie={recommendations.source_movie || undefined}
                  showGraph={showGraphs}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Info Section */}
      {!recommendations && !loading && (
        <div className="max-w-2xl mx-auto">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h4 className="text-lg font-semibold text-blue-900 mb-2">How Guest Mode Works</h4>
            <ul className="space-y-2 text-sm text-blue-800">
              <li className="flex items-start space-x-2">
                <span className="font-bold">1.</span>
                <span>Search for any movie you love by typing its name</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="font-bold">2.</span>
                <span>Select your movie from the search results</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="font-bold">3.</span>
                <span>Get instant recommendations for similar movies with AI-powered explanations</span>
              </li>
            </ul>
            <p className="mt-4 text-xs text-blue-700">
              No account needed! Try searching for: "Toy Story", "Matrix", "Inception", or "Star Wars"
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default GuestMode;
