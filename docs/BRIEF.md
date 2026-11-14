# Builder brief (fill in, then give to the builder agent)

The main session fills in every `<...>` and sends this whole page as the builder agent's prompt. Delete lines that do not apply.

---

You are building a narrated, animated explainer video with the video-gen engine. Read `video-gen/README.md` and every file in `video-gen/docs/` before writing anything. A wrong fact in a video is worse than a missing one.

## Setup

- Engine repo: `<path to the video-gen clone>`. Python: `<venv>/bin/python` (made by `setup.sh`). Commands: `PY=<venv>/bin/python; VG=<repo>/engine/vg.py`.
- Project folder: `<project path>` (made with `vg.py init`; outside the repo).
- Every shell command must finish within 10 minutes. Render one scene per command (or `render-all`, which stops at its 8-minute budget; run it again to continue). Leave nothing running in the background.

## The video

- Topic: `<topic in one line>`
- Audience: `<who, what they already know>` (default: a total beginner; Chapter 0 teaches the vocabulary)
- Decisions: see `<project>/DECISIONS.md` (`<one-line summary>`)
- Outline:

| Chapter | Title | Target minutes | Main ideas, in order |
|---|---|---|---|
| ch0 | `<...>` | `<...>` | `<...>` |
| ch1 | `<...>` | `<...>` | `<...>` |

- Sources (already saved in `<project>/sources/`): `<file: what it is>`. These are the source of truth: do not change their findings. Outside research only adds background and examples, and is labelled as such.
- Characters: `<LEAD name: description>`, `<CHECK name: description>` (set in `<project>/characters.py`; see STYLE.md "Characters").
- Flavor: `<references to use, e.g. the viewer's campus life>`.
- Style: the locked house style in `docs/STYLE.md`. Do not change it.

## Stage A: scripts only (no voice calls)

For each chapter:

1. `script/chN_segments.py` (SCRIPT_FORMAT.md): 1-3 sentence segments; title card, a short recap hook, background for every new idea, the content, two recall questions (each question segment with `pause=3.0`), a one-line bridge (the last chapter: a short sign-off).
2. `script/chN_<slug>.md` from `templates/chapter_notes_template.md`: narration, on-screen plan (what appears on which phrase), recall questions, bridge, Sources table.
3. Rows in `script/claims.md` for every factual or numeric claim in the narration and the planned on-screen text, each with a short exact quote from a file in `sources/` or the URL you opened, and the label it will carry on screen (verified, secondhand, a guess, unverified, estimate). Keep the source's own labels; list any label you changed at the top of the file.
4. `chapters/chN.py` may be drafted now (no rendering yet).

Then run and fix until clean:

```bash
$PY $VG <project> estimate
$PY $VG <project> claims
$PY $VG <project> leakcheck <sealed sample exam file>     # course packs only
```

**Stop and report**: per chapter, its length estimate and segment count; the `claims` result; every label change; anything you could not source; names the voice may mispronounce. Do not start Stage B until the main session says so (it will send exact edits first).

## Stage B: narration, render, check

Narration, one segment at a time:

- Run `$PY $VG <project> chN voice-todo`. For each listed segment, call `mcp__Speko__audio_synthesize` once with exactly this body (the command prints it, filled in):
  `{"text": "<segment say text>", "intent": {"language": "en-US"}, "voice": "Puck", "constraints": {"allowedProviders": {"tts": ["google-tts:gemini-3.8-flash-lite-tts"]}}}`
- The harness saves the result as a WAV under `/tmp/claude-tool-results/...`: copy it **at once** to `<project>/audio/chN/NNN.wav` (the path `voice-todo` shows).
- One call per segment. **Never re-call a segment that succeeded** (each call spends the user's credit, and a retake sounds different). If wording must change, change it before synthesizing.
- Use no other Speko tool, and no ElevenLabs tools at all.
- When `voice-todo` shows 0 to go, run `timing`.

Then, for each chapter (with the checkpoint on: the first chapter only, then stop and report):

```bash
$PY $VG <project> chN timing
$PY $VG <project> chN stills SCENE t1,t2,...    # the busiest moments of EVERY scene; open and look at each PNG
$PY $VG <project> chN render SCENE              # one scene per command
$PY $VG <project> chN audio
$PY $VG <project> chN assemble
$PY $VG <project> chN check                     # must end with ALL SCENES MATCH
```

Look at stills before rendering anything: text inside the frame, nothing over the caption band, legible at phone size, labels and source tags present. After `check`, open the five `frames/chN_final_*.jpg`.

When every chapter passes: `$PY $VG <project> join` (and `app-copies` for course packs).

## Report

Under 300 words: what was built (chapters, lengths, paths of the MP4s, `.srt` files and `script/full_script.md`); what `check` and `join` **measured** (frame counts, durations, loudness, voice-to-bed gap, silences); what you looked at; anything unverified, left out or rough; names the voice may mispronounce. Nobody can hear the audio: report measurements, never "sounds good".
