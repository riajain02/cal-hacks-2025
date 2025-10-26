import torch
from transformers import CLIPProcessor, CLIPModel
import chromadb

def search_images(query_text, top_k=3):
    print(f"Searching for: '{query_text}'")
    
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    client = chromadb.PersistentClient(path="./storage/chromadb")
    collection = client.get_collection(name="image_embeddings")
    
    inputs = processor(text=[query_text], return_tensors="pt", padding=True)
    
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
        query_embedding = text_features.cpu().numpy().flatten()
    
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )
    
    print(f"\nTop {top_k} matches:")
    for i, (metadata, distance) in enumerate(zip(results['metadatas'][0], results['distances'][0])):
        print(f"{i+1}. {metadata['filename']} (similarity: {1-distance:.3f})")
    
    return results

if __name__ == "__main__":
    search_images("playing basketball", top_k=3)
    print("\n" + "="*50 + "\n")
    search_images("travel", top_k=3)
