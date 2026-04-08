# LEARN
# - https://dev.to/saranshabd/python-w-strict-typechecker-3l7g
# - https://www.linkedin.com/pulse/demystifying-llm-quantization-suffixes-what-q4km-q80-q6k-paul-ilves-i0yvf



import os, sys
from pathlib import Path
from utils import log, timer, slugify, boot_ollama, save_cache
from utils import DIR_PROJECT, LLM_OPTIONS
from utils import List, PostQueryResults

from fn_chuck import chunk_by_time
from fn_query import query_clip_fulltext, query_clip_trailer_fulltext
from fn_save_clips import cut_and_save_clips, output_text
from fn_transcribe import transcribe_with_whisperx
from fn_post_processing import post_clean_obvious_clips, post_query_filter_relevant_clip


# -------- Configs -------- #

MODEL_NAME = "llama3" # no-long-context, mehmeh-quality
# MODEL_NAME = "qwen2.5:7b-instruct-q4_K_M" # meh-quality-clips
MODEL_NAME = "yi:9b-chat-v1.5-q6_K" # +long context, meh_ok-quality, 
# MODEL_NAME = "spooknik/hermes-2-pro-mistral-7b:q8" # ..
# MODEL_NAME = "qwen3:4b-thinking-2507-fp16" # insanely slo, but has thinking output which we don't want




# TRY: MythoMax-L2
# TRY?: OpenChat 3.6

# -uncensored

# ------- variable config ------- #
arg_video_path=f'{DIR_PROJECT}/pod car dude.mp4'
arg_video_path=f'{DIR_PROJECT}/pod mark Coleman.mp4'

use_cached_transcription=True # won't redo transcribe  sys.argv[1]
used_cached_llm_output=False # won't redo prompts (only useful if you are testing postprocessing)

guest_name=Path(arg_video_path).name.split('.mp4')[0] or "Unknown Guest"

def main():
    assert os.path.exists(arg_video_path), f"File not found: {arg_video_path}"
    boot_ollama()
    log('', 2)
    log(f"Start='{guest_name}', Model='{MODEL_NAME}', cache_transcript={str(use_cached_transcription)}, cache_llm_output={str(used_cached_llm_output)} ")
    timer.start('@')
    # Step 1 — transcribe video
    transcription = transcribe_with_whisperx(arg_video_path, guest_name, use_cached_transcription)
    # word_segments = transcription['word_segments']
    segments = transcription['segments']
    
    
    # Step 2 — Query the chunks
    all_results: PostQueryResults = []
    chunks = chunk_by_time(segments, minutes=5)
    for i, chunk in enumerate(chunks):
        log(f"[+] Processing chuck: {i+1}/{len(chunks)}")
        results = query_clip_trailer_fulltext(chunk, MODEL_NAME, LLM_OPTIONS['best_b'], used_cached_llm_output, 3)
        all_results.extend(results)

    save_cache('./all_results.json', all_results)
    # Step 3 — Post process output (middlewares)
    post_results = post_clean_obvious_clips(all_results)
    # post_results = post_rank_top(all_results, 10)
    post_results = post_query_filter_relevant_clip(post_results)

    # Step 4 — Output results
    output_text(post_results, slugify(MODEL_NAME, ''))
    cut_and_save_clips(post_results, arg_video_path, slugify(f"{MODEL_NAME}_{guest_name}", ''))
    print(f"[v] Finished cut! Duration: {timer.end('@')}")
  
    


if __name__ == "__main__":
    print('[i] Start main')
    main()
