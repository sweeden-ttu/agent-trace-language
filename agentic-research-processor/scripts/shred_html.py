import os
import re
import sys
from pathlib import Path

def shred_html(file_path, output_dir):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by h1 tags (typical chapter marker)
    # We want to keep the h1 tag in the chunk
    sections = re.split(r'(<h1.*?>)', content)
    
    # The first element might be the preamble (before first h1)
    preamble = sections[0]
    with open(os.path.join(output_dir, "00_preamble.html"), 'w', encoding='utf-8') as f:
        f.write(preamble)
    
    # Process pairs of (h1_tag, body)
    for i in range(1, len(sections), 2):
        h1_tag = sections[i]
        body = sections[i+1] if i+1 < len(sections) else ""
        
        # Try to find a title in the h1 tag or the body
        title_match = re.search(r'>(.*?)<', h1_tag)
        title = title_match.group(1) if title_match else f"section_{i//2 + 1}"
        # Sanitize title for filename
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        if not safe_title:
            safe_title = f"section_{i//2 + 1}"
            
        filename = f"{i//2 + 1:02d}_{safe_title}.html"
        file_out = os.path.join(output_dir, filename)
        
        with open(file_out, 'w', encoding='utf-8') as f:
            f.write(h1_tag + body)
        
        print(f"Created: {file_out}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python shred_html.py <file_path> <output_dir>")
        sys.exit(1)
    
    shred_html(sys.argv[1], sys.argv[2])
