"""Mix narration + music bed + title sting into audio/<ch>_mix.wav (48 kHz stereo), from the timing json.

Levels: voice normalised to VOICE_LUFS; the bed is set MUSIC_BELOW dB under the voice (integrated
loudness) and ducked a further DUCK_DB while someone is speaking; the sting plays on the title card
STING_LUFS_BELOW dB under the voice level. Stems are written next to the mix so `check` can measure them.
"""
import re
import subprocess
import wave

import numpy as np

import music
import project
import timeline

SR = 48000
VOICE_LUFS = -16.0
MUSIC_BELOW = 22.0      # bed integrated loudness this many dB under the voice (never less than 18)
DUCK_DB = 4.0
STING_AT = 0.2          # seconds into the title card
STING_LUFS_BELOW = 4.0  # sting this many dB under the voice level (it plays alone)


def load_wav48(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ar", str(SR), "-ac", "1",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = x[:, None]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).round().astype("<i2").tobytes())


def lufs(path, start=None, dur=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if start is not None:
        cmd += ["-ss", f"{start:.3f}", "-t", f"{dur:.3f}"]
    cmd += ["-i", str(path), "-map", "0:a", "-af", "ebur128", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    return float(m[-1]) if m else float("-inf")


def db(x):
    return 10 ** (x / 20)


def build(ch):
    t = timeline.load(ch)
    adir = project.root() / "audio"
    total = t["total"]
    n = int(round(total * SR))
    voice = np.zeros(n, np.float32)
    speaking = np.zeros(n, np.float32)
    for sc in t["scenes"]:
        for seg in sc["segments"]:
            x = load_wav48(project.wav_path(ch, seg["id"]))
            i = int(round((sc["start"] + seg["start"]) * SR))
            j = min(n, i + len(x))
            voice[i:j] += x[: j - i]
            speaking[i:j] = 1.0
    write_wav(adir / f"{ch}_voice_raw.wav", voice)
    g = db(VOICE_LUFS - lufs(adir / f"{ch}_voice_raw.wav"))
    voice *= g
    # soft limiter for speech peaks above 0.7 (keeps loudness, avoids scaling the whole mix down)
    over = np.abs(voice) > 0.7
    voice[over] = np.sign(voice[over]) * (0.7 + 0.27 * np.tanh((np.abs(voice[over]) - 0.7) / 0.27))

    # music bed: starts under the end of the title card, fades out at the end
    has_title = bool(t["scenes"]) and not t["scenes"][0]["segments"]
    title_end = t["scenes"][0]["dur"] if has_title else 0.0
    bed_start = max(0.0, title_end - 1.0)
    b = music.bed(total - bed_start)
    bed = np.zeros((n, 2), np.float32)
    bed[int(bed_start * SR): int(bed_start * SR) + len(b)] = b[: n - int(bed_start * SR)]
    tt = np.arange(n) / SR
    fade = np.clip((tt - bed_start) / 2.0, 0, 1) * np.clip((total - tt) / 3.0, 0, 1)
    # ducking envelope: smooth the speaking mask (~0.4 s attack/release)
    k = int(0.4 * SR)
    kernel = np.ones(k, np.float32) / k
    sm = np.convolve(speaking, kernel, mode="same")
    duck = 1 - (1 - db(-DUCK_DB)) * np.clip(sm * 1.5, 0, 1)
    bed *= (fade * duck)[:, None]
    write_wav(adir / f"{ch}_bed_raw.wav", bed)
    bed *= db(VOICE_LUFS - MUSIC_BELOW - lufs(adir / f"{ch}_bed_raw.wav"))

    # title sting (only when the chapter has a title card)
    stem_sting = np.zeros((n, 2), np.float32)
    if has_title:
        st = music.sting()
        i = int(STING_AT * SR)
        stem_sting[i:i + len(st)] = st[: n - i]
        write_wav(adir / f"{ch}_sting_raw.wav", stem_sting[: i + len(st)])
        stem_sting *= db(VOICE_LUFS - STING_LUFS_BELOW - lufs(adir / f"{ch}_sting_raw.wav"))

    mix = voice[:, None] * np.ones((1, 2), np.float32) + bed + stem_sting
    peak = np.abs(mix).max()
    if peak > 0.79:
        mix *= 0.79 / peak
        voice *= 0.79 / peak
        bed *= 0.79 / peak
    write_wav(adir / f"{ch}_stem_voice.wav", voice)
    write_wav(adir / f"{ch}_stem_bed.wav", bed)
    write_wav(adir / f"{ch}_mix.wav", mix)
    for f in ("voice_raw", "bed_raw", "sting_raw"):
        (adir / f"{ch}_{f}.wav").unlink(missing_ok=True)
    v, m_ = lufs(adir / f"{ch}_stem_voice.wav"), lufs(adir / f"{ch}_stem_bed.wav")
    print(f"voice {v:.1f} LUFS, bed {m_:.1f} LUFS, gap {v - m_:.1f} dB, mix peak {np.abs(mix).max():.2f}, "
          f"length {n / SR:.3f}s -> {adir / f'{ch}_mix.wav'}")
