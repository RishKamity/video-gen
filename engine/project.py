"""Where things live: the engine (this folder), the repo, and the current project.

A project is a folder outside the repo (made by `vg.py init`). Every engine module finds it through
root(): the VG_PROJECT environment variable, which vg.py sets for itself and for every child
process it starts. Without it, the nearest folder at or above the working directory that holds a
project.json is used.

Project layout:
  project.json          {"title": ..., "chapters": ["ch1", "ch2", ...]}  (the chapter order)
  characters.py         this video's two characters (LEAD, CHECK)
  chapters/chN.py       scene classes for chapter N (TITLE, OUT_NAME, NarratedScene subclasses)
  script/chN_segments.py, script/chN_*.md, script/claims.md, script/chN_timing.json
  sources/*.md          extracted source text (the claim checker reads these)
  audio/chN/NNN.wav     one narration WAV per segment; audio/chN_mix.wav and stems
  scenes/chN/SCENE.mp4  rendered scenes;  out/  finished chapters, .srt, full.mp4;  frames/ stills
"""
import ast
import importlib.util
import json
import os
import pathlib
import runpy
import sys

ENGINE = pathlib.Path(__file__).resolve().parent
REPO = ENGINE.parent
TEMPLATES = REPO / "templates"
DIRS = ("script", "chapters", "sources", "audio", "scenes", "out", "frames")


def root():
    env = os.environ.get("VG_PROJECT")
    if env:
        return pathlib.Path(env).resolve()
    here = pathlib.Path.cwd().resolve()
    for p in (here, *here.parents):
        if (p / "project.json").exists():
            return p
    raise SystemExit("no project: run through vg.py, set VG_PROJECT, or work inside a folder with project.json")


def use(path):
    """Make `path` the current project for this process and its children, and put the project
    folder on sys.path (after the engine) so chapter files can `import characters`."""
    p = pathlib.Path(path).resolve()
    os.environ["VG_PROJECT"] = str(p)
    for d in (str(ENGINE), str(p)):
        if d in sys.path:
            sys.path.remove(d)
    sys.path.insert(0, str(p))
    sys.path.insert(0, str(ENGINE))   # engine modules win over anything in the project folder
    return p


def config():
    f = root() / "project.json"
    if not f.exists():
        raise SystemExit(f"{f} is missing (make the project with: vg.py init <project>)")
    return json.loads(f.read_text())


def chapters():
    return list(config().get("chapters", []))


def chapter_file(ch):
    return root() / "chapters" / f"{ch}.py"


def chapter_meta(ch):
    """TITLE and OUT_NAME from chapters/<ch>.py without importing it (both must be literals).
    TITLE = (scene name, seconds) or None; OUT_NAME defaults to the chapter id."""
    f = chapter_file(ch)
    if not f.exists():
        raise SystemExit(f"{f} is missing")
    meta = {"TITLE": None, "OUT_NAME": ch}
    for node in ast.parse(f.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in meta:
                try:
                    meta[name] = ast.literal_eval(node.value)
                except ValueError:
                    raise SystemExit(f"{f}: {name} must be a literal (it is read without importing the file)")
    if meta["TITLE"] is not None:
        meta["TITLE"] = (str(meta["TITLE"][0]), float(meta["TITLE"][1]))
    return meta


def segments(ch):
    """SEGMENTS from script/<ch>_segments.py, validated."""
    f = root() / "script" / f"{ch}_segments.py"
    if not f.exists():
        raise SystemExit(f"{f} is missing")
    segs = runpy.run_path(str(f)).get("SEGMENTS")
    if not segs:
        raise SystemExit(f"{f} defines no SEGMENTS")
    known = {"id", "scene", "say", "cap", "pause"}
    seen = set()
    for s in segs:
        for k in ("id", "scene", "say"):
            if k not in s:
                raise SystemExit(f"{f}: a segment is missing '{k}': {s}")
        if not isinstance(s["id"], int) or s["id"] in seen:
            raise SystemExit(f"{f}: segment ids must be unique integers (problem at id {s['id']!r})")
        seen.add(s["id"])
        extra = set(s) - known
        if extra:
            print(f"note: {f.name} id {s['id']}: ignoring unknown field(s) {sorted(extra)}", file=sys.stderr)
    return segs


def wav_path(ch, seg_id):
    return root() / "audio" / ch / f"{seg_id:03d}.wav"


def load_chapter(ch):
    """Import chapters/<ch>.py as module <ch> (the project must be in use())."""
    if ch in sys.modules:
        return sys.modules[ch]
    spec = importlib.util.spec_from_file_location(ch, chapter_file(ch))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ch] = mod
    spec.loader.exec_module(mod)
    return mod


def scene_class(mod, name):
    """The NarratedScene subclass defined in mod whose NAME is name."""
    for v in vars(mod).values():
        if isinstance(v, type) and getattr(v, "NAME", None) == name and v.__module__ == mod.__name__:
            return v
    raise SystemExit(f"{mod.__name__}: no scene class with NAME = {name!r}")


def cache_dir():
    d = pathlib.Path(os.environ.get("VG_CACHE", pathlib.Path.home() / ".cache" / "video-gen"))
    d.mkdir(parents=True, exist_ok=True)
    return d
