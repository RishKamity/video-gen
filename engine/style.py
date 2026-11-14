"""The locked house style: output format, palette, fonts, layout zones and small text helpers.

Frame (ManimGX units): x in [-7.11, 7.11], y in [-4, 4]; 1 unit = 180 px at 2560x1440.
The caption band owns y < CAPTION_TOP; keep all content above SAFE_BOTTOM.
See docs/STYLE.md for the rules that go with these values.
"""
import manimgx as m

# ---- output ----
WIDTH, HEIGHT, FPS = 2560, 1440, 30
CRF, PRESET = 18, "medium"

# ---- palette (dark theme) ----
BG = "#0f1220"         # background
BG2 = "#171b2e"        # panels, cards
INK = "#edeff7"        # main text
MUTED = "#8a91ad"      # secondary text, source tags
LINE = "#3a4163"       # outlines, arrows, tracks
TEAL = "#4fd1c5"       # first character (Chip) and the main accent
TEAL_D = "#2c8f87"
PURPLE = "#9f7aea"     # second character (Brick)
AMBER = "#f6c445"      # key terms, highlights, the recall countdown
GREEN = "#48bb78"      # yes / correct / verified / answers
RED = "#f56565"        # no / wrong / danger
BLUE = "#63b3ed"       # outside things, secondhand
PINK = "#f687b3"       # spare accent

FONT = "Noto Sans"            # ships with manimgx-fonts
MONO = "DejaVu Sans Mono"     # system font (fonts-dejavu)

# ---- layout ----
CAPTION_TOP = -2.95     # caption band top edge
SAFE_BOTTOM = -2.75     # lowest y any content may reach
SAFE_TOP = 3.75
SAFE_X = 6.7


def setup_config():
    m.config.background_color = BG
    m.config.pixel_width = WIDTH
    m.config.pixel_height = HEIGHT
    m.config.frame_rate = FPS


def txt(s, size=40, color=INK, bold=False, font=FONT, **kw):
    return m.Text(s, font=font, font_size=size, color=color,
                  weight="BOLD" if bold else "NORMAL", **kw)


def mono(s, size=34, color=INK, **kw):
    return m.Text(s, font=MONO, font_size=size, color=color, **kw)


def heading(s, color=INK, size=58):
    """Top-of-screen idea title."""
    t = txt(s, size=size, color=color, bold=True)
    t.move_to([0, 3.25, 0])
    return t


def term(word, color=AMBER, size=52):
    """A key-term pill: the word on a rounded tag. Appears when the word is spoken."""
    t = txt(word, size=size, color=BG, bold=True)
    box = m.RoundedRectangle(width=t.width + 0.6, height=t.height + 0.38, corner_radius=0.22,
                             color=color, fill_color=color, fill_opacity=1, stroke_width=0)
    t.move_to(box)
    return m.VGroup(box, t)


def panel(w, h, color=LINE, fill=BG2, r=0.25, sw=4):
    return m.RoundedRectangle(width=w, height=h, corner_radius=r, color=color,
                              fill_color=fill, fill_opacity=1, stroke_width=sw)


def source_tag(s):
    """Small source credit, bottom-right above the caption band (kit.src adds a label chip)."""
    t = txt(s, size=26, color=MUTED)
    t.move_to([SAFE_X - t.width / 2, SAFE_BOTTOM + 0.25, 0])
    return t


def fit(mob, max_w=2 * SAFE_X, max_h=None):
    if mob.width > max_w:
        mob.scale_to_fit_width(max_w)
    if max_h and mob.height > max_h:
        mob.scale_to_fit_height(max_h)
    return mob
