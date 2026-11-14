"""Base class for narrated scenes: timing lookup, cue scheduling, burnt-in captions, recall countdown.

Subclass, set NAME (the scene key used in script/chN_segments.py) and write body():

    class Hook(NarratedScene):
        NAME = "sc01_hook"
        def body(self):
            self.cue(self.at(1), m.FadeIn(chip))                  # when segment 1 starts
            self.cue(self.at(1, "homework"), m.Write(label))      # when a phrase is (about) spoken
            # finish() waits to the scene's measured end automatically

CHAPTER defaults to the chapter file's name (chapters/ch2.py -> "ch2"); set it only to override.
Times come from measured audio, so new narration re-times every cue. The background (flat colour +
two drifting glows) is composited by ffmpeg behind the scene (background.py), not drawn here.
"""
import pathlib
import sys

import manimgx as m
import timeline
from style import INK, setup_config, txt

setup_config()  # at import: the renderer sizes its frames before construct() runs

CAPTION_SIZE = 34
CAPTION_Y = -3.47
CAPTION_MAX_W = 13.2


class NarratedScene(m.Scene):
    CHAPTER = None
    NAME = None
    CAPTIONS = True
    FADE_OUT = True     # fade the stage out just before the scene ends

    # ---------- lifecycle ----------
    def construct(self):
        ch = self.CHAPTER or pathlib.Path(sys.modules[type(self).__module__].__file__).stem
        self.timing = timeline.load(ch)
        try:
            self.info = next(s for s in self.timing["scenes"] if s["name"] == self.NAME)
        except StopIteration:
            raise SystemExit(f"{type(self).__name__}: NAME {self.NAME!r} is not a scene in {ch}_timing.json")
        self.segs = {s["id"]: s for s in self.info["segments"]}
        self._started = False
        self._keep = []          # mobjects clear_stage() leaves alone (captions)
        if self.CAPTIONS and self.info["segments"]:
            self._add_captions()
        self.body()
        self.finish()

    def body(self):
        raise NotImplementedError

    def finish(self):
        # ManimGX writes one extra frame at the scene's end, so stop one frame early: the file then
        # lasts exactly info["dur"] seconds. Stop just before the last frame instant so float
        # rounding cannot add a frame.
        end = (round(self.info["dur"] * timeline.FPS) - 1) / timeline.FPS - 1e-4
        if self.FADE_OUT and _stage_mobs(self) and self.time < end - 0.45:
            self.wait(end - 0.45 - self.time)
            clear_stage(self, run_time=0.4)
        if self.time < end - 1e-6:
            self.wait(end - self.time)
        elif self.time > end + 1e-3:
            raise RuntimeError(f"{self.NAME}: animations run to {self.time:.2f}s, past the scene end {end:.2f}s")

    # ---------- timing ----------
    @property
    def dur(self):
        return self.info["dur"]

    def at(self, seg_id, phrase=None, offset=0.0, end=False):
        """Scene-relative time of segment seg_id's start (or end), or of a phrase inside it.

        Phrase times are estimated by character position in the spoken text (no word alignment),
        so cue on phrases near the start of a segment when exact sync matters.
        """
        if seg_id not in self.segs:
            raise ValueError(f"{self.NAME}: segment {seg_id} is not in this scene (has {sorted(self.segs)})")
        s = self.segs[seg_id]
        if end:
            return s["start"] + s["dur"] + offset
        if phrase is None:
            return s["start"] + offset
        text = s["say"]
        i = text.lower().find(phrase.lower())
        if i < 0:
            text = s["cap"]
            i = text.lower().find(phrase.lower())
        if i < 0:
            raise ValueError(f"phrase {phrase!r} not in segment {seg_id}")
        lead, tail = 0.08, 0.15
        frac = i / max(1, len(text))
        return s["start"] + lead + frac * (s["dur"] - lead - tail) + offset

    def cue(self, t, *anims, run_time=0.8, **kw):
        """Wait until scene time t, then play anims. Late cues play immediately.

        The scene's first cue always starts on frame 0, so no scene opens on an empty background.
        """
        if not self._started and anims:
            t = 0.0
        if t > self.time + 1e-6:
            self.wait(t - self.time)
        if anims:
            self.play(*anims, run_time=run_time, **kw)
            self._started = True

    def wait_to(self, t):
        if t > self.time + 1e-6:
            self.wait(t - self.time)

    # ---------- captions ----------
    def _add_captions(self):
        items = []
        for seg in self.info["segments"]:
            for a, b, text in seg["chunks"]:
                t = txt(text, size=CAPTION_SIZE, color=INK)
                if t.width > CAPTION_MAX_W:
                    t.scale_to_fit_width(CAPTION_MAX_W)
                t.move_to([0, CAPTION_Y, 0])
                band = m.RoundedRectangle(width=t.width + 0.7, height=0.78, corner_radius=0.16,
                                          stroke_width=0, fill_color="#000000", fill_opacity=0.62)
                band.move_to([0, CAPTION_Y, 0])
                band.set_fill(opacity=0)
                t.set_opacity(0)
                items.append((seg["start"] + a, seg["start"] + b, band, t))
        group = m.VGroup(*[x for it in items for x in it[2:]])
        state = {"cur": -1}
        sc = self

        def upd(_):
            now = sc.time
            idx = -1
            for k, (a, b, _band, _t) in enumerate(items):
                if a <= now < b:
                    idx = k
                    break
            if idx != state["cur"]:
                if state["cur"] >= 0:
                    _, _, band, t = items[state["cur"]]
                    band.set_fill(opacity=0)
                    t.set_opacity(0)
                if idx >= 0:
                    _, _, band, t = items[idx]
                    band.set_fill(opacity=0.62)
                    t.set_opacity(1)
                state["cur"] = idx

        group.add_updater(upd)
        self.add_foreground_mobjects(group)
        self._captions = group
        self._keep.append(group)


