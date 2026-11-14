#!/usr/bin/env python3
"""video-gen: build narrated, animated explainer videos. Run with the venv's Python (setup.sh).

  vg.py init <project> [--title T]          new project folder (templates, folders, project.json)
  vg.py <project> estimate                  words and estimated minutes per chapter; flags stale cue phrases
  vg.py <project> claims                    check script/claims.md quotes against sources/ (exit 1 if any missing)
  vg.py <project> leakcheck <file>          flag narration/on-screen text sharing 6 words or a number with <file>
  vg.py <project> chN voice-todo            segments still without audio/chN/NNN.wav, with the text to send
  vg.py <project> chN timing                measure the WAVs -> script/chN_timing.json + out/<name>.srt
  vg.py <project> chN stills SCENE t1,t2    full-size PNGs of SCENE at those scene times -> frames/  [--layout]
  vg.py <project> chN render SCENE          one scene -> scenes/chN/SCENE.mp4 (temp file, renamed on success)
  vg.py <project> chN render-all            every missing or out-of-date scene, one process each  [--budget MIN] [--force]
  vg.py <project> chN audio                 voice + music bed + title sting -> audio/chN_mix.wav
  vg.py <project> chN assemble              concat scenes (-c copy) + mux audio (-c:v copy) -> out/<name>.mp4
  vg.py <project> chN check                 frame counts, streams, durations, loudness, sample frames
  vg.py <project> join                      chapters in project.json order -> out/full.mp4, out/full.srt, script/full_script.md
  vg.py <project> app-copies                720p H.264/AAC copies of each chapter in out/app/, each under 20 MB

Projects live outside the repo. Docs: docs/PIPELINE.md (the steps), docs/SCRIPT_FORMAT.md, docs/STYLE.md.
"""
import ast
import datetime
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

ENGINE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ENGINE))
import project  # noqa: E402

PY = sys.executable
MGX = pathlib.Path(sys.executable).parent / "manimgx"     # the manimgx CLI of this venv
RENDER_RATE = 7.0      # first guess: seconds of CPU per second of video (measured ~6.5 on 4 cores)
GLOBAL = {"estimate", "claims", "leakcheck", "join", "app-copies"}
CHAPTER_CMDS = {"voice-todo", "timing", "stills", "render", "render-all", "audio", "assemble", "check"}
SPEKO_BODY = {"text": None, "intent": {"language": "en-US"}, "voice": "Puck",
              "constraints": {"allowedProviders": {"tts": ["google-tts:gemini-3.8-flash-lite-tts"]}}}


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run([str(c) for c in cmd], **kw)


# ----------------------------------------------------------------------------- init
def cmd_init(path, title):
    root = pathlib.Path(path).expanduser().resolve()
    inside = project.REPO in (root, *root.parents)
    if inside and (project.REPO / "examples") not in root.parents:
        die(f"{root} is inside the engine repo; projects live outside it (demo projects go in examples/)")
    root.mkdir(parents=True, exist_ok=True)
    for d in project.DIRS:
        (root / d).mkdir(exist_ok=True)
    (root / "audio" / "ch1").mkdir(exist_ok=True)
    t = project.TEMPLATES
    copies = [(t / "chapter_template.py", root / "chapters" / "ch1.py"),
              (t / "segments_template.py", root / "script" / "ch1_segments.py"),
              (t / "chapter_notes_template.md", root / "script" / "ch1_notes.md"),
              (t / "characters.py", root / "characters.py"),
              (t / "claims.md", root / "script" / "claims.md"),
              (t / "DECISIONS.md", root / "DECISIONS.md")]
    title = title or root.name
    for src, dst in copies:
        if dst.exists():
            print(f"kept   {dst}")
        else:
            dst.write_text(src.read_text().replace("{{TITLE}}", title))
            print(f"wrote  {dst}")
    pj = root / "project.json"
    if pj.exists():
        print(f"kept   {pj}")
    else:
        pj.write_text(json.dumps({"title": title, "chapters": ["ch1"],
                                  "created": datetime.date.today().isoformat()}, indent=1) + "\n")
        print(f"wrote  {pj}")
    print(f"\nproject ready: {root}\nnext: write script/ch1_segments.py (docs/SCRIPT_FORMAT.md), then\n"
          f"  {PY} {ENGINE / 'vg.py'} {root} estimate")


