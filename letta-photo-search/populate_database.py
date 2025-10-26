import os
import sys
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import chromadb
from chromadb.config import Settings
import numpy as np

def populate_image_database():
    images_dir = "images"
    chroma_db_path = "./storage/chromadb"
    
    os.makedirs(chroma_db_path, exist_ok=True)
    
    print("Loading CLIP model...")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=chroma_db_path)
    
    try:
        client.delete_collection(name="image_embeddings")
        print("Deleted existing collection")
    except:
        pass
    
    collection = client.create_collection(
        name="image_embeddings",
        metadata={"hnsw:space": "cosine"}
    )
    
    print(f"Processing images from {images_dir}...")
    image_files = [f for f in os.listdir(images_dir) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    embeddings = []
    ids = []
    metadatas = []
    
    for idx, image_file in enumerate(image_files):
        image_path = os.path.join(images_dir, image_file)
        print(f"Processing {image_file}...")
        
        try:
            image = Image.open(image_path).convert('RGB')
            
            inputs = processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = model.get_image_features(**inputs)
                embedding = image_features.cpu().numpy().flatten()
            
            embeddings.append(embedding.tolist())
            ids.append(f"img_{idx}")
            metadatas.append({
                "filename": image_file,
                "path": image_path
            })
            
        except Exception as e:
            print(f"Error processing {image_file}: {e}")
            continue
    
    print(f"Adding {len(embeddings)} embeddings to ChromaDB...")
    collection.add(
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )
    
    print(f"✓ Successfully populated database with {len(embeddings)} images")
    print(f"✓ Database location: {chroma_db_path}")
    
    return collection

def test_database():
    chroma_db_path = "./storage/chromadb"
    
    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=chroma_db_path)
    
    try:
        collection = client.get_collection(name="image_embeddings")
        
        results = collection.get(include=['embeddings', 'metadatas'])
        
        embedding_dim = len(results['embeddings'][0]) if len(results['embeddings']) > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"Database contains {len(results['ids'])} images")
        print(f"CLIP embedding dimension: {embedding_dim}")
        print(f"{'='*60}\n")
        
        for i, (img_id, metadata, embedding) in enumerate(zip(results['ids'], results['metadatas'], results['embeddings'])):
            print(f"{i+1}. ID: {img_id}")
            print(f"   Filename: {metadata['filename']}")
            print(f"   Path: {metadata['path']}")
            print(f"   Embedding dimension: {len(embedding)}")
            print(f"   First 10 values: {embedding[:10]}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        print("Database may not exist. Run without 'test' argument first.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["test", "--verify"]:
        test_database()
    else:
        populate_image_database()
