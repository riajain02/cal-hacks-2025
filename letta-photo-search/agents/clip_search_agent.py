"""
CLIP-Based Image Search Agent using ChromaDB
Uses CLIP embeddings and vector similarity search to find relevant images
"""
import os
import torch
from transformers import CLIPProcessor, CLIPModel
import chromadb
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

class CLIPSearchAgent:
    """
    Agent that uses CLIP embeddings with ChromaDB for image search
    """

    def __init__(self, chroma_db_path='./storage/chromadb'):
        """
        Initialize the CLIP search agent

        Args:
            chroma_db_path: Path to ChromaDB persistence directory
        """
        print("Initializing CLIP Search Agent...")

        # Load CLIP model
        print("Loading CLIP model...")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        # Connect to ChromaDB
        print(f"Connecting to ChromaDB at {chroma_db_path}...")
        self.client = chromadb.PersistentClient(path=chroma_db_path)
        
        try:
            self.collection = self.client.get_collection(name="image_embeddings")
            count = self.collection.count()
            print(f"✓ CLIP Search Agent initialized with {count} photos")
        except Exception as e:
            print(f"Error: Could not load image_embeddings collection: {e}")
            print("Make sure to run populate_database.py first!")
            raise

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for photos using CLIP-based similarity

        Args:
            query: Natural language search query
            top_k: Number of top results to return

        Returns:
            List of matching photos with similarity scores
        """
        # Encode the text query using CLIP
        inputs = self.processor(text=[query], return_tensors="pt", padding=True)
        
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            query_embedding = text_features.cpu().numpy().flatten()

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )

        # Build response
        search_results = []
        for i, (metadata, distance) in enumerate(zip(results['metadatas'][0], results['distances'][0])):
            similarity_score = 1 - distance  # Convert distance to similarity
            
            result = {
                'id': i,
                'filename': metadata['filename'],
                'path': metadata['path'],
                'image_url': f"/images/{quote(metadata['filename'])}",
                'similarity_score': float(similarity_score),
                'relevance_score': int(similarity_score * 100),
                'title': metadata['filename'].replace('.jpeg', '').replace('.jpg', '').replace('.png', '').replace('-', ' ').title(),
                'description': f"Image: {metadata['filename']}",
                'tags': []
            }
            search_results.append(result)

        print(f"✓ Found {len(search_results)} results for query: '{query}'")
        for i, result in enumerate(search_results, 1):
            print(f"  {i}. {result['filename']} (similarity: {result['similarity_score']:.3f})")

        return search_results

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

    def get_photo_by_filename(self, filename: str) -> Optional[Dict]:
        """Get a specific photo by filename"""
        results = self.collection.get(
            where={"filename": filename}
        )
        
        if results['ids']:
            return {
                'filename': results['metadatas'][0]['filename'],
                'path': results['metadatas'][0]['path']
            }
        return None


# Test function
def test_agent():
    """Test the CLIP search agent"""
    print("\n" + "="*60)
    print("TESTING CLIP SEARCH AGENT")
    print("="*60 + "\n")

    agent = CLIPSearchAgent()

    test_queries = [
        "playing basketball",
        "people walking",
        "outdoor sports",
        "travel destination",
        "city street",
        "athletic activity",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        print(f"{'='*60}")

        results = agent.search(query, top_k=3)

        if results:
            for i, photo in enumerate(results, 1):
                print(f"\n{i}. {photo['filename']}")
                print(f"   Similarity: {photo['similarity_score']:.3f}")
                print(f"   Path: {photo['path']}")
        else:
            print("   No results found.")

    # Test with context
    print(f"\n\n{'='*60}")
    print("TESTING CONTEXT-BASED SEARCH")
    print(f"{'='*60}\n")

    results = agent.search_with_context(
        query="playing basketball",
        entities=["basketball", "sports"],
        context={"mood": "active", "setting": "outdoor", "attributes": ["athletic", "competitive"]},
        top_k=3
    )

    print("\nResults with context:")
    for i, photo in enumerate(results, 1):
        print(f"{i}. {photo['filename']} (score: {photo['similarity_score']:.3f})")


if __name__ == "__main__":
    test_agent()
