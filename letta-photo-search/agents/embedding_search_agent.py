"""
Embedding-Based Image Search Agent
Uses vector similarity search with sentence transformers to find relevant images
"""
import os
import json
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class EmbeddingSearchAgent:
    """
    Agent that uses embedding-based vector similarity search
    to find images matching natural language descriptions
    """

    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the embedding search agent

        Args:
            model_name: Name of the sentence-transformer model to use
        """
        print("Initializing Embedding Search Agent...")

        # Load sentence transformer model
        print(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)

        # Load photo database
        self.photo_database = self._load_photo_database()

        # Load or generate embeddings
        self.embeddings_file = 'data/photo_embeddings.npy'
        self.embeddings = self._load_or_generate_embeddings()

        print(f"✓ Embedding Search Agent initialized with {len(self.photo_database)} photos")

    def _load_photo_database(self) -> List[Dict]:
        """Load the photo database from JSON file"""
        db_path = 'data/photo_database.json'
        with open(db_path, 'r') as f:
            data = json.load(f)
        return data['photos']

    def _load_or_generate_embeddings(self) -> np.ndarray:
        """Load existing embeddings or generate new ones"""

        # Check if embeddings file exists
        if os.path.exists(self.embeddings_file):
            print("Loading existing embeddings...")
            return np.load(self.embeddings_file)

        print("Generating new embeddings for all photos...")
        return self._generate_embeddings()

    def _generate_embeddings(self) -> np.ndarray:
        """Generate embeddings for all photos in the database"""

        # Create text descriptions for each photo
        texts = []
        for photo in self.photo_database:
            # Combine title, description, and tags into one text
            combined_text = f"{photo['title']}. {photo['description']}. Tags: {', '.join(photo['tags'])}"
            texts.append(combined_text)

        # Generate embeddings
        print(f"Encoding {len(texts)} photo descriptions...")
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

        # Save embeddings
        print(f"Saving embeddings to {self.embeddings_file}...")
        os.makedirs('data', exist_ok=True)
        np.save(self.embeddings_file, embeddings)

        return embeddings

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for photos using embedding-based similarity

        Args:
            query: Natural language search query
            top_k: Number of top results to return

        Returns:
            List of matching photos with similarity scores
        """

        # Encode the query
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Build results
        results = []
        for idx in top_indices:
            photo = self.photo_database[idx].copy()
            photo['similarity_score'] = float(similarities[idx])
            photo['relevance_score'] = int(similarities[idx] * 100)  # Convert to 0-100 scale
            results.append(photo)

        print(f"✓ Found {len(results)} results for query: '{query}'")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']} (similarity: {result['similarity_score']:.3f})")

        return results

    def search_with_context(self, query: str, entities: List[str], context: Dict, top_k: int = 3) -> List[Dict]:
        """
        Enhanced search using extracted entities and context

        Args:
            query: Refined search query from voice agent
            entities: Extracted entities (objects, scenes, etc.)
            context: Contextual information (setting, mood, attributes)
            top_k: Number of results to return

        Returns:
            List of matching photos with scores
        """

        # Build enhanced query from all information
        enhanced_query_parts = [query]

        # Add entities
        if entities:
            enhanced_query_parts.extend(entities)

        # Add context information
        if context:
            if 'mood' in context:
                enhanced_query_parts.append(context['mood'])
            if 'setting' in context:
                enhanced_query_parts.append(context['setting'])
            if 'attributes' in context:
                enhanced_query_parts.extend(context['attributes'])

        # Combine into single query
        enhanced_query = ' '.join(enhanced_query_parts)

        print(f"Enhanced query: '{enhanced_query}'")

        # Perform search
        return self.search(enhanced_query, top_k=top_k)

    def get_photo_by_id(self, photo_id: int) -> Optional[Dict]:
        """Get a specific photo by ID"""
        for photo in self.photo_database:
            if photo['id'] == photo_id:
                return photo
        return None

    def regenerate_embeddings(self):
        """Force regeneration of all embeddings"""
        if os.path.exists(self.embeddings_file):
            os.remove(self.embeddings_file)
        self.embeddings = self._generate_embeddings()
        print("✓ Embeddings regenerated successfully")


# Test function
def test_agent():
    """Test the embedding search agent"""
    print("\n" + "="*60)
    print("TESTING EMBEDDING SEARCH AGENT")
    print("="*60 + "\n")

    agent = EmbeddingSearchAgent()

    test_queries = [
        "happy dog playing",
        "peaceful sunset beach",
        "hot coffee drink",
        "mountain nature landscape",
        "cute cat pet",
        "city lights at night",
        "fresh healthy fruit",
        "forest trees nature",
        "modern laptop workspace",
        "colorful flowers garden",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        print(f"{'='*60}")

        results = agent.search(query, top_k=3)

        if results:
            for i, photo in enumerate(results, 1):
                print(f"\n{i}. {photo['title']}")
                print(f"   Similarity: {photo['similarity_score']:.3f}")
                print(f"   Description: {photo['description'][:60]}...")
        else:
            print("   No results found.")

    # Test with context
    print(f"\n\n{'='*60}")
    print("TESTING CONTEXT-BASED SEARCH")
    print(f"{'='*60}\n")

    results = agent.search_with_context(
        query="happy dog",
        entities=["dog"],
        context={"mood": "happy", "setting": "outdoor", "attributes": ["pet", "playful"]},
        top_k=3
    )

    print("\nResults with context:")
    for i, photo in enumerate(results, 1):
        print(f"{i}. {photo['title']} (score: {photo['similarity_score']:.3f})")


if __name__ == "__main__":
    test_agent()