def countdown(scene, t_start, seconds, pos, radius=0.55, color=None):
    """Recall-question countdown: a ring that shrinks (clockwise from 12 o'clock) as the number
    counts down, then fades. Occupies [t_start, t_start + seconds]."""
    from style import AMBER, LINE
    import numpy as np
    color = color or AMBER
    pos = np.array(pos, dtype=float)
    base = m.Circle(radius=radius, color=LINE, stroke_width=10).move_to(pos)
    nums = [txt(str(k), size=48, color=color, bold=True).move_to(pos) for k in range(int(seconds), 0, -1)]
    state = {"t0": None}

    def arc_at(frac):
        frac = max(0.002, min(1.0, frac))
        return m.Arc(radius=radius, start_angle=m.PI / 2, angle=-2 * m.PI * frac, color=color,
                     stroke_width=10).shift(pos)

    ring = arc_at(1.0)

    def upd_ring(mob):
        if state["t0"] is None:
            return
        frac = 1 - (scene.time - state["t0"]) / seconds
        mob.become(arc_at(frac))

    num = nums[0].copy()

    def upd_num(mob):
        if state["t0"] is None:
            return
        k = min(len(nums) - 1, int((scene.time - state["t0"]) // 1))
        if getattr(mob, "_k", 0) != k:
            mob.become(nums[k])
            mob._k = k

    scene.cue(t_start, m.FadeIn(base), m.FadeIn(ring), m.FadeIn(num), run_time=0.2)
    state["t0"] = t_start
    ring.add_updater(upd_ring)
    num.add_updater(upd_num)
    end = t_start + seconds - 0.25
    if end > scene.time:
        scene.wait(end - scene.time)
    ring.clear_updaters()
    num.clear_updaters()
    scene.play(m.FadeOut(base), m.FadeOut(ring), m.FadeOut(num), run_time=0.25)


NarratedScene.countdown = countdown


def _stage_mobs(scene):
    keep = {id(x) for x in getattr(scene, "_keep", [])}
    return [x for x in scene.mobjects if id(x) not in keep]


def clear_stage(scene, run_time=0.6, shift=None):
    """Fade out everything except the captions."""
    mobs = _stage_mobs(scene)
    if mobs:
        kw = {"shift": shift} if shift is not None else {}
        scene.play(*[m.FadeOut(x, **kw) for x in mobs], run_time=run_time)


NarratedScene.clear_stage = clear_stage
