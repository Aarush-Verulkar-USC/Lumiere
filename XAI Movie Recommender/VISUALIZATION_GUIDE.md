# Visualization Guide

This guide explains how to use the visualization features in the XAI Movie Recommender.

## Overview

The project now includes interactive graph visualizations that show:
1. **Recommendation Paths** - How movies are connected through actors, directors, and genres
2. **User Networks** - A user's rated movies and their relationships
3. **Embedding Space** - 2D visualization of Node2Vec embeddings

## Setup

### Install Additional Dependencies

```bash
source .venv/bin/activate
pip install plotly scikit-learn
```

Or reinstall all requirements:

```bash
pip install -r requirements.txt
```

## Using Visualizations

### Option 1: Enhanced Streamlit App (Recommended)

Run the enhanced app with built-in visualizations:

```bash
streamlit run app_with_viz.py
```

**Features:**

#### 🎯 Get Recommendations Mode
- Enter a user ID
- View recommendations with interactive graph paths
- See how each recommended movie connects to your source movie
- Toggle visualization on/off

#### 🔍 Explore Graph Mode
- **Recommendation Path Tab**
  - Enter two movie titles
  - See the connection path through the knowledge graph
  - Visualize shared actors, directors, or genres

- **User Graph Tab**
  - Enter a user ID
  - See their rated movies and connections
  - Explore their taste profile

#### 📊 View Embeddings Mode
- Visualize Node2Vec embeddings in 2D space
- See clusters of similar movies, actors, genres
- Interactive zoom and pan
- Color-coded by node type

### Option 2: Command-Line Visualization

Use the standalone visualization script:

```bash
# Visualize path between two movies
python visualize.py --source "Toy Story (1995)" --target "Toy Story 2 (1999)"

# View embeddings
python visualize.py --embeddings

# Get user graph data
python visualize.py --user-id 1
```

### Option 3: Python API

Use visualizations programmatically:

```python
from visualize import GraphVisualizer

# Initialize visualizer
viz = GraphVisualizer()

# 1. Visualize recommendation path
fig = viz.visualize_recommendation_path(
    "Toy Story (1995)",
    "Finding Nemo (2003)"
)
fig.show()

# 2. Get user's movie graph
user_graph = viz.get_user_graph(user_id=1, limit=20)
print(f"Nodes: {user_graph.number_of_nodes()}")
print(f"Edges: {user_graph.number_of_edges()}")

# 3. Visualize embeddings in 2D
fig = viz.visualize_embeddings_2d(max_nodes=500)
fig.show()

# Close connection
viz.close()
```

## Understanding the Visualizations

### Recommendation Path Graph

**What it shows:**
- How a recommended movie connects to your source movie
- The intermediate nodes (actors, directors, genres)

**Node Colors:**
- 🔴 **Red**: Movies
- 🔵 **Blue**: Actors
- 🟠 **Orange**: Directors
- 🟢 **Green**: Genres

**How to read:**
- Nodes are positioned using spring layout
- Edges show relationships
- Hover to see node details

**Example:**
```
[Toy Story] --(Tom Hanks)--> [Forrest Gump]
```
This shows both movies feature Tom Hanks.

### User Network Graph

**What it shows:**
- User's highly-rated movies
- Connections to actors, directors, genres
- Pattern of preferences

**Use cases:**
- Understand user taste profile
- See common actors/directors they like
- Identify genre preferences

### Embeddings Visualization

**What it shows:**
- 64-dimensional vectors reduced to 2D using PCA
- Spatial relationships between nodes
- Clusters of similar entities

**How to interpret:**
- **Distance**: Closer points are more similar
- **Clusters**: Groups of related movies/actors/genres
- **Colors**: Different node types

**Principal Components:**
- PC1 and PC2 show the main axes of variation
- Percentage shows how much variance is explained

## Visualization Examples

### Example 1: See Why a Movie Was Recommended

```python
from visualize import GraphVisualizer

viz = GraphVisualizer()

# Get recommendations for user 1
from recommender import XAIRecommender
rec = XAIRecommender()
result = rec.get_recommendations(user_id=1, n=5)

source = result['source_movie']
target = result['recommendations'][0]['title']

# Visualize the connection
fig = viz.visualize_recommendation_path(source, target)
fig.show()

rec.close()
viz.close()
```

### Example 2: Explore Movie Similarities

```python
# Compare different movies to the same source
movies_to_compare = [
    "Toy Story 2 (1999)",
    "Monsters, Inc. (2001)",
    "Finding Nemo (2003)",
    "The Incredibles (2004)"
]

source = "Toy Story (1995)"

for movie in movies_to_compare:
    fig = viz.visualize_recommendation_path(source, movie)
    fig.write_html(f"path_{movie.replace(' ', '_')}.html")
    print(f"Saved visualization for {movie}")
```

