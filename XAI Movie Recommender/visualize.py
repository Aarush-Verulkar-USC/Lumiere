"""
Visualization Module for XAI Movie Recommender

This module provides interactive visualizations for:
1. Knowledge graph exploration
2. Recommendation paths
3. Node embeddings in 2D space
4. User-movie interaction graphs

Usage:
    python visualize.py --user-id 1 --mode graph
    streamlit run visualize.py
"""

import os
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from neo4j import GraphDatabase
from dotenv import load_dotenv
from sklearn.decomposition import PCA
import numpy as np
from gensim.models import KeyedVectors
import pandas as pd


class GraphVisualizer:
    """
    Visualizer for the movie recommendation knowledge graph.
    """

    def __init__(self):
        """Initialize Neo4j connection and load model."""
        load_dotenv()

        # Connect to Neo4j
        uri = os.getenv('NEO4J_URI')
        user = os.getenv('NEO4J_USER')
        password = os.getenv('NEO4J_PASSWORD')
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

        # Load Node2Vec model if available
        model_path = 'models/node2vec.model'
        self.wv = None
        if os.path.exists(model_path):
            self.wv = KeyedVectors.load(model_path)
            print(f"Loaded Node2Vec model with {len(self.wv)} embeddings")

    def close(self):
        """Close Neo4j connection."""
        self.driver.close()

    def get_recommendation_path(self, source_movie_title, target_movie_title):
        """
        Get the path between source and recommended movie.

        Args:
            source_movie_title: Title of source movie
            target_movie_title: Title of recommended movie

        Returns:
            NetworkX graph of the path
        """
        with self.driver.session() as session:
            query = """
            MATCH path = (m1:Movie {title: $source})-[*1..3]-(m2:Movie {title: $target})
            RETURN path
            LIMIT 1
            """
            result = session.run(query, {
                'source': source_movie_title,
                'target': target_movie_title
            })

            record = result.single()
            if not record:
                return None

            # Convert Neo4j path to NetworkX graph
            path = record['path']
            G = nx.Graph()

            for node in path.nodes:
                labels = list(node.labels)
                node_data = dict(node)
                node_id = node.id

                # Create a readable label
                if 'Movie' in labels:
                    label = node_data.get('title', f'Movie {node_id}')
                    node_type = 'Movie'
                elif 'Actor' in labels:
                    label = node_data.get('name', f'Actor {node_id}')
                    node_type = 'Actor'
                elif 'Director' in labels:
                    label = node_data.get('name', f'Director {node_id}')
                    node_type = 'Director'
                elif 'Genre' in labels:
                    label = node_data.get('name', f'Genre {node_id}')
                    node_type = 'Genre'
                else:
                    label = f'Node {node_id}'
                    node_type = 'Unknown'

                G.add_node(label, type=node_type, **node_data)

            for rel in path.relationships:
                start_node = path.nodes[0]
                end_node = path.nodes[-1]

                # Find node labels
                start_label = self._get_node_label(rel.start_node)
                end_label = self._get_node_label(rel.end_node)

                G.add_edge(start_label, end_label, type=rel.type)

            return G

    def _get_node_label(self, node):
        """Get readable label for a node."""
        labels = list(node.labels)
        node_data = dict(node)

        if 'Movie' in labels:
            return node_data.get('title', f'Movie {node.id}')
        elif 'Actor' in labels or 'Director' in labels or 'Genre' in labels:
            return node_data.get('name', f'Node {node.id}')
        else:
            return f'Node {node.id}'

    def visualize_recommendation_path(self, source_movie, target_movie):
        """
        Create an interactive visualization of the recommendation path.

        Args:
            source_movie: Source movie title
            target_movie: Recommended movie title

        Returns:
            Plotly figure
        """
        with self.driver.session() as session:
            # Get the path with all node details
            query = """
            MATCH path = (m1:Movie {title: $source})-[*1..2]-(m2:Movie {title: $target})
            WITH path, nodes(path) as pathNodes, relationships(path) as pathRels
            RETURN pathNodes, pathRels
            LIMIT 1
            """
            result = session.run(query, {
                'source': source_movie,
                'target': target_movie
            })

            record = result.single()
            if not record:
                return None

            nodes = record['pathNodes']
            rels = record['pathRels']

            # Build NetworkX graph for layout
            G = nx.Graph()
            node_info = {}

            for i, node in enumerate(nodes):
                labels = list(node.labels)
                node_type = labels[0] if labels else 'Unknown'

                if node_type == 'Movie':
                    label = node.get('title', 'Unknown Movie')
                else:
                    label = node.get('name', 'Unknown')

                G.add_node(i)
                node_info[i] = {
                    'label': label,
                    'type': node_type
                }

            for rel in rels:
                # Find indices of start and end nodes
                start_idx = next(i for i, n in enumerate(nodes) if n.id == rel.start_node.id)
                end_idx = next(i for i, n in enumerate(nodes) if n.id == rel.end_node.id)
                G.add_edge(start_idx, end_idx, type=rel.type)

            # Use spring layout for positioning
            pos = nx.spring_layout(G, k=2, iterations=50)

            # Create edges
            edge_trace = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]

                edge_trace.append(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=3, color='#888'),
                    hoverinfo='none',
                    showlegend=False
                ))

            # Create nodes
            node_x = []
            node_y = []
            node_text = []
            node_color = []
            node_size = []

            color_map = {
                'Movie': '#FF4B4B',
                'Actor': '#4B88FF',
                'Director': '#FFB84B',
                'Genre': '#4BFF88'
            }

            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)

                info = node_info[node]
                node_text.append(f"{info['type']}: {info['label']}")
                node_color.append(color_map.get(info['type'], '#999999'))
                node_size.append(40 if info['type'] == 'Movie' else 25)

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=[node_info[i]['label'] for i in G.nodes()],
                textposition="top center",
                hovertext=node_text,
                marker=dict(
                    size=node_size,
                    color=node_color,
                    line=dict(width=2, color='white')
                )
            )

            # Create figure
            fig = go.Figure(
                data=edge_trace + [node_trace],
                layout=go.Layout(
                    title=dict(
                        text=f"Recommendation Path: {source_movie} → {target_movie}",
                        font=dict(size=16)
                    ),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0, l=0, r=0, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='white'
                )
            )

            return fig

    def get_user_graph(self, user_id, limit=20):
        """
        Get subgraph of user's rated movies and their connections.

        Args:
            user_id: User ID
            limit: Maximum number of movies to include

        Returns:
            NetworkX graph
        """
        with self.driver.session() as session:
            query = """
            MATCH (u:User {userId: $userId})-[r:RATED]->(m:Movie)
            WITH m, r
            ORDER BY r.rating DESC, r.timestamp DESC
            LIMIT $limit
            MATCH (m)-[rel]-(connected)
            WHERE connected:Actor OR connected:Director OR connected:Genre
            RETURN m, rel, connected, r.rating as rating
            """
            result = session.run(query, {'userId': user_id, 'limit': limit})

            G = nx.Graph()

            for record in result:
                movie = record['m']
                connected = record['connected']
                rating = record['rating']

                movie_title = movie.get('title', 'Unknown')
                G.add_node(movie_title, type='Movie', rating=rating)

                conn_labels = list(connected.labels)
                conn_type = conn_labels[0] if conn_labels else 'Unknown'
                conn_name = connected.get('name', connected.get('title', 'Unknown'))

                G.add_node(conn_name, type=conn_type)
                G.add_edge(movie_title, conn_name)

            return G

    def visualize_embeddings_2d(self, node_ids=None, max_nodes=500):
        """
        Visualize Node2Vec embeddings in 2D using PCA.

        Args:
            node_ids: List of specific node IDs to visualize (optional)
            max_nodes: Maximum number of nodes to plot

        Returns:
            Plotly figure
        """
        if not self.wv:
            raise ValueError("Node2Vec model not loaded")

        # Get embeddings
        if node_ids:
            keys = [k for k in node_ids if k in self.wv]
        else:
            keys = list(self.wv.index_to_key)[:max_nodes]

        embeddings = np.array([self.wv[k] for k in keys])

        # Reduce to 2D using PCA
        pca = PCA(n_components=2)
        coords_2d = pca.fit_transform(embeddings)

        # Parse node types
        node_types = []
        node_labels = []
        for key in keys:
            if key.startswith('movie_'):
                node_types.append('Movie')
                node_labels.append(key.replace('movie_', 'M:'))
            elif key.startswith('actor_'):
                node_types.append('Actor')
                node_labels.append(key.replace('actor_', 'A:'))
            elif key.startswith('director_'):
                node_types.append('Director')
                node_labels.append(key.replace('director_', 'D:'))
            elif key.startswith('genre_'):
                node_types.append('Genre')
                node_labels.append(key.replace('genre_', 'G:'))
            else:
                node_types.append('Other')
                node_labels.append(key)

        # Create DataFrame
        df = pd.DataFrame({
            'x': coords_2d[:, 0],
            'y': coords_2d[:, 1],
            'type': node_types,
            'label': node_labels,
            'full_id': keys
        })

        # Create scatter plot
        fig = px.scatter(
            df,
            x='x',
            y='y',
            color='type',
            hover_data=['full_id'],
            title='Node2Vec Embeddings in 2D Space (PCA)',
            color_discrete_map={
                'Movie': '#FF4B4B',
                'Actor': '#4B88FF',
                'Director': '#FFB84B',
                'Genre': '#4BFF88',
                'User': '#FF4BFF'
            }
        )

        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.update_layout(
            plot_bgcolor='white',
            xaxis_title=f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)",
            yaxis_title=f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)"
        )

        return fig


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Visualize movie recommendation graph')
    parser.add_argument('--source', type=str, help='Source movie title')
    parser.add_argument('--target', type=str, help='Target movie title')
    parser.add_argument('--user-id', type=int, help='User ID to visualize')
    parser.add_argument('--embeddings', action='store_true', help='Visualize embeddings')

    args = parser.parse_args()

    viz = GraphVisualizer()

    try:
        if args.source and args.target:
            print(f"Visualizing path: {args.source} → {args.target}")
            fig = viz.visualize_recommendation_path(args.source, args.target)
            if fig:
                fig.show()
            else:
                print("No path found between movies")

        elif args.embeddings:
            print("Visualizing Node2Vec embeddings...")
            fig = viz.visualize_embeddings_2d(max_nodes=500)
            fig.show()

        elif args.user_id:
            print(f"Getting graph for user {args.user_id}")
            G = viz.get_user_graph(args.user_id)
            print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

        else:
            print("Please provide --source and --target, --user-id, or --embeddings")

    finally:
        viz.close()
