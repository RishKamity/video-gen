"""Original music, synthesized with numpy (nothing downloaded).

bed(seconds)  -> stereo float32 array: a soft, mellow lo-fi progression (Fmaj7 Em7 Dm7 Cmaj7 at 78 bpm)
               with electric-piano chords, a warm pad, a round bass and very quiet brushed ticks.
sting()       -> stereo float32 array: a short bright bell arpeggio for title cards (~2.6 s).
"""
import numpy as np

SR = 48000


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def _env(n, attack, decay):
    t = np.arange(n) / SR
    a = np.minimum(1.0, t / max(attack, 1e-4))
    return a * np.exp(-t / decay)


def _ep(freq, dur, vel=1.0):
    """Electric-piano-ish tone: fundamental + fading bright partials."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * freq * t)
            + 0.35 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 4)
            + 0.12 * np.sin(2 * np.pi * 3.01 * freq * t) * np.exp(-t * 7)
            + 0.05 * np.sin(2 * np.pi * 7.1 * freq * t) * np.exp(-t * 18))  # tine "tick"
    tremolo = 1 + 0.08 * np.sin(2 * np.pi * 4.2 * t)
    return (tone * tremolo * _env(n, 0.006, 1.1) * vel).astype(np.float32)


def _pad(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * t) + np.sin(2 * np.pi * freq * 1.003 * t)
         + 0.3 * np.sin(2 * np.pi * freq * 2.002 * t))
    fade = np.minimum(1, t / 0.9) * np.minimum(1, (dur - t) / 0.9)
    return (s * np.clip(fade, 0, 1) / 2.3).astype(np.float32)


def _bass(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.15 * np.sin(2 * np.pi * 2 * freq * t)
    return (s * _env(n, 0.01, 0.6)).astype(np.float32)


def _tick(rng, dur=0.08):
    n = int(dur * SR)
    noise = rng.standard_normal(n + 1)
    hp = np.diff(noise)                      # crude high-pass
    return (hp * _env(n, 0.001, 0.018)).astype(np.float32)


def _add(buf, sig, start, gain_l, gain_r):
    i = int(start * SR)
    if i >= buf.shape[0]:
        return
    j = min(buf.shape[0], i + len(sig))
    buf[i:j, 0] += sig[: j - i] * gain_l
    buf[i:j, 1] += sig[: j - i] * gain_r


CHORDS = [  # (bass root, chord tones) as MIDI notes
    (41, [57, 60, 64, 69]),   # Fmaj7 (A C E A)
    (40, [55, 59, 62, 67]),   # Em7   (G B D G)
    (38, [53, 57, 60, 65]),   # Dm7   (F A C F)
    (36, [55, 59, 64, 67]),   # Cmaj7 (G B E G)
]


def bed(seconds, bpm=78, seed=3):
    rng = np.random.default_rng(seed)
    beat = 60 / bpm
    bar = 4 * beat
    out = np.zeros((int((seconds + 3) * SR), 2), np.float32)
    nbars = int(seconds / bar) + 2
    for b in range(nbars):
        root, tones = CHORDS[b % 4]
        t0 = b * bar
        # pad: whole bar
        for k, n in enumerate(tones[:3]):
            _add(out, _pad(_midi(n), bar + 0.6), t0, 0.10 * (1.1 - 0.2 * k), 0.10 * (0.9 + 0.2 * k))
        # electric piano: soft strum on beat 1, a lighter re-hit on the "and" of 2, small melody on 4
        for k, n in enumerate(tones):
            _add(out, _ep(_midi(n), 2.4, 0.22), t0 + 0.012 * k, 0.9, 0.7)
        for k, n in enumerate(tones[1:]):
            _add(out, _ep(_midi(n), 1.6, 0.12), t0 + 1.5 * beat + 0.01 * k, 0.7, 0.9)
        mel = tones[(b * 3) % 4] + 12
        _add(out, _ep(_midi(mel), 1.4, 0.09), t0 + 3 * beat, 0.6, 0.8)
        # bass on 1 and 3
        _add(out, _bass(_midi(root), beat * 1.8), t0, 0.35, 0.35)
        _add(out, _bass(_midi(root + 7 if b % 2 else root), beat * 1.5), t0 + 2 * beat, 0.28, 0.28)
        # brushed ticks on off-beats
        for q in range(4):
            _add(out, _tick(rng), t0 + (q + 0.5) * beat, 0.035, 0.045)
    out = out[: int(seconds * SR)]
    # gentle smoothing (two-tap average) to round off highs
    out[1:] = 0.5 * (out[1:] + out[:-1])
    peak = np.abs(out).max() or 1
    return (out / peak * 0.8).astype(np.float32)


def _bell(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * t) + 0.45 * np.sin(2 * np.pi * 2.76 * freq * t) * np.exp(-t * 3)
         + 0.2 * np.sin(2 * np.pi * 5.4 * freq * t) * np.exp(-t * 6))
    return (s * _env(n, 0.003, 0.9)).astype(np.float32)


def sting():
    dur = 2.8
    out = np.zeros((int(dur * SR), 2), np.float32)
    notes = [72, 76, 79, 84]                      # C5 E5 G5 C6
    for k, n in enumerate(notes):
        _add(out, _bell(_midi(n), 2.2), 0.09 * k, 0.6 + 0.12 * k, 1.0 - 0.12 * k)
    _add(out, _bass(_midi(36), 1.6) * 1.2, 0.0, 0.6, 0.6)          # soft low hit
    for n in (60, 64, 67, 71):                                       # Cmaj7 shimmer tail
        _add(out, _pad(_midi(n), 2.2) * 0.6, 0.3, 0.5, 0.5)
    # small echo
    dry = out.copy()
    for d, g in ((0.13, 0.35), (0.27, 0.2), (0.41, 0.1)):
        i = int(d * SR)
        out[i:] += dry[:-i] * g
    t = np.arange(out.shape[0]) / SR
    out *= np.clip((dur - t) / 0.6, 0, 1)[:, None]
    return (out / np.abs(out).max() * 0.9).astype(np.float32)
