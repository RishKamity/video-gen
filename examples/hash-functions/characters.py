"""This video's two recurring characters (DECISIONS.md), drawn from simple shapes for the topic.

  LEAD  = Whizz, an overeager teal blender: anything tossed in comes out as a fingerprint (a hash)
  CHECK = Latch, a calm purple padlock who guards the login and checks fingerprints

Both stand on their feet, centred on x = 0, about 3.4 units tall at scale 1, and set self.mouth,
MOUTH_W and MOUTH_COLOR so face(c, "grin") works. Original designs: no brands, logos or mascots.
"""
import manimgx as m
from cast import Character, make_mouth   # noqa: F401
from style import AMBER, BG, INK, MUTED, PURPLE, TEAL, TEAL_D


def _rr(w, h, r, color, fill=None, opacity=1.0, sw=0):
    return m.RoundedRectangle(width=w, height=h, corner_radius=r, color=color,
                              fill_color=fill or color, fill_opacity=opacity, stroke_width=sw)


def _eyes(xs, y, r=0.2, pr=0.09, dx=0.03):
    return m.VGroup(*[m.VGroup(
        m.Circle(radius=r, color=INK, fill_color=INK, fill_opacity=1, stroke_width=0),
        m.Circle(radius=pr, color=BG, fill_color=BG, fill_opacity=1, stroke_width=0).shift([dx, -0.02, 0]))
        .move_to([x, y, 0]) for x in xs])


class Whizz(Character):
    """The blender (LEAD). A see-through jar with a face, a lid, blades, and a base with a dial."""
    MOUTH_W = 0.5
    MOUTH_COLOR = INK
    COLOR = TEAL

    def __init__(self, scale=1.0):
        super().__init__()
        feet = m.VGroup(*[_rr(0.36, 0.16, 0.07, TEAL_D).move_to([x, -1.78, 0]) for x in (-0.5, 0.5)])
        base = _rr(1.6, 0.78, 0.2, TEAL_D).move_to([0, -1.32, 0])
        self.dial = m.VGroup(
            m.Circle(radius=0.17, color=AMBER, fill_color=AMBER, fill_opacity=1, stroke_width=0),
            m.Line([0, 0, 0], [0, 0.13, 0], color=BG, stroke_width=5)).move_to([0, -1.32, 0])
        lights = m.VGroup(*[m.Circle(radius=0.05, color=c, fill_color=c, fill_opacity=1, stroke_width=0)
                            .move_to([x, -1.32, 0]) for x, c in ((-0.5, INK), (0.5, INK))])
        jar = m.Polygon([-0.55, -0.93, 0], [0.55, -0.93, 0], [0.8, 1.15, 0], [-0.8, 1.15, 0],
                        color=TEAL, fill_color=TEAL, fill_opacity=0.28, stroke_width=6)
        self.blades = m.VGroup(m.Line([-0.32, -0.62, 0], [0.32, -0.74, 0], color=MUTED, stroke_width=7),
                               m.Line([-0.32, -0.74, 0], [0.32, -0.62, 0], color=MUTED, stroke_width=7),
                               m.Dot([0, -0.68, 0], radius=0.06, color=MUTED))
        handle = m.VGroup(m.Line([0.74, 0.85, 0], [1.12, 0.85, 0], color=TEAL, stroke_width=12),
                          m.Line([1.12, 0.85, 0], [1.12, -0.25, 0], color=TEAL, stroke_width=12),
                          m.Line([1.12, -0.25, 0], [0.6, -0.25, 0], color=TEAL, stroke_width=12))
        lid = _rr(1.8, 0.28, 0.12, TEAL).move_to([0, 1.3, 0])
        knob = _rr(0.5, 0.22, 0.08, TEAL_D).move_to([0, 1.53, 0])
        self.eyes = _eyes((-0.3, 0.3), 0.45)
        self.mouth = make_mouth("grin", [0, 0.02, 0], self.MOUTH_W, color=self.MOUTH_COLOR)
        self.add(feet, handle, base, self.dial, lights, jar, self.blades, lid, knob, self.eyes, self.mouth)
        self._done(scale)


class Latch(Character):
    """The padlock (CHECK). A purple lock body with a silver shackle, calm eyes and a keyhole."""
    MOUTH_W = 0.42
    MOUTH_COLOR = BG
    COLOR = PURPLE
    SHACKLE = "#c9cde0"

    def __init__(self, scale=1.0):
        super().__init__()
        shackle = m.VGroup(
            m.Arc(radius=0.58, start_angle=0, angle=m.PI, color=self.SHACKLE, stroke_width=22).move_to([0, 1.17, 0]),
            m.Line([-0.58, 0.88, 0], [-0.58, 0.45, 0], color=self.SHACKLE, stroke_width=22),
            m.Line([0.58, 0.88, 0], [0.58, 0.45, 0], color=self.SHACKLE, stroke_width=22))
        legs = m.VGroup(*[_rr(0.34, 0.42, 0.12, "#5b4a8f").move_to([x, -1.42, 0]) for x in (-0.45, 0.45)])
        arms = m.VGroup(m.Line([-0.98, -0.25, 0], [-1.3, -0.75, 0], color="#7c63c9", stroke_width=14),
                        m.Line([0.98, -0.25, 0], [1.3, -0.75, 0], color="#7c63c9", stroke_width=14))
        body = _rr(2.0, 1.75, 0.32, PURPLE).move_to([0, -0.35, 0])
        rim = _rr(1.7, 0.12, 0.05, "#b9a3f0").move_to([0, 0.38, 0])
        self.eyes = _eyes((-0.38, 0.38), -0.05, r=0.2, pr=0.09, dx=0.0)
        self.brows = m.VGroup(m.Line([-0.58, 0.24, 0], [-0.18, 0.22, 0], color=BG, stroke_width=7),
                              m.Line([0.18, 0.22, 0], [0.58, 0.24, 0], color=BG, stroke_width=7))
        self.mouth = make_mouth("flat", [0, -0.45, 0], self.MOUTH_W, color=self.MOUTH_COLOR)
        self.keyhole = m.VGroup(
            m.Circle(radius=0.09, color=AMBER, fill_color=AMBER, fill_opacity=1, stroke_width=0).move_to([0, -0.78, 0]),
            m.Polygon([-0.06, -0.8, 0], [0.06, -0.8, 0], [0.09, -1.0, 0], [-0.09, -1.0, 0],
                      color=AMBER, fill_color=AMBER, fill_opacity=1, stroke_width=0))
        self.add(shackle, legs, arms, body, rim, self.eyes, self.brows, self.mouth, self.keyhole)
        self._done(scale)


# ---- the pair this video uses ----
LEAD, CHECK = Whizz, Latch
NAMES = {"LEAD": "Whizz", "CHECK": "Latch"}          # how the narration refers to them
