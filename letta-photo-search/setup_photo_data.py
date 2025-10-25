"""
Setup script to download photos for the database
"""
import json
import os
import requests
from pathlib import Path

def download_photos():
    """Download all photos from the database JSON file"""
    # Load photo database
    with open('data/photo_database.json', 'r') as f:
        data = json.load(f)

    # Create photos directory if it doesn't exist
    photos_dir = Path('data/photos')
    photos_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading photos...")
    for photo in data['photos']:
        filename = photo['filename']
        url = photo['url']
        filepath = photos_dir / filename

        # Skip if already downloaded
        if filepath.exists():
            print(f"✓ {filename} already exists")
            continue

        try:
            print(f"Downloading {filename}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"✓ Downloaded {filename}")
        except Exception as e:
            print(f"✗ Failed to download {filename}: {e}")

    print("\nPhoto setup complete!")

if __name__ == "__main__":
    download_photos()