# ----------------------------------------------------------------------------- chapter helpers
def class_scene_names(node):
    """NAME values assigned in one class body (NAME = "x" or CHAPTER, NAME = C, "x")."""
    names = set()
    for st in node.body:
        if isinstance(st, ast.Assign):
            for tg in st.targets:
                if isinstance(tg, ast.Name) and tg.id == "NAME" and isinstance(st.value, ast.Constant):
                    names.add(st.value.value)
                elif isinstance(tg, ast.Tuple) and isinstance(st.value, ast.Tuple):
                    for a, b in zip(tg.elts, st.value.elts):
                        if isinstance(a, ast.Name) and a.id == "NAME" and isinstance(b, ast.Constant):
                            names.add(b.value)
    return names


def scene_names_in_file(ch):
    """Scene NAMEs a chapter file defines, read with ast (classes with NAME = ..., make_title(...))."""
    names = set()
    for node in ast.walk(ast.parse(project.chapter_file(ch).read_text())):
        if isinstance(node, ast.ClassDef):
            names |= class_scene_names(node)
        elif isinstance(node, ast.Call) and getattr(node.func, "id", None) == "make_title":
            kw = {k.arg: k.value for k in node.keywords}
            names.add(kw["name"].value if "name" in kw and isinstance(kw["name"], ast.Constant) else "sc00_title")
    return names


def cue_problems(ch, segs=None):
    """self.at(N, "phrase") calls in chapters/chN.py whose segment or phrase is not in the script.

    Read with ast, so it works before any narration exists (estimate) and after (timing). Only literal
    arguments are checked; a stale phrase would otherwise fail only at stills or render time."""
    f = project.chapter_file(ch)
    if not f.exists():
        return []
    segs = {s["id"]: s for s in (segs or project.segments(ch))}
    out = []
    for node in ast.walk(ast.parse(f.read_text())):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "at"
                and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, int)):
            continue
        sid = node.args[0].value
        if sid not in segs:
            out.append(f"chapters/{ch}.py line {node.lineno}: segment {sid} is not in script/{ch}_segments.py")
            continue
        if len(node.args) > 1 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
            ph = node.args[1].value.lower()
            s = segs[sid]
            if ph not in s["say"].lower() and ph not in s.get("cap", s["say"]).lower():
                out.append(f"chapters/{ch}.py line {node.lineno}: phrase {node.args[1].value!r} "
                           f"is not in segment {sid}'s say or cap")
    return out


def report_cues(ch, segs=None):
    probs = cue_problems(ch, segs)
    for p in probs:
        print(f"cue: {p}")
    return probs


def missing_wavs(ch, segs):
    out = []
    for s in segs:
        w = project.wav_path(ch, s["id"])
        if not w.exists() or w.stat().st_size < 1000:
            out.append((s, w))
    return out


def cmd_voice_todo(ch):
    segs = project.segments(ch)
    todo = missing_wavs(ch, segs)
    print(f"{ch}: {len(segs) - len(todo)} of {len(segs)} segments have audio; {len(todo)} to go")
    if not todo:
        return
    print("For each: one mcp__Speko__audio_synthesize call with the body shown, then copy the saved WAV at once "
          "to the path shown. Never re-call a segment that already succeeded.\n")
    for s, w in todo:
        body = dict(SPEKO_BODY, text=s["say"])
        print(f"{s['id']:03d}  [{s['scene']}]  -> {w}")
        print("     " + json.dumps(body, ensure_ascii=False))


def cmd_timing(ch):
    import timeline
    segs = project.segments(ch)
    todo = missing_wavs(ch, segs)
    if todo:
        ids = ", ".join("%03d" % s["id"] for s, _ in todo)
        die(f"{ch}: {len(todo)} segment(s) have no audio yet: {ids} (see: vg.py <project> {ch} voice-todo)", 1)
    meta = project.chapter_meta(ch)
    t = timeline.build_timing(ch, segs, title=meta["TITLE"])
    srt = project.root() / "out" / f"{meta['OUT_NAME']}.srt"
    srt.write_text(timeline.srt(ch, t))
    for s in t["scenes"]:
        print(f"{s['name']:18s} start {s['start']:7.2f}  dur {s['dur']:6.2f}  segs {[x['id'] for x in s['segments']]}")
    print(f"total {t['total']:.2f}s ({t['total'] / 60:.2f} min) -> {timeline.timing_path(ch)}, {srt}")
    defined = scene_names_in_file(ch)
    lacking = [s["name"] for s in t["scenes"] if s["name"] not in defined]
    if lacking:
        print(f"note: chapters/{ch}.py has no scene class yet for: {', '.join(lacking)}")
    report_cues(ch, segs)


