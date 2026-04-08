#!/bin/bash

# Constant Frame Rate function - so much more
:pod-cfr() {
  input_file="$1"
  shift

  if [ -z "$input_file" ]; then
    cat <<EOF
Usage: pod-cfr /path/to/input.mov [options]

Options:
  -m MODE      Set mode: fast (default), superfast, simple
               fast      - libx264, preset fast, CRF 25, good quality
               superfast - libx264, preset ultrafast, CRF 28, faster encoding
               simple    - stream copy video/audio (no filters, no re-encoding)

  -scale       Apply scaling + padding to 1280x720 while preserving aspect ratio

Examples:
  pod-cfr input.mov
  pod-cfr input.mov -m superfast
  pod-cfr input.mov -m fast -scale
  pod-cfr input.mov -m simple

EOF
    return 1
  fi

  if [ ! -f "$input_file" ]; then
    echo "Error: File '$input_file' does not exist."
    return 1
  fi


  mode="fast"
  frame_rate=25
  video_args=()
  audio_args=(-c:a copy)
  vf_chain=("format=gray")

  filename=$(basename "$input_file" | sed 's/\.[^.]*$//')
  dirname=$(dirname "$input_file")
  timestamp=$(date '+%d-%m-%Y_%H%M%S')


  while [[ $# -gt 0 ]]; do
    case "$1" in
      -m)
        mode="$2"
        shift 2
        ;;
      -scale)
        vf_chain+=("scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2")
        shift
        ;;
      *)
        echo "Unknown option: $1"
        return 1
        ;;
    esac
  done


  if [[ ${#vf_chain[@]} -gt 0 ]]; then
    vf_joined=$(IFS=, ; echo "${vf_chain[*]}")
    vf_args=(-vf "$vf_joined")
  else
    vf_args=()
  fi

  case "$mode" in
    fast)
      echo "using: libx264, preset fast, CRF 25"
      video_args=(-c:v libx264 -preset fast -crf 25)
      ;;
    superfast)
      echo "using: libx264, preset ultrafast, CRF 28"
      video_args=(-c:v libx264 -preset ultrafast -crf 28)
      ;;
    simple)
      echo "Using: stream copy, no filters, forces CFR 25"
      video_args=(-c:v copy)
      audio_args=(-c:a copy)
      vf_args=()
      ;;
    *)
      echo "Error:Unknown mode: $mode"
      return 1
      ;;
  esac

  output_file="${dirname}/${filename}_${timestamp}_${mode}.mp4"

  echo "▶️  Converting '$input_file' with CFR 25 FPS..."
  ffmpeg -hide_banner -loglevel info -y -i "$input_file" -r $frame_rate \
    "${video_args[@]}" \
    "${audio_args[@]}" \
    "${vf_args[@]}" \
    -movflags +faststart \
    "$output_file"

  if [ $? -eq 0 ]; then
    echo "Conversion finished! Output file: $output_file"
  else
    echo "Error:Conversion failed!"
    return 1
  fi
}
