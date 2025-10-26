"""
Script 4: XAI Recommender Core Logic

This module contains the XAIRecommender class which provides the core
functionality for generating movie recommendations and explanations.

The recommender uses Node2Vec embeddings to find similar movies and
queries the Neo4j knowledge graph to provide explanations for why
movies are being recommended.
"""

import os
from neo4j import GraphDatabase
from gensim.models import KeyedVectors
import numpy as np
from dotenv import load_dotenv


class XAIRecommender:
    """
    Explainable AI Movie Recommender System.

    This class combines Node2Vec embeddings with knowledge graph queries
    to provide movie recommendations along with human-readable explanations.
    """

    def __init__(self):
        """
        Initialize the recommender by loading the model and connecting to Neo4j.
        """
        # Load environment variables
        load_dotenv(override=True)

        # Connect to Neo4j
        uri = os.getenv('NEO4J_URI')
        user = os.getenv('NEO4J_USER')
        password = os.getenv('NEO4J_PASSWORD')

        self.driver = GraphDatabase.driver(uri, auth=(user, password))

        # Load the trained Node2Vec model
        model_path = 'models/node2vec.model'
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. Please run train_models.py first."
            )

        self.wv = KeyedVectors.load(model_path)
        print(f"Loaded Node2Vec model with {len(self.wv)} node embeddings")

    def close(self):
        """Close the Neo4j driver connection."""
        self.driver.close()

    def _get_movie_node_id(self, movie_id):
        """
        Convert a movieId to the node identifier used in the embeddings.

        Args:
            movie_id (int): The movieId from the database

        Returns:
            str: The node identifier (e.g., 'movie_123')
        """
        return f"movie_{movie_id}"

    def _parse_node_id(self, node_id):
        """
        Parse a node identifier to extract type and ID.

        Args:
            node_id (str): Node identifier (e.g., 'movie_123', 'actor_Tom Hanks')

        Returns:
            tuple: (node_type, node_value)
        """
        if '_' in node_id:
            parts = node_id.split('_', 1)
            return parts[0], parts[1]
        return 'unknown', node_id

    def get_source_movie(self, user_id):
        """
        Find the most recent 5-star rated movie for a user.

        Args:
            user_id (int): The user ID

        Returns:
            dict: Movie information {'movieId': int, 'title': str} or None
        """
        with self.driver.session() as session:
            query = """
            MATCH (u:User {userId: $userId})-[r:RATED {rating: 5.0}]->(m:Movie)
            RETURN m.title AS title, m.movieId AS movieId, r.timestamp AS timestamp
            ORDER BY r.timestamp DESC
            LIMIT 1
            """
            result = session.run(query, {'userId': user_id})
            record = result.single()

            if record:
                return {
                    'movieId': record['movieId'],
                    'title': record['title']
                }
            return None

    def get_user_rated_movies(self, user_id):
        """
        Get all movies that a user has rated.

        Args:
            user_id (int): The user ID

        Returns:
            set: Set of movieIds that the user has rated
        """
        with self.driver.session() as session:
            query = """
            MATCH (u:User {userId: $userId})-[:RATED]->(m:Movie)
            RETURN m.movieId AS movieId
            """
            result = session.run(query, {'userId': user_id})
            return {record['movieId'] for record in result}

    def get_movie_title(self, movie_id):
        """
        Get the title of a movie by its ID.

        Args:
            movie_id (int): The movie ID

        Returns:
            str: Movie title or None if not found
        """
        with self.driver.session() as session:
            query = """
            MATCH (m:Movie {movieId: $movieId})
            RETURN m.title AS title
            """
            result = session.run(query, {'movieId': movie_id})
            record = result.single()
            return record['title'] if record else None

    def get_recommendations(self, user_id, n=5):
        """
        Generate movie recommendations for a user with explanations.

        Args:
            user_id (int): The user ID
            n (int): Number of recommendations to return (default: 5)

        Returns:
            dict: {
                'source_movie': str,
                'recommendations': [
                    {'movieId': int, 'title': str, 'similarity': float},
                    ...
                ]
            }
        """
        # Step 1: Find the source movie (most recent 5-star rating)
        source_movie = self.get_source_movie(user_id)

        if not source_movie:
            return {
                'source_movie': None,
                'recommendations': [],
                'message': f"No 5-star ratings found for user {user_id}"
            }

        source_movie_id = source_movie['movieId']
        source_title = source_movie['title']
        source_node_id = self._get_movie_node_id(source_movie_id)

        # Step 2: Check if source movie exists in embeddings
        if source_node_id not in self.wv:
            return {
                'source_movie': source_title,
                'recommendations': [],
                'message': f"Movie '{source_title}' not found in trained model"
            }

        # Step 3: Get movies the user has already rated (to filter them out)
        rated_movies = self.get_user_rated_movies(user_id)

        # Step 4: Find similar movies using Node2Vec embeddings
        # Request more than needed to allow for filtering
        try:
            similar_nodes = self.wv.most_similar(source_node_id, topn=n + 50)
        except KeyError:
            return {
                'source_movie': source_title,
                'recommendations': [],
                'message': f"Could not find similar movies for '{source_title}'"
            }

        # Step 5: Filter and process recommendations
        recommendations = []

        for node_id, similarity in similar_nodes:
            # Parse node ID to check if it's a movie
            node_type, node_value = self._parse_node_id(node_id)

            if node_type != 'movie':
                continue  # Skip non-movie nodes

            try:
                movie_id = int(node_value)
            except ValueError:
                continue  # Skip if movie ID is not a valid integer

            # Skip if it's the source movie or already rated by user
            if movie_id == source_movie_id or movie_id in rated_movies:
                continue

            # Get movie title
            title = self.get_movie_title(movie_id)
            if not title:
                continue  # Skip if movie not found in database

            recommendations.append({
                'movieId': movie_id,
                'title': title,
                'similarity': float(similarity)
            })

            # Stop when we have enough recommendations
            if len(recommendations) >= n:
                break

        return {
            'source_movie': source_title,
            'source_movie_id': source_movie_id,
            'recommendations': recommendations
        }

    def get_explanation(self, source_movie_title, recommended_movie_title):
        """
        Generate a human-readable explanation for why a movie is recommended.

        The explanation is based on finding a path through the knowledge graph
        between the source movie and the recommended movie.

        Args:
            source_movie_title (str): Title of the source movie
            recommended_movie_title (str): Title of the recommended movie

        Returns:
            str: Human-readable explanation
        """
        with self.driver.session() as session:
            # Query to find a short path between the two movies
            # We limit to path length 2 (e.g., Movie-Actor-Movie) for relevance
            query = """
            MATCH path = (m1:Movie {title: $source_title})-[*1..2]-(m2:Movie {title: $recommended_title})
            RETURN path
            LIMIT 1
            """

            result = session.run(query, {
                'source_title': source_movie_title,
                'recommended_title': recommended_movie_title
            })

            record = result.single()

            if not record:
                # No direct path found - return generic explanation
                return "it has similar characteristics to movies you've enjoyed"

            # Parse the path to create explanation
            path = record['path']
            nodes = path.nodes
            relationships = path.relationships

            # If path has 3 nodes (source-intermediate-target)
            if len(nodes) == 3:
                intermediate_node = nodes[1]
                labels = list(intermediate_node.labels)

                if 'Actor' in labels:
                    actor_name = intermediate_node.get('name', 'an actor')
                    return f"it also features **{actor_name}**"

                elif 'Director' in labels:
                    director_name = intermediate_node.get('name', 'a director')
                    return f"it was also directed by **{director_name}**"

                elif 'Genre' in labels:
                    genre_name = intermediate_node.get('name', 'a genre')
                    return f"it shares the **{genre_name}** genre"

            # If path has 2 nodes (direct connection, though unlikely for movies)
            elif len(nodes) == 2 and relationships:
                rel_type = relationships[0].type

                if rel_type == 'HAS_GENRE':
                    return "it shares similar genres"

            # Fallback explanation
            return "it has similar characteristics based on the knowledge graph"

    def explain_recommendation(self, user_id, recommended_movie_title):
        """
        Get a full explanation for why a specific movie is recommended to a user.

        Args:
            user_id (int): The user ID
            recommended_movie_title (str): Title of the recommended movie

        Returns:
            dict: Explanation information
        """
        source_movie = self.get_source_movie(user_id)

        if not source_movie:
            return {
                'explanation': f"No 5-star ratings found for user {user_id}",
                'source_movie': None
            }

        explanation = self.get_explanation(
            source_movie['title'],
            recommended_movie_title
        )

        return {
            'source_movie': source_movie['title'],
            'recommended_movie': recommended_movie_title,
            'explanation': explanation
        }

    def search_movies(self, query, limit=10):
        """
        Search for movies by title (supports fuzzy matching).

        Args:
            query (str): Search query (partial movie title)
            limit (int): Maximum number of results to return

        Returns:
            list: List of matching movies [{'movieId': int, 'title': str}, ...]
        """
        with self.driver.session() as session:
            # Case-insensitive search using CONTAINS
            cypher_query = """
            MATCH (m:Movie)
            WHERE toLower(m.title) CONTAINS toLower($query)
            RETURN m.movieId AS movieId, m.title AS title
            LIMIT $limit
            """
            result = session.run(cypher_query, {'query': query, 'limit': limit})

            movies = []
            for record in result:
                movies.append({
                    'movieId': record['movieId'],
                    'title': record['title']
                })

            return movies

    def get_movie_by_title(self, title):
        """
        Get movie information by exact title.

        Args:
            title (str): Exact movie title

        Returns:
            dict: Movie information {'movieId': int, 'title': str} or None
        """
        with self.driver.session() as session:
            query = """
            MATCH (m:Movie {title: $title})
            RETURN m.movieId AS movieId, m.title AS title
            """
            result = session.run(query, {'title': title})
            record = result.single()

            if record:
                return {
                    'movieId': record['movieId'],
                    'title': record['title']
                }
            return None

    def get_recommendations_by_movie(self, movie_title, n=5):
        """
        Generate movie recommendations based on a specific movie (for guest users).

        Args:
            movie_title (str): The title of the source movie
            n (int): Number of recommendations to return (default: 5)

        Returns:
            dict: {
                'source_movie': str,
                'source_movie_id': int,
                'recommendations': [
                    {'movieId': int, 'title': str, 'similarity': float},
                    ...
                ]
            }
        """
        # Step 1: Find the source movie
        source_movie = self.get_movie_by_title(movie_title)

        if not source_movie:
            return {
                'source_movie': None,
                'recommendations': [],
                'message': f"Movie '{movie_title}' not found in database"
            }

        source_movie_id = source_movie['movieId']
        source_title = source_movie['title']
        source_node_id = self._get_movie_node_id(source_movie_id)

        # Step 2: Check if source movie exists in embeddings
        if source_node_id not in self.wv:
            return {
                'source_movie': source_title,
                'source_movie_id': source_movie_id,
                'recommendations': [],
                'message': f"Movie '{source_title}' not found in trained model"
            }

        # Step 3: Find similar movies using Node2Vec embeddings
        try:
            similar_nodes = self.wv.most_similar(source_node_id, topn=n + 20)
        except KeyError:
            return {
                'source_movie': source_title,
                'source_movie_id': source_movie_id,
                'recommendations': [],
                'message': f"Could not find similar movies for '{source_title}'"
            }

        # Step 4: Filter and process recommendations
        recommendations = []

        for node_id, similarity in similar_nodes:
            # Parse node ID to check if it's a movie
            node_type, node_value = self._parse_node_id(node_id)

            if node_type != 'movie':
                continue  # Skip non-movie nodes

            try:
                movie_id = int(node_value)
            except ValueError:
                continue  # Skip if movie ID is not a valid integer

            # Skip if it's the source movie
            if movie_id == source_movie_id:
                continue

            # Get movie title
            title = self.get_movie_title(movie_id)
            if not title:
                continue  # Skip if movie not found in database

            recommendations.append({
                'movieId': movie_id,
                'title': title,
                'similarity': float(similarity)
            })

            # Stop when we have enough recommendations
            if len(recommendations) >= n:
                break

        return {
            'source_movie': source_title,
            'source_movie_id': source_movie_id,
            'recommendations': recommendations
        }


# Example usage
if __name__ == "__main__":
    # Initialize recommender
    recommender = XAIRecommender()

    try:
        # Get recommendations for user 1
        user_id = 1
        print(f"\nGetting recommendations for User {user_id}...")

        result = recommender.get_recommendations(user_id, n=5)

        print(f"\nBased on your love for: {result['source_movie']}")
        print("\nRecommended movies:")

        for i, rec in enumerate(result['recommendations'], 1):
            explanation = recommender.get_explanation(
                result['source_movie'],
                rec['title']
            )
            print(f"\n{i}. {rec['title']}")
            print(f"   Similarity: {rec['similarity']:.4f}")
            print(f"   Why? Because {explanation}")

    finally:
        # Close connection
        recommender.close()
