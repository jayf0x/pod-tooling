"""

Post-processing scripts

"""
import ollama
from utils import log
from utils import PostQueryResults, List, AllClips

def post_clean_obvious_clips(results:PostQueryResults, min_length_sec=5, max_length_sec=60):
    """
    Filter clips based on obvious bad criteria.
    Input: list of slips
    Output: filtered list of slips
    """
    cleaned: PostQueryResults = []
    for clip in results:
        if len(clip):    
            duration = clip[-1]['end'] - clip[0]['start']
            if duration < min_length_sec or duration > max_length_sec:
                continue
            cleaned.append(clip)
    log(f"[+] POST. post_clean_obvious_clips: {len(cleaned)}/{len(results)} clips left")
    return cleaned


# TODO: update me once more to become relevant ot this code base pls :)
def post_query_filter_relevant_clip(results:PostQueryResults, model="llama3"):
    """
    Use a lightweight LLM to decide if a clip is relevant and worth keeping.
    Optionally trim start/end text inside the clip.
    Input: list of slips
    Output: filtered list of slips
    """
    filtered = []
    for clip in results:
        text = " ".join([w['word'] for w in clip])
        prompt = f"""
Decide if the following clip is interesting enough to keep.
Criteria:
- Emotionally engaging OR intellectually valuable


Reply strictly with either "YES" or "NO"
Clip: `{text}`
"""
        resp = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        decision = resp.message.content.strip().upper()
        if "YES" in  decision and not "NO" in decision:
            filtered.append(clip)
    log(f"[+] POST. post_query_filter_relevant_clip:  {len(filtered)}/{len(results)} clips left")
    return filtered
