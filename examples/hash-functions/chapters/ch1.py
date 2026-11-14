"""Chapter 1: What's a hash function? One NarratedScene subclass per scene key in script/ch1_segments.py.

House rules (docs/STYLE.md): one idea per screen, little text, content above y = -2.75, and every
animation placed with self.cue(self.at(segment_id, "spoken phrase"), ...), never at a hard-coded time.
The SHA-256 values on screen are real (sources/sha256_demo.md).
"""
import manimgx as m
from style import *            # noqa: F401,F403  palette (TEAL, AMBER, ...), txt, mono, term, heading, panel, fit
from props import *            # noqa: F401,F403  simple-shape props: file_icon, database, sign, big_x, check, ...
from kit import make_title, RecallScene, src, arrow, card, tagged, stamp  # noqa: F401
from cast import face, hop
from narrated import NarratedScene
from characters import LEAD, CHECK     # Whizz (blender) and Latch (padlock)

TITLE = ("sc00_title", 4.0)     # title card: scene name and seconds (no narration; the sting plays here)
OUT_NAME = "ch1_hash_functions"  # out/ch1_hash_functions.mp4 and .srt

Title = make_title(1, "What's a hash function?", "a fingerprint for any data")

CAT = "77af778b51abd4a3…"      # SHA-256("cat"), first 16 of 64 hex characters
CATS = "d936608baaacc6b7…"     # SHA-256("cats")


def chip(s, color=INK, size=34, w=None):
    """A short input word on a small panel."""
    t = txt(s, size=size, color=color, bold=True)
    box = panel(w or t.width + 0.6, t.height + 0.45, color=color)
    t.move_to(box)
    return m.VGroup(box, t)


def code(s, color=AMBER, size=32):
    """A hash value in monospace on a dark panel."""
    t = mono(s, size=size, color=color)
    box = panel(t.width + 0.6, t.height + 0.5, color=color, fill="#0a0c16")
    t.move_to(box)
    return m.VGroup(box, t)


def smoothie(scale=1.0):
    cup = m.Polygon([-0.42, -0.6, 0], [0.42, -0.6, 0], [0.55, 0.55, 0], [-0.55, 0.55, 0],
                    color=PINK, fill_color=PINK, fill_opacity=0.85, stroke_width=0)
    lid = m.RoundedRectangle(width=1.25, height=0.18, corner_radius=0.08, color=INK, fill_color=INK,
                             fill_opacity=1, stroke_width=0).move_to([0, 0.62, 0])
    straw = m.Line([0.15, 0.62, 0], [0.4, 1.25, 0], color=AMBER, stroke_width=10)
    g = m.VGroup(straw, cup, lid)
    g.scale(scale)
    return g


class Hook(NarratedScene):
    NAME = "sc01_hook"

    def body(self):
        login = card("Log in", ["username: student42", "password: ••••••••"],
                     color=BLUE, w=5.0, h=2.5, title_size=40, body_size=32).move_to([-3.6, 0.7, 0])
        latch = CHECK(0.72).move_to([1.0, -0.55, 0])
        self.cue(self.at(1), m.FadeIn(login, shift=m.RIGHT * 0.3), m.FadeIn(latch, shift=m.LEFT * 0.5),
                 run_time=0.6)
        db = database(1.1, BLUE).move_to([4.7, 0.9, 0])
        lab = txt("no passwords stored", size=30, color=MUTED).next_to(db, m.DOWN, buff=0.3)
        self.cue(self.at(1, "without storing"), m.FadeIn(db, shift=m.UP * 0.2), m.FadeIn(lab), run_time=0.5)
        pill = term("hash function", size=52).move_to([-3.6, -1.35, 0])
        self.cue(self.at(1, "thanks to", -0.2), m.FadeIn(pill, scale=1.2), face(latch, "smile"), run_time=0.5)


