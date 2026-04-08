from utils import Clip, AllClips

def chunk_by_time(segments:Clip, minutes:int=10, overlap_seconds:int=60) -> AllClips:
    """
    function is used to chuck the transcribed words into sections (10min by default) with some overlap.
    This is used to feed as chucked contexts to the LLM.
    """
    chunk_duration = minutes * 60    
    chunks = []
    current_chunk = []
    current_start = 0
    for seg in segments:
        if seg['end'] <= current_start + chunk_duration:
            current_chunk.append(seg)
        else:
            chunks.append(current_chunk)
            current_start = current_chunk[-1]['end'] - overlap_seconds
            current_chunk = [seg]
    if current_chunk:
        chunks.append(current_chunk)
    return chunks