import sys
import json
from pydub import AudioSegment

input_audio = sys.argv[1]
segments_json = sys.argv[2]

speaker_tracks = {}
audio = AudioSegment.from_file(input_audio)

with open(segments_json) as f:
    data = json.load(f)

for segment in data["segments"]:
    start_ms = int(segment["start"] * 1000)
    end_ms = int(segment["end"] * 1000)
    speaker = segment["speaker"]

    if speaker not in speaker_tracks:
        speaker_tracks[speaker] = AudioSegment.silent(duration=0)
    speaker_tracks[speaker] += audio[start_ms:end_ms]

for speaker, track in speaker_tracks.items():
    output_name = f"{speaker.lower().replace(' ', '_')}.wav"
    track.export(output_name, format="wav")
    print(f"Exported: {output_name}")
