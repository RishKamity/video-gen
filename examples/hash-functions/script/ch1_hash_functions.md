# Chapter 1: What's a hash function? — narration script

One chapter, about 75 seconds, for a total beginner. `vg.py <project> join` reads the first line, the "Recall questions" section and the "Sources" table into `script/full_script.md`.

## Narration

The narration as captioned, scene by scene (the same text as `script/ch1_segments.py`).

**sc00_title** (4 s, no narration): "What's a hash function?" / "a fingerprint for any data"

**sc01_hook**

1. Good websites can check your password without storing it, thanks to a hash function.

**sc02_fingerprint**

2. A hash function, like Whizz here, turns any input, even a whole movie, into a short, fixed-length code.
3. Same input, same code, every time: a fingerprint. Add one letter, cat to cats, and it totally changes.

**sc03_oneway**

4. It's one-way, too: no practical way to run it backwards. Like un-blending a smoothie.
5. So sites store only your password's fingerprint, then hash each login try and compare.

**sc04_collision**

6. A collision is two different inputs, one fingerprint. Good hashes make those practically impossible to find.
7. In 2017, researchers found one for SHA-1: two different PDFs, one fingerprint.

**sc05_recall**

8. Quick check: can a site reverse your password's hash? (3 s countdown)
9. Nope. Sites just compare fingerprints.
10. Second one: what's a collision? (3 s countdown)
11. Two different inputs, same hash.
12. That's hashing. Go flex in the group chat.

## On-screen plan

What each scene shows, and when (the phrase it is cued on). One idea per screen; every outside figure, quote or incident gets a source tag with its label.

- sc00_title: "CHAPTER 1", title, subtitle; Whizz (blender) and Latch (padlock) slide in.
- sc01_hook: a "Log in" card (username, dotted password) and Latch at the door (seg 1 start); a database labelled "no passwords stored" ("without storing"); the "hash function" pill ("thanks to").
- sc02_fingerprint: "hash function" pill and Whizz (seg 2 start), Whizz hops ("Whizz"); a "cat" chip drops into the jar ("any input"), then a movie.mp4 file ("whole movie"); arrow to the real SHA-256 of "cat", 77af778b51abd4a3..., labelled 'SHA-256 of "cat"' ("into a short"); "SHA-256: always 64 characters" ("fixed-length"). Seg 3: rows cat -> 77af778b..., cat -> 77af778b... with a green "same" check ("same code"); "fingerprint" pill over Whizz ("a fingerprint"); cats -> d936608baaacc6b7... in red, "totally different" ("cat to cats").
- sc03_oneway: "one-way" pill, "input" -> "fingerprint" with a green "easy" arrow (seg 4 start); a red arrow back with an X, "no practical way to run it backwards" ("no practical"); Whizz looks worried beside a smoothie cup, "un-blend?" ("like un-blending"). Seg 5: database "stored: fingerprint only" ("store only"); a login card of dots -> Whizz -> "fingerprint" pill ("then hash", "login try"); "=" and Latch holding MATCH ("and compare"); a note "guessable passwords can still be guessed, so sites use slow hashes like bcrypt" [verified] and the tag "OWASP Password Storage Cheat Sheet; WashU InfoSec, Oct 27, 2022" [verified].
- sc04_collision: red "collision" pill; "input A" and "input B" ("two different") -> one "same fingerprint" box ("one fingerprint"); "good hashes: practically impossible to find" and the tag "NIST glossary, from SP 800-107 Rev. 1" [verified] ("good hashes"). Seg 7: "2017" and "SHA-1" pills; PDF 1 and PDF 2 ("found one") -> "same SHA-1 hash" ("two different"); a "COLLISION FOUND" stamp, Latch shocked, tags "Google Security Blog, Feb 23, 2017" [verified] and "NIST: phase SHA-1 out by Dec 31, 2030 (Dec 15, 2022)" [verified].
- sc05_recall: QUICK CHECK, two questions with countdowns, then "That's hashing!" with Whizz and Latch.

## Recall questions (shown, ~3 s countdown, then answered)

1. **Can a site reverse your password's hash?**  
   Answer: No. Sites just compare fingerprints.
2. **What's a collision?**  
   Answer: Two different inputs, same hash.

## Bridge to the next chapter

None (last chapter). Sign-off: "That's hashing. Go flex in the group chat."

## Sources

| Fact used | Source | URL | Date |
|---|---|---|---|
| Hash function: arbitrary-length input to a fixed-length output; "fingerprint" | NIST CSRC Glossary, "hash function" (SP 800-107 Rev. 1, SP 800-152) | https://csrc.nist.gov/glossary/term/hash_function | retrieved 2026-11-14 |
| Collision; collision resistance | NIST CSRC Glossary, "collision", "collision resistance" | https://csrc.nist.gov/glossary/term/collision | retrieved 2026-11-14 |
| One-way (preimage resistance) | NIST CSRC Glossary, "preimage resistance" | https://csrc.nist.gov/glossary/term/preimage_resistance | retrieved 2026-11-14 |
| Hashing is one-way; use slow password hashes (Argon2id, bcrypt, PBKDF2) | OWASP Password Storage Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html | retrieved 2026-11-14 |
| Systems store the hashed password and compare at login | WashU Office of Information Security, "Password-based Authentication" | https://informationsecurity.wustl.edu/?p=5802 | Oct 27, 2022 |
| First practical SHA-1 collision: two PDFs, same hash | Google Security Blog, "Announcing the first SHA1 collision" | https://security.googleblog.com/2017/02/announcing-first-sha1-collision.html | Feb 23, 2017 |
| SHA-1 to be phased out by Dec 31, 2030 | NIST, "NIST Retires SHA-1 Cryptographic Algorithm" | https://www.nist.gov/news-events/news/2022/12/nist-retires-sha-1-cryptographic-algorithm | Dec 15, 2022 |
| SHA-256 of cat and cats; 64 hex characters | Computed with Python hashlib (sources/sha256_demo.md) | | 2026-11-14 |
