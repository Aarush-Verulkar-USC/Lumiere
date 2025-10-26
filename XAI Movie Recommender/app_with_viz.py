"""
Enhanced Streamlit Frontend with Graph Visualizations

This version includes:
- Interactive recommendation path visualization
- Knowledge graph explorer
- Node embeddings visualization
- User rating history graphs

Usage:
    streamlit run app_with_viz.py

Prerequisites:
    - FastAPI backend running at http://127.0.0.1:8000
    - Neo4j database running
    - Trained Node2Vec model
"""

import streamlit as st
import requests
from typing import Optional
import plotly.graph_objects as go
import plotly.express as px
from visualize import GraphVisualizer
import pandas as pd


# Configuration
API_BASE_URL = "http://127.0.0.1:8000"


# Page config
st.set_page_config(
    page_title="XAI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def get_visualizer():
    """Get cached visualizer instance."""
    try:
        return GraphVisualizer()
    except Exception as e:
        st.error(f"Failed to initialize visualizer: {e}")
        return None


def check_api_health() -> bool:
    """Check if the FastAPI backend is running and healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('status') == 'healthy'
        return False
    except requests.exceptions.RequestException:
        return False


def get_recommendations(user_id: int, n: int = 5) -> Optional[dict]:
    """Fetch movie recommendations from the API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/recommend/{user_id}",
            params={"n": n},
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {'error': f"User {user_id} not found"}
        else:
            return {'error': f"API returned status code {response.status_code}"}

    except requests.exceptions.Timeout:
        return {'error': "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {'error': "Could not connect to the API"}
    except requests.exceptions.RequestException as e:
        return {'error': f"Request failed: {str(e)}"}


def get_user_rated_movies(user_id: int, limit: int = 10) -> Optional[dict]:
    """Fetch movies rated by a user from the API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/user/{user_id}/rated",
            params={"limit": limit},
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        return None

    except requests.exceptions.RequestException:
        return None


def main():
    """Main Streamlit application."""

    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #FF4B4B;
            text-align: center;
            margin-bottom: 1rem;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
        }
        .legend-box {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<h1 class="main-header">🎬 XAI Movie Recommender</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Explainable AI Recommendations with Interactive Visualizations</p>',
        unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Mode selection
        mode = st.radio(
            "Choose Mode",
            ["🎯 Get Recommendations", "🔍 Explore Graph", "📊 View Embeddings"],
            help="Select what you want to visualize"
        )

        st.divider()

        if mode == "🎯 Get Recommendations":
            user_id_input = st.text_input("User ID", value="1", key="user_id")
            num_recommendations = st.slider(
                "Number of recommendations",
                min_value=1,
                max_value=10,
                value=5
            )
            show_visualizations = st.checkbox("Show Graph Visualizations", value=True)

        st.divider()

        # API Health Check
        st.header("🏥 System Status")
        if check_api_health():
            st.success("✓ API is running")
        else:
            st.error("✗ API is not responding")
            st.code("python main.py", language="bash")

        # Legend
        st.header("🎨 Node Types")
        st.markdown("""
        <div class="legend-box">
        🔴 <b>Movies</b><br>
        🔵 <b>Actors</b><br>
        🟠 <b>Directors</b><br>
        🟢 <b>Genres</b>
        </div>
        """, unsafe_allow_html=True)

    # Main content
    if mode == "🎯 Get Recommendations":
        show_recommendation_mode(user_id_input, num_recommendations, show_visualizations)
    elif mode == "🔍 Explore Graph":
        show_graph_explorer_mode()
    elif mode == "📊 View Embeddings":
        show_embeddings_mode()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666;">
            <p>Built with Streamlit, FastAPI, Neo4j, and Node2Vec</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_recommendation_mode(user_id_input, num_recommendations, show_visualizations):
    """Show recommendation interface."""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🎯 Get Recommendations", type="primary", use_container_width=True):
            # Validate input
            if not user_id_input.strip():
                st.error("Please enter a User ID")
                return

            try:
                user_id = int(user_id_input)
            except ValueError:
                st.error("User ID must be a number")
                return

            if user_id < 1 or user_id > 610:
                st.warning("Valid User IDs are between 1 and 610")

            # Fetch recommendations
            with st.spinner("🔍 Analyzing your movie preferences..."):
                result = get_recommendations(user_id, n=num_recommendations)

            # Check for errors
            if result is None or 'error' in result:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
                return

            # Display results
            if result.get('message') and not result.get('recommendations'):
                st.warning(result['message'])
                return

            # Show source movie
            if result.get('source_movie'):
                st.markdown(
                    f"""
                    <div style="background-color: #e8f4f8; padding: 1.5rem; border-radius: 10px; text-align: center; margin: 2rem 0;">
                        <h3 style="margin: 0;">📽️ Based on your love for:</h3>
                        <h2 style="margin: 0.5rem 0; color: #FF4B4B;">{result['source_movie']}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Show recommendations with visualizations
            if result.get('recommendations'):
                st.markdown("### 🎯 Your Personalized Recommendations")

                for i, rec in enumerate(result['recommendations'], 1):
                    with st.container():
                        st.markdown(f"### {i}. {rec['movie_title']}")

                        col_left, col_right = st.columns([1, 1])

                        with col_left:
                            st.info(f"💡 {rec['explanation']}")

                            with st.expander("📊 Technical Details"):
                                st.metric("Similarity Score", f"{rec['similarity']:.4f}")
                                st.caption("Higher scores indicate stronger similarity in the graph embedding space")

                        with col_right:
                            if show_visualizations:
                                # Show path visualization
                                viz = get_visualizer()
                                if viz:
                                    with st.spinner("Generating graph..."):
                                        try:
                                            fig = viz.visualize_recommendation_path(
                                                result['source_movie'],
                                                rec['movie_title']
                                            )
                                            if fig:
                                                st.plotly_chart(fig, use_container_width=True)
                                            else:
                                                st.caption("No direct path visualization available")
                                        except Exception as e:
                                            st.caption(f"Visualization unavailable: {str(e)}")

                        st.markdown("---")


def show_graph_explorer_mode():
    """Show graph exploration interface."""
    st.header("🔍 Knowledge Graph Explorer")

    tab1, tab2 = st.tabs(["Recommendation Path", "User Graph"])

    with tab1:
        st.subheader("Explore Recommendation Paths")

        col1, col2 = st.columns(2)

        with col1:
            source_movie = st.text_input(
                "Source Movie Title",
                value="Toy Story (1995)",
                help="Enter the exact movie title"
            )

        with col2:
            target_movie = st.text_input(
                "Target Movie Title",
                value="Toy Story 2 (1999)",
                help="Enter the exact movie title"
            )

        if st.button("🔎 Find Path", type="primary"):
            viz = get_visualizer()
            if viz:
                with st.spinner("Finding path through knowledge graph..."):
                    try:
                        fig = viz.visualize_recommendation_path(source_movie, target_movie)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            st.success("Path found! This shows how the movies are connected.")
                        else:
                            st.warning("No path found between these movies. Try different titles.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.error("Visualizer not available")

    with tab2:
        st.subheader("User Rating Network")

        user_id = st.number_input("User ID", min_value=1, max_value=610, value=1)
        num_movies = st.slider("Number of movies to show", 5, 30, 15)

        if st.button("🎬 Show User's Movie Network", type="primary"):
            viz = get_visualizer()
            if viz:
                with st.spinner("Building user's movie network..."):
                    try:
                        G = viz.get_user_graph(user_id, limit=num_movies)
                        st.info(f"Network has {G.number_of_nodes()} nodes and {G.number_of_edges()} connections")

                        # Display basic stats
                        movie_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'Movie']
                        st.success(f"Found {len(movie_nodes)} movies with their connections to actors, directors, and genres")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.error("Visualizer not available")


def show_embeddings_mode():
    """Show embedding visualization interface."""
    st.header("📊 Node2Vec Embeddings Visualization")

    st.markdown("""
    This visualization shows how the Node2Vec algorithm represents nodes in a 2D space.
    Similar nodes (movies with shared actors, genres, etc.) appear closer together.
    """)

    max_nodes = st.slider("Number of nodes to visualize", 100, 1000, 500, step=100)

    if st.button("🎨 Generate Embedding Visualization", type="primary"):
        viz = get_visualizer()
        if viz and viz.wv:
            with st.spinner("Projecting embeddings to 2D space..."):
                try:
                    fig = viz.visualize_embeddings_2d(max_nodes=max_nodes)
                    st.plotly_chart(fig, use_container_width=True)

                    st.info("""
                    **How to read this chart:**
                    - Each point is a node (movie, actor, director, or genre)
                    - Distance represents similarity in the graph structure
                    - Colors indicate node types
                    - Clusters show groups of related entities
                    """)
                except Exception as e:
                    st.error(f"Error generating visualization: {str(e)}")
        else:
            st.error("Node2Vec model not loaded. Run train_models.py first.")


if __name__ == "__main__":
    main()
