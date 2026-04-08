#!/bin/bash

# Usage: 
# ./split_by_speaker.sh input_video.mp4

set -e

INPUT_VIDEO="$1"
BASENAME=$(basename "$INPUT_VIDEO" | cut -d. -f1)


ffmpeg -y -i "$INPUT_VIDEO" -ar 16000 -ac 1 -c:a pcm_s16le "${BASENAME}.wav"


python3 whisperx_pipeline.py "${BASENAME}.wav"
python3 split_audio_by_speaker.py "${BASENAME}.wav" diarization_segments.json




