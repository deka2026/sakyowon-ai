#!/usr/bin/env bash
# Enumerate sites linked from the sakyowon hub and probe each one.
# Usage: bash map-sites.sh [hub-url]
set -uo pipefail
HUB="${1:-https://sakyowon.co.kr/}"

echo "== links found on $HUB =="
curl -s --max-time 20 "$HUB" \
  | grep -oE 'href="https?://[^"]+"' \
  | sed 's/^href="//; s/"$//' \
  | grep -viE 'cdn\.|jsdelivr|googleapis|gstatic' \
  | sort -u > /tmp/_sites.txt
cat /tmp/_sites.txt

echo
echo "== probe =="
while read -r u; do
  [ -z "$u" ] && continue
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$u" || echo "ERR")
  srv=$(curl -s -I --max-time 15 "$u" 2>/dev/null | grep -i '^server:' | tr -d '\r' | cut -d' ' -f2-)
  printf '%-55s %s  %s\n' "$u" "$code" "${srv:-?}"
done < /tmp/_sites.txt

echo
echo "== next: read Caddyfile for subdomains/ports not linked from the hub =="
echo "   cat ~/haeory-sakyowon-site/server/Caddyfile"
