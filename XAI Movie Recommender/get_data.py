"""
Script 1: Data Preparation and Enrichment

This script prepares the MovieLens dataset by enriching movie data with
director and actor information from the TMDb API. The enriched data is
then saved for use in building the knowledge graph.

Usage:
    python get_data.py

Prerequisites:
    - MovieLens dataset in data/ml-latest-small/ directory
    - Valid TMDb API key in .env file
"""

import pandas as pd
import requests
import os
import time
from tqdm import tqdm
from dotenv import load_dotenv


def get_movie_details(tmdb_id, api_key):
    """
    Fetch director and top 5 actors for a movie from TMDb API.

    Args:
        tmdb_id (int): The TMDb movie ID
        api_key (str): TMDb API key for authentication

    Returns:
        tuple: (director_name, list_of_actor_names)
               Returns (None, []) if an error occurs
    """
    # Construct the API URL for movie credits endpoint
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits"
    params = {"api_key": api_key}

    try:
        # Make GET request to TMDb API
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes

        # Parse JSON response
        data = response.json()

        # Extract Director from crew
        director = None
        crew = data.get('crew', [])
        for person in crew:
            if person.get('job') == 'Director':
                director = person.get('name')
                break  # Take the first director found

        # Extract top 5 actors from cast
        cast = data.get('cast', [])
        # Sort by order (lower order = more prominent role)
        cast_sorted = sorted(cast, key=lambda x: x.get('order', 999))
        # Get top 5 actor names
        actors = [person.get('name') for person in cast_sorted[:5] if person.get('name')]

        return director, actors

    except requests.exceptions.RequestException as e:
        # Handle any request errors (network issues, timeouts, etc.)
        print(f"Error fetching data for TMDb ID {tmdb_id}: {e}")
        return None, []


def main():
    """
    Main execution function that orchestrates the data enrichment process.
    """
    # Load environment variables from .env file
    load_dotenv()
    api_key = os.getenv('TMDB_API_KEY')

    if not api_key or api_key == "YOUR_TMDB_API_KEY_HERE":
        print("ERROR: Please set a valid TMDB_API_KEY in the .env file")
        return

    # Define data paths
    movies_path = 'data/ml-latest-small/movies.csv'
    links_path = 'data/ml-latest-small/links.csv'
    output_path = 'data/processed/movies_enriched.csv'

    # Check if input files exist
    if not os.path.exists(movies_path) or not os.path.exists(links_path):
        print(f"ERROR: Required files not found in data/ml-latest-small/")
        print(f"Please download the MovieLens dataset and extract it to that directory")
        return

    print("Loading MovieLens data...")
    # Load movies and links data
    movies_df = pd.read_csv(movies_path)
    links_df = pd.read_csv(links_path)

    # Merge movies with their TMDb IDs
    merged_df = movies_df.merge(links_df, on='movieId', how='left')

    # Create columns for enriched data
    merged_df['director'] = None
    merged_df['actors'] = None

    print(f"Enriching {len(merged_df)} movies with TMDb data...")
    print("This may take a while due to API rate limiting...")

    # Iterate through each movie with progress bar
    for idx, row in tqdm(merged_df.iterrows(), total=len(merged_df)):
        tmdb_id = row['tmdbId']

        # Skip if TMDb ID is missing
        if pd.isna(tmdb_id):
            continue

        # Convert to integer for API call
        tmdb_id = int(tmdb_id)

        # Fetch movie details from TMDb
        director, actors = get_movie_details(tmdb_id, api_key)

        # Store results in DataFrame
        merged_df.at[idx, 'director'] = director
        # Store actors as pipe-separated string for easy parsing later
        merged_df.at[idx, 'actors'] = '|'.join(actors) if actors else None

        # Rate limiting: sleep to avoid overwhelming the API
        # TMDb allows 40 requests per 10 seconds, so 0.25s per request is safe
        time.sleep(0.25)

    # Create output directory if it doesn't exist
    os.makedirs('data/processed', exist_ok=True)

    # Save enriched data to CSV
    merged_df.to_csv(output_path, index=False)

    print(f"\nData enrichment complete!")
    print(f"Enriched data saved to: {output_path}")
    print(f"Total movies processed: {len(merged_df)}")
    print(f"Movies with director info: {merged_df['director'].notna().sum()}")
    print(f"Movies with actor info: {merged_df['actors'].notna().sum()}")


if __name__ == "__main__":
    main()