class Fingerprint(NarratedScene):
    NAME = "sc02_fingerprint"

    def body(self):
        whizz = LEAD(0.82).move_to([-5.2, -0.55, 0])
        top = term("hash function", size=46).move_to([0, 3.15, 0])
        self.cue(self.at(2), m.FadeIn(top, scale=1.2), m.FadeIn(whizz, shift=m.RIGHT), run_time=0.6)
        self.cue(self.at(2, "whizz"), hop(whizz), run_time=0.5)

        cat = chip("cat").move_to([-5.2, 2.15, 0])
        self.cue(self.at(2, "any input"), m.FadeIn(cat, shift=m.DOWN * 0.3), run_time=0.4)
        self.play(cat.animate.move_to(whizz.get_center() + m.UP * 0.2).scale(0.3).set_opacity(0), run_time=0.5)
        movie = file_icon("movie.mp4", BLUE).move_to([-5.2, 2.0, 0])
        self.cue(self.at(2, "whole movie"), m.FadeIn(movie, shift=m.DOWN * 0.3), run_time=0.4)
        self.play(movie.animate.move_to(whizz.get_center() + m.UP * 0.2).scale(0.3).set_opacity(0), run_time=0.5)

        out = code(CAT, size=36).move_to([2.2, 0.6, 0])
        lab = txt("SHA-256 of \"cat\"", size=28, color=MUTED).next_to(out, m.UP, buff=0.25)
        link = arrow(whizz.get_right() + m.RIGHT * 0.1, out.get_left() + m.LEFT * 0.1, color=LINE)
        self.cue(self.at(2, "into a short"), m.GrowArrow(link), m.FadeIn(out, shift=m.RIGHT * 0.3), m.FadeIn(lab),
                 face(whizz, "grin"), run_time=0.6)
        size = txt("SHA-256: always 64 characters", size=34, color=AMBER, bold=True).next_to(out, m.DOWN, buff=0.35)
        self.cue(self.at(2, "fixed-length", -0.3), m.FadeIn(size, shift=m.UP * 0.2), run_time=0.5)

        # segment 3: same in -> same out; one letter more -> totally different
        rows_x, in_x = 2.3, -2.6
        r1_in = chip("cat", size=32, w=1.7).move_to([in_x, 1.55, 0])
        r1_out = code(CAT, size=30).move_to([rows_x, 1.55, 0])
        r1_ar = arrow(r1_in.get_right(), r1_out.get_left(), color=LINE)
        self.cue(self.at(3), m.FadeOut(out), m.FadeOut(lab), m.FadeOut(link), m.FadeOut(size),
                 m.FadeIn(r1_in), m.GrowArrow(r1_ar), m.FadeIn(r1_out), run_time=0.5)
        r2_in = chip("cat", size=32, w=1.7).move_to([in_x, 0.35, 0])
        r2_out = code(CAT, size=30).move_to([rows_x, 0.35, 0])
        r2_ar = arrow(r2_in.get_right(), r2_out.get_left(), color=LINE)
        ok = m.VGroup(check(0.42, GREEN, 10), txt("same", size=30, color=GREEN, bold=True)).arrange(m.RIGHT, buff=0.15)
        ok.next_to(r2_out, m.RIGHT, buff=0.3)
        self.cue(self.at(3, "same code"), m.FadeIn(r2_in), m.GrowArrow(r2_ar), m.FadeIn(r2_out), run_time=0.5)
        self.play(m.FadeIn(ok, scale=1.2), run_time=0.3)
        fp = term("fingerprint", size=36).move_to([-5.25, 2.4, 0])
        self.cue(self.at(3, "a fingerprint"), m.FadeIn(fp, scale=1.2), run_time=0.5)
        r3_in = chip("cats", color=RED, size=32, w=1.7).move_to([in_x, -0.85, 0])
        r3_out = code(CATS, color=RED, size=30).move_to([rows_x, -0.85, 0])
        r3_ar = arrow(r3_in.get_right(), r3_out.get_left(), color=LINE)
        bad = txt("totally different", size=30, color=RED, bold=True).next_to(r3_out, m.DOWN, buff=0.25)
        self.cue(self.at(3, "cat to cats"), m.FadeIn(r3_in), run_time=0.4)
        self.cue(self.at(3, "and it totally", -0.3), m.GrowArrow(r3_ar), m.FadeIn(r3_out), m.FadeIn(bad),
                 face(whizz, "o"), run_time=0.5)


