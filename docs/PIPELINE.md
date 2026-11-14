# Pipeline: building one chapter, step by step

Every command is `vg.py <project> ...` run with the venv's Python. Projects live **outside** the repo; every command takes the project folder. Set two shell variables once:

```bash
bash video-gen/setup.sh                       # venv at ~/.venvs/video-gen (VG_VENV=... to change)
PY=~/.venvs/video-gen/bin/python
VG=video-gen/engine/vg.py
P=~/videos/tides                              # the project folder
```

Rules that apply throughout: **one scene per render command**, **every command under 10 minutes**, and nothing left running in the background.

## 0. Make the project

```bash
$PY $VG init $P --title "How tides work"
```

Creates `script/ chapters/ sources/ audio/ scenes/ out/ frames/`, `project.json` (title and chapter order, starting with `["ch1"]`), and copies the templates: `chapters/ch1.py`, `script/ch1_segments.py`, `script/ch1_notes.md`, `characters.py`, `script/claims.md`, `DECISIONS.md`. Running `init` again keeps existing files.

## 1. Sources

Save the text of every source as one Markdown file in `sources/` (`sources/noaa_tides.md`, ...): the extracted text of a PDF or page, with its title, URL and date at the top. The claim checker matches quotes against these files, so keep the wording as published.

## 2. Script (Stage A: no voice calls)

- `characters.py`: pick the two characters (LEAD acts, CHECK checks). See STYLE.md.
- `script/ch1_segments.py`: the narration, one dict per 1-3 sentence segment (SCRIPT_FORMAT.md).
- `script/ch1_<slug>.md`: rename `ch1_notes.md`; narration, on-screen plan, recall questions, bridge, Sources table.
- `script/claims.md`: one row per factual or numeric claim with an exact quote from `sources/` or the URL opened.

```bash
$PY $VG $P estimate          # words and estimated minutes per chapter (within ~2% on the first build)
$PY $VG $P claims            # every quote must be found in its source file; exit 1 lists the misses
$PY $VG $P leakcheck SAMPLE  # course packs only: nothing may share wording or numbers with the sealed sample exam
```

Stop here and report. The main session fact-checks every claim before any narration is recorded.

## 3. Narration (Stage B starts)

```bash
$PY $VG $P ch1 voice-todo    # each missing segment, the WAV file to write, and the exact Speko request body
```

For each listed segment: one `mcp__Speko__audio_synthesize` call with the body shown (voice Puck), then copy the WAV the harness saved (under `/tmp/claude-tool-results/...`) to the path shown, `audio/ch1/NNN.wav`, straight away. Never re-call a segment that already succeeded. Run `voice-todo` again until it says 0 to go.

## 4. Timing

```bash
$PY $VG $P ch1 timing
```

Measures every WAV with ffprobe and writes `script/ch1_timing.json` (scenes, segment starts, caption chunks) and `out/<OUT_NAME>.srt`. Re-run it after any narration change: cues, captions and the audio mix all follow the new timing. It also notes scene keys that have no scene class yet.

## 5. Scenes

Edit `chapters/ch1.py`: set `TITLE` (title card scene and seconds) and `OUT_NAME` (output file name), keep the `make_title(...)` title card, write one `NarratedScene` subclass per scene key with `NAME = "<scene key>"`, and end with a `RecallScene`. Place every animation with `self.cue(self.at(seg_id, "spoken phrase"), ...)` (SCRIPT_FORMAT.md). Reuse `kit.py` (cards, bullets, bars, stamps, source tags, label chips), `props.py` (terminal, files, cloud, database, signs, ...) and `style.py`.

## 6. Stills before rendering

```bash
$PY $VG $P ch1 stills sc01_idea 3,12.5          # frames/ch1_sc01_idea_t03.00.png, ..._t12.50.png
$PY $VG $P ch1 stills sc01_idea 12.5 --layout   # plus ManimGX's layout report (advisory)
```

Full-size PNGs with the real background, drawn without encoding video (seconds per scene). **Look at them**: the busiest moment of every scene, text inside the frame, nothing on the caption band (content above y = -2.75), legible at phone size. Times are scene-relative; `script/ch1_timing.json` gives each segment's `start` and `dur`. `--layout` also runs `manimgx inspect` at the same times and lists clipped content, overlapping text and tiny labels.

## 7. Render

```bash
$PY $VG $P ch1 render sc01_idea        # one scene -> scenes/ch1/sc01_idea.mp4
$PY $VG $P ch1 render-all              # every missing or out-of-date scene, one process per scene
```

