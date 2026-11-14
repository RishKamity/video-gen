"""Chapter 1: {{TITLE}}. One NarratedScene subclass per scene key in script/ch1_segments.py.

Copy this file to chapters/chN.py for each new chapter (the chapter id comes from the file name) and
add "chN" to project.json. House rules (docs/STYLE.md): one idea per screen, little text, content
above y = -2.75 (the caption band is below it), and every animation placed with
self.cue(self.at(segment_id, "spoken phrase"), ...), never at a hard-coded time.

Timing helpers (all in seconds from the start of the scene, all from the measured narration):
  self.at(2)                     segment 2 starts
  self.at(2, "recall")           about when "recall" is spoken in segment 2 (found in say, then cap)
  self.at(2, "recall", -0.2)     the same, 0.2 s earlier
  self.at(2, end=True)           segment 2's audio ends
  self.cue(t, anim, ...)         wait until t, then play; a late cue plays at once; the first cue starts at 0
  self.wait_to(t)                just wait until t
"""
import manimgx as m
from style import *            # noqa: F401,F403  palette (TEAL, AMBER, ...), txt, mono, term, heading, panel, fit
from props import *            # noqa: F401,F403  simple-shape props: terminal, file_icon, cloud, database, sign, ...
from kit import make_title, RecallScene, src, head, arrow, card, label_chip, tagged, bullets, stamp  # noqa: F401
from cast import face, hop
from narrated import NarratedScene
from characters import LEAD, CHECK     # this video's two characters (characters.py)

TITLE = ("sc00_title", 4.0)     # title card: scene name and seconds (no narration; the sting plays here)
OUT_NAME = "ch1_intro"          # the chapter's files: out/ch1_intro.mp4 and out/ch1_intro.srt

Title = make_title(1, "{{TITLE}}", "a one-line promise of what this chapter teaches")


class Idea(NarratedScene):
    NAME = "sc01_idea"

    def body(self):
        # segment 1, the hook. The first cue always starts on frame 0, so the screen is never empty.
        h = head("One idea per screen")
        lead = LEAD(0.75).move_to([-4.7, -0.55, 0])
        self.cue(self.at(1), m.FadeIn(h, shift=m.DOWN * 0.2), m.FadeIn(lead, shift=m.RIGHT), run_time=0.6)
        q = txt("?", size=120, color=AMBER, bold=True).next_to(lead, m.UP, buff=0.1)
        self.cue(self.at(1, "what if"), m.FadeIn(q, scale=1.5), face(lead, "o"), run_time=0.5)

        # a tiny diagram: the narrator says it, the screen shows it
        say = card("say it", ["the narrator"], color=TEAL, w=3.2, h=1.8).move_to([-0.6, 0.9, 0])
        show = card("show it", ["on screen"], color=AMBER, w=3.2, h=1.8).move_to([4.2, 0.9, 0])
        link = arrow(say.get_right(), show.get_left(), color=LINE)
        self.cue(self.at(1, "exactly one"), m.FadeOut(q), m.FadeIn(say), run_time=0.5)
        self.cue(self.at(1, "the rule"), m.GrowArrow(link), m.FadeIn(show, shift=m.LEFT * 0.3), run_time=0.6)

        # segment 2: the key term appears as a pill when it is spoken
        pill = term("recall", color=AMBER, size=48).move_to([1.8, -1.0, 0])
        self.cue(self.at(2, "recall"), m.FadeIn(pill, scale=1.3), face(lead, "grin"), run_time=0.5)

        # the second character checks; a source tag (bottom right) carries an evidence label
        check = CHECK(0.7).move_to([4.9, -0.75, 0])
        self.cue(self.at(2, "Chip tries"), hop(lead), run_time=0.5)
        self.cue(self.at(2, "Brick checks"), m.FadeOut(show), m.FadeOut(link),
                 m.FadeIn(check, shift=m.LEFT), run_time=0.6)
        ok = sign("CHECKED", GREEN, 0.6).next_to(check, m.UP, buff=0.15)
        tag = src("Source name, Mon D, YYYY", "verified")
        self.cue(self.at(2, end=True) - 0.6, m.FadeIn(ok, shift=m.UP * 0.2), m.FadeIn(tag), run_time=0.4)
        # finish() fades the stage and waits to the scene's measured end


class Recall(RecallScene):
    """Two recall questions, then the bridge. Q = (question segment, answer segment, question, answer).
    Each question segment has pause=3.0 in the segments file; the countdown ring fills it."""
    NAME = "sc02_recall"
    Q = [(3, 4, "1. What does a term pill do?", "Shows the key word the moment it's said."),
         (5, 6, "2. How many ideas go on one screen?", "One.")]
    BRIDGE = (7, "Next: Chapter 2")
