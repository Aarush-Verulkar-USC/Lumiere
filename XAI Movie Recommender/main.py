"""
Script 5: FastAPI Backend Application

This module provides a REST API for the XAI Movie Recommender system.
It exposes endpoints for getting movie recommendations with explanations.

Usage:
    uvicorn main:app --reload

    or

    python -m uvicorn main:app --host 0.0.0.0 --port 8000

Endpoints:
    GET /recommend/{user_id} - Get movie recommendations for a user
    GET /health - Health check endpoint
"""

from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from recommender import XAIRecommender


# Pydantic models for API request/response validation
class Recommendation(BaseModel):
    """Model for a single movie recommendation."""
    movie_title: str = Field(..., description="Title of the recommended movie")
    movie_id: int = Field(..., description="MovieLens movie ID")
    explanation: str = Field(..., description="Explanation for why this movie is recommended")
    similarity: float = Field(..., description="Similarity score from Node2Vec embeddings")


class RecommendationResponse(BaseModel):
    """Model for the complete recommendation response."""
    source_movie: Optional[str] = Field(None, description="Title of the movie used as basis for recommendations")
    source_movie_id: Optional[int] = Field(None, description="MovieLens ID of the source movie")
    recommendations: List[Recommendation] = Field(default_factory=list, description="List of recommended movies")
    message: Optional[str] = Field(None, description="Optional message (e.g., error or info message)")


class HealthResponse(BaseModel):
    """Model for health check response."""
    status: str
    model_loaded: bool
    neo4j_connected: bool


