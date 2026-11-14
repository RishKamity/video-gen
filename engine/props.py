"""Reusable simple-shape props (no logos, no brands). All return VGroups you can scale and move.

terminal, file_icon, folder_icon, server_rack, cloud, gpu_chip, building, keycard, door,
speech_bubble, big_x, check, dollar, wifi_bars, book, database, sign (a word on a paddle board).
"""
import numpy as np
import manimgx as m
from style import (BG, BG2, INK, MUTED, LINE, TEAL, PURPLE, AMBER, GREEN, RED, BLUE, PINK,
                   txt, mono, panel)


def terminal(lines=(), w=7.0, h=3.2, size=30):
    """A terminal window: title bar with three dots, monospace lines. Returns (group, line_mobs)."""
    frame = panel(w, h, color=LINE, fill="#0a0c16")
    bar = m.RoundedRectangle(width=w, height=0.42, corner_radius=0.2, color=LINE, fill_color=LINE,
                             fill_opacity=1, stroke_width=0).align_to(frame, m.UP)
    dots = m.VGroup(*[m.Circle(radius=0.07, color=c, fill_color=c, fill_opacity=1, stroke_width=0)
                      for c in (RED, AMBER, GREEN)]).arrange(m.RIGHT, buff=0.14)
    dots.move_to(bar).align_to(bar, m.LEFT).shift(m.RIGHT * 0.25)
    title = txt("terminal", size=20, color=MUTED).move_to(bar)
    g = m.VGroup(frame, bar, dots, title)
    mobs = []
    y = frame.get_top()[1] - 0.75
    for s, col in lines:
        t = mono(s, size=size, color=col)
        t.move_to([frame.get_left()[0] + 0.35 + t.width / 2, y, 0])
        mobs.append(t)
        y -= 0.55
    return g, mobs


def file_icon(label, color=BLUE, scale=1.0):
    """Page with a folded corner and a label under it."""
    w, h, f = 0.9, 1.15, 0.28
    page = m.Polygon([-w / 2, h / 2, 0], [w / 2 - f, h / 2, 0], [w / 2, h / 2 - f, 0],
                     [w / 2, -h / 2, 0], [-w / 2, -h / 2, 0],
                     color=color, fill_color=color, fill_opacity=0.25, stroke_width=4)
    fold = m.Polygon([w / 2 - f, h / 2, 0], [w / 2 - f, h / 2 - f, 0], [w / 2, h / 2 - f, 0],
                     color=color, fill_color=color, fill_opacity=0.8, stroke_width=3)
    lines = m.VGroup(*[m.Line([-0.28, y, 0], [0.28, y, 0], color=color, stroke_width=4)
                       for y in (0.12, -0.08, -0.28)])
    lab = txt(label, size=26, color=INK).next_to(page, m.DOWN, buff=0.15)
    g = m.VGroup(page, fold, lines, lab)
    g.scale(scale)
    return g


def folder_icon(label, color=AMBER, scale=1.0):
    tab = m.RoundedRectangle(width=0.55, height=0.3, corner_radius=0.08, color=color,
                             fill_color=color, fill_opacity=0.9, stroke_width=0).move_to([-0.35, 0.45, 0])
    body = m.RoundedRectangle(width=1.4, height=0.95, corner_radius=0.12, color=color,
                              fill_color=color, fill_opacity=0.9, stroke_width=0)
    lab = txt(label, size=26, color=INK).next_to(body, m.DOWN, buff=0.15)
    g = m.VGroup(tab, body, lab)
    g.scale(scale)
    return g


def server_rack(scale=1.0, color=TEAL):
    box = panel(1.5, 2.2, color=color, fill=BG2)
    units = m.VGroup()
    for i in range(4):
        y = 0.75 - i * 0.5
        u = m.RoundedRectangle(width=1.2, height=0.36, corner_radius=0.06, color=LINE, fill_color="#0a0c16",
                               fill_opacity=1, stroke_width=2).move_to([0, y, 0])
        led = m.Circle(radius=0.05, color=GREEN, fill_color=GREEN, fill_opacity=1, stroke_width=0).move_to([0.45, y, 0])
        units.add(u, led)
    g = m.VGroup(box, units)
    g.scale(scale)
    return g


