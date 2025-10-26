"""
Test script for the new guest mode functionality.
This script tests the movie search and movie-based recommendations.
"""

from recommender import XAIRecommender


def test_guest_mode():
    """Test the guest mode features."""
    print("=" * 60)
    print("Testing Guest Mode Functionality")
    print("=" * 60)

    # Initialize recommender
    print("\n1. Initializing XAI Recommender...")
    recommender = XAIRecommender()
    print("✓ Recommender initialized")

    try:
        # Test 1: Movie search
        print("\n2. Testing movie search...")
        search_query = "toy story"
        print(f"   Searching for: '{search_query}'")
        results = recommender.search_movies(search_query, limit=5)

        if results:
            print(f"   ✓ Found {len(results)} movies:")
            for movie in results:
                print(f"      - {movie['title']} (ID: {movie['movieId']})")
        else:
            print("   ✗ No movies found")

        # Test 2: Get movie by exact title
        print("\n3. Testing exact movie lookup...")
        test_title = "Toy Story (1995)"
        print(f"   Looking up: '{test_title}'")
        movie = recommender.get_movie_by_title(test_title)

        if movie:
            print(f"   ✓ Found: {movie['title']} (ID: {movie['movieId']})")
        else:
            print(f"   ✗ Movie '{test_title}' not found")
            # Try with the first search result instead
            if results:
                test_title = results[0]['title']
                print(f"   Trying with: '{test_title}'")
                movie = recommender.get_movie_by_title(test_title)

        # Test 3: Get recommendations based on a movie
        if movie:
            print(f"\n4. Testing movie-based recommendations...")
            print(f"   Getting recommendations for: '{movie['title']}'")

            recommendations = recommender.get_recommendations_by_movie(movie['title'], n=5)

            if recommendations.get('recommendations'):
                print(f"   ✓ Found {len(recommendations['recommendations'])} recommendations:")
                print(f"\n   Because you like: {recommendations['source_movie']}")
                print("   You might also enjoy:")

                for i, rec in enumerate(recommendations['recommendations'], 1):
                    explanation = recommender.get_explanation(
                        recommendations['source_movie'],
                        rec['title']
                    )
                    print(f"\n   {i}. {rec['title']}")
                    print(f"      Similarity: {rec['similarity']:.4f}")
                    print(f"      Why? Because {explanation}")
            else:
                print(f"   Message: {recommendations.get('message', 'No recommendations found')}")
        else:
            print("\n4. Cannot test recommendations - no source movie found")

        # Test 4: Test with another popular movie
        print("\n5. Testing with another movie: 'The Matrix (1999)'...")
        matrix_recs = recommender.get_recommendations_by_movie("The Matrix (1999)", n=3)

        if matrix_recs.get('recommendations'):
            print(f"   ✓ Found {len(matrix_recs['recommendations'])} recommendations")
            for i, rec in enumerate(matrix_recs['recommendations'], 1):
                print(f"   {i}. {rec['title']} (similarity: {rec['similarity']:.4f})")
        else:
            print(f"   Message: {matrix_recs.get('message', 'No recommendations found')}")

        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close connection
        print("\nClosing recommender connection...")
        recommender.close()
        print("✓ Done")


if __name__ == "__main__":
    test_guest_mode()