# Initialize FastAPI application
app = FastAPI(
    title="XAI Movie Recommender API",
    description="An Explainable AI system for movie recommendations using knowledge graphs and Node2Vec",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow cross-origin requests (needed for web frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global recommender instance
# Initialize on startup to avoid recreating for each request
recommender: Optional[XAIRecommender] = None


@app.on_event("startup")
async def startup_event():
    """
    Initialize the recommender system when the application starts.
    """
    global recommender
    try:
        print("Initializing XAI Recommender...")
        recommender = XAIRecommender()
        print("✓ Recommender initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing recommender: {e}")
        print("API will start but recommendations will fail until this is fixed")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources when the application shuts down.
    """
    global recommender
    if recommender:
        print("Closing recommender connections...")
        recommender.close()
        print("✓ Connections closed")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "XAI Movie Recommender API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "user_recommendations": "/recommend/{user_id}",
            "guest_recommendations": "/recommend/by-movie/{movie_title}",
            "movie_search": "/movies/search?q={query}",
            "user_rated_movies": "/user/{user_id}/rated",
            "health": "/health"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API and its dependencies are working.

    Returns:
        HealthResponse: Status of the API and its components
    """
    model_loaded = False
    neo4j_connected = False

    if recommender:
        # Check if model is loaded
        model_loaded = recommender.wv is not None

        # Check if Neo4j is connected
        try:
            with recommender.driver.session() as session:
                result = session.run("RETURN 1")
                result.single()
                neo4j_connected = True
        except Exception:
            neo4j_connected = False

    status = "healthy" if (model_loaded and neo4j_connected) else "unhealthy"

    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        neo4j_connected=neo4j_connected
    )


@app.get("/recommend/{user_id}", response_model=RecommendationResponse, tags=["Recommendations"])
async def get_recommendations(
    user_id: int = Path(..., description="The MovieLens user ID", ge=1),
    n: int = 5
):
    """
    Get movie recommendations for a specific user.

    The recommendations are based on the user's most recent 5-star rated movie
    and use Node2Vec embeddings to find similar movies. Each recommendation
    includes an explanation based on the knowledge graph.

    Args:
        user_id: The MovieLens user ID
        n: Number of recommendations to return (default: 5)

    Returns:
        RecommendationResponse: Recommended movies with explanations

    Raises:
        HTTPException: If the recommender is not initialized or an error occurs
    """
    if not recommender:
        raise HTTPException(
            status_code=503,
            detail="Recommender system not initialized. Please check server logs."
        )

    try:
        # Get recommendations from the recommender system
        result = recommender.get_recommendations(user_id, n=n)

        # If no source movie found or no recommendations
        if not result.get('source_movie'):
            return RecommendationResponse(
                source_movie=None,
                recommendations=[],
                message=result.get('message', f"No 5-star ratings found for user {user_id}")
            )

        # Build list of recommendations with explanations
        recommendations_with_explanations = []

        for rec in result['recommendations']:
            # Get explanation for this recommendation
            explanation = recommender.get_explanation(
                result['source_movie'],
                rec['title']
            )

            recommendations_with_explanations.append(
                Recommendation(
                    movie_title=rec['title'],
                    movie_id=rec['movieId'],
                    explanation=f"Recommended because {explanation}",
                    similarity=rec['similarity']
                )
            )

        return RecommendationResponse(
            source_movie=result['source_movie'],
            source_movie_id=result.get('source_movie_id'),
            recommendations=recommendations_with_explanations,
            message=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@app.get("/user/{user_id}/rated", tags=["Users"])
async def get_user_rated_movies(
    user_id: int = Path(..., description="The MovieLens user ID", ge=1),
    limit: int = 10
):
    """
    Get a list of movies rated by a specific user.

    Args:
        user_id: The MovieLens user ID
        limit: Maximum number of movies to return (default: 10)

    Returns:
        dict: User's rated movies

    Raises:
        HTTPException: If an error occurs
    """
    if not recommender:
        raise HTTPException(
            status_code=503,
            detail="Recommender system not initialized"
        )

    try:
        with recommender.driver.session() as session:
            query = """
            MATCH (u:User {userId: $userId})-[r:RATED]->(m:Movie)
            RETURN m.title AS title, m.movieId AS movieId, r.rating AS rating
            ORDER BY r.timestamp DESC
            LIMIT $limit
            """
            result = session.run(query, {'userId': user_id, 'limit': limit})

            movies = []
            for record in result:
                movies.append({
                    'movie_id': record['movieId'],
                    'title': record['title'],
                    'rating': record['rating']
                })

            return {
                'user_id': user_id,
                'rated_movies': movies,
                'count': len(movies)
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching user movies: {str(e)}"
        )


@app.get("/movies/search", tags=["Movies"])
async def search_movies(
    q: str,
    limit: int = 10
):
    """
    Search for movies by title (fuzzy matching).

    Args:
        q: Search query (partial movie title)
        limit: Maximum number of results to return (default: 10)

    Returns:
        dict: List of matching movies

    Raises:
        HTTPException: If an error occurs
    """
    if not recommender:
        raise HTTPException(
            status_code=503,
            detail="Recommender system not initialized"
        )

    if not q or len(q.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    try:
        movies = recommender.search_movies(q, limit=limit)
        return {
            'query': q,
            'results': movies,
            'count': len(movies)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching movies: {str(e)}"
        )


@app.get("/recommend/by-movie/{movie_title}", response_model=RecommendationResponse, tags=["Recommendations"])
async def get_recommendations_by_movie(
    movie_title: str = Path(..., description="The movie title to base recommendations on"),
    n: int = 5
):
    """
    Get movie recommendations based on a specific movie (guest mode).

    This endpoint allows guest users to get recommendations without needing a user ID.
    Simply provide a movie title and receive similar movies with explanations.

    Args:
        movie_title: The title of the movie to base recommendations on
        n: Number of recommendations to return (default: 5)

    Returns:
        RecommendationResponse: Recommended movies with explanations

    Raises:
        HTTPException: If the recommender is not initialized or an error occurs
    """
    if not recommender:
        raise HTTPException(
            status_code=503,
            detail="Recommender system not initialized. Please check server logs."
        )

    try:
        # Get recommendations from the recommender system
        result = recommender.get_recommendations_by_movie(movie_title, n=n)

        # If no source movie found or no recommendations
        if not result.get('source_movie'):
            return RecommendationResponse(
                source_movie=None,
                recommendations=[],
                message=result.get('message', f"Movie '{movie_title}' not found")
            )

        # Build list of recommendations with explanations
        recommendations_with_explanations = []

        for rec in result['recommendations']:
            # Get explanation for this recommendation
            explanation = recommender.get_explanation(
                result['source_movie'],
                rec['title']
            )

            recommendations_with_explanations.append(
                Recommendation(
                    movie_title=rec['title'],
                    movie_id=rec['movieId'],
                    explanation=f"Recommended because {explanation}",
                    similarity=rec['similarity']
                )
            )

        return RecommendationResponse(
            source_movie=result['source_movie'],
            source_movie_id=result.get('source_movie_id'),
            recommendations=recommendations_with_explanations,
            message=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@app.get("/graph/path/{source_title}/{target_title}", tags=["Graph"])
async def get_recommendation_path(
    source_title: str = Path(..., description="Source movie title"),
    target_title: str = Path(..., description="Target movie title")
):
    """
    Get the graph path between two movies for visualization.

    Args:
        source_title: The source movie title
        target_title: The target movie title

    Returns:
        dict: Graph data with nodes and edges

    Raises:
        HTTPException: If an error occurs
    """
    if not recommender:
        raise HTTPException(
            status_code=503,
            detail="Recommender system not initialized"
        )

    try:
        with recommender.driver.session() as session:
            # Query to find path between movies
            query = """
            MATCH path = (m1:Movie {title: $source})-[*1..2]-(m2:Movie {title: $target})
            WITH path, nodes(path) as pathNodes, relationships(path) as pathRels
            RETURN pathNodes, pathRels
            LIMIT 1
            """
            result = session.run(query, {
                'source': source_title,
                'target': target_title
            })

            record = result.single()

            if not record:
                return {
                    'nodes': [],
                    'edges': [],
                    'message': 'No path found between these movies'
                }

            nodes_data = record['pathNodes']
            rels_data = record['pathRels']

            # Build nodes list
            nodes = []
            node_map = {}

            for i, node in enumerate(nodes_data):
                labels = list(node.labels)
                node_type = labels[0] if labels else 'Unknown'

                if node_type == 'Movie':
                    label = node.get('title', 'Unknown Movie')
                else:
                    label = node.get('name', 'Unknown')

                node_id = f"{node_type}_{i}"
                node_map[node.id] = node_id

                nodes.append({
                    'id': node_id,
                    'label': label,
                    'type': node_type
                })

            # Build edges list
            edges = []
            for rel in rels_data:
                source_id = node_map.get(rel.start_node.id)
                target_id = node_map.get(rel.end_node.id)

                if source_id and target_id:
                    edges.append({
                        'source': source_id,
                        'target': target_id,
                        'type': rel.type
                    })

            return {
                'nodes': nodes,
                'edges': edges
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching graph path: {str(e)}"
        )


# Run the application
if __name__ == "__main__":
    import uvicorn

    print("Starting XAI Movie Recommender API...")
    print("API Documentation will be available at: http://127.0.0.1:8000/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
