import React, { useState } from 'react';
import { FaStar, FaChartLine, FaInfoCircle, FaProjectDiagram } from 'react-icons/fa';
import type { Recommendation } from '../types';
import GraphVisualization from './GraphVisualization';

interface RecommendationCardProps {
  recommendation: Recommendation;
  index: number;
  sourceMovie?: string;
  showGraph?: boolean;
  isOpen?: boolean;
  onToggle?: () => void;
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  index,
  sourceMovie,
  showGraph = false,
  isOpen = false,
  onToggle
}) => {
  const [showGraphViz, setShowGraphViz] = useState(false);

  // Calculate a visual rating from similarity (0-5 stars)
  const visualRating = Math.round(recommendation.similarity * 5);

  return (
    <div className="bg-navy-600 rounded-xl shadow-lg p-6 border border-primary-500/20 group hover:scale-[1.02] hover:border-accent-500/40 transition-all duration-300">
      {/* Header with rank */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-br from-accent-500 to-primary-500 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg shadow-md">
            {index}
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-cream-200 group-hover:text-accent-400 transition-colors">
              {recommendation.movie_title}
            </h3>
          </div>
        </div>
      </div>

      {/* Similarity Stars */}
      <div className="flex items-center space-x-2 mb-3">
        <div className="flex">
          {[...Array(5)].map((_, i) => (
            <FaStar
              key={i}
              className={`${
                i < visualRating ? 'text-accent-500' : 'text-navy-700'
              } text-sm`}
            />
          ))}
        </div>
        <span className="text-sm text-cream-200/60">
          {(recommendation.similarity * 100).toFixed(1)}% match
        </span>
      </div>

      {/* Explanation */}
      <div className="bg-primary-500/10 border-l-4 border-primary-500 p-4 mb-4 rounded">
        <div className="flex">
          <div className="flex-shrink-0">
            <FaInfoCircle className="text-accent-500 mt-0.5" />
          </div>
          <div className="ml-3">
            <p className="text-sm text-cream-200/90">{recommendation.explanation}</p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={onToggle}
          className="flex items-center space-x-2 text-accent-400 hover:text-accent-300 text-sm font-medium transition-colors"
        >
          <FaChartLine />
          <span>{isOpen ? 'Hide' : 'Show'} Technical Details</span>
        </button>

        {showGraph && sourceMovie && (
          <button
            onClick={() => setShowGraphViz(!showGraphViz)}
            className="flex items-center space-x-2 text-primary-400 hover:text-primary-300 text-sm font-medium transition-colors"
          >
            <FaProjectDiagram />
            <span>{showGraphViz ? 'Hide' : 'Show'} Connection Graph</span>
          </button>
        )}
      </div>

      {/* Technical Details */}
      {isOpen && (
        <div className="mt-4 p-4 bg-navy-700 rounded-lg border border-primary-500/20 animate-fade-in">
          <h4 className="font-semibold text-cream-200 mb-2">Technical Details</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-cream-200/60">Movie ID:</span>
              <span className="font-mono text-cream-200">{recommendation.movie_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-cream-200/60">Similarity Score:</span>
              <span className="font-mono text-cream-200">
                {recommendation.similarity.toFixed(4)}
              </span>
            </div>
            <div className="mt-3 pt-3 border-t border-primary-500/20">
              <p className="text-xs text-cream-200/50">
                This score represents cosine similarity in the Node2Vec embedding space.
                Higher values indicate stronger structural similarity in the knowledge graph.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Graph Visualization */}
      {showGraphViz && showGraph && sourceMovie && (
        <div className="mt-4 animate-fade-in">
          <h4 className="font-semibold text-cream-200 mb-3">Connection Path</h4>
          <GraphVisualization
            sourceMovie={sourceMovie}
            targetMovie={recommendation.movie_title}
          />
        </div>
      )}
    </div>
  );
};

export default RecommendationCard;
