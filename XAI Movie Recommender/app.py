"""
Script 6: Streamlit Frontend Application

This module provides a user-friendly web interface for the XAI Movie Recommender.
Users can enter their user ID and receive personalized movie recommendations
with explanations.

Usage:
    streamlit run app.py

Prerequisites:
    - FastAPI backend running at http://127.0.0.1:8000
"""

import streamlit as st
import requests
from typing import Optional


# Configuration
API_BASE_URL = "http://127.0.0.1:8000"


def check_api_health() -> bool:
    """
    Check if the FastAPI backend is running and healthy.

    Returns:
        bool: True if API is healthy, False otherwise
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('status') == 'healthy'
        return False
    except requests.exceptions.RequestException:
        return False


def get_recommendations(user_id: int, n: int = 5) -> Optional[dict]:
    """
    Fetch movie recommendations from the API.

    Args:
        user_id: The user ID to get recommendations for
        n: Number of recommendations to fetch

    Returns:
        dict: API response data or None if request fails
    """
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
        return {'error': "Request timed out. The API might be processing a large request."}
    except requests.exceptions.ConnectionError:
        return {'error': "Could not connect to the API. Make sure the backend is running."}
    except requests.exceptions.RequestException as e:
        return {'error': f"Request failed: {str(e)}"}


def get_user_rated_movies(user_id: int, limit: int = 5) -> Optional[dict]:
    """
    Fetch movies rated by a user from the API.

    Args:
        user_id: The user ID
        limit: Maximum number of movies to fetch

    Returns:
        dict: API response data or None if request fails
    """
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


def search_movies(query: str, limit: int = 10) -> Optional[dict]:
    """
    Search for movies by title from the API.

    Args:
        query: Search query (partial movie title)
        limit: Maximum number of results to fetch

    Returns:
        dict: API response data or None if request fails
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/movies/search",
            params={"q": query, "limit": limit},
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        return None

    except requests.exceptions.RequestException:
        return None


