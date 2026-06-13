import zipfile
import os
import sys

def extract_scaffold(zip_path, extract_to):
    if not os.path.exists(zip_path):
        print(f"Zip file not found: {zip_path}")
        return

    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"Extracted {zip_path} to {extract_to}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_scaffold.py <zip_path> <extract_to>")
        sys.exit(1)
    
    extract_scaffold(sys.argv[1], sys.argv[2])
