"""
Script 3: Node2Vec Model Training

This script trains a Node2Vec model on the Neo4j knowledge graph.
Node2Vec creates vector embeddings for nodes in the graph, which can
be used to find similar movies based on graph structure.

Usage:
    python train_models.py

Prerequisites:
    - Running Neo4j database with loaded graph data
    - Valid Neo4j credentials in .env file
"""

import os
import networkx as nx
from neo4j import GraphDatabase
from node2vec import Node2Vec
from dotenv import load_dotenv
from tqdm import tqdm


def fetch_graph_from_neo4j(driver):
    """
    Fetch the entire graph from Neo4j and convert it to a NetworkX graph.
    Uses node identifiers (movieId for movies, names for others) as node keys.

    Args:
        driver: Neo4j driver instance

    Returns:
        networkx.Graph: A NetworkX graph representation of the knowledge graph
    """
    print("Fetching graph data from Neo4j...")

    # Create an empty undirected graph
    G = nx.Graph()

    with driver.session() as session:
        # Query to get all relationships with node identifiers
        # We use movie IDs for movies and names for other node types
        query = """
        MATCH (n)-[r]->(m)
        RETURN
            CASE
                WHEN 'Movie' IN labels(n) THEN 'movie_' + toString(n.movieId)
                WHEN 'User' IN labels(n) THEN 'user_' + toString(n.userId)
                WHEN 'Genre' IN labels(n) THEN 'genre_' + n.name
                WHEN 'Director' IN labels(n) THEN 'director_' + n.name
                WHEN 'Actor' IN labels(n) THEN 'actor_' + n.name
                ELSE 'unknown_' + toString(id(n))
            END AS source,
            CASE
                WHEN 'Movie' IN labels(m) THEN 'movie_' + toString(m.movieId)
                WHEN 'User' IN labels(m) THEN 'user_' + toString(m.userId)
                WHEN 'Genre' IN labels(m) THEN 'genre_' + m.name
                WHEN 'Director' IN labels(m) THEN 'director_' + m.name
                WHEN 'Actor' IN labels(m) THEN 'actor_' + m.name
                ELSE 'unknown_' + toString(id(m))
            END AS target,
            type(r) AS relationship
        """

        result = session.run(query)

        # Add edges to the NetworkX graph
        edge_count = 0
        for record in tqdm(result, desc="Loading edges"):
            source = record['source']
            target = record['target']
            rel_type = record['relationship']

            # Add edge with relationship type as attribute
            G.add_edge(source, target, relationship=rel_type)
            edge_count += 1

        print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    return G


def train_node2vec_model(graph, dimensions=64, walk_length=30, num_walks=200, workers=4):
    """
    Train a Node2Vec model on the given graph.

    Node2Vec learns vector representations of nodes by performing random walks
    on the graph and then applying Word2Vec-style learning.

    Args:
        graph: NetworkX graph
        dimensions (int): Embedding dimensions (default: 64)
        walk_length (int): Length of each random walk (default: 30)
        num_walks (int): Number of walks per node (default: 200)
        workers (int): Number of parallel workers (default: 4)

    Returns:
        node2vec.Node2Vec: Trained Node2Vec model
    """
    print("\nInitializing Node2Vec model...")
    print(f"  Dimensions: {dimensions}")
    print(f"  Walk length: {walk_length}")
    print(f"  Walks per node: {num_walks}")
    print(f"  Workers: {workers}")

    # Initialize Node2Vec
    # p and q parameters control the random walk strategy:
    # - p: return parameter (likelihood of returning to previous node)
    # - q: in-out parameter (likelihood of exploring vs. staying local)
    # Default values (p=1, q=1) give unbiased random walks
    node2vec = Node2Vec(
        graph,
        dimensions=dimensions,
        walk_length=walk_length,
        num_walks=num_walks,
        workers=workers,
        quiet=False
    )

    print("\nTraining Node2Vec model...")
    print("This may take several minutes depending on graph size...")

    # Train the model using Word2Vec
    # window: maximum distance between current and predicted node in a walk
    # min_count: ignores all nodes with total frequency lower than this
    # batch_words: number of nodes to process in each batch
    model = node2vec.fit(
        window=10,
        min_count=1,
        batch_words=4
    )

    print("Model training complete!")

    return model


def save_model(model, output_path='models/node2vec.model'):
    """
    Save the trained Node2Vec model to disk.

    Args:
        model: Trained Node2Vec model
        output_path (str): Path to save the model
    """
    # Create models directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the model
    model.wv.save(output_path)
    print(f"\nModel saved to: {output_path}")


def print_model_info(model):
    """
    Print information about the trained model.

    Args:
        model: Trained Node2Vec model
    """
    print("\n" + "="*50)
    print("Model Information")
    print("="*50)
    print(f"  Total nodes embedded: {len(model.wv)}")
    print(f"  Embedding dimensions: {model.wv.vector_size}")
    print(f"  Example nodes in model:")

    # Show sample of different node types
    node_types = ['movie_', 'actor_', 'director_', 'genre_', 'user_']
    for node_type in node_types:
        matching_nodes = [key for key in list(model.wv.index_to_key)[:100]
                         if key.startswith(node_type)]
        if matching_nodes:
            print(f"    {node_type[:-1].capitalize()}: {matching_nodes[0]}")

    print("="*50)


def test_similarity(model):
    """
    Test the model by finding similar nodes to a sample movie.

    Args:
        model: Trained Node2Vec model
    """
    print("\n" + "="*50)
    print("Testing Model - Finding Similar Movies")
    print("="*50)

    # Find a movie node to test with
    movie_nodes = [key for key in model.wv.index_to_key if key.startswith('movie_')]

    if movie_nodes:
        # Test with the first movie
        test_node = movie_nodes[0]
        print(f"Test node: {test_node}")

        # Find similar nodes
        similar = model.wv.most_similar(test_node, topn=10)

        print("\nTop 10 most similar nodes:")
        for node, similarity in similar:
            print(f"  {node}: {similarity:.4f}")

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

    # Connect to Neo4j
    print(f"Connecting to Neo4j at {uri}...")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        # Step 1: Fetch graph from Neo4j
        graph = fetch_graph_from_neo4j(driver)

        if graph.number_of_nodes() == 0:
            print("ERROR: Graph is empty. Please run load_graph.py first.")
            return

        # Step 2: Train Node2Vec model
        model = train_node2vec_model(
            graph,
            dimensions=64,
            walk_length=30,
            num_walks=200,
            workers=4
        )

        # Step 3: Save the model
        save_model(model, 'models/node2vec.model')

        # Step 4: Print model information
        print_model_info(model)

        # Step 5: Test the model
        test_similarity(model)

        print("\n✓ Model training complete!")
        print("You can now use the model for recommendations with recommender.py")

    except Exception as e:
        print(f"\n✗ Error during model training: {e}")
        raise

    finally:
        # Close Neo4j connection
        driver.close()
        print("\nNeo4j connection closed")


if __name__ == "__main__":
    main()