`render` writes to `scenes/ch1/SCENE.tmp.mp4` and renames it only when the render succeeds, so a failed render never leaves a broken file. Speed on a 4-core CPU: about 3x real time for simple scenes, about 6.5x for busy ones. Keep scenes under about 60 seconds of video.

`render-all` re-renders scenes that are missing or older than the chapter file, the timing json or `characters.py` (`--force` renders all). It stops before starting a scene that would push it past its budget (`--budget 8`, minutes, the default) and exits with status 3, listing what is left; run it again to continue. After editing one scene, `render SCENE` is cheaper than `render-all`.

## 8. Audio

```bash
$PY $VG $P ch1 audio
```

Voice normalised to -16 LUFS, the original music bed 22 dB under it (ducked a further 4 dB while speaking), and a sting on the title card -> `audio/ch1_mix.wav` plus stems `audio/ch1_stem_voice.wav` and `audio/ch1_stem_bed.wav`.

## 9. Assemble and check

```bash
$PY $VG $P ch1 assemble      # concat demuxer -c copy, then mux the mix (-c:v copy, AAC 192k 48 kHz) -> out/<OUT_NAME>.mp4
$PY $VG $P ch1 check         # exit 1 on any problem
```

`check` prints each scene's frame count against the timing (they must match exactly), the final streams, video duration against the timing total, volume, integrated loudness, voice and bed stem loudness and their gap, silences of a second or more under -55 dB, and five sample frames in `frames/ch1_final_*.jpg`. Look at the frames. Nobody can hear the audio: report the measured numbers, not how it sounds.

## 10. More chapters, then join

For chapter N: copy `chapters/ch1.py` to `chapters/chN.py` and `script/ch1_segments.py` to `script/chN_segments.py` (or start again from `video-gen/templates/`), change `TITLE`, `OUT_NAME` and the title card, and add `"chN"` to `project.json`'s `chapters` list in viewing order. Then steps 3-9.

```bash
$PY $VG $P join              # -> out/full.mp4, out/full.srt, script/full_script.md, plus measurements
$PY $VG $P app-copies        # -> out/app/<OUT_NAME>.mp4, 720p, each under 20 MB (study apps)
```

`join` first checks that every chapter has identical stream settings (codec, profile, size, frame rate, pixel format, time base, audio rate and channels) and refuses otherwise; then it concatenates with the concat demuxer and `-c copy`, shifts every chapter's captions by the chapters before it, writes the combined script (narration, recall questions, sources merged from each chapter's `.md`), and measures: joined duration against the sum of chapters, silences, loudness per chapter, and one frame per chapter (`frames/join_chN.jpg`).

## Redoing things

| Changed | Run again |
|---|---|
| Narration wording of a segment | delete its WAV, `voice-todo`, synthesize that one segment, `timing`, `render-all`, `audio`, `assemble`, `check` |
| One scene's drawing | `stills`, `render SCENE`, `assemble`, `check` |
| `characters.py` | `render-all` (every scene is out of date), `assemble`, `check` |
| Chapter order | `project.json`, then `join` |

## What lives where

| Path | Written by |
|---|---|
| `script/chN_timing.json`, `out/<name>.srt` | `timing` |
| `frames/chN_SCENE_tSS.SS.png` | `stills` |
| `scenes/chN/SCENE.mp4` | `render`, `render-all` |
| `audio/chN_mix.wav`, `audio/chN_stem_*.wav` | `audio` |
| `out/<name>.mp4` | `assemble` |
| `frames/chN_final_*.jpg` | `check` |
| `out/full.mp4`, `out/full.srt`, `script/full_script.md`, `frames/join_*.jpg` | `join` |
| `out/app/*.mp4` | `app-copies` |

Environment variables: `VG_VENV` (setup.sh's venv folder), `VG_CACHE` (where the background glow images are cached; default `~/.cache/video-gen`), `VG_PROJECT` (set by vg.py for its child processes).

## Troubleshooting

- `phrase '...' not in segment N`: the phrase passed to `self.at` is not in that segment's `say` or `cap` (case is ignored). Use words that are really there.
- `animations run to X s, past the scene end`: a scene's animations outlast its narration. Shorten run times or cue earlier.
- `Object ... cannot be converted to an animation`: a mobject was passed to `cue` instead of an animation; wrap it, as in `m.FadeIn(tag)`.
- Frame-count mismatch in `check`: re-render that scene; if it persists, the scene file is older than the timing (run `render-all`).
- `refusing to join: stream settings differ`: re-assemble the odd chapter so all chapters come from the same engine settings.
