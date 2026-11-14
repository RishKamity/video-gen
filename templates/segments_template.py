# Narration for chapter 1, by segment (docs/SCRIPT_FORMAT.md). Replace the placeholder lines.
#   id     unique integer; its WAV is audio/ch1/NNN.wav (001, 002, ...)
#   scene  the scene key: the NAME of a scene class in chapters/ch1.py; a scene's segments sit together
#   say    exactly what the voice reads: 1-3 sentences; numbers, years and acronyms written as spoken
#   cap    optional caption text when it should read differently from say ("2.5%" for "two point five percent")
#   pause  optional extra silence after the segment, in seconds (3.0 after every recall question)
SEGMENTS = [
 # sc01: recap hook, then one idea
 dict(id=1, scene="sc01_idea",
      say="Quick recap, then a question: what if every screen taught exactly one thing? That's the rule here."),
 dict(id=2, scene="sc01_idea",
      say="A key term, like recall, pops up as a pill the moment it's said. Chip tries things first, and Brick checks them."),
 # sc02: two recall questions, each followed by a three-second countdown, then the bridge
 dict(id=3, scene="sc02_recall", say="Quick check: what does a term pill do?", pause=3.0),
 dict(id=4, scene="sc02_recall", say="It puts the key word on screen the moment the narrator says it."),
 dict(id=5, scene="sc02_recall", say="Second one: how many ideas go on one screen?", pause=3.0),
 dict(id=6, scene="sc02_recall", say="Just one. One idea per screen."),
 dict(id=7, scene="sc02_recall", say="Next up: chapter two, where the real content starts."),
]