def get_recommendations_by_movie(movie_title: str, n: int = 5) -> Optional[dict]:
    """
    Fetch movie recommendations based on a movie title from the API.

    Args:
        movie_title: The movie title to base recommendations on
        n: Number of recommendations to fetch

    Returns:
        dict: API response data or None if request fails
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/recommend/by-movie/{movie_title}",
            params={"n": n},
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {'error': f"Movie '{movie_title}' not found"}
        else:
            return {'error': f"API returned status code {response.status_code}"}

    except requests.exceptions.Timeout:
        return {'error': "Request timed out. The API might be processing a large request."}
    except requests.exceptions.ConnectionError:
        return {'error': "Could not connect to the API. Make sure the backend is running."}
    except requests.exceptions.RequestException as e:
        return {'error': f"Request failed: {str(e)}"}


def main():
    """
    Main Streamlit application.
    """
    # Page configuration
    st.set_page_config(
        page_title="XAI Movie Recommender",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #FF4B4B;
            text-align: center;
            margin-bottom: 2rem;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 3rem;
        }
        .recommendation-card {
            background-color: #f0f2f6;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 5px solid #FF4B4B;
        }
        .source-movie {
            background-color: #e8f4f8;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<h1 class="main-header">🎬 XAI Movie Recommender</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Get personalized movie recommendations with explanations powered by AI and Knowledge Graphs</p>',
        unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        st.header("About")
        st.info(
            """
            This recommender system uses:
            - **Node2Vec** embeddings to find similar movies
            - **Neo4j** knowledge graph for explanations
            - **Explainable AI** to show why movies are recommended

            **Two ways to use:**
            - **User Mode**: Get recommendations based on your rating history
            - **Guest Mode**: Search for a movie and discover similar ones
            """
        )

        st.header("Settings")
        num_recommendations = st.slider(
            "Number of recommendations",
            min_value=1,
            max_value=10,
            value=5,
            help="How many movie recommendations to show"
        )

        # API Health Check
        st.header("System Status")
        if check_api_health():
            st.success("✓ API is running")
        else:
            st.error("✗ API is not responding")
            st.warning("Make sure the FastAPI backend is running:\n```\npython main.py\n```")

    # Main content area - Create tabs for User and Guest modes
    tab1, tab2 = st.tabs(["👤 User Mode", "🎬 Guest Mode"])

    # ===== TAB 1: USER MODE =====
    with tab1:
        st.markdown("### Get recommendations based on your rating history")
        st.caption("Enter your User ID to get personalized recommendations")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # User input
            user_id_input = st.text_input(
                "Enter your User ID",
                value="1",
                help="Enter a MovieLens user ID (typically a number between 1 and 610)",
                key="user_id_input"
            )

            # Get recommendations button
            if st.button("🎯 Get Recommendations", type="primary", use_container_width=True, key="user_recommend_btn"):
                # Validate input
                if not user_id_input.strip():
                    st.error("Please enter a User ID")
                else:
                    try:
                        user_id = int(user_id_input)
                    except ValueError:
                        st.error("User ID must be a number")
                        user_id = None

                    if user_id and user_id < 1:
                        st.error("User ID must be a positive number")
                        user_id = None

                    if user_id:
                        # Show loading spinner
                        with st.spinner("🔍 Analyzing your movie preferences..."):
                            # Fetch recommendations
                            result = get_recommendations(user_id, n=num_recommendations)

                        # Check for errors
                        if result is None:
                            st.error("Failed to fetch recommendations")
                        elif 'error' in result:
                            st.error(f"Error: {result['error']}")
                        elif result.get('message') and not result.get('recommendations'):
                            st.warning(result['message'])

                            # Show what movies the user has rated
                            st.info("Let's see what movies you've rated:")
                            rated_movies = get_user_rated_movies(user_id, limit=10)

                            if rated_movies and rated_movies.get('rated_movies'):
                                for movie in rated_movies['rated_movies']:
                                    st.write(f"⭐ **{movie['title']}** - Rating: {movie['rating']}/5.0")
                            else:
                                st.write("No rating history found for this user.")
                        else:
                            # Show source movie
                            if result.get('source_movie'):
                                st.markdown(
                                    f"""
                                    <div class="source-movie">
                                        <h3>📽️ Based on your love for:</h3>
                                        <h2>{result['source_movie']}</h2>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            # Show recommendations
                            if result.get('recommendations'):
                                st.markdown("### 🎯 Recommended Movies for You:")

                                for i, rec in enumerate(result['recommendations'], 1):
                                    with st.container():
                                        col_num, col_content = st.columns([0.5, 9.5])

                                        with col_num:
                                            st.markdown(f"### {i}")

                                        with col_content:
                                            st.markdown(f"### {rec['movie_title']}")

                                            # Explanation
                                            st.info(f"💡 {rec['explanation']}")

                                            # Similarity score in an expander
                                            with st.expander("📊 Technical Details"):
                                                st.write(f"**Similarity Score:** {rec['similarity']:.4f}")
                                                st.write(f"**Movie ID:** {rec['movie_id']}")
                                                st.caption(
                                                    "The similarity score represents how close this movie is "
                                                    "to your favorite movie in the knowledge graph embedding space."
                                                )

                                        st.markdown("---")
                            else:
                                st.info("No recommendations found. Try a different user ID.")

    # ===== TAB 2: GUEST MODE =====
    with tab2:
        st.markdown("### Get recommendations based on a movie you like")
        st.caption("No account needed! Just enter a movie title to discover similar movies")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Movie search input
            movie_query = st.text_input(
                "Search for a movie",
                placeholder="e.g., Toy Story, The Matrix, Inception...",
                help="Start typing to search for movies in our database",
                key="movie_search_input"
            )

            # Show search results
            if movie_query and len(movie_query) >= 2:
                with st.spinner("🔍 Searching movies..."):
                    search_results = search_movies(movie_query, limit=10)

                if search_results and search_results.get('results'):
                    st.markdown("**Found movies:**")

                    # Let user select from search results
                    movie_options = {movie['title']: movie for movie in search_results['results']}
                    selected_movie = st.selectbox(
                        "Select a movie:",
                        options=list(movie_options.keys()),
                        key="movie_select"
                    )

                    # Get recommendations button
                    if st.button("🎯 Get Similar Movies", type="primary", use_container_width=True, key="guest_recommend_btn"):
                        if selected_movie:
                            # Show loading spinner
                            with st.spinner(f"🔍 Finding movies similar to {selected_movie}..."):
                                # Fetch recommendations
                                result = get_recommendations_by_movie(selected_movie, n=num_recommendations)

                            # Check for errors
                            if result is None:
                                st.error("Failed to fetch recommendations")
                            elif 'error' in result:
                                st.error(f"Error: {result['error']}")
                            elif result.get('message') and not result.get('recommendations'):
                                st.warning(result['message'])
                            else:
                                # Show source movie
                                if result.get('source_movie'):
                                    st.markdown(
                                        f"""
                                        <div class="source-movie">
                                            <h3>📽️ Because you like:</h3>
                                            <h2>{result['source_movie']}</h2>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

                                # Show recommendations
                                if result.get('recommendations'):
                                    st.markdown("### 🎯 You Might Also Like:")

                                    for i, rec in enumerate(result['recommendations'], 1):
                                        with st.container():
                                            col_num, col_content = st.columns([0.5, 9.5])

                                            with col_num:
                                                st.markdown(f"### {i}")

                                            with col_content:
                                                st.markdown(f"### {rec['movie_title']}")

                                                # Explanation
                                                st.info(f"💡 {rec['explanation']}")

                                                # Similarity score in an expander
                                                with st.expander("📊 Technical Details"):
                                                    st.write(f"**Similarity Score:** {rec['similarity']:.4f}")
                                                    st.write(f"**Movie ID:** {rec['movie_id']}")
                                                    st.caption(
                                                        "The similarity score represents how close this movie is "
                                                        "to the selected movie in the knowledge graph embedding space."
                                                    )

                                            st.markdown("---")
                                else:
                                    st.info("No recommendations found. Try a different movie.")
                else:
                    st.info("No movies found. Try a different search term.")
            elif movie_query:
                st.info("Type at least 2 characters to search")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666;">
            <p>Built with Streamlit, FastAPI, Neo4j, and Node2Vec</p>
            <p>MovieLens dataset courtesy of GroupLens Research</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
