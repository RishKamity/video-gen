"""Timing: measure each narration WAV and lay out scenes, segments and caption chunks.

Everything downstream (scene animation cues, burnt-in captions, the .srt, the audio mix) reads
script/<chapter>_timing.json, so swapping in new narration WAVs and re-running `vg.py <project> chN
timing` re-times the whole chapter.
"""
import json
import math
import re
import subprocess

import project

FPS = 30

# The voice WAVs (Gemini TTS via Speko) carry ~0.19 s of lead-in and ~0.30 s of tail silence of their
# own, so these add to that.
PAD_IN = 0.3      # silence at the start of a narrated scene
GAP = 0.2         # silence between segments (heard as ~0.7 s with the WAVs' own silence)
PAD_OUT = 0.4     # silence at the end of a narrated scene
CAP_MAX = 54      # max characters per caption line


def fr(x):
    """Snap a time to the frame grid."""
    return round(x * FPS) / FPS


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def _split_long(sentence, limit):
    """Split one long sentence into balanced pieces, preferring breaks after commas/colons."""
    words = sentence.split()
    n = math.ceil(len(sentence) / limit)
    while True:
        target = len(sentence) / n
        pieces, cur = [], ""
        for w in words:
            cand = (cur + " " + w).strip()
            remaining = n - len(pieces)
            if cur and remaining > 1 and (len(cand) > target + 6 or
                                          (len(cur) >= target * 0.7 and cur[-1] in ",:;")):
                pieces.append(cur)
                cur = w
            else:
                cur = cand
        pieces.append(cur)
        if all(len(p) <= limit for p in pieces) or n > 6:
            return pieces
        n += 1


def chunk_caption(text, limit=CAP_MAX):
    """Split caption text into display lines of <= limit chars: sentences first, then balanced splits."""
    # a sentence ends at . ? or ! followed by a space or the end (so "2.5" and "$4.78" stay whole)
    sentences = re.findall(r"\S.*?(?:[.?!]+[\"”]?(?=\s|$)|$)", text)
    sentences = [x.strip() for x in sentences if x.strip()]
    chunks = []
    for snt in sentences:
        parts = [snt] if len(snt) <= limit else _split_long(snt, limit)
        for p in parts:
            if chunks and len(chunks[-1]) + 1 + len(p) <= limit and len(p) < 18 and len(chunks[-1]) < 30:
                chunks[-1] = chunks[-1] + " " + p
            else:
                chunks.append(p)
    return chunks


def caption_times(chunks, dur, lead=0.08, tail=0.15):
    """Spread chunks across the voiced part of a segment by character count."""
    voiced = max(0.5, dur - lead - tail)
    total = sum(len(c) + 4 for c in chunks)
    t, out = lead, []
    for c in chunks:
        d = voiced * (len(c) + 4) / total
        out.append([round(t, 3), round(t + d, 3), c])
        t += d
    out[-1][1] = round(dur, 3)
    return out


def timing_path(chapter):
    return project.root() / "script" / f"{chapter}_timing.json"


def build_timing(chapter, segments, title=("sc00_title", 4.0)):
    """segments: list of dicts with id, scene, say, optional cap and pause. Writes the timing json
    (only when its content changed, so render-all's staleness check stays meaningful)."""
    scenes, order = {}, []
    for s in segments:
        if s["scene"] not in scenes:
            scenes[s["scene"]] = []
            order.append(s["scene"])
        scenes[s["scene"]].append(s)

    out = {"chapter": chapter, "fps": FPS, "scenes": []}
    t_abs = 0.0
    if title:
        out["scenes"].append({"name": title[0], "start": 0.0, "dur": fr(title[1]), "segments": []})
        t_abs = fr(title[1])
    for name in order:
        t = PAD_IN
        segs = []
        for s in scenes[name]:
            wav = project.wav_path(chapter, s["id"])
            dur = probe(wav)
            start = fr(t)
            cap = s.get("cap", s["say"])
            segs.append({"id": s["id"], "start": start, "dur": round(dur, 3), "abs": round(t_abs + start, 4),
                         "wav": str(wav), "say": s["say"], "cap": cap,
                         "chunks": caption_times(chunk_caption(cap), dur)})
            t = start + dur + GAP + s.get("pause", 0.0)
        dur = fr(t - GAP + PAD_OUT + 0.0001)
        dur = math.ceil(dur * FPS - 1e-6) / FPS
        out["scenes"].append({"name": name, "start": round(t_abs, 4), "dur": dur, "segments": segs})
        t_abs += dur
    out["total"] = round(t_abs, 4)
    path = timing_path(chapter)
    text = json.dumps(out, indent=1)
    if not path.exists() or path.read_text() != text:
        path.write_text(text)
    return out


def load(chapter):
    path = timing_path(chapter)
    if not path.exists():
        raise SystemExit(f"{path} is missing: run `vg.py <project> {chapter} timing` first")
    return json.loads(path.read_text())


def ts(x):
    ms = int(round(x * 1000))
    h, ms = divmod(ms, 3600000)
    mnt, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{mnt:02d}:{s:02d},{ms:03d}"


def srt_entries(timing, offset=0.0):
    """(start, end, text) for every caption chunk, shifted by offset seconds."""
    for sc in timing["scenes"]:
        for seg in sc["segments"]:
            for a, b, text in seg["chunks"]:
                yield (offset + sc["start"] + seg["start"] + a, offset + sc["start"] + seg["start"] + b, text)


def srt_text(entries):
    lines = []
    for n, (a, b, text) in enumerate(entries, 1):
        lines += [str(n), f"{ts(a)} --> {ts(b)}", text, ""]
    return "\n".join(lines)


def srt(chapter, timing=None):
    return srt_text(srt_entries(timing or load(chapter)))
