import re
from typing import List

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def chunk_text(text: str, size: int = 800, overlap: int = 100) -> List[str]:
    if not text:
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = min(start + size, text_len)
        chunk = text[start:end]
        
        # If we are not at the end, try to break at a space to avoid splitting words
        if end < text_len:
            last_space = chunk.rfind(' ')
            if last_space > size * 0.5: # Only truncate if space is somewhat near the end
                end = start + last_space
                chunk = text[start:end]
        
        chunks.append(chunk)
        start += size - overlap
        
        # Prevent infinite loops if progress isn't made (e.g. huge word)
        if start >= end:
            start = end
            
    return chunks
