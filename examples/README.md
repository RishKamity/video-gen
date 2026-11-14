# Examples

Projects normally live outside the repo; a demo kept here holds only its source files (scripts, chapter files, characters, sources, decisions, `project.json`), never rendered audio or video. The repo's `.gitignore` keeps `audio/`, `scenes/`, `frames/`, `out/`, `*.wav` and `*.mp4` out.

## hash-functions: "What's a hash function?"

A 74-second, one-chapter video for a total beginner, built end to end with this engine and the `/video-gen` skill (taking the skill's defaults, except one chapter of 60-75 seconds and no checkpoint). It covers what a hash function is (any input to a fixed-size fingerprint, same input same output, one added letter changes everything, with real SHA-256 values), why it is one-way and how sites use that for passwords, and what a collision is, with the 2017 SHA-1 collision as the real example. Then two recall questions and a sign-off.

| File | What it is |
|---|---|
| `DECISIONS.md` | The decisions taken (defaults, since nobody answered), the outline and the source list |
| `characters.py` | An original pair drawn from simple shapes: Whizz, an overeager teal blender (LEAD), and Latch, a calm purple padlock who checks logins (CHECK) |
| `script/ch1_segments.py` | The narration: 12 segments, 142 words, read by Puck |
| `script/ch1_hash_functions.md` | Narration as captioned, the on-screen plan with its cue phrases, recall questions and sources |
| `script/claims.md` | 18 claims, each with an exact quote from `sources/`, plus the fact-check edits made before narration |
| `script/ch1_timing.json` | The timing measured from the narration WAVs, kept so the scenes can be drawn without them |
| `chapters/ch1.py` | Six scenes: title card, hook, fingerprint, one-way and logins, collisions, recall |
| `sources/*.md` | Exact excerpts from NIST glossary entries, OWASP, a university security office, the Google/CWI SHA-1 announcement and NIST's SHA-1 retirement notice, plus a SHA-256 computation |

Measured on the build: 74.13 s (the estimate said 75.0), every scene's frame count exact, voice -16.0 LUFS, bed -38.0 LUFS (22.0 dB under), final -16.1 LUFS, no silences of a second or more. Rendering took 4 minutes on 4 cores (about 3.2x real time).

Try it without voice credits:

```bash
PY=~/.venvs/video-gen/bin/python
$PY engine/vg.py examples/hash-functions estimate                     # length from the script; flags stale cue phrases
$PY engine/vg.py examples/hash-functions claims                       # every quote found in sources/
$PY engine/vg.py examples/hash-functions ch1 stills sc02_fingerprint 14.4    # frames/ (ignored by git)
$PY engine/vg.py examples/hash-functions ch1 render sc04_collision     # scenes/ (ignored by git)
```

`timing`, `audio`, `assemble` and `check` need the narration WAVs in `audio/ch1/`, which are not kept here: synthesize them (`ch1 voice-todo`) or make placeholder tones (docs/LESSONS.md, "Testing without voice credits"; never deliver a video made with them). `timing` rewrites `script/ch1_timing.json` from whatever WAVs are there.
