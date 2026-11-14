"""Child process: draw full-size (2560x1440) still frames of one scene at chosen scene times, with the
same background composite as the video, without encoding a video.

  python stills.py <project> <chapter> <scene> 3,12.5   -> frames/<chapter>_<scene>_t03.00.png ...
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import project  # noqa: E402


def main(proj, ch, name, times):
    project.use(proj)
    import numpy as np
    import manimgx as m
    from manimgx.rendering.film import Cut
    from PIL import Image
    import style
    import background
    import timeline

    cls = project.scene_class(project.load_chapter(ch), name)
    info = next(s for s in timeline.load(ch)["scenes"] if s["name"] == name)
    last = round(info["dur"] * style.FPS) - 1
    want = sorted({min(last, max(0, round(float(t) * style.FPS))) for t in times.split(",") if t.strip()})
    left = list(want)
    out = []
    fdir = project.root() / "frames"
    fdir.mkdir(exist_ok=True)

    def sink(frame):
        while left and frame.index <= left[0] < frame.index + frame.repeat:
            k = left.pop(0)
            px = np.frombuffer(frame.pixels(), np.uint8).reshape(style.HEIGHT, style.WIDTH, 4)
            img = Image.fromarray(background.composite_still(px, k / style.FPS), "RGB")
            p = fdir / f"{ch}_{name}_t{k / style.FPS:05.2f}.png"
            img.save(p)
            out.append(p)
        if not left:
            raise Cut()

    m.config.background_opacity = 0.0
    cls().render(None, frames=sink)
    for p in out:
        print(p)
    if left:
        print(f"not drawn (past the scene's last frame?): {[k / style.FPS for k in left]}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