class OneWay(NarratedScene):
    NAME = "sc03_oneway"

    def body(self):
        top = term("one-way", size=46).move_to([0, 3.15, 0])
        c_in = chip("input", size=34).move_to([-3.4, 1.3, 0])
        c_out = code("fingerprint", size=36).move_to([2.6, 1.3, 0])
        fwd = arrow(c_in.get_right(), c_out.get_left(), color=GREEN, sw=8)
        easy = txt("easy", size=28, color=GREEN, bold=True).next_to(fwd, m.UP, buff=0.12)
        self.cue(self.at(4), m.FadeIn(top, scale=1.2), m.FadeIn(c_in), m.GrowArrow(fwd), m.FadeIn(easy),
                 m.FadeIn(c_out), run_time=0.6)
        back = arrow([c_out.get_left()[0], 0.3, 0], [c_in.get_right()[0], 0.3, 0], color=RED, sw=8)
        x = big_x(0.55, RED, 12).move_to(back.get_center())
        nope = txt("no practical way to run it backwards", size=30, color=RED, bold=True).next_to(back, m.DOWN, buff=0.3)
        self.cue(self.at(4, "no practical"), m.GrowArrow(back), run_time=0.5)
        self.play(m.FadeIn(x, scale=1.3), m.FadeIn(nope), run_time=0.4)
        whizz = LEAD(0.6).move_to([-5.3, -1.1, 0])
        cup = smoothie(0.9).move_to([-3.6, -1.45, 0])
        q = txt("un-blend?", size=30, color=PINK, bold=True).next_to(cup, m.RIGHT, buff=0.3)
        self.cue(self.at(4, "like un-blending", -0.3), m.FadeIn(whizz, shift=m.RIGHT), m.FadeIn(cup, shift=m.UP * 0.2),
                 m.FadeIn(q), run_time=0.5)
        self.play(face(whizz, "worried"), run_time=0.3)

        # segment 5: store only the fingerprint; hash each login attempt and compare
        self.cue(self.at(5) - 0.25, *[m.FadeOut(mob) for mob in (top, c_in, c_out, fwd, easy, back, x, nope, cup, q)],
                 whizz.animate.scale(0.9).move_to([-2.65, 0.05, 0]), run_time=0.4)
        db = database(0.95, BLUE).move_to([3.4, 1.0, 0])
        db_lab = txt("stored: fingerprint only", size=26, color=MUTED).next_to(db, m.DOWN, buff=0.25)
        tag = src("OWASP Password Storage Cheat Sheet; WashU InfoSec, Oct 27, 2022", "verified")
        self.cue(self.at(5), face(whizz, "smile"), m.FadeIn(db, shift=m.UP * 0.2), m.FadeIn(db_lab), m.FadeIn(tag),
                 run_time=0.5)
        note = tagged("guessable passwords can still be guessed, so sites use slow hashes like bcrypt", "verified", size=26)
        fit(note, 12.4).move_to([0, -1.88, 0])
        self.cue(self.at(5, "fingerprint"), m.FadeIn(note), run_time=0.4)
        typed = card("login", ["\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022"], color=INK, w=2.5, h=1.6,
                     title_size=30, body_size=34).move_to([-5.3, 0.6, 0])
        a1 = arrow(typed.get_right(), [-3.3, 0.45, 0], color=LINE)
        fp = term("fingerprint", size=34).move_to([0.15, 0.95, 0])
        a2 = arrow([-1.95, 0.6, 0], fp.get_left(), color=LINE)
        self.cue(self.at(5, "then hash", -0.3), m.FadeIn(typed, shift=m.RIGHT * 0.3), m.GrowArrow(a1), run_time=0.4)
        self.cue(self.at(5, "each login"), m.GrowArrow(a2), m.FadeIn(fp, scale=1.2), hop(whizz), run_time=0.5)
        eq = txt("=", size=72, color=GREEN, bold=True).move_to([(fp.get_right()[0] + db.get_left()[0]) / 2, 0.95, 0])
        latch = CHECK(0.5).move_to([6.0, -0.6, 0])
        ok = sign("MATCH", GREEN, 0.5).move_to([6.0, 0.8, 0])
        self.cue(self.at(5, "try and", -0.2), m.FadeIn(eq, scale=1.3), m.FadeIn(latch, shift=m.LEFT * 0.4),
                 m.FadeIn(ok, shift=m.UP * 0.2), run_time=0.4)
        self.play(face(latch, "smile"), run_time=0.3)


