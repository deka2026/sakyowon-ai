#!/usr/bin/env bash
# Waits for each student's v2 selection to be complete, then renders it.
# Runs detached (no Claude involvement) so it survives API usage limits.
cd "$(dirname "$0")" || exit 1
export PATH="$PATH:/c/Users/User/AppData/Roaming/npm:/c/Users/User/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.1-full_build/bin"
mkdir -p logs
LOG=logs/watcher.log
SLUGS=(kim-boyoung choi-hojun hwang-seojin kim-hyunsik kim-siyul park-sunwoo choi-inyoung seo-jian kim-soeun kim-yooju)
STABLE_SEC=180        # JSON must be untouched this long (agent finished writing)
MAX_SEC=$((14*3600))  # give up after 14h
START=$(date +%s)
declare -A DONE

log(){ echo "$(date '+%m-%d %H:%M:%S') $*" >> "$LOG"; }
log "watcher start; waiting for: ${SLUGS[*]}"

ready() {  # slug -> 0 if the v2 selection is complete and stable
  local s="$1" j="students/$1.json" p="/d/VideoWorks/catalog/pick_$1.md" c="compositions/$1.html"
  [ -f "$j" ] && [ -f "$p" ] && [ -f "$c" ] || return 1
  grep -q 'v2' "$p" || return 1
  local now jm cm; now=$(date +%s); jm=$(stat -c %Y "$j"); cm=$(stat -c %Y "$c")
  [ $((now - jm)) -ge $STABLE_SEC ] || return 1       # still being written
  [ "$cm" -ge "$jm" ] || return 1                     # agent has not rebuilt after last JSON edit
  # every referenced media file must exist
  python - "$j" <<'PY' >/dev/null 2>&1 || return 1
import json,sys,os,io
d=json.load(io.open(sys.argv[1],encoding='utf-8'))
srcs=[d['hero']['src'],d['cert']['src']]+[x['src'] for x in d['shots']]
assert all(os.path.exists(s) for s in srcs), 'missing'
assert len(set(srcs))==len(srcs), 'dupe'
assert 8<=len(d['shots'])<=12 and len(d['messages'])==5
PY
  return 0
}

while :; do
  for s in "${SLUGS[@]}"; do
    [ -n "${DONE[$s]:-}" ] && continue
    if ready "$s"; then
      log "READY $s -> rendering"
      if bash render-all.sh "$s" >> "logs/watcher-render-$s.log" 2>&1 && [ -f "renders/$s.mp4" ]; then
        DONE[$s]=1; log "OK    $s ($(du -h "renders/$s.mp4" | cut -f1))"
      else
        log "FAIL  $s (see logs/watcher-render-$s.log); will retry in next pass"
      fi
    fi
  done
  [ "${#DONE[@]}" -eq "${#SLUGS[@]}" ] && { log "ALL DONE (${#DONE[@]})"; break; }
  [ $(( $(date +%s) - START )) -gt $MAX_SEC ] && { log "TIMEOUT; done=${!DONE[*]}"; break; }
  sleep 60
done
