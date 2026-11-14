"""This video's two recurring characters, decided in the grilling. Chapter files and the shared title
card and recall scene use LEAD and CHECK from here.

  LEAD  = the one who acts first: overeager, curious, makes the mistakes the viewer would make
  CHECK = the one who checks: calm, skeptical, asks "how do we know?"

The engine's library (engine/cast.py) has Chip (a robot intern, teal) and Brick (a bouncer in dark
glasses, purple). Pick them as they are, restyle them with arguments (Chip(badge="ROOKIE"),
Brick(tag="COACH")) by subclassing as below, or draw a new pair for the topic.

Drawing a new character (docs/STYLE.md, "New characters"):
  - subclass cast.Character; build it only from simple shapes (rounded rectangles, circles, lines,
    polygons) in the palette (style.py); give it one signature colour (COLOR)
  - stand it on its feet: about 3.4 units tall at scale 1, centred on x = 0, feet at the bottom
  - set self.mouth (start it with make_mouth(kind, centre, MOUTH_W, MOUTH_COLOR)) so face(c, "grin")
    works; kinds: smile, grin, o, worried, flat; keep handy parts as attributes (eyes, arms, ...)
  - end __init__ with self._done(scale)
  - original designs only: no brands, logos, mascots, real people or characters from existing media
Check a new character with `vg.py <project> chN stills SCENE t` before using it everywhere.
"""
import manimgx as m
from cast import Character, Chip, Brick, make_mouth   # noqa: F401
from style import AMBER, BG, INK, PINK


class Lead(Chip):
    def __init__(self, scale=1.0):
        super().__init__(scale, badge="INTERN")     # the badge word suits the topic: "ROOKIE", "NEW", ...


class Check(Brick):
    def __init__(self, scale=1.0):
        super().__init__(scale, tag="STAFF")        # the shirt word: "COACH", "EDITOR", "REF", ...


class Owl(Character):
    """Example of a new character drawn from simple shapes (not used unless you pick it above)."""
    MOUTH_W = 0.3
    MOUTH_COLOR = BG
    COLOR = PINK

    def __init__(self, scale=1.0):
        super().__init__()
        body = m.Ellipse(width=2.2, height=2.7, color=PINK, fill_color=PINK, fill_opacity=1,
                         stroke_width=0).move_to([0, 0.15, 0])
        belly = m.Ellipse(width=1.4, height=1.6, color="#fbd3e4", fill_color="#fbd3e4", fill_opacity=1,
                          stroke_width=0).move_to([0, -0.35, 0])
        tuft_l = m.Polygon([-0.95, 1.05, 0], [-0.55, 1.35, 0], [-0.85, 1.7, 0], color=PINK, fill_color=PINK,
                           fill_opacity=1, stroke_width=0)
        tuft_r = tuft_l.copy().flip(m.UP).move_to([0.75, 1.37, 0])
        self.eyes = m.VGroup(*[m.VGroup(
            m.Circle(radius=0.36, color=INK, fill_color=INK, fill_opacity=1, stroke_width=0),
            m.Circle(radius=0.15, color=BG, fill_color=BG, fill_opacity=1, stroke_width=0))
            .move_to([x, 0.75, 0]) for x in (-0.42, 0.42)])
        beak = m.Polygon([-0.14, 0.42, 0], [0.14, 0.42, 0], [0, 0.2, 0], color=AMBER, fill_color=AMBER,
                         fill_opacity=1, stroke_width=0)
        self.mouth = make_mouth("flat", [0, 0.08, 0], self.MOUTH_W, color=self.MOUTH_COLOR)
        feet = m.VGroup(*[m.RoundedRectangle(width=0.42, height=0.16, corner_radius=0.08, color=AMBER,
                                             fill_color=AMBER, fill_opacity=1, stroke_width=0)
                          .move_to([x, -1.2, 0]) for x in (-0.38, 0.38)])
        self.add(tuft_l, tuft_r, body, belly, self.eyes, beak, self.mouth, feet)
        self._done(scale)


# ---- the pair this video uses (pick any two classes above or from cast.py) ----
LEAD, CHECK = Lead, Check
NAMES = {"LEAD": "Chip", "CHECK": "Brick"}          # how the narration refers to them
