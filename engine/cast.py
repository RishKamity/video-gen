"""Character library: original recurring characters built from simple shapes.

A video uses two of them, picked in the project's characters.py (LEAD = the one who acts,
CHECK = the one who checks). Every character follows the same small interface so the shared title
card and recall scene can use any pair:

    c = Chip(scale)                 # feet at the bottom, about 3.4 units tall at scale 1
    c.mouth                         # the mouth mobject (animate with Transform)
    c.mouth_to("grin")              # a new mouth: smile, grin, o (shocked), worried, flat
    face(c, "o")                    # = m.Transform(c.mouth, c.mouth_to("o"))
    hop(c)                          # a small jump (use as an animation)

Included:
  Chip   - an overeager robot intern. Teal. Parts: eyes, mouth, arm_l, arm_r, antenna_ball, badge.
  Brick  - a calm bouncer in dark glasses. Purple. Parts: glasses, mouth, arms. tag= sets his shirt word.
  Person - a plain generic human (head + body), for extras.

To draw a new character, subclass Character (docs/STYLE.md, "New characters"): build it from
rounded rectangles, circles and lines in the palette, set self.mouth, MOUTH_W and MOUTH_COLOR,
and finish __init__ with self._done(scale). No brands, logos, real people or existing characters.
"""
import numpy as np
import manimgx as m
from style import TEAL, TEAL_D, PURPLE, AMBER, BG, INK, txt


def make_mouth(kind, center, width, color=INK, sw=6):
    c = np.array(center, dtype=float)
    w = width
    if kind == "smile":
        return m.ArcBetweenPoints(c + [-w / 2, 0.04, 0], c + [w / 2, 0.04, 0], angle=m.PI * 0.6,
                                  color=color, stroke_width=sw).move_to(c)
    if kind == "grin":   # big open smile
        arc = m.ArcBetweenPoints(c + [-w / 2, 0, 0], c + [w / 2, 0, 0], angle=m.PI,
                                 color=color, stroke_width=sw)
        shape = m.VGroup(arc, m.Line(c + [-w / 2, 0, 0], c + [w / 2, 0, 0], color=color, stroke_width=sw))
        return shape.move_to(c)
    if kind == "o":      # shocked
        return m.Circle(radius=w * 0.18, color=color, stroke_width=sw).move_to(c)
    if kind == "worried":
        return m.ArcBetweenPoints(c + [-w / 2, -0.03, 0], c + [w / 2, -0.03, 0], angle=m.PI * 0.5,
                                  color=color, stroke_width=sw).flip(m.RIGHT).move_to(c)
    # flat
    return m.Line(c + [-w / 2, 0, 0], c + [w / 2, 0, 0], color=color, stroke_width=sw)


class Character(m.VGroup):
    """Base for recurring characters. Subclasses draw parts, set self.mouth, then call _done(scale)."""
    MOUTH_W = 0.4
    MOUTH_COLOR = INK
    COLOR = TEAL           # the character's signature colour (used for name labels)

    def _done(self, scale):
        self._h0 = self.height       # unscaled height, so mouth_to works after any later .scale()
        self.scale(scale)

    @property
    def size(self):
        return self.height / self._h0

    def mouth_to(self, kind):
        """A new mouth of this kind at the current mouth position (use with Transform)."""
        s = self.size
        return make_mouth(kind, self.mouth.get_center(), self.MOUTH_W * s, color=self.MOUTH_COLOR, sw=6 * s)


def face(char, kind, **kw):
    return m.Transform(char.mouth, char.mouth_to(kind), **kw)


def hop(char, height=0.3):
    return char.animate(rate_func=m.there_and_back).shift(m.UP * height)


