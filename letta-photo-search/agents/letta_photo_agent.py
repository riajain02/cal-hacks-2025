"""
Letta Photo Search Agent
This agent searches for photos based on user queries using intelligent semantic matching
"""
import os
import json
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PhotoSearchAgent:
    """Intelligent photo search agent with semantic understanding"""

    def __init__(self):
        """Initialize the photo search agent"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create console handler if not already exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.api_key = os.getenv('LETTA_API_KEY')

        # Load photo database
        self.photo_database = self._load_photo_database()

        # Build semantic keyword mappings for smarter search
        self.semantic_mappings = {
            'pet': ['dog', 'cat', 'animal'],
            'animal': ['dog', 'cat', 'pet'],
            'nature': ['mountain', 'forest', 'beach', 'ocean', 'sunset', 'landscape', 'tree', 'flower'],
            'outdoor': ['park', 'mountain', 'forest', 'beach', 'ocean', 'hiking'],
            'indoor': ['workspace', 'office', 'desk', 'cafe'],
            'drink': ['coffee', 'beverage'],
            'food': ['fruit', 'coffee'],
            'work': ['laptop', 'workspace', 'office', 'desk'],
            'scenery': ['sunset', 'mountain', 'landscape', 'ocean', 'beach'],
            'city': ['urban', 'skyline', 'building'],
            'plant': ['flower', 'tree', 'garden'],
        }

        self.logger.info("Photo Search Agent initialized with semantic understanding")

    def _load_photo_database(self) -> List[Dict]:
        """Load the photo database from JSON file"""
        db_path = 'data/photo_database.json'
        with open(db_path, 'r') as f:
            data = json.load(f)
        return data['photos']

    def search_photos(self, query: str) -> List[Dict]:
        """
        Search for photos based on user query with semantic understanding

        Args:
            query: User's search query

        Returns:
            List of matching photos with their details
        """
        query_lower = query.lower().strip()

        # Expand query with semantic mappings
        search_terms = [query_lower]
        for synonym_group_key, synonyms in self.semantic_mappings.items():
            if query_lower == synonym_group_key or query_lower in synonyms:
                search_terms.extend(synonyms)
                if query_lower in synonyms:
                    search_terms.append(synonym_group_key)

        # Remove duplicates
        search_terms = list(set(search_terms))

        matches = []
        for photo in self.photo_database:
            score = 0
            matched_terms = []

            # Check each search term
            for term in search_terms:
                # Exact title match (highest weight)
                if term == photo['title'].lower():
                    score += 20
                    matched_terms.append(f"exact title match: '{term}'")
                # Title contains term
                elif term in photo['title'].lower():
                    score += 15
                    matched_terms.append(f"title contains: '{term}'")

                # Description match
                if term in photo['description'].lower():
                    score += 8
                    matched_terms.append(f"description contains: '{term}'")

                # Tag matches
                for tag in photo['tags']:
                    if term == tag.lower():
                        score += 10
                        matched_terms.append(f"exact tag: '{tag}'")
                    elif term in tag.lower() or tag.lower() in term:
                        score += 5
                        matched_terms.append(f"tag match: '{tag}'")

            if score > 0:
                matches.append({
                    **photo,
                    'relevance_score': score,
                    'match_explanation': ', '.join(matched_terms[:3]),  # Top 3 reasons
                    'search_query': query
                })

        # Sort by relevance score (highest first)
        matches.sort(key=lambda x: x['relevance_score'], reverse=True)

        # Return top 3 matches
        top_matches = matches[:3]

        if top_matches:
            self.logger.info(f"Found {len(top_matches)} match(es) for '{query}':")
            for i, match in enumerate(top_matches, 1):
                self.logger.debug(f"  {i}. {match['title']} (score: {match['relevance_score']})")
        else:
            self.logger.warning(f"No matches found for '{query}'")

        return top_matches

    def get_photo_by_id(self, photo_id: int) -> Optional[Dict]:
        """Get a specific photo by ID"""
        for photo in self.photo_database:
            if photo['id'] == photo_id:
                return photo
        return None

    def list_all_photos(self) -> List[Dict]:
        """List all available photos"""
        return self.photo_database


# Test function
def test_agent():
    """Test the photo search agent"""
    print("\n" + "="*60)
    print("TESTING PHOTO SEARCH AGENT")
    print("="*60 + "\n")

    agent = PhotoSearchAgent()

    # Test queries including semantic ones
    test_queries = [
        "dog",
        "pet",
        "sunset",
        "coffee",
        "nature",
        "work",
        "animal",
        "city",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        print(f"{'='*60}")

        results = agent.search_photos(query)

        if results:
            for i, photo in enumerate(results, 1):
                print(f"\n{i}. {photo['title']}")
                print(f"   Score: {photo.get('relevance_score', 0)}")
                print(f"   Reason: {photo.get('match_explanation', 'N/A')}")
                print(f"   Description: {photo['description'][:60]}...")
        else:
            print("   No results found.")

        print()


if __name__ == "__main__":
    test_agent()
