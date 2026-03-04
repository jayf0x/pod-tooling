import whisperx
import sys
import torch
import json

audio_file = sys.argv[1]

device = "cpu"  # Use "mps" for Metal acceleration on M-series Macs
batch_size = 16
compute_type = "int8"


model = whisperx.load_model("large-v2", device, compute_type=compute_type)
transcription = model.transcribe(audio_file, batch_size=batch_size)

model_a, metadata = whisperx.load_align_model(language_code=transcription["language"], device=device)
aligned = whisperx.align(transcription["segments"], model_a, metadata, audio_file, device)

diarize_model = whisperx.DiarizationPipeline(use_auth_token=True, device=device)
diarize_segments = diarize_model(audio_file)


final_result = whisperx.assign_word_speakers(diarize_segments, aligned)


output_segments = []
for seg in final_result["segments"]:
    output_segments.append({
        "start": seg["start"],
        "end": seg["end"],
        "speaker": seg.get("speaker", "Speaker_1")
    })


with open("diarization_segments.json", "w") as f:
    json.dump({"segments": output_segments}, f, indent=2)
