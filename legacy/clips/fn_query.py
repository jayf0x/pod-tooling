import ollama

from utils import log, timer, load_cache, save_cache, slugify
from utils import Clip, AllClips
from utils import DIR_CACHE

from fn_parsers import fuzzy_parse_fullTexts




def query_clip_fulltext(chuck: Clip, model_name: str, options: dict, use_cache=False, retry_count = 0):
    raw_text = " ".join([seg['text'].lower() for seg in chuck])
    prompt = f"""
    Your task is to identify impactful excerpts from the following text. 

    - Extract short, self-contained excerpts of exactly 30 words that are emotionally engaging or convey a key insight. 
    - These excerpts should be clear, attention-grabbing, and meaningful on their own.
    - The excerpts should feel impactful, exciting, thought-provoking, or funny.

    Return ONLY the excerpts in valid JSON format, like this:
    ["excerpt 1", "excerpt 2", "excerpt 3"]

    If no suitable excerpts exist, return [].

    Text:
    ```{raw_text}```
    """ 
    
    
    prompt = f"""
    Your are given a chuck of the full context of a podcast.
    Extract the top moments/pieces-of-text from this part, but make sure that:
    - extract about 3 moment of loosely 30 words (doesn't need to be super strict) 
    - each should be self-contained and something that stand out, something thats awesome, deep or relatable.

    Return ONLY the excerpts in valid JSON format, like this:
    ["That was so awesome because.. ", ""]

    If no suitable excerpts exist, return [].

    Text:
    ```{raw_text}```
    """ 

    # 3 — Query LLM
    timer.start("LLM")
    content:str = ""
    path_cache_current_prompt = f"{DIR_CACHE}/cached_output_{slugify(model_name, '')}_{slugify(raw_text[:20], '')}.txt"
    if use_cache:
        content = load_cache(path_cache_current_prompt)
        if not content:
            log('[ERR]: query. Failed to load cached, resume with prompt.')
            
    if not content:
        chat_response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert at identifying impactful excerpts from text."},
                {"role": "user", "content": prompt}
            ],
            options=options
        )
        content = chat_response.message.content
        save_cache(path_cache_current_prompt, content)
        
    log(f"[+] query_fulltext. Took {timer.end('LLM')} ({len(prompt)} chars)")
    
    def retry():
        log(f"[+] Retry query: {retry_count}")
        query_clip_fulltext(chuck, model_name, options, False, retry_count - 1)
    
    return fuzzy_parse_fullTexts(content, chuck, retry if retry_count != 0 and use_cache is True else None)

    



def query_clip_trailer_fulltext(chuck: Clip, model_name: str, options: dict, use_cache=False, retry_count = 0):
    raw_text = " ".join([seg['text'].lower() for seg in chuck])    
    prompt = f"""
    Your are given a chuck of the full context of a podcast. The goal is to create a trailer with different clips. 
    Your tasks is to identify those clips out of a chuck of the full context.
    
    Extract the top moments/pieces-of-text from this part, but take these things into account
    - extract about 3 moment of loosely 30-60 words. 
    - each should be self-contained and something that stand out, be a punchline, an interesting question, a "waw" moment, something thats awesome, deep or feel relatable.
    - remember that this is mean.

    Return ONLY the excerpts in valid JSON format, like this:
    ["Some time ago..", ".. when she knew."]

    If no suitable excerpts exist, return an empty array [].

    Your personal text chuck:
    ```txt
    {raw_text}
    ```
    """ 

    # 3 — Query LLM
    timer.start("LLM")
    content:str = ""
    path_cache_current_prompt = f"{DIR_CACHE}/cached_output_{slugify(model_name, '')}_{slugify(raw_text[:20], '')}.txt"
    if use_cache:
        content = load_cache(path_cache_current_prompt)
        if not content:
            print('[i]: query. No cached, resume with prompt.')
            
    if not content:
        chat_response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert at identifying impactful excerpts from text."},
                {"role": "user", "content": prompt}
            ],
            options=options
        )
        content = chat_response.message.content
        save_cache(path_cache_current_prompt, content)
        
    log(f"[+] query_fulltext. Took {timer.end('LLM')} ({len(prompt)} chars)")
    
    def retry():
        log(f"[+] Retry query: {retry_count - 1}")
        query_clip_fulltext(chuck, model_name, options, False, retry_count - 1)
    
    return fuzzy_parse_fullTexts(content, chuck, retry if retry_count != 0 and use_cache is True else None)

    
    
    