def cloud(scale=1.0, color=BLUE, label=None):
    puffs = m.VGroup(
        m.Circle(radius=0.55).move_to([-0.6, -0.05, 0]),
        m.Circle(radius=0.75).move_to([0.05, 0.25, 0]),
        m.Circle(radius=0.5).move_to([0.72, -0.08, 0]),
        m.RoundedRectangle(width=2.2, height=0.7, corner_radius=0.35).move_to([0.05, -0.28, 0]),
    )
    for p in puffs:
        p.set_fill(color, opacity=1).set_stroke(width=0)
    g = m.VGroup(puffs)
    if label:
        g.add(txt(label, size=28, color=BG, bold=True).move_to([0.05, -0.1, 0]))
    g.scale(scale)
    return g


def gpu_chip(scale=1.0, color=PINK):
    die = m.RoundedRectangle(width=1.6, height=1.6, corner_radius=0.12, color=color, fill_color=BG2,
                             fill_opacity=1, stroke_width=6)
    core = m.VGroup(*[m.Square(side_length=0.28, color=color, fill_color=color, fill_opacity=0.7,
                               stroke_width=0).move_to([x, y, 0])
                      for x in (-0.4, 0, 0.4) for y in (-0.4, 0, 0.4)])
    pins = m.VGroup()
    for k in (-0.5, -0.17, 0.17, 0.5):
        for a, b in (([k, 0.8, 0], [k, 1.05, 0]), ([k, -0.8, 0], [k, -1.05, 0]),
                     ([0.8, k, 0], [1.05, k, 0]), ([-0.8, k, 0], [-1.05, k, 0])):
            pins.add(m.Line(a, b, color=color, stroke_width=5))
    g = m.VGroup(pins, die, core)
    g.scale(scale)
    return g


def building(scale=1.0, color=TEAL, label=None):
    body = panel(3.0, 2.2, color=color, fill=BG2)
    roof = m.Polygon([-1.7, 1.1, 0], [0, 1.9, 0], [1.7, 1.1, 0], color=color, fill_color=color,
                     fill_opacity=0.35, stroke_width=5)
    door = m.RoundedRectangle(width=0.5, height=0.8, corner_radius=0.08, color=color, fill_color=color,
                              fill_opacity=0.5, stroke_width=0).move_to([0, -0.7, 0])
    g = m.VGroup(body, roof, door)
    if label:
        g.add(txt(label, size=28, color=INK, bold=True).next_to(body, m.DOWN, buff=0.2))
    g.scale(scale)
    return g


def keycard(scale=1.0, color=AMBER, label="ROOM 214"):
    card = m.RoundedRectangle(width=1.6, height=1.0, corner_radius=0.12, color=color, fill_color=color,
                              fill_opacity=1, stroke_width=0)
    stripe = m.Rectangle(width=1.6, height=0.18, color=BG, fill_color=BG, fill_opacity=0.6,
                         stroke_width=0).move_to([0, 0.22, 0])
    lab = txt(label, size=22, color=BG, bold=True).move_to([0, -0.22, 0])
    g = m.VGroup(card, stripe, lab)
    g.scale(scale)
    return g


def door(scale=1.0, color=LINE, label=None, label_color=INK):
    frame = m.RoundedRectangle(width=1.3, height=2.2, corner_radius=0.08, color=color, fill_color=BG2,
                               fill_opacity=1, stroke_width=6)
    knob = m.Circle(radius=0.07, color=AMBER, fill_color=AMBER, fill_opacity=1, stroke_width=0).move_to([0.42, -0.1, 0])
    g = m.VGroup(frame, knob)
    if label:
        g.add(txt(label, size=26, color=label_color, bold=True).move_to([0, 0.75, 0]))
    g.scale(scale)
    return g


def speech_bubble(text, w=None, size=30, color=INK, fill=BG2, tail="down-left"):
    t = txt(text, size=size, color=color)
    w = w or t.width + 0.6
    box = m.RoundedRectangle(width=w, height=t.height + 0.5, corner_radius=0.22, color=LINE,
                             fill_color=fill, fill_opacity=1, stroke_width=4)
    t.move_to(box)
    bl = box.get_corner(m.DL)
    if tail == "down-left":
        tip = m.Polygon(bl + [0.35, 0.02, 0], bl + [0.75, 0.02, 0], bl + [0.2, -0.35, 0],
                        color=LINE, fill_color=fill, fill_opacity=1, stroke_width=4)
    else:
        br = box.get_corner(m.DR)
        tip = m.Polygon(br + [-0.35, 0.02, 0], br + [-0.75, 0.02, 0], br + [-0.2, -0.35, 0],
                        color=LINE, fill_color=fill, fill_opacity=1, stroke_width=4)
    return m.VGroup(tip, box, t)


