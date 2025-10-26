import React from 'react';
import { FaFilm } from 'react-icons/fa';

interface LoadingSpinnerProps {
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative">
        {/* Outer spinning ring */}
        <div className="w-20 h-20 border-4 border-primary-500/30 border-t-accent-500 rounded-full animate-spin"></div>
        {/* Inner icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <FaFilm className="text-accent-500 text-2xl animate-pulse" />
        </div>
      </div>
      <p className="mt-4 text-cream-200/80 font-medium">{message}</p>
    </div>
  );
};

export default LoadingSpinner;
