import logging
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

def sanitize_transcript(text: str) -> str:
    """ Detects and removes common prompt injection attempts from video transcripts. """
    suspicious_patterns = [
        r"(?i)(ignore|disregard|forget) (all )?(previous )?instructions",
        r"(?i)you are now a",
        r"(?i)system prompt",
    ]
    sanitized = text
    for pattern in suspicious_patterns:
        sanitized = re.sub(pattern, "[REDACTED INJECTION ATTEMPT]", sanitized)
    return sanitized

def structure_transcript(segments: list, chunk_size=1000, chunk_overlap=200) -> list:
    """
    Takes a list of faster-whisper segments.
    Creates semantic chunks and maps them to approximate start and end times.
    """
    logger.info("Structuring transcript into semantic chunks...")
    
    # Reconstruct the full text while keeping track of segment boundaries
    full_text = ""
    segment_mapping = []
    
    for seg in segments:
        start_idx = len(full_text)
        text = seg['text'].strip()
        if not text:
            continue
            
        full_text += text + " "
        end_idx = len(full_text) - 1
        
        segment_mapping.append({
            "start_time": seg['start'],
            "end_time": seg['end'],
            "start_idx": start_idx,
            "end_idx": end_idx
        })
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    raw_chunks = splitter.split_text(full_text)
    
    structured_chunks = []
    search_start = 0
    
    for chunk in raw_chunks:
        # Find where this chunk starts in the full text
        chunk_start_idx = full_text.find(chunk, search_start)
        if chunk_start_idx == -1:
            chunk_start_idx = search_start # Fallback
            
        chunk_end_idx = chunk_start_idx + len(chunk)
        search_start = chunk_start_idx + len(chunk) - chunk_overlap # Optimization
        
        # Estimate timestamps
        start_time = 0.0
        end_time = 0.0
        
        # Find the segment that contains the start of the chunk
        for sm in segment_mapping:
            if sm["end_idx"] > chunk_start_idx:
                start_time = sm["start_time"]
                break
                
        # Find the segment that contains the end of the chunk
        for sm in reversed(segment_mapping):
            if sm["start_idx"] <= chunk_end_idx:
                end_time = sm["end_time"]
                break
                
        structured_chunks.append({
            "text": chunk,
            "start": start_time,
            "end": end_time
        })
        
    logger.info(f"Created {len(structured_chunks)} structured chunks.")
    return structured_chunks