def big_x(size=1.0, color=RED, sw=14):
    a = m.Line([-size / 2, -size / 2, 0], [size / 2, size / 2, 0], color=color, stroke_width=sw)
    b = m.Line([-size / 2, size / 2, 0], [size / 2, -size / 2, 0], color=color, stroke_width=sw)
    return m.VGroup(a, b)


def check(size=1.0, color=GREEN, sw=14):
    p = m.VMobject(color=color, stroke_width=sw)
    p.set_points_as_corners([[-size / 2, 0, 0], [-size / 8, -size / 2.6, 0], [size / 2, size / 2.4, 0]])
    return p


def dollar(scale=1.0):
    bill = m.RoundedRectangle(width=1.4, height=0.75, corner_radius=0.08, color=GREEN, fill_color=GREEN,
                              fill_opacity=0.3, stroke_width=4)
    s = txt("$", size=40, color=GREEN, bold=True).move_to(bill)
    g = m.VGroup(bill, s)
    g.scale(scale)
    return g


def wifi_bars(n_on=4, scale=1.0, on=INK, off=LINE):
    bars = m.VGroup()
    for i in range(4):
        h = 0.2 + 0.18 * i
        b = m.RoundedRectangle(width=0.16, height=h, corner_radius=0.04, color=on if i < n_on else off,
                               fill_color=on if i < n_on else off, fill_opacity=1, stroke_width=0)
        b.move_to([i * 0.26, h / 2, 0])
        bars.add(b)
    bars.scale(scale)
    return bars


def book(scale=1.0, color=PURPLE):
    left = m.Polygon([-1.2, 0.8, 0], [0, 0.65, 0], [0, -0.8, 0], [-1.2, -0.65, 0], color=color,
                     fill_color=BG2, fill_opacity=1, stroke_width=5)
    right = m.Polygon([1.2, 0.8, 0], [0, 0.65, 0], [0, -0.8, 0], [1.2, -0.65, 0], color=color,
                      fill_color=BG2, fill_opacity=1, stroke_width=5)
    lines = m.VGroup(*[m.Line([-1.0, y, 0], [-0.2, y - 0.08, 0], color=LINE, stroke_width=3) for y in (0.45, 0.2, -0.05, -0.3)],
                     *[m.Line([0.2, y - 0.08, 0], [1.0, y, 0], color=LINE, stroke_width=3) for y in (0.45, 0.2, -0.05, -0.3)])
    g = m.VGroup(left, right, lines)
    g.scale(scale)
    return g


def database(scale=1.0, color=BLUE, label=None):
    top = m.Ellipse(width=1.8, height=0.5, color=color, fill_color=color, fill_opacity=0.9, stroke_width=0).move_to([0, 0.75, 0])
    body = m.Rectangle(width=1.8, height=1.5, color=color, fill_color=color, fill_opacity=0.35, stroke_width=0)
    bot = m.Ellipse(width=1.8, height=0.5, color=color, fill_color=color, fill_opacity=0.35, stroke_width=0).move_to([0, -0.75, 0])
    rings = m.VGroup(*[m.Arc(radius=0.9, start_angle=m.PI, angle=m.PI, color=color, stroke_width=4)
                       .stretch(0.28, 1).move_to([0, y, 0]) for y in (0.2, -0.3)])
    g = m.VGroup(bot, body, rings, top)
    if label:
        g.add(txt(label, size=26, color=INK, bold=True).next_to(bot, m.DOWN, buff=0.2))
    g.scale(scale)
    return g


def sign(word, color=AMBER, scale=1.0, text_color=BG):
    """A word on a rounded paddle board a character can hold up: sign("YES", GREEN), sign("NO", RED)."""
    lab = txt(word, size=44, color=text_color, bold=True)
    board = m.RoundedRectangle(width=lab.width + 0.6, height=0.85, corner_radius=0.18, color=color,
                               fill_color=color, fill_opacity=1, stroke_width=0)
    lab.move_to(board)
    g = m.VGroup(board, lab)
    g.scale(scale)
    return g
