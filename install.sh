#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
default_bin="${HOME}/curie"
default_openclaw_home="${HOME}/.openclaw"

bin_target="${CURIE_BIN_TARGET:-$default_bin}"
openclaw_home="${OPENCLAW_HOME:-$default_openclaw_home}"
extensions_target="${openclaw_home}/extensions"
skills_target="${openclaw_home}/skills"
mode="symlink"
dry_run=0

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

Options:
  --bin-target PATH       Install the curie CLI at PATH.
  --openclaw-home PATH    Target OpenClaw home directory. Default: ~/.openclaw
  --copy                  Copy files instead of symlinking them.
  --dry-run               Print actions without changing anything.
  -h, --help              Show this help.

Environment:
  CURIE_BIN_TARGET        Override the curie CLI target path.
  OPENCLAW_HOME           Override the OpenClaw home directory.
EOF
}

log() {
  printf '%s\n' "$*"
}

run() {
  if [[ "$dry_run" -eq 1 ]]; then
    printf '[dry-run] '
    printf '%q ' "$@"
    printf '\n'
    return 0
  fi
  "$@"
}

link_or_copy_file() {
  local src="$1"
  local dest="$2"
  run mkdir -p "$(dirname "$dest")"
  if [[ "$mode" == "copy" ]]; then
    run install -m 755 "$src" "$dest"
  else
    run ln -sfn "$src" "$dest"
  fi
}

link_or_copy_dir() {
  local src="$1"
  local dest="$2"
  run mkdir -p "$(dirname "$dest")"
  if [[ "$mode" == "copy" ]]; then
    run rm -rf "$dest"
    run cp -a "$src" "$dest"
  else
    run ln -sfn "$src" "$dest"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bin-target)
      bin_target="$2"
      shift 2
      ;;
    --openclaw-home)
      openclaw_home="$2"
      extensions_target="${openclaw_home}/extensions"
      skills_target="${openclaw_home}/skills"
      shift 2
      ;;
    --copy)
      mode="copy"
      shift
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      log "Unknown option: $1"
      usage
      exit 2
      ;;
  esac
done

log "Repo root: ${repo_root}"
log "Install mode: ${mode}"
log "CLI target: ${bin_target}"
log "OpenClaw home: ${openclaw_home}"

link_or_copy_file "${repo_root}/scripts/curie" "${bin_target}"
link_or_copy_dir "${repo_root}/extensions/curie-command-router" "${extensions_target}/curie-command-router"

for skill_dir in \
  adeept-battery \
  adeept-distance \
  adeept-line \
  adeept-look \
  curie \
  curie-super \
  pi-camera-whatsapp
do
  link_or_copy_dir "${repo_root}/skills/${skill_dir}" "${skills_target}/${skill_dir}"
done

log "Curie install complete."
if [[ "$mode" == "symlink" ]]; then
  log "Symlinked repo paths into ${openclaw_home} and ${bin_target}."
else
  log "Copied repo paths into ${openclaw_home} and ${bin_target}."
fi
