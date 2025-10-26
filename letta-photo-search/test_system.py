#!/usr/bin/env python3
"""
Quick system test to verify all components are working
"""
import os
import sys

def test_component(name, test_func):
    """Test a single component"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")

    try:
        test_func()
        print(f"✓ {name} - PASSED")
        return True
    except Exception as e:
        print(f"✗ {name} - FAILED")
        print(f"  Error: {e}")
        return False

def test_voice_agent():
    """Test Letta voice processing agent"""
    from agents.letta_voice_agent import VoiceProcessingAgent
    agent = VoiceProcessingAgent()
    result = agent.process_voice_input("Find me a happy dog")
    assert result['intent'] == 'search'
    assert 'dog' in result['entities']
    print(f"  Query: 'Find me a happy dog'")
    print(f"  Intent: {result['intent']}")
    print(f"  Entities: {result['entities']}")
    print(f"  Search: {result['search_query']}")

def test_embedding_search():
    """Test embedding-based search agent"""
    from agents.clip_search_agent import CLIPSearchAgent
    agent = CLIPSearchAgent()
    results = agent.search("dog", top_k=3)
    assert len(results) > 0
    print(f"  Query: 'dog'")
    print(f"  Results: {len(results)}")
    for i, r in enumerate(results, 1):
        print(f"    {i}. {r['title']} (score: {r['similarity_score']:.3f})")

def test_env_variables():
    """Test environment variables"""
    from dotenv import load_dotenv
    load_dotenv()

    required_keys = [
        'LETTA_API_KEY',
        'FETCH_API_KEY',
        'FISH_AUDIO_API_KEY',
        'OPENAI_API_KEY'
    ]

    for key in required_keys:
        value = os.getenv(key)
        if value:
            print(f"  ✓ {key}: {'*' * 10}{value[-10:]}")
        else:
            print(f"  ✗ {key}: NOT SET")
            raise ValueError(f"{key} not set in .env")

def test_database():
    """Test photo database"""
    import json
    with open('data/photo_database.json', 'r') as f:
        data = json.load(f)
    photos = data['photos']
    print(f"  Photos in database: {len(photos)}")
    for i, photo in enumerate(photos[:3], 1):
        print(f"    {i}. {photo['title']}")

def test_embeddings():
    """Test photo embeddings"""
    import numpy as np
    if os.path.exists('data/photo_embeddings.npy'):
        embeddings = np.load('data/photo_embeddings.npy')
        print(f"  Embeddings shape: {embeddings.shape}")
        print(f"  Embeddings found: {len(embeddings)}")
    else:
        print("  Embeddings not yet generated (will be created on first run)")

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SYSTEM COMPONENT TESTS")
    print("="*70)

    tests = [
        ("Environment Variables", test_env_variables),
        ("Photo Database", test_database),
        ("Photo Embeddings", test_embeddings),
        ("Voice Processing Agent", test_voice_agent),
        ("Embedding Search Agent", test_embedding_search),
    ]

    results = []
    for name, test_func in tests:
        results.append(test_component(name, test_func))

    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    print(f"  Total tests: {len(results)}")
    print(f"  Passed: {sum(results)}")
    print(f"  Failed: {len(results) - sum(results)}")

    if all(results):
        print(f"\n  ✓ ALL TESTS PASSED - System ready to run!")
    else:
        print(f"\n  ✗ SOME TESTS FAILED - Please fix errors above")
        sys.exit(1)

    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
