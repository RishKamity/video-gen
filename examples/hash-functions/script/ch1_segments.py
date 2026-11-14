# Narration for chapter 1, "What's a hash function?" (docs/SCRIPT_FORMAT.md). One chapter, about 70 s.
SEGMENTS = [
 # sc01: hook (the only chapter, so no recap): sites check passwords they never store
 dict(id=1, scene="sc01_hook",
      say="Good websites can check your password without storing it, thanks to a hash function."),
 # sc02: any input in, fixed-size fingerprint out; same in, same out; one letter changes everything
 dict(id=2, scene="sc02_fingerprint",
      say="A hash function, like Whizz here, turns any input, even a whole movie, into a short, fixed-length code."),
 dict(id=3, scene="sc02_fingerprint",
      say="Same input, same code, every time: a fingerprint. Add one letter, cat to cats, and it totally changes."),
 # sc03: one-way, so sites store the fingerprint and compare at login
 dict(id=4, scene="sc03_oneway",
      say="It's one-way, too: no practical way to run it backwards. Like un-blending a smoothie."),
 dict(id=5, scene="sc03_oneway",
      say="So sites store only your password's fingerprint, then hash each login try and compare."),
 # sc04: collisions, and the real SHA-1 collision
 dict(id=6, scene="sc04_collision",
      say="A collision is two different inputs, one fingerprint. Good hashes make those practically impossible to find."),
 dict(id=7, scene="sc04_collision",
      say="In twenty seventeen, researchers found one for S H A one: two different PDFs, one fingerprint.",
      cap="In 2017, researchers found one for SHA-1: two different PDFs, one fingerprint."),
 # sc05: two recall questions, then the sign-off (last chapter)
 dict(id=8, scene="sc05_recall", say="Quick check: can a site reverse your password's hash?", pause=3.0),
 dict(id=9, scene="sc05_recall", say="Nope. Sites just compare fingerprints."),
 dict(id=10, scene="sc05_recall", say="Second one: what's a collision?", pause=3.0),
 dict(id=11, scene="sc05_recall", say="Two different inputs, same hash."),
 dict(id=12, scene="sc05_recall", say="That's hashing. Go flex in the group chat."),
]
