import React, { useState, useEffect } from 'react';
import { FaSearch, FaCheckCircle, FaTimesCircle, FaFilm, FaUser } from 'react-icons/fa';
import Header from './components/Header';
import RecommendationCard from './components/RecommendationCard';
import GuestMode from './components/GuestMode';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorAlert from './components/ErrorAlert';
import Squares from './components/Squares';
import apiService from './services/api';
import type { RecommendationResponse, HealthStatus } from './types';

type AppMode = 'user' | 'guest';

function App() {
  const [mode, setMode] = useState<AppMode>('user');
  const [userId, setUserId] = useState<string>('1');
  const [recommendationCount, setRecommendationCount] = useState<number>(5);
  const [showGraphs, setShowGraphs] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [openCardId, setOpenCardId] = useState<number | null>(null);

  // Check API health on mount
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const healthData = await apiService.getHealth();
      setHealth(healthData);
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const handleGetRecommendations = async () => {
    setError(null);
    setRecommendations(null);
    setOpenCardId(null);

    // Validation
    const userIdNum = parseInt(userId);
    if (isNaN(userIdNum) || userIdNum < 1 || userIdNum > 610) {
      setError('Please enter a valid User ID (1-610)');
      return;
    }

    setLoading(true);

    try {
      const data = await apiService.getRecommendations(userIdNum, recommendationCount);
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

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleGetRecommendations();
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-navy-500 relative">
      <Squares
        direction="up"
        speed={0.5}
        borderColor="#1565C0"
        squareSize={40}
        hoverFillColor="#0D47A1"
      />
      <Header />

      <main className="flex-1 container mx-auto px-4 py-8 max-w-6xl relative z-10">
        {/* Hero Section */}
        <div className="text-center mb-8">
          <h2 className="text-4xl md:text-5xl font-bold text-cream-200 mb-4">
            Discover Your Next
            <span className="bg-gradient-to-r from-accent-500 to-primary-500 bg-clip-text text-transparent">
              {' '}
              Favorite Movie
            </span>
          </h2>
          <p className="text-lg text-cream-200/70 max-w-2xl mx-auto">
            Get personalized movie recommendations powered by AI and knowledge graphs.
            Every recommendation comes with an explanation of why it's perfect for you.
          </p>
        </div>

        {/* Mode Tabs */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-navy-600 rounded-lg shadow-md p-1">
            <button
              onClick={() => {
                setMode('user');
                setRecommendations(null);
                setError(null);
                setOpenCardId(null);
              }}
              className={`px-6 py-3 rounded-md font-medium transition-all flex items-center space-x-2 ${
                mode === 'user'
                  ? 'bg-primary-500 text-white shadow-sm'
                  : 'text-cream-200/60 hover:text-cream-200'
              }`}
            >
              <FaUser />
              <span>User Mode</span>
            </button>
            <button
              onClick={() => {
                setMode('guest');
                setRecommendations(null);
                setError(null);
                setOpenCardId(null);
              }}
              className={`px-6 py-3 rounded-md font-medium transition-all flex items-center space-x-2 ${
                mode === 'guest'
                  ? 'bg-primary-500 text-white shadow-sm'
                  : 'text-cream-200/60 hover:text-cream-200'
              }`}
            >
              <FaFilm />
              <span>Guest Mode</span>
            </button>
          </div>
        </div>

        {/* System Status */}
        <div className="mb-8 flex justify-center">
          <div className="inline-flex items-center space-x-4 bg-navy-600 px-6 py-3 rounded-full shadow-md">
            <div className="flex items-center space-x-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  health?.status === 'healthy' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`}
              ></div>
              <span className="text-sm font-medium text-cream-200">
                {health?.status === 'healthy' ? 'System Online' : 'System Offline'}
              </span>
            </div>
            {health && (
              <>
                <span className="text-cream-200/30">|</span>
                <div className="flex items-center space-x-2 text-sm">
                  {health.model_loaded ? (
                    <FaCheckCircle className="text-green-500" />
                  ) : (
                    <FaTimesCircle className="text-red-500" />
                  )}
                  <span className="text-cream-200/70">Model</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  {health.neo4j_connected ? (
                    <FaCheckCircle className="text-green-500" />
                  ) : (
                    <FaTimesCircle className="text-red-500" />
                  )}
                  <span className="text-cream-200/70">Database</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Settings Bar */}
        <div className="bg-navy-600 rounded-xl shadow-lg p-6 max-w-2xl mx-auto mb-8 border border-primary-500/20">
          <div className="space-y-4">
            <div>
              <label htmlFor="count" className="block text-sm font-medium text-cream-200 mb-2">
                Number of Recommendations: {recommendationCount}
              </label>
              <input
                type="range"
                id="count"
                value={recommendationCount}
                onChange={(e) => setRecommendationCount(parseInt(e.target.value))}
                min="1"
                max="10"
                className="w-full h-2 bg-navy-700 rounded-lg appearance-none cursor-pointer accent-accent-500"
              />
              <div className="flex justify-between text-xs text-cream-200/50 mt-1">
                <span>1</span>
                <span>10</span>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-navy-700 rounded-lg">
              <div>
                <label htmlFor="showGraphs" className="font-medium text-cream-200 cursor-pointer">
                  Show Connection Graphs
                </label>
                <p className="text-xs text-cream-200/60 mt-1">
                  Visualize how movies are connected through actors, directors, and genres
                </p>
              </div>
              <input
                type="checkbox"
                id="showGraphs"
                checked={showGraphs}
                onChange={(e) => setShowGraphs(e.target.checked)}
                className="w-5 h-5 text-accent-500 bg-navy-600 border-primary-500/30 rounded focus:ring-accent-500 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Content Based on Mode */}
        {mode === 'user' ? (
          <>
            {/* User Mode Input */}
            <div className="bg-navy-600 rounded-xl shadow-lg p-6 max-w-2xl mx-auto mb-12 border border-primary-500/20">
              <div className="space-y-6">
                <div>
                  <label htmlFor="userId" className="block text-sm font-medium text-cream-200 mb-2">
                    User ID
                  </label>
                  <input
                    type="number"
                    id="userId"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    onKeyPress={handleKeyPress}
                    min="1"
                    max="610"
                    className="w-full px-4 py-3 rounded-lg bg-navy-700 border border-primary-500/30 text-cream-200 placeholder-cream-200/40 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent transition-all"
                    placeholder="Enter your User ID (1-610)"
                  />
                  <p className="mt-2 text-sm text-cream-200/50">
                    Try these: 1, 15, 133, 414 (most active), or 599
                  </p>
                </div>

                <button
                  onClick={handleGetRecommendations}
                  disabled={loading || health?.status !== 'healthy'}
                  className="w-full px-6 py-3 bg-gradient-to-r from-primary-500 to-accent-500 text-white font-semibold rounded-lg hover:shadow-lg hover:scale-[1.02] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center space-x-2"
                >
                  <FaSearch />
                  <span>{loading ? 'Finding Movies...' : 'Get Recommendations'}</span>
                </button>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="max-w-2xl mx-auto mb-8">
                <ErrorAlert message={error} onClose={() => setError(null)} />
              </div>
            )}

            {/* Loading State */}
            {loading && <LoadingSpinner message="Analyzing your movie preferences..." />}

            {/* Results */}
            {!loading && recommendations && recommendations.recommendations.length > 0 && (
              <div className="animate-fade-in">
                {/* Source Movie */}
                {recommendations.source_movie && (
                  <div className="max-w-2xl mx-auto mb-8">
                    <div className="bg-gradient-to-r from-primary-500 to-accent-500 text-white p-6 rounded-xl shadow-lg">
                      <div className="flex items-center space-x-3 mb-2">
                        <FaFilm className="text-2xl" />
                        <h3 className="text-lg font-semibold">Based on your love for:</h3>
                      </div>
                      <p className="text-2xl font-bold">{recommendations.source_movie}</p>
                    </div>
                  </div>
                )}

                {/* Recommendations Grid */}
                <div className="mb-8">
                  <h3 className="text-2xl font-bold text-cream-200 mb-6 text-center">
                    Your Personalized Recommendations
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {recommendations.recommendations.map((rec, index) => (
                      <RecommendationCard
                        key={rec.movie_id}
                        recommendation={rec}
                        index={index + 1}
                        sourceMovie={recommendations.source_movie || undefined}
                        showGraph={showGraphs}
                        isOpen={openCardId === rec.movie_id}
                        onToggle={() => setOpenCardId(openCardId === rec.movie_id ? null : rec.movie_id)}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          /* Guest Mode */
          <GuestMode
            recommendationCount={recommendationCount}
            showGraphs={showGraphs}
            healthStatus={health?.status}
          />
        )}

        {/* How It Works Section */}
        <section id="how-it-works" className="mt-16 pt-16 border-t border-primary-500/20">
          <h3 className="text-3xl font-bold text-center text-cream-200 mb-8">How It Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="bg-primary-500/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 border border-primary-500/30">
                <span className="text-2xl font-bold text-accent-500">1</span>
              </div>
              <h4 className="text-xl font-semibold mb-2 text-cream-200">Your Preferences</h4>
              <p className="text-cream-200/70">
                We analyze your highest-rated movies to understand your taste
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary-500/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 border border-primary-500/30">
                <span className="text-2xl font-bold text-accent-500">2</span>
              </div>
              <h4 className="text-xl font-semibold mb-2 text-cream-200">Knowledge Graph</h4>
              <p className="text-cream-200/70">
                Our AI explores connections between movies, actors, directors, and genres
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary-500/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 border border-primary-500/30">
                <span className="text-2xl font-bold text-accent-500">3</span>
              </div>
              <h4 className="text-xl font-semibold mb-2 text-cream-200">Explainable Results</h4>
              <p className="text-cream-200/70">
                Get recommendations with clear explanations of why they match your taste
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-navy-600 border-t border-primary-500/20 mt-16">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-cream-200/80 text-sm">
            <span className="font-bold text-accent-500">Lumiere</span> - Built with React, TypeScript, Tailwind CSS, FastAPI, Neo4j, and Node2Vec
          </p>
          <p className="text-center text-cream-200/50 text-xs mt-2">
            MovieLens dataset courtesy of GroupLens Research
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
