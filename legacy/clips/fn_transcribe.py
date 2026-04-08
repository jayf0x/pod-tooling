import whisperx, os

from utils import load_cache, save_cache, timer, log
from utils import Transcript
from utils import DIR_PROJECT, DIR_CACHE, DIR_OUTPUT

def transcribe_with_whisperx(video_path:str, guest_name:str, use_cache=False) -> Transcript:
    path_transcript= f"{DIR_CACHE}/{guest_name}.json"

    if use_cache and os.path.exists(path_transcript):
        log(f"[+] Using cached 'transcript'")
        return load_cache(path_transcript)

    timer.start('T')
    log(f"[+] Starting transcribing video: '{video_path}'...")
    model = whisperx.load_model("small.en", device="cpu", compute_type="int8")
    audio = whisperx.load_audio(video_path)
    transcription = model.transcribe(audio, batch_size=16, language="en")

    log(f"[+] Performing transcription word-level alignment (transcribe took {timer.get('T')})...")
    model_a, metadata = whisperx.load_align_model(language_code='en', device="cpu")
    transcription = whisperx.align(transcription["segments"], model_a, metadata, audio, device="cpu")
    
    save_cache(path_transcript, transcription)
    total_duration = transcription['segments'][-1]['end'] - transcription["segments"][0]["start"]
    log(f"[+] Transcript finished in {timer.end('T')}. Total video duration: {total_duration}")
    return transcription