class Chip(Character):
    """Robot intern. Height about 3.4 units at scale 1, feet at the bottom."""
    MOUTH_W = 0.42
    COLOR = TEAL
    DARK = "#163a3a"

    def __init__(self, scale=1.0, badge="INTERN"):
        super().__init__()
        head = m.RoundedRectangle(width=1.7, height=1.3, corner_radius=0.32, color=TEAL,
                                  fill_color=TEAL, fill_opacity=1, stroke_width=0)
        head.move_to([0, 0.9, 0])
        screen = m.RoundedRectangle(width=1.34, height=0.9, corner_radius=0.22, color=self.DARK,
                                    fill_color=self.DARK, fill_opacity=1, stroke_width=0).move_to(head)
        eye_l = m.Circle(radius=0.15, color=INK, fill_color=INK, fill_opacity=1, stroke_width=0).move_to([-0.3, 1.0, 0])
        eye_r = eye_l.copy().move_to([0.3, 1.0, 0])
        pup_l = m.Circle(radius=0.07, color=BG, fill_color=BG, fill_opacity=1, stroke_width=0).move_to([-0.27, 0.98, 0])
        pup_r = pup_l.copy().move_to([0.33, 0.98, 0])
        self.eyes = m.VGroup(eye_l, eye_r, pup_l, pup_r)
        self.mouth = make_mouth("smile", [0, 0.68, 0], self.MOUTH_W)
        ear_l = m.RoundedRectangle(width=0.16, height=0.5, corner_radius=0.06, color=TEAL_D,
                                   fill_color=TEAL_D, fill_opacity=1, stroke_width=0).move_to([-0.93, 0.9, 0])
        ear_r = ear_l.copy().move_to([0.93, 0.9, 0])
        stalk = m.Line([0, 1.55, 0], [0, 1.95, 0], color=TEAL_D, stroke_width=8)
        self.antenna_ball = m.Circle(radius=0.12, color=AMBER, fill_color=AMBER, fill_opacity=1,
                                     stroke_width=0).move_to([0, 2.0, 0])
        neck = m.Rectangle(width=0.3, height=0.16, color=TEAL_D, fill_color=TEAL_D, fill_opacity=1,
                           stroke_width=0).move_to([0, 0.18, 0])
        body = m.RoundedRectangle(width=1.25, height=1.05, corner_radius=0.22, color=TEAL_D,
                                  fill_color=TEAL_D, fill_opacity=1, stroke_width=0).move_to([0, -0.45, 0])
        self.arm_l = m.VGroup(
            m.Line([-0.62, -0.15, 0], [-1.0, -0.75, 0], color=TEAL_D, stroke_width=14),
            m.Circle(radius=0.13, color=TEAL, fill_color=TEAL, fill_opacity=1, stroke_width=0).move_to([-1.0, -0.8, 0]))
        self.arm_r = m.VGroup(
            m.Line([0.62, -0.15, 0], [1.0, -0.75, 0], color=TEAL_D, stroke_width=14),
            m.Circle(radius=0.13, color=TEAL, fill_color=TEAL, fill_opacity=1, stroke_width=0).move_to([1.0, -0.8, 0]))
        leg_l = m.RoundedRectangle(width=0.26, height=0.5, corner_radius=0.1, color=TEAL_D,
                                   fill_color=TEAL_D, fill_opacity=1, stroke_width=0).move_to([-0.3, -1.2, 0])
        leg_r = leg_l.copy().move_to([0.3, -1.2, 0])
        parts = [stalk, self.antenna_ball, ear_l, ear_r, head, screen, self.eyes, self.mouth,
                 neck, leg_l, leg_r, body, self.arm_l, self.arm_r]
        self.badge = None
        if badge:
            cord = m.VMobject(color=AMBER, stroke_width=4)
            cord.set_points_as_corners([[-0.3, 0.1, 0], [0, -0.35, 0], [0.3, 0.1, 0]])
            card = m.RoundedRectangle(width=0.95, height=0.44, corner_radius=0.06, color=INK,
                                      fill_color=INK, fill_opacity=1, stroke_width=0).move_to([0, -0.52, 0])
            lab = txt(badge, size=18, color=BG, bold=True).move_to(card)
            if lab.width > 0.85:
                lab.scale_to_fit_width(0.85)
            self.badge = m.VGroup(cord, card, lab)
            parts.append(self.badge)
        self.add(*parts)
        self._done(scale)


