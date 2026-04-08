# Pure raw video compression, audio untouched. Usefull for screenreordings as well...
:pod-compress() {
  input_file="$1"
  shift

  if [ -z "$input_file" ]; then
    cat <<EOF
Usage: pod-compress /path/to/input.mov [options]

Options:
  -m MODE      Compression mode: normal (default), fast, superfast
               normal    - libx264, preset medium
               fast      - libx264, preset fast
               superfast - libx264, preset ultrafast

Examples:
  pod-compress input.mov
  pod-compress input.mov -m fast
  pod-compress input.mov -m superfast
EOF
    return 1
  fi

  if [ ! -f "$input_file" ]; then
    echo "Error: File '$input_file' does not exist."
    return 1
  fi

  mode="normal"
  audio_args=(-c:a copy)
  filename=$(basename "$input_file" | sed 's/\.[^.]*$//')
  dirname=$(dirname "$input_file")
  timestamp=$(date '+%d-%m-%Y_%H%M%S')


  while [[ $# -gt 0 ]]; do
    case "$1" in
      -m)
        mode="$2"
        shift 2
        ;;
      *)
        echo "Unknown option: $1"
        return 1
        ;;
    esac
  done

  case "$mode" in
    normal)
      video_args=(-c:v libx264 -preset medium)
      ;;
    fast)
      video_args=(-c:v libx264 -preset fast)
      ;;
    superfast)
      video_args=(-c:v libx264 -preset ultrafast)
      ;;
    *)
      echo "Error:Unknown mode: $mode"
      return 1
      ;;
  esac

  output_file="${dirname}/${filename}_${timestamp}_${mode}_compressed.mp4"

  echo "▶️ Compressing '$input_file'..."
  ffmpeg -hide_banner -loglevel info -y -i "$input_file" \
    "${video_args[@]}" \
    "${audio_args[@]}" \
    -movflags +faststart \
    "$output_file" 
    #2>&1 | tail -n 5 -f

  if [ $? -eq 0 ]; then
    echo "Compression finished! Output file: $output_file"
  else
    echo "Error:Compression failed!"
    return 1
  fi
}
