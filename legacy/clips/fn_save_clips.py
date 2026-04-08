import json, subprocess, re
from utils import PostQueryResults, log, timestamp_date
from utils import DIR_OUTPUT, FILE_METADATA

def cut_and_save_clips(results: PostQueryResults, src_video_path: str, clip_file_name:str = ""):    
    for i, clip in enumerate(results):
        try:
            start_time = clip[0]['start']
            end_time = clip[-1]['end']
            path_clip= f"{DIR_OUTPUT}/clip{str(i)}_{start_time:.0f}-_{end_time:.0f}_{clip_file_name}.mp4"
            cut_clip(src_video_path, path_clip, start_time, end_time)
        except Exception as e:
            log(f"[ERR] Failed to cut clip [{str(i)}/{str(len(results))}]: {json.dumps(e)}")            


    with open(FILE_METADATA, 'w') as f:
        # TODO:  PostQueryResults
        metadata_json = {
            'texts': [ " ".join([i['word'] for i in section]) for section in results],
            'clips': results,
        }
        json.dump(metadata_json, f, indent=2)
    print(f"[i] Saved clips to: {DIR_OUTPUT}")



def output_text(results: PostQueryResults, name:str):
    out_path= f"{DIR_OUTPUT}/output_{name}.txt"
    with open(out_path, "w", encoding='utf-8') as f:
        # for words in results:
        #     start = words[0]['start']
        #     end = words[-1]['end'] 
        #     text = " ".join([w['word'] for w in words])
        #     f.write(f"[{start:.2f} - {end:.2f}] {text}\n")
        json.dump(results, f,  ensure_ascii=False, indent=4)
                
def cut_clip(input_path: str, output_path: str, start: float, end: float):
    duration = end - start
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", input_path,
        "-t", str(duration),
        "-c", "copy",
        output_path
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        # print(f"[i] Clip '{Path(output_path).name}' saved.")
    except Exception as e:
        log(f"Error - Failed to cut video: {e.stderr}")