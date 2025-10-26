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
from openai import OpenAI
from PIL import Image

load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
            self.collection = self.client.get_or_create_collection(
                name="image_embeddings",
                metadata={"hnsw:space": "cosine"}
            )
            count = self.collection.count()
            print(f"✓ CLIP Search Agent initialized with {count} photos")
        except Exception as e:
            print(f"Error: Could not load image_embeddings collection: {e}")
            print("Make sure to run populate_database.py first!")
            raise

    def _generate_memory_title_and_description(self, image_path: str, query: str) -> tuple:
        """
        Generate evocative memory-focused title and description using GPT-4 Vision

        Args:
            image_path: Path to the image file
            query: User's search query for context

        Returns:
            Tuple of (title, description)
        """
        try:
            # Convert image to base64
            import base64
            from pathlib import Path

            image_file_path = Path(image_path)
            if not image_file_path.exists():
                return self._fallback_title_description(image_path)

            with open(image_file_path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
                ext = image_file_path.suffix.lower()
                mime_type = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }.get(ext, 'image/jpeg')
                image_url = f"data:{mime_type};base64,{image_data}"

            # Call GPT-4 Vision to generate memory-focused title and description
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"You are helping blind users discover their photo memories. Based on this image (related to user's search: '{query}'), create:\n1) A short, evocative memory title (4-6 words, past tense, nostalgic)\n2) A warm, descriptive sentence (15-25 words) that brings the memory to life\n\nExamples:\nTitle: 'That Golden Afternoon by the Lake'\nDescription: 'A serene moment captured as sunlight danced across the water, creating ripples of pure golden magic.'\n\nTitle: 'When We Laughed Until Sunset'\nDescription: 'Friends gathered around the picnic table, sharing stories and joy as the day gently faded into twilight.'\n\nFormat: TITLE: [your title]\nDESCRIPTION: [your description]"
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }],
                max_tokens=150
            )

            content = response.choices[0].message.content

            # Parse response
            lines = content.strip().split('\n')
            title = "A Cherished Memory"
            description = "A beautiful moment frozen in time."

            for line in lines:
                if line.startswith('TITLE:'):
                    title = line.replace('TITLE:', '').strip()
                elif line.startswith('DESCRIPTION:'):
                    description = line.replace('DESCRIPTION:', '').strip()

            return (title, description)

        except Exception as e:
            print(f"Error generating memory title: {e}")
            return self._fallback_title_description(image_path)

    def _fallback_title_description(self, image_path: str) -> tuple:
        """Fallback title and description if AI generation fails"""
        filename = Path(image_path).stem

        # Create more evocative fallback titles
        fallback_titles = [
            "A Moment Worth Remembering",
            "That Special Day",
            "A Memory from the Past",
            "When Time Stood Still",
            "A Glimpse of Yesterday"
        ]

        import random
        title = random.choice(fallback_titles)
        description = f"A cherished memory captured in this photograph."

        return (title, description)

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

            # Use simple fallback titles for speed (avoid OpenAI calls in search)
            title, description = self._fallback_title_description(metadata['path'])

            result = {
                'id': i,
                'filename': metadata['filename'],
                'path': metadata['path'],
                'image_url': f"/images/{quote(metadata['filename'])}",
                'similarity_score': float(similarity_score),
                'relevance_score': int(similarity_score * 100),
                'title': title,
                'description': description,
                'tags': []
            }
            search_results.append(result)

        print(f"✓ Found {len(search_results)} results for query: '{query}'")
        for i, result in enumerate(search_results, 1):
            print(f"  {i}. {result['title']} (similarity: {result['similarity_score']:.3f})")

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
