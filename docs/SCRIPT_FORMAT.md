# Script format

A chapter's narration lives in `script/chN_segments.py`; its drawing lives in `chapters/chN.py`. The timing step joins them through scene keys and segment ids.

## Segments: `script/chN_segments.py`

```python
SEGMENTS = [
 # sc01: recap hook
 dict(id=1, scene="sc01_hook", say="Last time: the moon pulls on the ocean. So why are there two high tides a day?"),
 # sc02: the bulge on the far side
 dict(id=2, scene="sc02_far_side", say="The moon pulls the near side of Earth a little harder than the middle..."),
 dict(id=3, scene="sc02_far_side", say="That's about twelve hours and twenty-five minutes between high tides.",
      cap="That's about 12 hours and 25 minutes between high tides."),
 # sc03: recall
 dict(id=4, scene="sc03_recall", say="Quick check: why is there a bulge on the far side too?", pause=3.0),
 dict(id=5, scene="sc03_recall", say="Because the far side is pulled least, so it gets left behind."),
 dict(id=6, scene="sc03_recall", say="Next: why some places get one tide a day."),
]
```

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Unique integer within the chapter. The narration WAV is `audio/chN/NNN.wav` (`id=3` -> `003.wav`). Number in viewing order. |
| `scene` | yes | The scene key: the `NAME` of a scene class in `chapters/chN.py`. A scene's segments sit together; scenes play in the order they first appear. |
| `say` | yes | Exactly what the voice reads. 1-3 sentences (the voice drifts on long reads). |
| `cap` | no | Caption text when it should read differently from `say` (digits, symbols, names). Defaults to `say`. |
| `pause` | no | Extra silence after the segment, in seconds. Use `3.0` after every recall question (the countdown fills it). |

Any other field is ignored with a note. The file is plain Python, so comments are welcome; keep one comment per scene saying what it shows.

How the timing step lays a chapter out: the title card (`TITLE` seconds, no narration), then each scene: 0.3 s lead-in, each segment's WAV followed by 0.2 s (plus its `pause`), 0.4 s tail, all snapped to the 30 fps frame grid. The WAVs carry about 0.2 s of lead-in and 0.3 s of tail silence of their own, so segments are heard about 0.7 s apart.

## Scenes: `chapters/chN.py`

```python
TITLE = ("sc00_title", 4.0)     # title card scene name and seconds (None for no title card)
OUT_NAME = "ch2_far_side"       # out/ch2_far_side.mp4 and .srt
Title = make_title(2, "Two tides a day", "and why the far side bulges too")

class FarSide(NarratedScene):
    NAME = "sc02_far_side"
    def body(self):
        earth = m.Circle(radius=1.2, color=BLUE).move_to([0, 0.4, 0])
        self.cue(self.at(2), m.FadeIn(earth))                              # segment 2 starts
        self.cue(self.at(2, "near side"), m.Indicate(earth))               # "near side" is (about) spoken
        self.cue(self.at(3, "twelve hours"), m.FadeIn(term("12 h 25 min")))

class Recall(RecallScene):
    NAME = "sc03_recall"
    Q = [(4, 5, "Why is there a bulge on the far side too?", "It's pulled least, so it's left behind.")]
    BRIDGE = (6, "Next: one tide a day")
```

`TITLE` and `OUT_NAME` must be plain literals (they are read without importing the file). The chapter id comes from the file name; a scene's `CHAPTER` is set automatically.

### Timing cues

| Call | Scene time it returns |
|---|---|
| `self.at(3)` | segment 3 starts |
| `self.at(3, "twelve hours")` | about when that phrase is spoken in segment 3 |
| `self.at(3, "twelve hours", -0.2)` | the same, 0.2 s earlier (the third argument is an offset) |
| `self.at(3, end=True)` | segment 3's audio ends |
| `self.dur` | the scene's length |

