"""Shared building blocks for chapters: title card, evidence-label chips, source tags, lists, cards,
bars, stamps, and the reusable recall (quick-check) scene. Same look everywhere (style.py).

The title card and the recall scene's bridge use the project's two characters (characters.py:
LEAD and CHECK); without a characters.py they fall back to Chip and Brick.
"""
import sys

import numpy as np
import manimgx as m
from style import (BG, BG2, INK, MUTED, LINE, TEAL, PURPLE, AMBER, GREEN, RED, BLUE, PINK,
                   SAFE_X, SAFE_BOTTOM, txt, mono, term, panel, fit, heading)
from cast import Chip, Brick, Person, face, hop
from narrated import NarratedScene

# Evidence labels, as shown on screen next to a claim or a source tag (docs/STYLE.md).
# Add topic-specific ones in a chapter with LABELS["reviewer's estimate"] = PURPLE.
LABELS = {
    "verified": GREEN,
    "secondhand": BLUE,
    "a guess": AMBER,
    "unverified": RED,
    "estimate": PURPLE,
}


def cast_pair():
    """(LEAD, CHECK) character classes from the project's characters.py."""
    try:
        import characters
        return characters.LEAD, characters.CHECK
    except (ImportError, AttributeError):
        return Chip, Brick


def label_chip(kind, size=22):
    col = LABELS.get(kind, MUTED)
    t = txt(kind, size=size, color=BG, bold=True)
    box = m.RoundedRectangle(width=t.width + 0.28, height=t.height + 0.16, corner_radius=0.09,
                             color=col, fill_color=col, fill_opacity=1, stroke_width=0)
    t.move_to(box)
    return m.VGroup(box, t)


def src(source, label=None, row=0, max_w=10.5):
    """Small source tag ("Name, Mon D, YYYY") at the bottom right, just above the caption band, with an
    optional evidence label chip. row=1 sits one line up (for a second tag)."""
    t = txt(source, size=24, color=MUTED)
    g = m.VGroup(t, label_chip(label, 20)).arrange(m.RIGHT, buff=0.18) if label else m.VGroup(t)
    fit(g, max_w)
    g.move_to([SAFE_X - g.width / 2, SAFE_BOTTOM + 0.25 + row * 0.42, 0])
    return g


def tagged(text, label, size=30, color=INK, chip_size=20):
    """A line of text followed by its evidence label chip."""
    t = txt(text, size=size, color=color)
    return m.VGroup(t, label_chip(label, chip_size)).arrange(m.RIGHT, buff=0.22)


def bullets(items, size=34, color=INK, mark=AMBER, buff=0.3, mark_kind="dot"):
    """Left-aligned rows with a dot, check or x mark. Items are strings or mobjects."""
    from props import check, big_x
    rows = m.VGroup()
    for it in items:
        body = it if isinstance(it, m.Mobject) else txt(it, size=size, color=color)
        if mark_kind == "dot":
            mk = m.Dot(radius=0.07, color=mark)
        elif mark_kind == "check":
            mk = check(0.32, GREEN, 9)
        else:
            mk = big_x(0.28, RED, 9)
        rows.add(m.VGroup(mk, body).arrange(m.RIGHT, buff=0.25))
    rows.arrange(m.DOWN, aligned_edge=m.LEFT, buff=buff)
    return rows


def card(title, lines=(), color=TEAL, w=4.2, h=2.4, title_size=34, body_size=26, body_color=INK):
    """A panel with a coloured title and a few short lines."""
    box = panel(w, h, color=color)
    tt = txt(title, size=title_size, color=color, bold=True)
    fit(tt, w - 0.4)
    tt.move_to(box).align_to(box, m.UP).shift(m.DOWN * 0.3)
    g = m.VGroup(box, tt)
    y = tt.get_bottom()[1] - 0.25
    for ln in lines:
        b = ln if isinstance(ln, m.Mobject) else txt(ln, size=body_size, color=body_color)
        fit(b, w - 0.4)
        b.move_to([box.get_center()[0], y - b.height / 2, 0])
        y -= b.height + 0.16
        g.add(b)
    return g


