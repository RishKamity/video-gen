# Course-pack mode (videos for a study guide)

When the source is a study-guide course pack (`courses/<id>/` in a clone of the study-guide engine; read that repo's `docs/CONTENT_FORMAT.md` for the pack's files), the videos are short, one per exam topic, and can ship inside the study app.

## Shape

- **One video per exam topic, 2-4 minutes**, in the pack's topic order. The grilling asks which units to cover, not a per-topic outline.
- Each topic is one "chapter" of the project: chapter ids `ch1`, `ch2`, ... in topic order (list them in `project.json`), with `OUT_NAME` set to the topic id so the files are named by topic (`OUT_NAME = "8A"` -> `out/8A.mp4`).
- Title card: `Title = make_title("8A", "<topic title>", "<one-line promise>", kicker="TOPIC 8A")`.
- No primer chapter; a short recap hook can name the topic before it.

## Content

- Content comes from the pack's stations (rules, worked examples, exam traps) and the course files behind them. The course's own terms, notation and conventions win over outside sources; when course sources disagree, the lecture slides win.
- Save the station text and the course excerpts you use in `sources/` so `claims` can check quotes against them.
- Worked examples on screen: rebuild them with **new numbers** of your own, never the course's or the sample exam's.

## Recall questions

The two recall questions per video come from that topic's **question bank**: pick a question and use one of its reworded `alts`, never its main wording. The answer on screen is the bank's answer, shortened.

## Never use the sealed sample exam

Nothing from the sealed sample exam may appear in a video: not its questions, wording, numbers or scenarios. Before any narration is recorded, and again after any script change:

```bash
$PY $VG <project> leakcheck <path to the sample exam file>
```

It flags every segment (`say` and `cap`) and every quoted string in `chapters/*.py` that shares a run of 6 words or a distinctive number (3+ digits, a decimal, a percentage or money, compared by value) with the file. The file can be Markdown or text, JSON (all string values are read) or HTML. Exit status 1 when anything is flagged: reword or renumber until it is clean, then run `claims` again.

## App copies

The study app plays small copies:

```bash
$PY $VG <project> app-copies
```

writes `out/app/<OUT_NAME>.mp4` for every chapter: 1280x720 H.264 (high profile, CRF 23 under a bitrate cap chosen from the length) with AAC 128 kb/s, `+faststart`, each checked to be **under 20 MB** (re-encoded at a lower cap if not). A 4-minute topic usually lands well under the limit.

## Watch buttons in the study app

Videos are an optional extra on the study guide's Full tier (an intake question, default No, because rendering takes several times the video's length). Each topic's station shows a Watch button that plays its app copy. Publishing limits for the copies: at most 20 MB per file and 64 MB per publish call, so spread a long course over several republishes of the same artifact. Changes to the study-guide engine itself are proposed to the user first and pushed only after they agree.