class Collision(NarratedScene):
    NAME = "sc04_collision"

    def body(self):
        top = term("collision", color=RED, size=46).move_to([0, 3.15, 0])
        a = chip("input A", color=BLUE, size=32).move_to([-4.3, 1.55, 0])
        b = chip("input B", color=PINK, size=32).move_to([-4.3, -0.35, 0])
        self.cue(self.at(6), m.FadeIn(top, scale=1.2), run_time=0.5)
        self.cue(self.at(6, "two different"), m.FadeIn(a, shift=m.RIGHT * 0.3), m.FadeIn(b, shift=m.RIGHT * 0.3),
                 run_time=0.5)
        fp = code("same fingerprint", color=AMBER, size=34).move_to([2.4, 0.6, 0])
        aa = arrow(a.get_right(), fp.get_left() + m.UP * 0.15, color=BLUE)
        bb = arrow(b.get_right(), fp.get_left() + m.DOWN * 0.15, color=PINK)
        self.cue(self.at(6, "one fingerprint"), m.GrowArrow(aa), m.GrowArrow(bb), m.FadeIn(fp, scale=1.15),
                 run_time=0.6)
        good = txt("good hashes: practically impossible to find", size=32, color=GREEN, bold=True).move_to([0, -1.55, 0])
        tag = src("NIST glossary, from SP 800-107 Rev. 1", "verified")
        self.cue(self.at(6, "good hashes"), m.FadeIn(good, shift=m.UP * 0.2), m.FadeIn(tag), run_time=0.5)

        # segment 7: the real SHA-1 collision (2017)
        self.cue(self.at(7) - 0.25, *[m.FadeOut(x) for x in (a, b, aa, bb, fp, good, tag, top)], run_time=0.35)
        yr = term("2017", size=46).move_to([-1.6, 3.15, 0])
        algo = term("SHA-1", color=RED, size=46).next_to(yr, m.RIGHT, buff=0.4)
        self.cue(self.at(7), m.FadeIn(yr, scale=1.2), m.FadeIn(algo, scale=1.2), run_time=0.5)
        p1 = file_icon("PDF 1", BLUE, 1.15).move_to([-4.4, 1.25, 0])
        p2 = file_icon("PDF 2", PINK, 1.15).move_to([-4.4, -0.85, 0])
        self.cue(self.at(7, "found one"), m.FadeIn(p1, shift=m.RIGHT * 0.3), m.FadeIn(p2, shift=m.RIGHT * 0.3),
                 run_time=0.5)
        same = code("same SHA-1 hash", color=RED, size=34).move_to([1.4, 0.25, 0])
        a1 = arrow(p1.get_right(), same.get_left() + m.UP * 0.15, color=BLUE)
        a2 = arrow(p2.get_right(), same.get_left() + m.DOWN * 0.15, color=PINK)
        self.cue(self.at(7, "two different"), m.GrowArrow(a1), m.GrowArrow(a2), m.FadeIn(same, scale=1.15),
                 run_time=0.5)
        st = stamp("COLLISION FOUND", RED, 40).move_to([1.4, 1.75, 0])
        latch = CHECK(0.5).move_to([5.6, 0.15, 0])
        t1 = src("Google Security Blog, Feb 23, 2017", "verified", row=1)
        t2 = src("NIST: phase SHA-1 out by Dec 31, 2030 (Dec 15, 2022)", "verified")
        self.cue(self.at(7, "two different", 0.3), m.FadeIn(st, scale=1.3), m.FadeIn(latch, shift=m.LEFT * 0.4),
                 m.FadeIn(t1), m.FadeIn(t2), run_time=0.5)
        self.play(face(latch, "o"), run_time=0.3)


class Recall(RecallScene):
    """Two recall questions, then the sign-off (this is the last chapter)."""
    NAME = "sc05_recall"
    Q = [(8, 9, "1. Can a site reverse your password's hash?", "No. Sites just compare fingerprints."),
         (10, 11, "2. What's a collision?", "Two different inputs, same hash.")]
    BRIDGE = (12, "That's hashing!")
