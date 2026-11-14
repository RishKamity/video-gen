# video-gen

An engine for narrated, animated explainer videos that teach a topic from zero: diagrams that build while the narrator speaks, burnt-in captions with a matching `.srt`, original music generated in code, recall questions with a countdown, and two original recurring characters. Every chapter comes out at 2560x1440, 30 fps, H.264 + AAC, in one fixed house style.

It is the engine behind the **`/video-gen` skill** for Claude. The skill grills the user about the video, has a builder agent write the scripts, fact-checks every claim, narrates each segment (Google "Puck" voice through the Speko connector), and drives this repo's CLI to render, check and deliver. You can also drive it by hand.

## What a build looks like

```
topic / doc / course folder
  -> sources/*.md                    extracted source text
  -> script/chN_segments.py          narration in 1-3 sentence segments
  -> script/claims.md                every claim with an exact source quote  (vg.py claims)
  -> audio/chN/NNN.wav               one narration WAV per segment          (vg.py chN voice-todo)
  -> chapters/chN.py                 ManimGX scenes, cued on spoken phrases
  -> out/chN_*.mp4 + .srt            rendered, mixed, assembled, measured   (timing, stills, render, audio, assemble, check)
  -> out/full.mp4 + full.srt + script/full_script.md                        (vg.py join)
```

## Quick start

```bash
git clone --depth 1 https://github.com/RishKamity/video-gen
bash video-gen/setup.sh                 # Python 3.13 venv at ~/.venvs/video-gen (VG_VENV to change),
                                        # pinned packages, ffmpeg check, one 2560x1440 test frame
PY=~/.venvs/video-gen/bin/python
VG=video-gen/engine/vg.py

$PY $VG init ~/videos/demo --title "Demo"     # a project folder outside the repo, from templates/
$PY $VG ~/videos/demo estimate                # minutes per chapter from the script
$PY $VG ~/videos/demo ch1 voice-todo          # segments still needing narration
```

Then follow [docs/PIPELINE.md](docs/PIPELINE.md). Requirements: Python 3.13, ffmpeg with libx264 and AAC, and a CPU (no GPU needed; rendering runs at about 3-7x real time on 4 cores).

## Commands

```
vg.py init <project> [--title T]
vg.py <project> estimate | claims | leakcheck <file> | join | app-copies
vg.py <project> chN voice-todo | timing | stills SCENE t1,t2 | render SCENE | render-all | audio | assemble | check
```

`python engine/vg.py --help` describes each one.

## Layout

```
setup.sh, requirements.txt
engine/      vg.py (the CLI) and the engine: style, narrated scenes, timing, captions, background,
             characters (cast.py), props, kit (title card, recall scene, labels), music, mix, checks, join,
             claims and leak checkers, length estimate
templates/   copied into a new project by `vg.py init`
docs/        PIPELINE, SCRIPT_FORMAT, STYLE, BRIEF (the builder agent's brief), FALLBACK, COURSE_PACK, LESSONS
examples/    demo projects
```

## Docs

- [PIPELINE.md](docs/PIPELINE.md): building one chapter, step by step, and joining chapters
- [SCRIPT_FORMAT.md](docs/SCRIPT_FORMAT.md): segments, timing cues, captions, writing for the voice, claims
- [STYLE.md](docs/STYLE.md): the locked house style and how to draw a new character pair
- [BRIEF.md](docs/BRIEF.md): fill-in brief for the builder agent (Stage A scripts, Stage B build)
- [COURSE_PACK.md](docs/COURSE_PACK.md): short per-topic videos for a study-guide course pack
- [FALLBACK.md](docs/FALLBACK.md): switching to Manim Community if ManimGX fails
- [LESSONS.md](docs/LESSONS.md): what went wrong before, so it does not again

## Content rules

All music is generated in code; the characters are original drawings made of simple shapes. Never add copyrighted or branded characters, logos, real people's likenesses, memes from existing media or downloaded music. Every factual claim in a video traces to a source.
