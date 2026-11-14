"""Join the finished chapters (project.json order) into one video, one caption file and one script,
and make small copies for a study app.

  join()        out/full.mp4 (concat demuxer, -c copy, after checking every chapter's streams match),
                out/full.srt (every chapter's captions shifted by the chapters before it),
                script/full_script.md (narration per chapter, recall questions, combined sources),
                then measures the result (duration vs sum, silences, loudness per chapter, a frame each).
  app_copies()  out/app/<name>.mp4: 720p H.264/AAC, each under 20 MB.
"""
import json
import os
import re
import subprocess

import checks
import project
import timeline

APP_LIMIT = 20_000_000      # bytes ("under 20 MB")
APP_TARGET = 18_500_000     # aim here, so one encode is almost always enough


def chapter_files():
    root = project.root()
    chs = project.chapters()
    if not chs:
        raise SystemExit("project.json lists no chapters")
    files = [(ch, root / "out" / f"{project.chapter_meta(ch)['OUT_NAME']}.mp4") for ch in chs]
    missing = [str(f) for _, f in files if not f.exists()]
    if missing:
        raise SystemExit("missing chapter files (run assemble first):\n  " + "\n  ".join(missing))
    return files


def ffprobe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def sig(path):
    """(stream settings that must match for -c copy concat, duration)."""
    d = ffprobe(path)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    vs = (v["codec_name"], v.get("profile"), v["width"], v["height"], v["r_frame_rate"], v["pix_fmt"], v.get("time_base"))
    as_ = (a["codec_name"], a["sample_rate"], a["channels"], a.get("time_base")) if a else None
    return (vs, as_), float(d["format"]["duration"])


def md_section(text, title_start):
    """Body of the first '## <title_start>...' section of a chapter script, up to the next '## '."""
    m_ = re.search(rf"^## {re.escape(title_start)}.*?$(.*?)(?=^## |\Z)", text, re.S | re.M | re.I)
    return m_.group(1).strip() if m_ else ""


def table_rows(section):
    """Rows of the first markdown table in a section, as dicts keyed by lower-case header."""
    lines = [ln.strip() for ln in section.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return []
    split = lambda ln: [c.strip() for c in re.split(r"(?<!\\)\|", ln.strip().strip("|"))]   # noqa: E731
    hdr = [h.lower() for h in split(lines[0])]
    return [dict(zip(hdr, split(ln))) for ln in lines[1:] if not re.match(r"^\|[\s:|-]+\|?$", ln)]


def pick(row, *names):
    for n in names:
        for k, v in row.items():
            if n in k:
                return v
    return ""


def join():
    root = project.root()
    files = chapter_files()
    sigs = []
    for ch, f in files:
        s, dur = sig(f)
        sigs.append(s)
        print(f"{ch:6s} {f.name:32s} {dur:9.3f}s  {s}")
    if not all(s == sigs[0] for s in sigs):
        raise SystemExit("refusing to join: stream settings differ between chapters (re-assemble them)")
    print("all chapter streams match")

    # video
    lst = root / "out" / "full_concat.txt"
    lst.write_text("".join(f"file '{f}'\n" for _, f in files))
    tmp = root / "out" / "full.tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", "-f", "mp4", str(tmp)], check=True)
    os.replace(tmp, root / "out" / "full.mp4")
    lst.unlink()

    # captions
    offs, t = [], 0.0
    for _, f in files:
        offs.append(t)
        t += sig(f)[1]
    entries = []
    for (ch, _), off in zip(files, offs):
        entries += list(timeline.srt_entries(timeline.load(ch), off))
    (root / "out" / "full.srt").write_text(timeline.srt_text(entries))
    print(f"wrote out/full.mp4 and out/full.srt ({len(entries)} captions); chapter offsets "
          f"{[round(o, 3) for o in offs]}, sum {t:.3f}s")

    write_script(files, offs)
    check_full(files, offs, t)


