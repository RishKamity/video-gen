"""Estimate each chapter's length from its script, before any narration exists.

Model, calibrated on a finished 29-minute, 8-chapter build (204 Puck segments, 4,278 words, 1,609 s
of measured narration): one segment's WAV lasts about 0.765 s + 0.0593 s per character of `say`
(that includes the voice's own lead-in and tail silence). Chapter length = title card + for each scene
(PAD_IN + PAD_OUT) + for each segment (WAV + GAP + pause) - one GAP per scene, exactly as the timing
step lays it out. On the calibration build every chapter's estimate was within 2% of the real length.
Puck speaks about 160 words a minute; with title cards, recall pauses and gaps a chapter runs at
about 146 words a minute overall.
"""
import json

import project
import timeline

SEG_BASE = 0.765      # seconds per segment
SEG_PER_CHAR = 0.0593  # seconds per character of `say`


def seg_seconds(say):
    return SEG_BASE + SEG_PER_CHAR * len(say)


def chapter(ch):
    segs = project.segments(ch)
    title = project.chapter_meta(ch)["TITLE"] if project.chapter_file(ch).exists() else ("sc00_title", 4.0)
    scenes = {}
    for s in segs:
        scenes.setdefault(s["scene"], []).append(s)
    total = title[1] if title else 0.0
    voice = 0.0
    for ss in scenes.values():
        t = timeline.PAD_IN
        for s in ss:
            d = seg_seconds(s["say"])
            voice += d
            t += d + timeline.GAP + s.get("pause", 0.0)
        total += t - timeline.GAP + timeline.PAD_OUT
    nwords = sum(len(s["say"].split()) for s in segs)
    measured = None
    tp = timeline.timing_path(ch)
    if tp.exists():
        measured = json.loads(tp.read_text())["total"]
    return {"ch": ch, "segments": len(segs), "scenes": len(scenes), "words": nwords, "voice": voice,
            "total": total, "measured": measured}


def run():
    root = project.root()
    chs = project.chapters()
    extra = sorted(p.name[:-len("_segments.py")] for p in (root / "script").glob("*_segments.py")
                   if p.name[:-len("_segments.py")] not in chs)
    print(f"{'chapter':8s} {'segs':>5s} {'scenes':>6s} {'words':>6s} {'voice':>8s} {'est. length':>12s} {'measured':>9s}")
    tw = tt = 0.0
    for ch in chs:
        if not (root / "script" / f"{ch}_segments.py").exists():
            print(f"{ch:8s}  (no script/{ch}_segments.py yet)")
            continue
        r = chapter(ch)
        tw += r["words"]
        tt += r["total"]
        meas = f"{r['measured'] / 60:6.2f} min" if r["measured"] else ""
        print(f"{ch:8s} {r['segments']:5d} {r['scenes']:6d} {r['words']:6d} {r['voice']:7.0f}s "
              f"{r['total'] / 60:8.2f} min {meas:>9s}")
    print(f"{'total':8s} {'':5s} {'':6s} {int(tw):6d} {'':8s} {tt / 60:8.2f} min")
    print("(Puck at ~160 words/min of speech; about 146 words/min with title cards, pauses and gaps)")
    if extra:
        print(f"note: segment files not in project.json: {', '.join(extra)}")
