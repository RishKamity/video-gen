# The house style (locked)

Every video looks and sounds the same. Change these only when the user asks. The values live in `engine/style.py`, `engine/kit.py`, `engine/narrated.py` and `engine/mix.py`.

## Output

2560x1440, 30 fps constant, H.264 yuv420p (CRF 18), AAC 48 kHz stereo. Each chapter is its own MP4 with a matching `.srt`; `join` makes `full.mp4`.

## Palette (dark theme)

| Name | Hex | Use |
|---|---|---|
| `BG` | `#0f1220` | background (with two slow, soft drifting glows, `#1c2a4a` and `#2a1c4a`) |
| `BG2` | `#171b2e` | panels, cards |
| `INK` | `#edeff7` | main text |
| `MUTED` | `#8a91ad` | secondary text, source tags |
| `LINE` | `#3a4163` | outlines, arrows, tracks |
| `TEAL` | `#4fd1c5` | the first character, main accent, the QUICK CHECK header |
| `PURPLE` | `#9f7aea` | the second character |
| `AMBER` | `#f6c445` | key terms, highlights, chapter number, countdown ring, "Next" line |
| `GREEN` | `#48bb78` | yes, correct, answers, "verified" |
| `RED` | `#f56565` | no, wrong, danger |
| `BLUE` | `#63b3ed` | outside things, "secondhand" |
| `PINK` | `#f687b3` | spare accent |

Fonts: Noto Sans (ships with manimgx-fonts) for everything; DejaVu Sans Mono for code and commands. Bold for headings, terms and answers.

## Frame and safe area

The frame is 14.22 x 8 units (x from -7.11 to 7.11, y from -4 to 4; one unit is 180 px).

- Content stays inside x = ±6.7 and between y = 3.75 and **y = -2.75**.
- **The caption band owns everything below y = -2.95.** Captions sit on a rounded black band (62% opacity) centred at y = -3.47, text size 34, at most 13.2 units wide. Nothing else goes there, ever (the title card, which has no captions, is the only exception).
- Headings: `head("...")` at y = 3.25, size 56-58, bold.
- Check with `stills` before rendering: text inside the frame, nothing touching the band, legible at phone size (nothing smaller than size 24 except tiny decorative labels).

## Layout rules

- **One idea per screen.** A scene builds one diagram while the narrator explains it, then clears. Little text: a heading, a few labels, at most one short sentence.
- Things appear when they are spoken (cued on the phrase), never all at once at the start.
- Content from the first frame: the first cue starts on frame 0 (enforced by `cue`).
- Diagrams over bullet lists. Simple shapes, generous spacing, the palette only.
- Motion is calm: fades, short shifts, `GrowArrow`, `Create`, gentle scale-ins (1.1-1.3), small hops for the characters.

## Key-term pills

`term("word", color=AMBER, size=52)`: the word in bold `BG`-coloured text on a rounded pill. It appears the moment the term is first spoken, usually with `m.FadeIn(pill, scale=1.2)`. One or two per screen.

## Source tags and evidence labels

Every outside figure, quote or incident gets a source tag: `src("Source name, Mon D, YYYY", "verified")`, small `MUTED` text at the bottom right just above the caption band, with a coloured label chip. A second tag goes one line up (`row=1`).

Labels say plainly how sure the video is, and must survive from the source into the video:

| Label | Colour | Meaning |
|---|---|---|
| `verified` | green | checked against a primary or reliable source |
| `secondhand` | blue | reported by someone else, not checked at the origin |
| `a guess` | amber | an estimate or opinion, including the source's own guesses |
| `unverified` | red | could not be checked |
| `estimate` | purple | a number someone estimated |

Add topic-specific labels in a chapter with `LABELS["reviewer's claim"] = PURPLE` (kit.py). `tagged(text, label)` puts a label chip after a line of text. Quotes on screen are under 15 words.

## Title card

`make_title(num, title, subtitle)` (kit.py): "CHAPTER N" in amber over an amber rule, the title (size 80, bold), the subtitle in muted text, and the two characters sliding in from the sides, one hopping. 4 seconds by default (`TITLE` in the chapter file), no narration, the music sting under it. Course packs use `kicker="TOPIC 8A"`.

## Recall questions

`RecallScene` (kit.py): a teal "QUICK CHECK" pill at the top, the question in bold at y = 1.6, a 3-second countdown (an amber ring that shrinks clockwise from 12 o'clock around the counting number, at y = -0.5), then the answer in green in the same place as the narrator says it. Two questions per chapter, then the bridge: "Next: ..." in amber with both characters, the first one grinning and hopping.

## Music and sound

All music is generated in code (`engine/music.py`), nothing downloaded:

- A soft lo-fi bed (Fmaj7, Em7, Dm7, Cmaj7 at 78 bpm: electric piano, pad, round bass, quiet brushed ticks) at **22 dB under the voice** (integrated loudness; never less than 18), ducked another 4 dB while someone speaks, fading in under the end of the title card and out over the last 3 seconds.
- A short bell sting (C major arpeggio with a soft low hit) on each title card, 4 dB under the voice level.
- Voice normalised to -16 LUFS, soft-limited above 0.7, mix peak at most 0.79.

## Characters

Each video has two original recurring characters, decided in the grilling, chosen in the project's `characters.py`:

- `LEAD`: the one who acts first (overeager, curious, makes the viewer's mistakes for them).
- `CHECK`: the one who checks (calm, skeptical, asks how we know).

The library (`engine/cast.py`) has **Chip**, a teal robot intern with a screen face, antenna and lanyard badge (`Chip(scale, badge="INTERN")`), and **Brick**, a purple bouncer with dark glasses, an earpiece and folded arms (`Brick(scale, tag="STAFF")`), plus `Person` for extras. Change the badge or shirt word to suit the topic.

Every character has a `mouth` you can change with `face(char, kind)` (kinds: `smile`, `grin`, `o`, `worried`, `flat`) and hops with `hop(char)`. Chip also exposes `eyes`, `arm_l`, `arm_r`, `antenna_ball`, `badge`; Brick exposes `glasses` and `arms`.

### New characters

When a topic wants its own pair (a chef and a food inspector, a rookie detective and a veteran), draw them in the project's `characters.py`; `templates/characters.py` includes a worked example (an owl).

1. Subclass `cast.Character`. Build it only from simple shapes (`RoundedRectangle`, `Circle`, `Ellipse`, `Line`, `Polygon`) in the palette, with one signature colour (`COLOR`) that matches its role (`TEAL` for LEAD, `PURPLE` for CHECK, or another palette colour that is not already used for meaning on screen).
2. Draw it standing, centred on x = 0, about 3.4 units tall at scale 1 with its feet at the bottom, so it can replace Chip or Brick anywhere.
3. Give it a face that reads at small sizes: big eyes, a clear mouth. Set `self.mouth = make_mouth("smile", centre, MOUTH_W, MOUTH_COLOR)` and the class attributes `MOUTH_W` and `MOUTH_COLOR` so `face()` works. Keep other animatable parts as attributes.
4. End `__init__` with `self._done(scale)`.
5. Set `LEAD, CHECK = YourLead, YourCheck` at the end of `characters.py` and the names in `NAMES`.
6. Look at it in a still on a title card and in the bridge before using it everywhere.

Never use copyrighted or branded characters, logos, mascots, real people's likenesses or memes from existing media.

## Tone

A casual TA talking to a friend: as fun as possible, real jokes and everyday analogies, never talking down. Keep the source's conclusions and bluntness; say plainly on screen when something is secondhand, a guess or unverified.
