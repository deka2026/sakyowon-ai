#!/usr/bin/env bash
# Build + render every student short. Usage: bash render-all.sh [slug ...]
set -u
export PATH="$PATH:/c/Users/User/AppData/Roaming/npm:/c/Users/User/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.1-full_build/bin"
cd "$(dirname "$0")" || exit 1

OUT=/d/VideoWorks/output
mkdir -p "$OUT" renders logs

if [ "$#" -gt 0 ]; then
  SLUGS=("$@")
else
  mapfile -t SLUGS < <(ls students/*.json | xargs -n1 basename | sed 's/\.json$//' | grep -v '^_')
fi

# --- normalize source stills once (huge 4000px phone photos slow the capture) ---
normalize() {
  local d="$1"
  for f in "$d"/*.jpg; do
    [ -f "$f" ] || continue
    local w h
    w=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$f" 2>/dev/null)
    h=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$f" 2>/dev/null)
    [ -z "${w:-}" ] && continue
    local long=$(( w > h ? w : h ))
    if [ "$long" -gt 3200 ]; then
      ffmpeg -v error -i "$f" -vf "scale='if(gt(iw,ih),3200,-2)':'if(gt(iw,ih),-2,3200)':flags=lanczos" -q:v 3 -y "$f.tmp.jpg" 2>/dev/null \
        && mv -f "$f.tmp.jpg" "$f" && echo "    normalized $(basename "$f") (${w}x${h} -> long 3200)"
    fi
  done
}

ok=(); fail=()
for slug in "${SLUGS[@]}"; do
  echo "=============================================================="
  echo "  $slug"
  echo "=============================================================="
  [ -d "assets/media/$slug" ] && normalize "assets/media/$slug"

  if ! node build.mjs "$slug" > "logs/$slug.build.log" 2>&1; then
    echo "  BUILD FAILED — see logs/$slug.build.log"; fail+=("$slug"); continue
  fi
  cat "logs/$slug.build.log"

  if npx hyperframes render --composition "compositions/$slug.html" --output "renders/$slug.mp4" --quality high --crf 22 --quiet > "logs/$slug.render.log" 2>&1; then
    if [ -f "renders/$slug.mp4" ]; then
      cp -f "renders/$slug.mp4" "$OUT/$slug.mp4"
      dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "renders/$slug.mp4" 2>/dev/null)
      size=$(du -h "renders/$slug.mp4" | cut -f1)
      echo "  OK  ${size}  ${dur}s  -> $OUT/$slug.mp4"
      ok+=("$slug")
    else
      echo "  RENDER reported success but no file — see logs/$slug.render.log"; fail+=("$slug")
    fi
  else
    echo "  RENDER FAILED — see logs/$slug.render.log"; tail -12 "logs/$slug.render.log"; fail+=("$slug")
  fi
done

echo
echo "=============================================================="
echo "  done: ${#ok[@]} ok / ${#fail[@]} failed"
[ "${#ok[@]}" -gt 0 ] && printf '  ok:     %s\n' "${ok[*]}"
[ "${#fail[@]}" -gt 0 ] && printf '  failed: %s\n' "${fail[*]}"
echo "=============================================================="
