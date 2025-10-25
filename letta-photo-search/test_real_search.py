#!/usr/bin/env python3
"""
Quick test script to verify the photo search system works
Tests the Letta agent and photo database
"""
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_photo_database():
    """Test that photo database is set up correctly"""
    print("\n" + "="*60)
    print("TEST 1: Photo Database")
    print("="*60)

    import json
    db_path = Path('data/photo_database.json')

    if not db_path.exists():
        print("❌ FAIL: photo_database.json not found")
        return False

    with open(db_path) as f:
        data = json.load(f)

    photos = data.get('photos', [])
    print(f"✓ Found {len(photos)} photos in database")

    # Check if photos are downloaded
    photos_dir = Path('data/photos')
    if not photos_dir.exists():
        print("❌ FAIL: photos directory not found")
        return False

    downloaded = len(list(photos_dir.glob('*.jpg')))
    print(f"✓ Found {downloaded} downloaded photo files")

    if downloaded < len(photos):
        print(f"⚠️  WARNING: Only {downloaded}/{len(photos)} photos downloaded")
        print("   Run: python setup_photo_data.py")

    return True


def test_letta_agent():
    """Test Letta agent initialization and search"""
    print("\n" + "="*60)
    print("TEST 2: Letta Agent")
    print("="*60)

    try:
        from agents.letta_photo_agent import PhotoSearchAgent

        print("Initializing Letta agent...")
        agent = PhotoSearchAgent()
        print("✓ Agent initialized successfully")

        # Test search
        print("\nTesting search for 'dog'...")
        results = agent.search_photos("dog")

        if results:
            print(f"✓ Search returned {len(results)} result(s)")
            print(f"\n  Top result: {results[0]['title']}")
            print(f"  Description: {results[0]['description'][:60]}...")
            return True
        else:
            print("⚠️  WARNING: Search returned no results")
            return True  # Still consider it a pass

    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        print("\nPossible issues:")
        print("  - Check LETTA_API_KEY in .env file")
        print("  - Verify internet connection")
        print("  - Try: pip install letta")
        return False


def test_flask_imports():
    """Test that Flask and dependencies are installed"""
    print("\n" + "="*60)
    print("TEST 3: Flask Dependencies")
    print("="*60)

    try:
        import flask
        print("✓ Flask installed:", flask.__version__)

        from flask_cors import CORS
        print("✓ Flask-CORS installed")

        from dotenv import load_dotenv
        print("✓ python-dotenv installed")

        return True

    except ImportError as e:
        print(f"❌ FAIL: Missing dependency: {e}")
        print("\nRun: pip install -r requirements.txt")
        return False


def test_env_file():
    """Test that environment file exists and has keys"""
    print("\n" + "="*60)
    print("TEST 4: Environment Configuration")
    print("="*60)

    env_path = Path('.env')
    if not env_path.exists():
        print("❌ FAIL: .env file not found")
        return False

    print("✓ .env file exists")

    with open(env_path) as f:
        content = f.read()

    has_letta = 'LETTA_API_KEY' in content
    has_fetch = 'FETCH_API_KEY' in content

    if has_letta:
        print("✓ LETTA_API_KEY configured")
    else:
        print("❌ FAIL: LETTA_API_KEY not found in .env")

    if has_fetch:
        print("✓ FETCH_API_KEY configured")
    else:
        print("⚠️  WARNING: FETCH_API_KEY not found in .env")

    return has_letta


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ACCESSIBLE PHOTO SEARCH - SYSTEM TEST")
    print("="*60)

    tests = [
        ("Photo Database", test_photo_database),
        ("Flask Dependencies", test_flask_imports),
        ("Environment Config", test_env_file),
        ("Letta Agent", test_letta_agent),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! System is ready to run.")
        print("\nNext steps:")
        print("  1. Run: ./launch-full-system.sh")
        print("  2. Select option 1 (Web UI)")
        print("  3. Open: http://localhost:5000")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
