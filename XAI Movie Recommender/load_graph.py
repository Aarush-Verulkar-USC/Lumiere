"""
Script 2: Neo4j Knowledge Graph Loader

This script loads the enriched MovieLens data into a Neo4j graph database.
It creates nodes for Movies, Users, Genres, Directors, and Actors, along with
their relationships (RATED, DIRECTED, ACTED_IN, HAS_GENRE).

Usage:
    python load_graph.py

Prerequisites:
    - Running Neo4j database instance
    - Enriched movies data in data/processed/movies_enriched.csv
    - Ratings data in data/ml-latest-small/ratings.csv
    - Valid Neo4j credentials in .env file
"""

import pandas as pd
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from tqdm import tqdm


class GraphLoader:
    """
    A class to manage loading data into the Neo4j knowledge graph.
    """

    def __init__(self, uri, user, password):
        """
        Initialize connection to Neo4j database.

        Args:
            uri (str): Neo4j connection URI (e.g., bolt://localhost:7687)
            user (str): Neo4j username
            password (str): Neo4j password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"Connected to Neo4j at {uri}")

    def close(self):
        """Close the Neo4j driver connection."""
        self.driver.close()
        print("Neo4j connection closed")

    def run_query(self, query, parameters=None):
        """
        Execute a Cypher query.

        Args:
            query (str): The Cypher query to execute
            parameters (dict): Query parameters for parameterized queries

        Returns:
            list: Query results
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record for record in result]

    def create_constraints(self):
        """
        Create uniqueness constraints on node properties.
        This ensures data integrity and significantly improves query performance.
        """
        print("\nCreating database constraints...")

        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Movie) REQUIRE m.movieId IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.userId IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Director) REQUIRE d.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Actor) REQUIRE a.name IS UNIQUE"
        ]

        for constraint in constraints:
            try:
                self.run_query(constraint)
                print(f"  ✓ Created constraint")
            except Exception as e:
                # Constraint might already exist, which is fine
                if "already exists" in str(e).lower():
                    print(f"  - Constraint already exists (skipping)")
                else:
                    print(f"  ✗ Error creating constraint: {e}")

        print("Constraints setup complete")

    def load_movies_and_relations(self):
        """
        Load movies and their relationships with genres, directors, and actors.
        Uses efficient batch processing with multi-part Cypher queries.
        """
        print("\nLoading movies, genres, directors, and actors...")

        # Load enriched movies data
        movies_path = 'data/processed/movies_enriched.csv'
        if not os.path.exists(movies_path):
            print(f"ERROR: {movies_path} not found. Run get_data.py first.")
            return

        movies_df = pd.read_csv(movies_path)
        print(f"Found {len(movies_df)} movies to load")

        # Process each movie
        with self.driver.session() as session:
            for idx, row in tqdm(movies_df.iterrows(), total=len(movies_df)):
                movie_id = int(row['movieId'])
                title = str(row['title'])

                # Parse genres (format: "Action|Adventure|Sci-Fi")
                genres = []
                if pd.notna(row['genres']) and row['genres'] != '(no genres listed)':
                    genres = [g.strip() for g in str(row['genres']).split('|')]

                # Parse director
                director = None
                if pd.notna(row['director']):
                    director = [str(row['director'])]

                # Parse actors (format: "Actor1|Actor2|Actor3")
                actors = []
                if pd.notna(row['actors']):
                    actors = [a.strip() for a in str(row['actors']).split('|')]

                # Build comprehensive Cypher query
                # This single query creates the movie and all its relationships
                query = """
                // Create or merge the movie node
                MERGE (m:Movie {movieId: $movieId})
                SET m.title = $title

                // Create director relationship if director exists
                WITH m
                FOREACH (director_name IN CASE WHEN $director IS NOT NULL THEN $director ELSE [] END |
                    MERGE (d:Director {name: director_name})
                    MERGE (d)-[:DIRECTED]->(m)
                )

                // Create actor relationships if actors exist
                WITH m
                FOREACH (actor_name IN CASE WHEN $actors IS NOT NULL THEN $actors ELSE [] END |
                    MERGE (a:Actor {name: actor_name})
                    MERGE (a)-[:ACTED_IN]->(m)
                )

                // Create genre relationships if genres exist
                WITH m
                FOREACH (genre_name IN CASE WHEN $genres IS NOT NULL THEN $genres ELSE [] END |
                    MERGE (g:Genre {name: genre_name})
                    MERGE (m)-[:HAS_GENRE]->(g)
                )
                """

                # Execute query with parameters
                session.run(query, {
                    'movieId': movie_id,
                    'title': title,
                    'director': director if director else None,
                    'actors': actors if actors else None,
                    'genres': genres if genres else None
                })

        print("Movies and relationships loaded successfully")

    def load_users_and_ratings(self):
        """
        Load users and their movie ratings.
        Creates User nodes and RATED relationships to Movie nodes.
        """
        print("\nLoading users and ratings...")

        # Load ratings data
        ratings_path = 'data/ml-latest-small/ratings.csv'
        if not os.path.exists(ratings_path):
            print(f"ERROR: {ratings_path} not found.")
            return

        ratings_df = pd.read_csv(ratings_path)
        print(f"Found {len(ratings_df)} ratings to load")

        # Process ratings in batches for better performance
        batch_size = 1000
        with self.driver.session() as session:
            for i in tqdm(range(0, len(ratings_df), batch_size)):
                batch = ratings_df.iloc[i:i + batch_size]

                # Prepare batch data
                ratings_batch = []
                for _, row in batch.iterrows():
                    ratings_batch.append({
                        'userId': int(row['userId']),
                        'movieId': int(row['movieId']),
                        'rating': float(row['rating']),
                        'timestamp': int(row['timestamp'])
                    })

                # Batch insert query
                query = """
                UNWIND $ratings AS rating
                MERGE (u:User {userId: rating.userId})
                WITH u, rating
                MATCH (m:Movie {movieId: rating.movieId})
                MERGE (u)-[r:RATED]->(m)
                SET r.rating = rating.rating, r.timestamp = rating.timestamp
                """

                session.run(query, {'ratings': ratings_batch})

        print("Users and ratings loaded successfully")

    def print_statistics(self):
        """
        Print statistics about the loaded graph.
        """
        print("\n" + "="*50)
        print("Graph Statistics")
        print("="*50)

        stats_queries = [
            ("Movies", "MATCH (m:Movie) RETURN count(m) AS count"),
            ("Users", "MATCH (u:User) RETURN count(u) AS count"),
            ("Genres", "MATCH (g:Genre) RETURN count(g) AS count"),
            ("Directors", "MATCH (d:Director) RETURN count(d) AS count"),
            ("Actors", "MATCH (a:Actor) RETURN count(a) AS count"),
            ("Ratings", "MATCH ()-[r:RATED]->() RETURN count(r) AS count"),
            ("DIRECTED relationships", "MATCH ()-[r:DIRECTED]->() RETURN count(r) AS count"),
            ("ACTED_IN relationships", "MATCH ()-[r:ACTED_IN]->() RETURN count(r) AS count"),
            ("HAS_GENRE relationships", "MATCH ()-[r:HAS_GENRE]->() RETURN count(r) AS count"),
        ]

        for label, query in stats_queries:
            result = self.run_query(query)
            count = result[0]['count'] if result else 0
            print(f"  {label}: {count:,}")

        print("="*50)


def main():
    """
    Main execution function.
    """
    # Load environment variables
    load_dotenv()
    uri = os.getenv('NEO4J_URI')
    user = os.getenv('NEO4J_USER')
    password = os.getenv('NEO4J_PASSWORD')

    # Validate credentials
    if not all([uri, user, password]) or password == "YOUR_NEO4J_PASSWORD_HERE":
        print("ERROR: Please set valid Neo4j credentials in the .env file")
        return

    # Initialize graph loader
    loader = GraphLoader(uri, user, password)

    try:
        # Execute loading steps in order
        loader.create_constraints()
        loader.load_movies_and_relations()
        loader.load_users_and_ratings()
        loader.print_statistics()

        print("\n✓ Graph loading complete!")
        print("Your Neo4j knowledge graph is ready for training.")

    except Exception as e:
        print(f"\n✗ Error during graph loading: {e}")
        raise

    finally:
        # Always close the connection
        loader.close()


if __name__ == "__main__":
    main()
