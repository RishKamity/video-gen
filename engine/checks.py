"""Measurements after a build. Nobody in the pipeline can hear or watch the result, so these print
what can be measured: frame counts per scene, streams and durations, loudness, silences, and sample
frames to look at.
"""
import json
import re
import subprocess

import mix
import project
import timeline


def probe_json(path, *args):
    out = subprocess.run(["ffprobe", "-v", "error", "-of", "json", *args, str(path)], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"ffprobe failed on {path}: {out.stderr.strip()}")
    return json.loads(out.stdout)


def grab(video, t, out):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                    "-q:v", "3", str(out)], check=True)
    return out


def silences(path, noise_db=-55, min_s=1.0):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "info", "-i", str(path), "-map", "0:a", "-af",
                        f"silencedetect=n={noise_db}dB:d={min_s}", "-f", "null", "-"], capture_output=True, text=True)
    return [ln.split("]")[-1].strip() for ln in r.stderr.splitlines() if "silence_end" in ln]


def chapter(ch):
    """Returns True when every scene has the expected frame count and the final file matches the timing."""
    root = project.root()
    t = timeline.load(ch)
    name = project.chapter_meta(ch)["OUT_NAME"]
    ok = True
    for sc in t["scenes"]:
        p = root / "scenes" / ch / f"{sc['name']}.mp4"
        if not p.exists():
            print(f"{sc['name']:16s} MISSING ({p})")
            ok = False
            continue
        j = probe_json(p, "-count_frames", "-show_entries",
                       "stream=nb_read_frames,width,height,r_frame_rate,pix_fmt,codec_name")
        s = j["streams"][0]
        want = round(sc["dur"] * timeline.FPS)
        flag = "" if int(s["nb_read_frames"]) == want else "  <-- MISMATCH"
        ok &= not flag
        print(f"{sc['name']:16s} {s['codec_name']} {s['width']}x{s['height']} {s['r_frame_rate']} {s['pix_fmt']} "
              f"frames {s['nb_read_frames']} (want {want}){flag}")
    final = root / "out" / f"{name}.mp4"
    if not final.exists():
        print(f"final file missing: {final} (run assemble)")
        return False
    j = probe_json(final, "-show_entries",
                   "stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channels,duration"
                   ":format=duration")
    for s in j["streams"]:
        print("final stream:", {k: v for k, v in s.items() if k != "disposition"})
    dur = float(j["format"]["duration"])
    vdur = next(float(s["duration"]) for s in j["streams"] if s["codec_type"] == "video")
    diff = vdur - t["total"]
    print(f"final duration {dur:.3f}s, video {vdur:.3f}s, timing total {t['total']:.3f}s (video diff {diff:+.3f}s)")
    if abs(diff) > 1.5 / timeline.FPS:
        print("  <-- video length differs from the timing by more than a frame")
        ok = False
    vol = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(final), "-map", "0:a", "-af",
                          "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    print("volume:", "; ".join(ln.split("]")[-1].strip() for ln in vol.splitlines()
                               if "mean_volume" in ln or "max_volume" in ln))
    print(f"final integrated loudness: {mix.lufs(final):.1f} LUFS")
    adir = root / "audio"
    if (adir / f"{ch}_stem_voice.wav").exists():
        v, b = mix.lufs(adir / f"{ch}_stem_voice.wav"), mix.lufs(adir / f"{ch}_stem_bed.wav")
        print(f"voice stem {v:.1f} LUFS, bed stem {b:.1f} LUFS, gap {v - b:.1f} dB")
    sil = silences(final)
    print(f"silences under -55 dB for 1 s or more: {len(sil)}", *sil[:6], sep="\n  ")
    for k, frac in enumerate((0.02, 0.27, 0.5, 0.72, 0.9)):
        out = grab(final, dur * frac, root / "frames" / f"{ch}_final_{k}.jpg")
        print(f"frame {dur * frac:7.2f}s -> {out}")
    print("ALL SCENES MATCH" if ok else "PROBLEMS FOUND (see above)")
    return ok