def child_env():
    env = dict(os.environ)
    env["VG_PROJECT"] = str(project.root())
    env["PYTHONPATH"] = os.pathsep.join([str(ENGINE), str(project.root())] +
                                        ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
    return env


def cmd_stills(ch, name, times, layout=False):
    import timeline
    timeline.load(ch)
    r = run([PY, ENGINE / "stills.py", project.root(), ch, name, times], env=child_env())
    if r.returncode != 0:
        die("stills failed", r.returncode)
    if layout:
        # ManimGX's own layout checks (clipped content, overlapping text, small labels) at the same times.
        # It draws without the background composite; its findings are advisory.
        cls = None
        mod_src = project.chapter_file(ch)
        tree = ast.parse(mod_src.read_text())
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and name in class_scene_names(node):
                cls = node.name
        if not cls:
            die(f"--layout: no class statement for {name} in {mod_src.name} (make_title scenes are skipped)", 1)
        out = project.root() / "frames" / f"{ch}_{name}_layout.png"
        run([MGX, "inspect", mod_src, cls, "-t", times, "-o", out], env=child_env(), cwd=project.root())


def render_one(ch, name, info):
    d = project.root() / "scenes" / ch
    d.mkdir(parents=True, exist_ok=True)
    tmp, final = d / f"{name}.tmp.mp4", d / f"{name}.mp4"
    tmp.unlink(missing_ok=True)
    t0 = time.time()
    r = run([PY, ENGINE / "render.py", project.root(), ch, name, tmp], env=child_env())
    if r.returncode != 0:
        tmp.unlink(missing_ok=True)
        die(f"render of {name} failed (exit {r.returncode}); {final.name} left as it was", r.returncode or 1)
    os.replace(tmp, final)
    el = time.time() - t0
    print(f"ok {final}  ({info['dur']:.1f}s of video in {el:.0f}s, {el / max(info['dur'], 0.1):.1f}x)")
    return el


def scene_info(ch, name):
    import timeline
    for s in timeline.load(ch)["scenes"]:
        if s["name"] == name:
            return s
    die(f"{name} is not a scene of {ch} (see script/{ch}_timing.json)")


def cmd_render(ch, name):
    render_one(ch, name, scene_info(ch, name))


def cmd_render_all(ch, budget_min=8.0, force=False):
    import timeline
    root = project.root()
    t = timeline.load(ch)
    deps = [project.chapter_file(ch), timeline.timing_path(ch), root / "characters.py"]
    newest = max(p.stat().st_mtime for p in deps if p.exists())
    todo = []
    for s in t["scenes"]:
        f = root / "scenes" / ch / f"{s['name']}.mp4"
        if force or not f.exists() or f.stat().st_mtime < newest:
            todo.append(s)
        else:
            print(f"up to date: {f.name}")
    t0, rate, done = time.time(), RENDER_RATE, 0
    for k, s in enumerate(todo):
        guess = s["dur"] * rate
        elapsed = time.time() - t0
        if done and elapsed + guess > budget_min * 60:
            left = [x["name"] for x in todo[k:]]
            print(f"\nstopping before the {budget_min:g}-minute budget: {len(left)} scene(s) left "
                  f"({', '.join(left)}). Run render-all again to continue.")
            sys.exit(3)
        if guess > budget_min * 60:
            print(f"warning: {s['name']} ({s['dur']:.0f}s) may take ~{guess / 60:.1f} min; split long scenes")
        el = render_one(ch, s["name"], s)
        rate = max(rate * 0.5, el / max(s["dur"], 0.1))
        done += 1
    print(f"render-all: {done} rendered, {len(t['scenes']) - len(todo)} already up to date")


def cmd_assemble(ch):
    import timeline
    root = project.root()
    t = timeline.load(ch)
    name = project.chapter_meta(ch)["OUT_NAME"]
    d = root / "scenes" / ch
    missing = [s["name"] for s in t["scenes"] if not (d / f"{s['name']}.mp4").exists()]
    if missing:
        die(f"not rendered yet: {', '.join(missing)}", 1)
    mixf = root / "audio" / f"{ch}_mix.wav"
    if not mixf.exists():
        die(f"{mixf} is missing (run: vg.py <project> {ch} audio)", 1)
    lst = d / "concat.txt"
    lst.write_text("".join(f"file '{d / (s['name'] + '.mp4')}'\n" for s in t["scenes"]))
    silent = root / "out" / f"{name}.video.tmp.mp4"
    final_tmp = root / "out" / f"{name}.tmp.mp4"
    r = run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-map", "0:v", "-c", "copy",
             "-f", "mp4", silent])
    if r.returncode == 0:
        r = run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", mixf,
                 "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                 "-movflags", "+faststart", "-f", "mp4", final_tmp])
    silent.unlink(missing_ok=True)
    if r.returncode != 0:
        final_tmp.unlink(missing_ok=True)
        die("assemble failed", 1)
    os.replace(final_tmp, root / "out" / f"{name}.mp4")
    print("ok", root / "out" / f"{name}.mp4")


