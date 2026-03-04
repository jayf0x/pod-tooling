from pathlib import Path
import os, json, re
# ------------------------------- #
# ----------- consts ------------ #
# ------------------------------- #

DIR_PROJECT = f"{Path(__file__).resolve().parent.parent}/clips"
DIR_CACHE = f"{DIR_PROJECT}/cache"
DIR_OUTPUT = f"{DIR_PROJECT}/output"

FILE_METADATA=f"{DIR_OUTPUT}/metadata.json"

os.makedirs(DIR_CACHE, exist_ok=True)
os.makedirs(DIR_OUTPUT, exist_ok=True)


# ------------------------------- #
# ------------ Utils ------------ #
# ------------------------------- #
from time import time, gmtime, strftime
from datetime import datetime
import subprocess

def load_cache(file_path: str) -> str:
    if os.path.exists(file_path):
        print(f"[i] Loaded cache from '{file_path}'")
        with open(file_path, 'r') as f:
            return json.load(f)
    return ''

def save_cache(file_path: str, content: any, append=False) -> None:
    with open(file_path, 'a' if append else 'w') as f:
        json.dump(content, f)
    print(f"[i] Saved cache to '{file_path}'")


def log(content: any, newlines=1) -> None:
    print(content)
    with open(f"{DIR_PROJECT}/logs.txt", 'a') as f:
        f.write('\n' * newlines)
        f.write(f"{timestamp_time()}  {str(content)}")
        # json.dump(content, f, indent=2)

def timestamp_date() -> str:
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

def timestamp_time():
    return strftime("%H:%M:%S", gmtime())

def slugify(input:str, replacer="-") -> str:
    return re.sub('\W',replacer, input)

def boot_ollama():
    subprocess.run("ollama list", shell=True, capture_output=True)

class timer:
    _timers = {}

    @classmethod
    def start(cls, name: str):
        """Start a timer with the given name."""
        cls._timers[name] = time()

    @classmethod
    def end(cls, name: str) -> str:
        """End the timer with the given name and return the elapsed time as a string."""
        if name not in cls._timers:
            raise RuntimeError(f"Timer '{name}' has not been started.")
        
        start_time = cls._timers.pop(name)
        elapsed = time() - start_time
        return f"{elapsed:.2f}sec"

    @classmethod
    def get(cls, name: str) -> str:
        start_time = cls._timers[name]
        elapsed = time() - start_time
        if elapsed > 120:
            return f"{(elapsed/60):.2f}min"
        return f"{elapsed:.2f}sec"


    
# ------------------------------- #
# ----------- Typing ------------ #
# ------------------------------- #
from typing import TypedDict, List


class Word(TypedDict):
    word: str
    start: float
    end: float
    score: float

class Segment(TypedDict):
    start: float
    end: float
    text: str
    words: List[Word]

class Transcript(TypedDict):
    segments: List[Segment]
    word_segments: List[Word]

# a list of multiple parts of a single clip
Clip = List[Segment]
AllClips = List[Clip]
PostQueryResults = List[List[Word]]


LLM_OPTIONS={
    "best_b": {
        "format": "json", 
        # creativity
        "temperature": 0.5, 
        # Allows the model to sample from a wider probability mass — helps with varied but still relevant results.
        "top_p": 0.9, 
        # 	Reasonable — you could also try omitting it (defaults tend to work well), or go up to 40 to let it explore slightly more options.
        # "top_k": 20
        # "top_k": 40,
        # "repeat_penalty": 1.3,
        # "repeat_last_n": 64,
        # "num_predict": 256,
    }
}