class Brick(Character):
    """The bouncer: dark glasses, earpiece, folded arms. Height about 3.6 units at scale 1."""
    MOUTH_W = 0.36
    MOUTH_COLOR = "#3b2d63"
    COLOR = PURPLE
    SKIN = "#b9a3f0"     # lavender: deliberately not a human skin tone
    SHIRT = "#22243a"

    def __init__(self, scale=1.0, tag="STAFF"):
        super().__init__()
        body = m.RoundedRectangle(width=2.7, height=2.0, corner_radius=0.55, color=PURPLE,
                                  fill_color=self.SHIRT, fill_opacity=1, stroke_width=6).move_to([0, -0.55, 0])
        head = m.RoundedRectangle(width=1.35, height=1.3, corner_radius=0.45, color=self.SKIN,
                                  fill_color=self.SKIN, fill_opacity=1, stroke_width=0).move_to([0, 1.05, 0])
        lens_l = m.RoundedRectangle(width=0.5, height=0.26, corner_radius=0.09, color="#0b0c14",
                                    fill_color="#0b0c14", fill_opacity=1, stroke_width=0).move_to([-0.3, 1.15, 0])
        lens_r = lens_l.copy().move_to([0.3, 1.15, 0])
        bridge = m.Line([-0.05, 1.18, 0], [0.05, 1.18, 0], color="#0b0c14", stroke_width=6)
        shine = m.Line([-0.45, 1.2, 0], [-0.36, 1.25, 0], color=INK, stroke_width=3)
        self.glasses = m.VGroup(lens_l, lens_r, bridge, shine)
        self.mouth = make_mouth("flat", [0, 0.72, 0], self.MOUTH_W, color=self.MOUTH_COLOR)
        ear = m.Circle(radius=0.08, color="#0b0c14", fill_color="#0b0c14", fill_opacity=1,
                       stroke_width=0).move_to([0.7, 1.0, 0])
        wire = m.VMobject(color="#0b0c14", stroke_width=3)
        wire.set_points_smoothly([[0.72, 0.93, 0], [0.8, 0.7, 0], [0.7, 0.5, 0], [0.85, 0.3, 0]])
        parts = []
        if tag:
            t = txt(tag, size=22, color=PURPLE, bold=True).move_to([0, 0.0, 0])
            if t.width > 1.6:
                t.scale_to_fit_width(1.6)
            parts.append(t)
        fore_l = m.RoundedRectangle(width=1.75, height=0.46, corner_radius=0.23, color="#8f78d6",
                                    fill_color=self.SKIN, fill_opacity=1, stroke_width=4).rotate(0.12).move_to([-0.3, -0.72, 0])
        fore_r = m.RoundedRectangle(width=1.75, height=0.46, corner_radius=0.23, color="#8f78d6",
                                    fill_color=self.SKIN, fill_opacity=1, stroke_width=4).rotate(-0.12).move_to([0.3, -0.66, 0])
        self.arms = m.VGroup(fore_l, fore_r)
        leg_l = m.RoundedRectangle(width=0.45, height=0.45, corner_radius=0.12, color=self.SHIRT,
                                   fill_color=self.SHIRT, fill_opacity=1, stroke_width=0).move_to([-0.5, -1.72, 0])
        leg_r = leg_l.copy().move_to([0.5, -1.72, 0])
        self.add(leg_l, leg_r, body, *parts, self.arms, head, self.glasses, self.mouth, ear, wire)
        self._done(scale)


class Person(m.VGroup):
    """Generic simple human (head + body) for extras: a student, a customer, a crowd."""

    def __init__(self, color=AMBER, label=None, scale=1.0):
        super().__init__()
        head = m.Circle(radius=0.42, color=color, fill_color=color, fill_opacity=1, stroke_width=0).move_to([0, 0.75, 0])
        body = m.RoundedRectangle(width=1.3, height=1.1, corner_radius=0.5, color=color,
                                  fill_color=color, fill_opacity=0.85, stroke_width=0).move_to([0, -0.3, 0])
        self.add(body, head)
        if label:
            t = txt(label, size=30, color=BG, bold=True).move_to(body)
            self.add(t)
        self.scale(scale)


LIBRARY = {"Chip": Chip, "Brick": Brick}