### Example 3: User Preference Analysis

```python
# Analyze multiple users
for user_id in [1, 15, 133, 288, 414]:
    graph = viz.get_user_graph(user_id, limit=15)

    # Count node types
    actors = [n for n, d in graph.nodes(data=True) if d.get('type') == 'Actor']
    directors = [n for n, d in graph.nodes(data=True) if d.get('type') == 'Director']
    genres = [n for n, d in graph.nodes(data=True) if d.get('type') == 'Genre']

    print(f"User {user_id}: {len(actors)} actors, {len(directors)} directors, {len(genres)} genres")
```

## Integration with Main App

The enhanced Streamlit app (`app_with_viz.py`) integrates visualizations seamlessly:

### Automatic Path Visualization
When you get recommendations, each one shows:
1. The recommendation card
2. The explanation text
3. An interactive graph showing the connection

### Toggle Visualizations
Use the checkbox in the sidebar to enable/disable graphs if you prefer faster loading.

### Multi-Tab Interface
Switch between different visualization modes without reloading.

## Performance Tips

### For Large Graphs
- Limit the number of nodes visualized
- Use the `max_nodes` parameter in embedding visualization
- Filter user graphs with the `limit` parameter

### For Faster Loading
- Cache the visualizer: `@st.cache_resource`
- Pre-generate common visualizations
- Use the API for bulk operations

### For Better Visuals
- Adjust graph layout parameters in `visualize.py`
- Customize colors in the color_map
- Modify node sizes for emphasis

## Troubleshooting

### "Visualizer not available"
**Cause**: Neo4j connection failed or model not loaded

**Solution**:
```bash
# Check Neo4j is running
# Verify .env credentials
python -c "from visualize import GraphVisualizer; v = GraphVisualizer()"
```

### "No path found"
**Cause**: Movies not connected within path length limit

**Solution**:
- Check movie titles are exact (with year)
- Try movies with more obvious connections
- Increase path length in query (edit `visualize.py`)

### Slow Visualization
**Cause**: Too many nodes or complex graph

**Solution**:
- Reduce `max_nodes` parameter
- Limit user graph size
- Use simpler layouts

### Import Errors
**Cause**: Missing dependencies

**Solution**:
```bash
pip install plotly scikit-learn
```

## Advanced Customization

### Change Colors

Edit the `color_map` in `visualize.py`:

```python
color_map = {
    'Movie': '#FF4B4B',    # Red
    'Actor': '#4B88FF',    # Blue
    'Director': '#FFB84B', # Orange
    'Genre': '#4BFF88'     # Green
}
```

### Adjust Layout

Modify spring layout parameters:

```python
pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
# k: optimal distance between nodes
# iterations: layout refinement steps
# seed: for reproducible layouts
```

### Export Visualizations

Save figures to files:

```python
# As HTML (interactive)
fig.write_html("recommendation_path.html")

# As static image (requires kaleido)
fig.write_image("path.png", width=1200, height=800)
```

## Neo4j Browser Queries

For manual exploration in Neo4j Browser (http://localhost:7474):

### Find Path Between Movies
```cypher
MATCH path = (m1:Movie {title: 'Toy Story (1995)'})-[*1..2]-(m2:Movie {title: 'Toy Story 2 (1999)'})
RETURN path
LIMIT 1
```

### User's Movie Network
```cypher
MATCH (u:User {userId: 1})-[r:RATED]->(m:Movie)
WHERE r.rating >= 4.0
MATCH (m)-[rel]-(connected)
WHERE connected:Actor OR connected:Director OR connected:Genre
RETURN m, rel, connected
LIMIT 100
```

### Find Similar Movies by Genre
```cypher
MATCH (m1:Movie {title: 'The Matrix (1999)'})-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(m2:Movie)
RETURN m2.title, collect(g.name) as shared_genres
LIMIT 10
```

## Best Practices

1. **Start Simple**: Begin with basic path visualizations
2. **Iterate**: Refine visualizations based on insights
3. **Combine Methods**: Use UI for exploration, API for automation
4. **Document**: Save interesting visualizations for reference
5. **Optimize**: Balance detail vs. performance

## Future Enhancements

Ideas for extending visualizations:

- **3D Embeddings**: Use t-SNE for 3D visualization
- **Animated Paths**: Show step-by-step recommendation reasoning
- **Heatmaps**: Visualize similarity matrices
- **Timeline**: Show movie release dates in graphs
- **Interactive Filtering**: Filter by genre, year, rating
- **Comparison View**: Side-by-side path comparisons

---

**Happy Visualizing! 🎨📊**

For questions or issues, refer to the main [README.md](README.md) or [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md).