# ----------------------------------------------------------------------------- main
def main(argv):
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    if argv[0] == "init":
        if len(argv) < 2:
            die("usage: vg.py init <project> [--title T]")
        title = argv[argv.index("--title") + 1] if "--title" in argv else None
        cmd_init(argv[1], title)
        return 0
    if len(argv) < 2:
        die(__doc__)
    proj = pathlib.Path(argv[0]).expanduser()
    if not (proj / "project.json").exists():
        die(f"{proj} is not a project (no project.json); make one with: vg.py init {proj}")
    project.use(proj)
    cmd, rest = argv[1], argv[2:]
    if cmd in GLOBAL:
        if cmd == "estimate":
            import estimate
            estimate.run()
            for c in project.chapters():
                if (project.root() / "script" / f"{c}_segments.py").exists():
                    report_cues(c)
        elif cmd == "claims":
            import claims
            return claims.run()
        elif cmd == "leakcheck":
            if not rest:
                die("usage: vg.py <project> leakcheck <file>")
            import leakcheck
            return leakcheck.run(rest[0])
        elif cmd == "join":
            import join
            join.join()
        elif cmd == "app-copies":
            import join
            join.app_copies()
        return 0
    ch = cmd
    if not rest or rest[0] not in CHAPTER_CMDS:
        die(f"unknown command {' '.join(argv[1:3])!r}\n\n{__doc__}")
    if ch not in project.chapters():
        print(f"note: {ch} is not listed in project.json's chapters (join will skip it)", file=sys.stderr)
    what, args = rest[0], rest[1:]
    flags = {a for a in args if a.startswith("--")}
    pos = [a for a in args if not a.startswith("--")]
    if what == "voice-todo":
        cmd_voice_todo(ch)
    elif what == "timing":
        cmd_timing(ch)
    elif what == "stills":
        if len(pos) < 2:
            die("usage: vg.py <project> chN stills SCENE t1,t2,...")
        cmd_stills(ch, pos[0], pos[1], layout="--layout" in flags)
    elif what == "render":
        if not pos:
            die("usage: vg.py <project> chN render SCENE")
        cmd_render(ch, pos[0])
    elif what == "render-all":
        budget = 8.0
        if "--budget" in args:
            budget = float(args[args.index("--budget") + 1])
        cmd_render_all(ch, budget, force="--force" in flags)
    elif what == "audio":
        import mix
        mix.build(ch)
    elif what == "assemble":
        cmd_assemble(ch)
    elif what == "check":
        import checks
        return 0 if checks.chapter(ch) else 1
    return 0


if __name__ == "__main__":
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        die("ffmpeg and ffprobe must be on PATH")
    try:
        sys.exit(main(sys.argv[1:]) or 0)
    except BrokenPipeError:           # output piped into head and the like
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
