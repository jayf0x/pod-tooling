_POD_TOOLING_SCRIPT_DIR_LEGACY="$_POD_TOOLING_SCRIPT_DIR/legacy"

source $_POD_TOOLING_SCRIPT_DIR_LEGACY/fn-pod-cfr.sh
source $_POD_TOOLING_SCRIPT_DIR_LEGACY/fn-pod-compress.sh


# sometimes files can have vfr and vbr and the audio is out of sync with the video and you can fix it by simply moving either as the rates are not in sync
# this is supposed to fix that sync 
:pod-sync() {
  input="$1"
  if [ -z "$input" ] || [ ! -f "$input" ]; then
    echo "wanker.."
    return 1
  fi

  dir=$(dirname "$input")
  base=$(basename "$input")
  name="${base%.*}"
  ext="${base##*.}"
  date_tag=$(date '+%Y%m%d_%H%M%S')
  output="${dir}/${name}_${date_tag}.mp4"

  ffmpeg -hide_banner -loglevel info -y -fflags +genpts -i "$input" \
    -vf "fps=25" -vsync cfr \
    -c:v libx264 -preset fast -crf 23 \
    -c:a aac -b:a 192k -af "aresample=async=1" \
    -movflags +faststart \
    "$output"

  if [ $? -eq 0 ]; then
    return 0
  else
    echo "Uppss failed. Blame the furniture!"
    return 1
  fi
}