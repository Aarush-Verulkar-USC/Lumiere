#!/bin/bash

# Setup script for XAI Movie Recommender
# This script automates the initial setup process

set -e  # Exit on error

echo "=========================================="
echo "XAI Movie Recommender - Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo "${GREEN}✓ Virtual environment created${NC}"
else
    echo "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo "${GREEN}✓ Dependencies installed${NC}"

# Check if MovieLens data exists
echo ""
if [ ! -d "data/ml-latest-small" ] || [ ! -f "data/ml-latest-small/movies.csv" ]; then
    echo "${YELLOW}MovieLens dataset not found. Downloading...${NC}"

    mkdir -p data

    # Download MovieLens dataset
    curl -o data/ml-latest-small.zip https://files.grouplens.org/datasets/movielens/ml-latest-small.zip

    # Extract
    unzip data/ml-latest-small.zip -d data/

    # Cleanup
    rm data/ml-latest-small.zip

    echo "${GREEN}✓ MovieLens dataset downloaded${NC}"
else
    echo "${GREEN}✓ MovieLens dataset already exists${NC}"
fi

# Check .env file
echo ""
if [ -f ".env" ]; then
    if grep -q "YOUR_TMDB_API_KEY_HERE" .env || grep -q "YOUR_NEO4J_PASSWORD_HERE" .env; then
        echo "${RED}⚠ WARNING: Please update your .env file with real credentials!${NC}"
        echo "  - Add your TMDb API key"
        echo "  - Add your Neo4j password"
        echo ""
    else
        echo "${GREEN}✓ .env file configured${NC}"
    fi
else
    echo "${RED}✗ .env file not found${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. ${YELLOW}Activate the virtual environment:${NC}"
echo "   source venv/bin/activate"
echo ""
echo "2. ${YELLOW}Update your .env file with:${NC}"
echo "   - TMDb API Key (get from https://www.themoviedb.org/settings/api)"
echo "   - Neo4j credentials (ensure Neo4j is running)"
echo ""
echo "3. ${YELLOW}Run the data pipeline:${NC}"
echo "   python get_data.py        # Enrich movie data"
echo "   python load_graph.py      # Load into Neo4j"
echo "   python train_models.py    # Train embeddings"
echo ""
echo "4. ${YELLOW}Start the applications:${NC}"
echo "   python main.py            # Start FastAPI backend"
echo "   streamlit run app.py      # Start Streamlit frontend"
echo ""
echo "For more information, see README.md"
echo ""