def hbar(frac, w=6.0, h=0.5, color=TEAL, track=LINE):
    tr = m.RoundedRectangle(width=w, height=h, corner_radius=h / 2, color=track, fill_color=track,
                            fill_opacity=1, stroke_width=0)
    fw = max(h, w * frac)
    fl = m.RoundedRectangle(width=fw, height=h, corner_radius=h / 2, color=color, fill_color=color,
                            fill_opacity=1, stroke_width=0)
    fl.align_to(tr, m.LEFT)
    return m.VGroup(tr, fl)


def vbars(values, labels, colors, max_h=3.0, w=1.1, gap=0.7, fmt="{:g}%", size=30, label_size=24,
          vmax=None):
    """Vertical bar chart, bottoms aligned at y=0 (move the group afterwards)."""
    vmax = vmax or max(values)
    g = m.VGroup()
    for i, (v, lab, col) in enumerate(zip(values, labels, colors)):
        hgt = max(0.04, max_h * v / vmax)
        r = m.Rectangle(width=w, height=hgt, color=col, fill_color=col, fill_opacity=1, stroke_width=0)
        r.move_to([i * (w + gap), hgt / 2, 0])
        val = txt(fmt.format(v), size=size, color=col, bold=True).next_to(r, m.UP, buff=0.12)
        lb = txt(lab, size=label_size, color=INK)
        fit(lb, w + gap - 0.1)
        lb.next_to(r, m.DOWN, buff=0.15)
        g.add(m.VGroup(r, val, lb))
    return g


def stamp(text, color=RED, size=44, angle=0.12):
    t = txt(text, size=size, color=color, bold=True)
    b = m.RoundedRectangle(width=t.width + 0.5, height=t.height + 0.35, corner_radius=0.12, color=color,
                           stroke_width=7, fill_opacity=0)
    t.move_to(b)
    return m.VGroup(b, t).rotate(angle)


def doc_card(title="notes", w=3.4, h=4.2, color=INK):
    """A document page with a title and grey lines (stands for "the source" or any document)."""
    box = panel(w, h, color=LINE)
    tt = txt(title, size=28, color=color, bold=True).move_to(box).align_to(box, m.UP).shift(m.DOWN * 0.35)
    fit(tt, w - 0.4)
    lines = m.VGroup(*[m.Line([0, 0, 0], [ww, 0, 0], color=MUTED, stroke_width=5)
                       for ww in (2.6, 2.2, 2.5, 1.8, 2.4, 2.0, 2.3)])
    lines.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.32).next_to(tt, m.DOWN, buff=0.35)
    lines.align_to(box, m.LEFT).shift(m.RIGHT * 0.4)
    return m.VGroup(box, tt, lines)


def make_title(num, title, sub, kicker=None, name="sc00_title"):
    """The chapter title card scene (no narration; the audio mix puts the sting under it).

        Title = make_title(1, "How tides work", "the moon, the sun and a lot of water")
        Title = make_title("8A", "Topic title", "subtitle", kicker="TOPIC 8A")     # course packs
    """
    lead_cls, check_cls = cast_pair()
    kick = kicker or f"CHAPTER {num}"

    class Title(NarratedScene):
        NAME, CAPTIONS = name, False

        def body(self):
            n = txt(kick, size=40, color=AMBER, bold=True).move_to([0, 2.05, 0])
            t = fit(txt(title, size=80, color=INK, bold=True), 12.4).move_to([0, 0.75, 0])
            s = fit(txt(sub, size=38, color=MUTED), 12.0).move_to([0, -0.35, 0])
            a = lead_cls(0.62).move_to([-4.8, -2.05, 0])     # the title card has no captions,
            b = check_cls(0.62).move_to([4.8, -1.95, 0])     # so the pair may stand low
            line = m.Line([-3.2, 1.6, 0], [3.2, 1.6, 0], color=AMBER, stroke_width=5)
            self.cue(0.0, m.FadeIn(n, shift=m.DOWN * 0.3), m.Create(line), m.FadeIn(a, shift=m.RIGHT * 1.5),
                     m.FadeIn(b, shift=m.LEFT * 1.5), run_time=0.5)
            self.play(m.FadeIn(t, scale=1.15), run_time=0.6)
            self.play(m.FadeIn(s), run_time=0.5)
            self.play(a.animate.shift(m.UP * 0.25), rate_func=m.there_and_back, run_time=0.5)
            self.wait_to(self.dur - 0.6)
            self.clear_stage(run_time=0.5)

    Title.__name__ = f"Title{num}"
    Title.__qualname__ = Title.__name__
    Title.__module__ = sys._getframe(1).f_globals["__name__"]   # so vg.py finds it in the chapter
    return Title