def write_script(files, offs):
    root = project.root()
    cfg = project.config()
    out = [f"# {cfg.get('title', 'Video')}: full narration script", "",
           "Every chapter in order: narration as captioned, the recall questions, and every source used, combined.", ""]
    srcs, nseg = {}, 0
    for (ch, f), off in zip(files, offs):
        segs = project.segments(ch)
        nseg += len(segs)
        mds = sorted((root / "script").glob(f"{ch}_*.md"))
        md = mds[0].read_text() if mds else ""
        title = md.splitlines()[0].lstrip("# ").strip() if md else project.chapter_meta(ch)["OUT_NAME"]
        title = re.sub(r"\s+[—-]+\s+narration script$", "", title)
        mm, ss = divmod(off, 60)
        out += [f"## {title}", "", f"Starts at {int(mm)}:{ss:04.1f} in `out/full.mp4` (chapter file `out/{f.name}`).", ""]
        scene = None
        for s in segs:
            if s["scene"] != scene:
                if scene is not None:
                    out += [""]
                scene = s["scene"]
                out += [f"**{scene}**", ""]
            out += [f"{s['id']}. {s.get('cap') or s['say']}"]
        out += [""]
        rq = md_section(md, "Recall questions")
        if rq:
            out += ["### Recall questions", "", rq, ""]
        for row in table_rows(md_section(md, "Sources")):
            name, url, date = pick(row, "source"), pick(row, "url", "link"), pick(row, "date")
            if not name and not url:
                continue
            v = srcs.setdefault((name, url), {"date": date, "chs": []})
            if ch not in v["chs"]:
                v["chs"].append(ch)
    out += ["## Sources (all chapters, combined)", "", "| Source | URL | Date | Used in |", "|---|---|---|---|"]
    for (name, url), v in srcs.items():
        out += [f"| {name} | {url} | {v['date']} | {', '.join(v['chs'])} |"]
    out += ["", "Analogies, jokes and plain-language definitions not tied to a row above were written for the video "
            "and are not from a source.", ""]
    (root / "script" / "full_script.md").write_text("\n".join(out))
    print(f"wrote script/full_script.md: {nseg} segments, {len(srcs)} distinct sources")


def check_full(files, offs, total):
    root = project.root()
    full = root / "out" / "full.mp4"
    _, d_full = sig(full)
    print(f"joined duration {d_full:.3f}s, sum of chapters {total:.3f}s, difference {d_full - total:+.3f}s")
    for st in ffprobe(full)["streams"]:
        print("  stream", st["codec_type"], st["codec_name"], st.get("width", ""), st.get("height", ""),
              st.get("r_frame_rate", ""), st.get("pix_fmt", ""), st.get("sample_rate", ""), st.get("duration"))
    sil = checks.silences(full)
    print(f"silences under -55 dB for 1 s or more: {len(sil)}", *sil[:10], sep="\n  ")
    import mix
    for (ch, f), off in zip(files, offs):
        dur = sig(f)[1]
        loud = mix.lufs(full, off, dur)
        mid = off + min(dur * 0.4, max(0.0, dur - 1))
        jpg = checks.grab(full, mid, root / "frames" / f"join_{ch}.jpg")
        print(f"{ch:6s} starts {off:8.3f}s  length {dur:8.3f}s  integrated {loud:.1f} LUFS  frame {jpg} @ {mid:.2f}s")


def app_copies():
    root = project.root()
    adir = root / "out" / "app"
    adir.mkdir(parents=True, exist_ok=True)
    audio_k = 128
    for ch, f in chapter_files():
        dur = sig(f)[1]
        out = adir / f.name
        tmp = adir / (f.stem + ".tmp.mp4")
        # video budget: what is left of the target after audio and ~2% container overhead, capped
        vk = int(min(3000, max(120, (APP_TARGET * 8 / dur / 1000) * 0.98 - audio_k)))
        for attempt in range(5):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(f), "-vf", "scale=-2:720:flags=lanczos",
                            "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "23",
                            "-maxrate", f"{vk}k", "-bufsize", f"{2 * vk}k", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", f"{audio_k}k", "-ar", "48000", "-ac", "2",
                            "-movflags", "+faststart", "-f", "mp4", str(tmp)], check=True)
            size = tmp.stat().st_size
            if size < APP_LIMIT:
                break
            vk = int(vk * 0.85 * APP_TARGET / size)
            print(f"{f.name}: {size / 1e6:.1f} MB is too big; retrying at {vk} kb/s")
        else:
            raise SystemExit(f"{f.name}: could not get under 20 MB")
        os.replace(tmp, out)
        d = ffprobe(out)
        v = next(s for s in d["streams"] if s["codec_type"] == "video")
        print(f"{out}  {size / 1e6:.2f} MB  {v['width']}x{v['height']}  {float(d['format']['duration']):.2f}s  "
              f"(video cap {vk} kb/s)")
