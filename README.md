# 🎬 Lumiere

> Explainable AI Movie Recommendations powered by Knowledge Graphs

Lumiere is an intelligent movie recommendation system that not only suggests movies you'll love but also explains **why** you'll love them. Using Node2Vec embeddings and Neo4j knowledge graphs, every recommendation comes with a clear explanation based on actors, directors, and genres.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)

## ✨ Features

- 🎯 **Two Modes**:
  - **User Mode**: Get personalized recommendations based on your rating history
  - **Guest Mode**: Discover similar movies without an account

- 🧠 **Explainable AI**: Every recommendation includes a clear explanation
- 📊 **Knowledge Graph**: Visual connections between movies, actors, directors, and genres
- ⚡ **Real-time Search**: Fast fuzzy search across thousands of movies
- 🎨 **Beautiful UI**: Modern, responsive React interface with Manrope font
- 🔍 **Graph Visualization**: Interactive D3.js visualizations of movie relationships

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  React Frontend │────▶│  FastAPI Backend │────▶│  Neo4j Database │
│   (TypeScript)  │     │     (Python)     │     │  (Graph Data)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  Node2Vec    │
                        │  Embeddings  │
                        └──────────────┘
```

**Tech Stack**:
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, D3.js
- **Backend**: FastAPI, Python 3.10+
- **Database**: Neo4j (Graph Database)
- **ML**: Node2Vec, NetworkX, Gensim
- **Data**: MovieLens dataset

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Neo4j 5.x
- 4GB RAM minimum

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lumiere.git
cd lumiere
```

### 2. Backend Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
# Create .env file with:
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your-password
```

### 3. Database Setup

```bash
# Start Neo4j (adjust for your installation)
neo4j start

# Download and prepare data
python get_data.py

# Load into Neo4j
python load_graph.py

# Train Node2Vec model (takes 5-10 minutes)
python train_models.py
```

### 4. Start Backend

```bash
# Start FastAPI server
python main.py
# API will be available at http://localhost:8000
```

### 5. Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend will be available at http://localhost:3000
```

### 6. Open Your Browser

Visit **http://localhost:3000** and start exploring! 🎉

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Deploy to production
- **[Guest Mode Guide](GUEST_MODE_GUIDE.md)** - Using the guest mode feature
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)
- **[Project Overview](PROJECT_OVERVIEW.md)** - Detailed technical overview
- **[Quick Start](QUICKSTART.md)** - Detailed setup instructions

## 🎮 Usage

### User Mode
1. Enter your User ID (e.g., 1, 15, 133)
2. Click "Get Recommendations"
3. View personalized recommendations with explanations

### Guest Mode
1. Click "Guest Mode" tab
2. Search for a movie you like (e.g., "Toy Story")
3. Select from results
4. Click "Get Similar Movies"
5. Discover new movies with AI explanations!

## 🛠️ Development

### Project Structure

```
lumiere/
├── frontend/           # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── types/
│   └── package.json
├── models/            # Trained ML models
├── data/              # MovieLens data
├── main.py            # FastAPI backend
├── recommender.py     # Core recommendation logic
├── load_graph.py      # Neo4j data loader
├── train_models.py    # Node2Vec training
└── requirements.txt   # Python dependencies
```

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /recommend/{user_id}` - User-based recommendations
- `GET /recommend/by-movie/{title}` - Movie-based recommendations (guest mode)
- `GET /movies/search?q={query}` - Search movies
- `GET /user/{user_id}/rated` - Get user's ratings
- `GET /graph/path/{source}/{target}` - Get graph path for visualization

### Running Tests

```bash
# Test guest mode functionality
python test_guest_mode.py

# Test API health
curl http://localhost:8000/health

# Search for movies
curl "http://localhost:8000/movies/search?q=matrix"
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **MovieLens Dataset** - Provided by [GroupLens Research](https://grouplens.org/datasets/movielens/)
- **Neo4j** - Graph database platform
- **Node2Vec** - Graph embedding algorithm
- **FastAPI** - Modern Python web framework
- **React** - UI library

