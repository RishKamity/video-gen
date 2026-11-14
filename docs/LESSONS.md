# Lessons from the builds (do not repeat these)

From the first full build (a 29-minute, 8-chapter explainer: 204 narrated segments, about 1,760 seconds of video), from packaging and testing this engine, and from the second build (below).

## Rendering

- **ManimGX merges identical frames**, so a still stretch of a scene would drop frames and break constant 30 fps. The engine renders scenes on a transparent background and lets ffmpeg composite a slowly drifting background behind them; `render.py` writes each frame its repeat count, so every scene file has exactly `round(dur x 30)` frames.
- **ManimGX adds one closing frame** at the end of a scene. `NarratedScene.finish()` stops one frame early so each file is exact and the files join without drift.
- **Scenes opened on an empty background for half a second.** The first cue of every scene now starts on frame 0, so content is on screen or entering from the first frame (the very first frame of a fade-in is still transparent; that single frame is expected).
- **Soft glows showed hard circular edges and banding.** Glows are images with a Gaussian falloff that reaches zero at the rim plus a little alpha dither, composited by ffmpeg (also much faster than ManimGX fills).
- `setup_config()` runs when `narrated.py` is imported, so render, stills and inspect all draw at 2560x1440.
- **Render speed** on a 4-core CPU: about 3x real time for simple scenes, about 6.5x for busy ones. A 5-minute chapter takes 15-35 minutes of rendering, so it never fits one 10-minute command: one scene per command, or `render-all` with its budget, run repeatedly. Keep scenes under about 60 seconds.
- `render` writes to a temp file and renames it on success: a killed render never leaves a half-written scene that `assemble` would pick up.
- The timing json is rewritten only when its content changes, so `render-all` can tell which scenes are out of date.

## Timing and captions

- **Cues come from estimated word positions**, not true word timing (there is no aligner), so a phrase late in a long segment can land a little early or late. Cue on phrases near the start of a segment, or split long segments.
- A scene ends 0.4 s after its last segment, and the stage fades 0.45 s before the end: anything revealed at the very end of the last segment is visible for well under a second. Reveal it earlier.
- **Captions split at decimal points** ("2." / "5%") in an early version. Sentences now end only at `.`, `?` or `!` followed by a space or the end of the text.
- Never hard-code times; when narration changed, every hard-coded time was wrong.

## Narration and audio

- **Nobody in the pipeline can hear the audio.** Measure it (integrated loudness, voice-to-bed gap, silences, duration against timing) and report the numbers. Flag names the voice may mispronounce instead of claiming they sound right.
- One synthesis call per segment: the voice drifts on long reads, and a retake of a successful segment costs credit and sounds different. Fix wording before synthesizing.
- The Puck WAVs carry about 0.19 s of lead-in and 0.30 s of tail silence; the timing gaps are set with that in mind (segments are heard about 0.7 s apart).
- Length estimates: one segment lasts about 0.765 s + 0.0593 s per character of `say`. On the first build every chapter's estimate was within 2% of the measured length; overall about 146 words a minute (160 while speaking).

## Content

- **A source's labels (verified, secondhand, guess) must survive into the video in plain words**, as label chips on screen and in the narration ("one report says", "nobody has tested this").
- A wrong fact is worse than a missing one: every claim in `claims.md` with a quote the checker can find, and the main session checks every claim before narration.
- Quotes in `claims.md` drift from the source (curly quotes, dashes, markdown links). The checker normalises those, but not paraphrase: copy quotes exactly.

## Writing scene code

- `cue()` takes animations, not mobjects: `self.cue(t, m.FadeIn(tag))`, not `self.cue(t, tag)` (the error is "cannot be converted to an animation").
- Characters standing low collide with the source tag (bottom right, just above the caption band). With a source tag on screen, keep feet above about y = -2.3.
- `stills --layout` (ManimGX's inspect) flags clipped content, overlapping text and tiny labels. Its findings are advisory: Chip's badge, for instance, is always reported as small text.
- In a project's `characters.py`, define every character class before the line that picks `LEAD, CHECK`.

## From the second build (a 74-second, one-chapter demo: examples/hash-functions)

- **The voice-to-bed gap was really 25 dB, not 22.** The voice stem was written and measured mono, but it plays on both channels, and a mono file measures 3 dB quieter than the same signal on two channels. The mix now measures the voice as stereo. The soft limiter's ceiling (0.97) was also above the 0.79 mix-peak cap, so the cap scaled the whole mix down and the voice ended near -17.8 instead of -16 LUFS; the limiter now starts at 0.6 with a ceiling of 0.76 (it touched 0.13% of samples on this build).
- **Fact-check edits broke three cue phrases** (the narration changed, the `self.at(...)` phrases did not), which would only have failed at render time. `estimate` and `timing` now list every stale cue phrase.
- **Short videos have a lot of fixed time.** The 75-second target held 142 words, not the ~180 that 146 words a minute suggests; `estimate` was within 1.2% of the measured length.
- **Reveals near the end of a scene's last segment flash by.** On the first stills, a source tag and a note cued on the last words of a scene were visible for under half a second before the stage faded. Cue tags and notes at the start of the segment they belong to.
- **Sources may only be readable through a fetch tool** (the build machine's proxy refused every source site). Save the exact sentences the fetch tool returns, say so at the top of the source file, and keep claim quotes to those sentences.

## Testing without voice credits

Placeholder narration lets the whole pipeline run with no Speko calls: for each segment, a quiet tone as long as Puck would take.

```bash
# duration = 0.765 + 0.0593 * len(say)
ffmpeg -v error -f lavfi -i "sine=frequency=220:duration=6.6:sample_rate=24000" -af "volume=0.05" -ac 1 audio/ch1/001.wav
```

Never deliver a video made with placeholder audio.

## Tooling

- In bash with `set -o pipefail`, `cmd | grep -q x` can fail because grep exits early and `cmd` dies of SIGPIPE: capture the output first (`out="$(cmd)"; grep -q x <<<"$out"`).
- Nothing may hard-code a home folder or venv path: the engine finds its repo from `__file__`, the project from the command line, and the manimgx CLI next to `sys.executable`.
