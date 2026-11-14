#!/usr/bin/env bash
# Set up the video-gen engine: a Python 3.13 venv with pinned packages, an ffmpeg check, and one
# test frame at 2560x1440. Safe to run again (it reuses the venv and skips installed packages).
#
#   bash setup.sh                         venv at ~/.venvs/video-gen
#   VG_VENV=/some/dir bash setup.sh       venv somewhere else
#
# Afterwards run the engine with:  $VG_VENV/bin/python <repo>/engine/vg.py ...
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${VG_VENV:-$HOME/.venvs/video-gen}"

say() { printf '[setup] %s\n' "$*"; }
fail() { printf '[setup] ERROR: %s\n' "$*" >&2; exit 1; }

# 1. Python 3.13
PY=""
for c in python3.13 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 13) else 1)'; then
    PY="$(command -v "$c")"; break
  fi
done
[ -n "$PY" ] || fail "Python 3.13 not found (install python3.13 and python3.13-venv)"
say "python: $PY ($("$PY" --version 2>&1))"

# 2. venv (reused when it already has a working Python 3.13)
if [ -x "$VENV/bin/python" ] && "$VENV/bin/python" -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 13) else 1)'; then
  say "venv: $VENV (exists)"
else
  say "venv: creating $VENV"
  mkdir -p "$(dirname "$VENV")"
  "$PY" -m venv "$VENV" || fail "could not create the venv (on Debian/Ubuntu: apt install python3.13-venv)"
fi

# 3. packages (pip skips what is already installed at the pinned version)
"$VENV/bin/python" -m pip install --quiet --disable-pip-version-check -r "$REPO/requirements.txt" \
  || fail "pip install failed (is PyPI reachable?)"
say "packages: $("$VENV/bin/python" -c 'import importlib.metadata as m; print(", ".join(f"{p} {m.version(p)}" for p in ("manimgx", "numpy", "pillow")))')"
[ -x "$VENV/bin/manimgx" ] || fail "manimgx CLI missing from $VENV/bin"

# 4. ffmpeg / ffprobe (with libx264 and AAC)
command -v ffmpeg >/dev/null 2>&1 || fail "ffmpeg not found (apt install ffmpeg)"
command -v ffprobe >/dev/null 2>&1 || fail "ffprobe not found (apt install ffmpeg)"
ENCODERS="$(ffmpeg -hide_banner -encoders 2>/dev/null || true)"
grep -q libx264 <<<"$ENCODERS" || fail "ffmpeg lacks libx264"
grep -qE ' aac ' <<<"$ENCODERS" || fail "ffmpeg lacks the aac encoder"
FFV="$(ffmpeg -version 2>/dev/null || true)"
say "ffmpeg: ${FFV%%$'\n'*}"

# 5. fonts: Noto Sans ships with manimgx-fonts; the monospace font comes from the system
if command -v fc-list >/dev/null 2>&1 && ! grep -qi "DejaVu Sans Mono" <<<"$(fc-list 2>/dev/null || true)"; then
  say "warning: DejaVu Sans Mono not found (apt install fonts-dejavu-core); code text will fall back"
fi

# 6. one test frame at 2560x1440
OUT="$VENV/video-gen-test-frame.png"
"$VENV/bin/python" "$REPO/engine/testframe.py" "$OUT" >/dev/null || fail "test frame failed (see docs/FALLBACK.md)"
say "test frame: $OUT"
echo "$OUT"
say "ready. Engine: $VENV/bin/python $REPO/engine/vg.py   (docs/PIPELINE.md)"