- `self.cue(t, anim, ..., run_time=0.8)` waits until `t`, then plays the animations together. A cue whose time has passed plays at once. The scene's first cue always starts on frame 0, so no scene opens on an empty screen.
- `self.wait_to(t)` waits without playing anything; `self.play(...)` plays right after the previous animation.
- The phrase is searched (case-insensitive) in `say`, then in `cap`. Its time is estimated from its character position in the text, spread over the segment's measured audio: there is no word alignment, so a phrase near the end of a long segment can land a few tenths early or late. Cue the important reveals on phrases near the start of a segment, or split the segment.
- Never hard-code times. When narration changes, `timing` re-times every cue.
- `finish()` runs after `body()`: it fades the stage out just before the scene ends and waits to the exact end. If animations run past the end it raises an error naming the scene.

## Captions

Captions are generated from `cap` (or `say`) and burnt in, and the same chunks go into the `.srt`.

- At most 54 characters per caption line. Text is split at sentence ends first (a `.`, `?` or `!` followed by a space; never inside a number such as `2.5` or `$4.78`), long sentences are split into balanced pieces preferring breaks after commas, colons and semicolons, and a very short piece joins its neighbour.
- Chunks are shown in proportion to their length across the segment's voiced part.
- Captions show only while a segment is speaking, on a dark band centred at y = -3.47. Nothing else may sit there (STYLE.md).
- Keep captions to plain words: digits and symbols are fine in `cap`, emoji and markup are not.

## Writing for the voice (Puck)

- Write `say` exactly as it should be spoken: "twenty twenty-five" (a year), "five point five" (a decimal), "forty percent", "about three thousand dollars". Put the normal written form in `cap`: `2025`, `5.5`, `40%`, `$3,000`.
- Acronyms said as letters get spaces: "G P T", "N A S A" if it is spelled out; acronyms said as words stay as words ("NASA" if the narrator should say "nasa"). Write "AI" as "AI".
- Unusual names and terms: spell them phonetically in `say` and correctly in `cap`, and list them in `DECISIONS.md` as possible mispronunciations (nobody in the pipeline can listen).
- Short sentences, contractions, one idea per segment. A casual TA talking to a friend: real jokes and everyday analogies, never talking down.
- Keep the source's conclusions and bluntness. When something is secondhand, a guess or unverified, say so in words ("one report says", "nobody has tested this").
- Quotes from sources: under 15 words, attributed, with a source tag on screen.
- Puck speaks about 160 words a minute; a chapter with title card, gaps and recall pauses runs at about 146 words a minute. `estimate` gives each chapter's length from the script.

## Recall questions

Every chapter ends with two: question segment (with `pause=3.0`), answer segment, then the second pair, then a one-line bridge to the next chapter (the last chapter ends with a short sign-off instead). The question on screen is short (it shows at size 52 and is shrunk to fit), the answer is one or two short lines.

## The chapter notes: `script/chN_<slug>.md`

Start from `templates/chapter_notes_template.md`. `join` reads three things from it: the first line (`# Chapter N: Title — narration script`; the " — narration script" part is dropped), the `## Recall questions` section (copied as is), and the first table in `## Sources` (columns named Source, URL and Date are merged across chapters).

## Claims: `script/claims.md`

One markdown table for the whole video, with a column whose header contains "Source" (the template has `| Ch | Seg | Claim | Label | Source |`). A Source cell holds:

- `sources/<file>.md: "exact quote"`, several quotes (`"a" "b"`), or several files (`sources/a.md: "x"; sources/b.md: "y"`). `...` inside a quote stands for omitted words; write a quote inside a quote as `\"` or with single quotes.
- or the URL that was opened (`claims` lists these for the main session to open).

`vg.py <project> claims` normalises both sides (markdown links to their text, emphasis marks and brackets dropped, every kind of dash to `-`, quote marks ignored, whitespace collapsed, case ignored) and lists every quote not found, every missing source file and every row without a source, with line numbers. Exit status 1 if there is any.
