"""Child process: render one scene. ManimGX draws it on a transparent background, and each frame is
piped into ffmpeg, which lays it over the BG colour and the drifting glows (background.py) and
encodes H.264. vg.py runs this once per scene (a fresh process each time).

  python render.py <project> <chapter> <scene> <out.mp4>

ManimGX hands over each distinct frame once with a repeat count (static stretches are drawn once);
the file gets exactly round(dur * FPS) frames, so scene files concatenate to the timing json.
"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import project  # noqa: E402


def main(proj, ch, name, out):
    project.use(proj)
    import manimgx as m
    import style
    import background
    import timeline

    cls = project.scene_class(project.load_chapter(ch), name)
    m.config.background_opacity = 0.0          # premultiplied RGBA out; ffmpeg adds BG + glows
    info = next(s for s in timeline.load(ch)["scenes"] if s["name"] == name)
    want = round(info["dur"] * style.FPS)
    cmd = (["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s",
            f"{style.WIDTH}x{style.HEIGHT}", "-r", str(style.FPS), "-i", "-"] + background.ffmpeg_inputs() +
           ["-filter_complex", background.ffmpeg_filter(), "-frames:v", str(want), "-c:v", "libx264",
            "-crf", str(style.CRF), "-preset", style.PRESET, "-pix_fmt", "yuv420p", "-r", str(style.FPS),
            "-movflags", "+faststart", "-f", "mp4", out])
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    state = {"n": 0, "last": None}

    def sink(frame):
        if state["n"] >= want:
            return
        px = frame.pixels()
        state["last"] = px
        k = min(frame.repeat, want - state["n"])
        for _ in range(k):
            ff.stdin.write(px)
        state["n"] += k

    try:
        cls().render(None, frames=sink)
        while state["n"] < want:                    # pad with the last frame if ManimGX ended early
            ff.stdin.write(state["last"])
            state["n"] += 1
    finally:
        ff.stdin.close()
        rc = ff.wait()
    if rc != 0:
        raise SystemExit("ffmpeg failed")
    print(f"{name}: wrote {state['n']} frames (want {want})")


if __name__ == "__main__":
    main(*sys.argv[1:5])
