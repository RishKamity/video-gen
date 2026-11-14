"""Draw one test frame at 2560x1440 with the house style, without a project (setup.sh runs this).

  python testframe.py OUT.png

It exercises what every render needs: ManimGX, the fonts, the shapes of both library characters,
a term pill, a caption band, and the ffmpeg-equivalent background composite.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import manimgx as m  # noqa: E402
from manimgx.rendering.film import Cut  # noqa: E402
from PIL import Image  # noqa: E402

import style  # noqa: E402
from style import AMBER, INK, MUTED, txt, mono, term, fit  # noqa: E402
import background  # noqa: E402
from cast import Chip, Brick  # noqa: E402

style.setup_config()


class TestFrame(m.Scene):
    def construct(self):
        title = fit(txt("video-gen test frame", size=72, color=INK, bold=True)).move_to([0, 2.6, 0])
        sub = txt("2560 x 1440, 30 fps, house style", size=36, color=MUTED).move_to([0, 1.7, 0])
        code = mono("vg.py <project> ch1 render sc01", size=30, color=AMBER).move_to([0, 0.9, 0])
        pill = term("key term", size=48).move_to([0, -0.4, 0])
        a = Chip(0.8).move_to([-4.6, -0.7, 0])
        b = Brick(0.8).move_to([4.6, -0.6, 0])
        cap = txt("Captions sit on a band at the bottom.", size=34, color=INK).move_to([0, -3.47, 0])
        band = m.RoundedRectangle(width=cap.width + 0.7, height=0.78, corner_radius=0.16, stroke_width=0,
                                  fill_color="#000000", fill_opacity=0.62).move_to([0, -3.47, 0])
        self.add(title, sub, code, pill, a, b, band, cap)
        self.wait(1)


def main(out):
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    m.config.background_opacity = 0.0
    done = {}

    def sink(frame):
        px = np.frombuffer(frame.pixels(), np.uint8).reshape(style.HEIGHT, style.WIDTH, 4)
        Image.fromarray(background.composite_still(px, 0.0), "RGB").save(out)
        done["ok"] = True
        raise Cut()

    TestFrame().render(None, frames=sink)
    if not done:
        raise SystemExit("no frame was drawn")
    w, h = Image.open(out).size
    if (w, h) != (style.WIDTH, style.HEIGHT):
        raise SystemExit(f"test frame is {w}x{h}, expected {style.WIDTH}x{style.HEIGHT}")
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
