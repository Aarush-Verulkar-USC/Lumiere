import React from 'react';
import { FaFilm, FaGithub, FaInfoCircle } from 'react-icons/fa';

const Header: React.FC = () => {
  return (
    <header className="bg-navy-700 shadow-xl sticky top-0 z-50 border-b-2 border-primary-500/50 backdrop-blur-md">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <div>
              <h1 className="text-3xl font-black bg-gradient-to-r from-accent-500 to-primary-500 bg-clip-text text-transparent">
                Lumiere
              </h1>
              <p className="text-sm font-semibold text-cream-200/70">Explainable AI Recommendations ✨</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-4">
            <a
              href="#how-it-works"
              className="flex items-center space-x-2 bg-primary-500/20 border border-primary-500/30 px-5 py-3 rounded-xl font-bold text-cream-200 hover:bg-primary-500/30 hover:border-primary-500/50 transition-all hover:-translate-y-1 shadow-md"
            >
              <FaInfoCircle />
              <span>How it Works</span>
            </a>
            <a
              href="https://github.com/yourusername/lumiere"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 bg-accent-500/20 border border-accent-500/30 px-5 py-3 rounded-xl font-bold text-cream-200 hover:bg-accent-500/30 hover:border-accent-500/50 transition-all hover:-translate-y-1 shadow-md"
            >
              <FaGithub />
              <span>GitHub</span>
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
