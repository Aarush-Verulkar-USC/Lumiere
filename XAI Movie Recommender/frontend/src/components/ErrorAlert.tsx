import React from 'react';
import { FaExclamationTriangle, FaTimes } from 'react-icons/fa';

interface ErrorAlertProps {
  message: string;
  onClose?: () => void;
}

const ErrorAlert: React.FC<ErrorAlertProps> = ({ message, onClose }) => {
  return (
    <div className="bg-red-900/20 border-l-4 border-red-500 p-4 rounded-lg shadow-md animate-slide-up backdrop-blur-sm">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <FaExclamationTriangle className="text-red-400 text-xl mt-0.5" />
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-300">Error</h3>
          <p className="mt-1 text-sm text-cream-200/80">{message}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-auto flex-shrink-0 text-red-400 hover:text-red-300 transition-colors"
          >
            <FaTimes />
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorAlert;
