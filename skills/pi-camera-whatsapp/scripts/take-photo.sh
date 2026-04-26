#!/usr/bin/env bash
set -euo pipefail

out_dir="${1:-./out}"
stem="${2:-camera}"
view="${3:-}"

mkdir -p "$out_dir"

if [[ -n "$view" ]]; then
  case "$view" in
    up|straight|down)
      /usr/bin/python3 /home/curie/openclaw/skills/adeept-look/scripts/look.py "$view" >/dev/null
      sleep 0.5
      ;;
    *)
      echo "Unsupported view '$view'. Use up, straight, or down." >&2
      exit 1
      ;;
  esac
fi

timestamp="$(date +%Y%m%d-%H%M%S)"
outfile="${out_dir%/}/${stem}-${timestamp}.jpg"

capture_bin=""
if command -v rpicam-still >/dev/null 2>&1; then
  capture_bin="rpicam-still"
elif command -v libcamera-still >/dev/null 2>&1; then
  capture_bin="libcamera-still"
else
  echo "No supported camera capture command found (need rpicam-still or libcamera-still)." >&2
  exit 1
fi

"$capture_bin" -n -o "$outfile" --timeout 1500 >/dev/null

if [[ ! -s "$outfile" ]]; then
  echo "Camera capture failed: output file was not created." >&2
  exit 1
fi

printf '%s\n' "$outfile"