class RecallScene(NarratedScene):
    """QUICK CHECK. Q = [(question_seg, answer_seg, question_text, answer_text), ...];
    BRIDGE = (seg, text) for the "Next: ..." card with both characters, or None.

    Give each question segment pause=3.0 in the segments file: the countdown ring fills that pause."""
    Q = []
    BRIDGE = None
    HEADER = "QUICK CHECK"
    COUNTDOWN = 3.0

    def body(self):
        hdr = term(self.HEADER, color=TEAL, size=40).move_to([0, 3.2, 0])
        shown = []
        for k, (qs, as_, qt, at) in enumerate(self.Q):
            if shown:
                self.cue(self.at(qs) - 0.25, *[m.FadeOut(x) for x in shown], run_time=0.3)
                shown = []
            q = fit(txt(qt, size=52, color=INK, bold=True), 12.6).move_to([0, 1.6, 0])
            if k == 0:
                self.cue(self.at(qs), m.FadeIn(hdr, scale=1.2), m.FadeIn(q, shift=m.UP * 0.3), run_time=0.5)
            else:
                self.cue(self.at(qs), m.FadeIn(q, shift=m.UP * 0.3), run_time=0.5)
            self.countdown(self.at(qs, end=True) + 0.1, self.COUNTDOWN, [0, -0.5, 0])
            a = fit(txt(at, size=40, color=GREEN), 12.4).move_to([0, -0.5, 0])
            self.cue(self.at(as_), m.FadeIn(a, shift=m.UP * 0.2), run_time=0.5)
            shown = [q, a]
        if self.BRIDGE:
            lead_cls, check_cls = cast_pair()
            bs, bt = self.BRIDGE
            self.cue(self.at(bs) - 0.25, *[m.FadeOut(x) for x in shown + [hdr]], run_time=0.3)
            a = lead_cls(0.8).move_to([-2.0, -0.8, 0])
            b = check_cls(0.8).move_to([2.0, -0.7, 0])
            up = fit(txt(bt, size=54, color=AMBER, bold=True), 12.6).move_to([0, 2.2, 0])
            self.cue(self.at(bs), m.FadeIn(a, shift=m.RIGHT), m.FadeIn(b, shift=m.LEFT), m.FadeIn(up),
                     run_time=0.6)
            self.play(face(a, "grin"), a.animate.shift(m.UP * 0.3), rate_func=m.there_and_back, run_time=0.5)


def arrow(a, b, color=LINE, sw=6, buff=0.1):
    return m.Arrow(np.array(a, dtype=float), np.array(b, dtype=float), buff=buff, color=color, stroke_width=sw)


def head(text, size=56, color=INK):
    """Top-of-screen heading, shrunk to fit the frame width."""
    return fit(heading(text, color=color, size=size), 13.2)


def figure(color, label, scale=1.0, size=26):
    """A plain person with the label under it."""
    p = Person(color, None, scale)
    lab = txt(label, size=size, color=color, bold=True).next_to(p, m.DOWN, buff=0.12)
    return m.VGroup(p, lab)


def magnifier(scale=1.0):
    g = m.VGroup(m.Circle(radius=0.36, color=INK, stroke_width=7),
                 m.Line([0.25, -0.25, 0], [0.62, -0.62, 0], color=INK, stroke_width=9))
    g.scale(scale)
    return g
