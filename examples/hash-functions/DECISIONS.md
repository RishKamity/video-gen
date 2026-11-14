# Decisions: What is a hash function?

What was decided in the grilling (or the default taken when nobody answered). The builder agent reads this; the locked house style (docs/STYLE.md) is not repeated here.

Request: "/video-gen teach me what a hash function is". The user was away, so the skill's defaults were taken except where the request fixed a choice (one chapter of about 60-75 seconds, no checkpoint).

| Decision | Choice | Default (used if the user is away) | Source of the choice |
|---|---|---|---|
| Viewer level | Total beginner; no separate primer chapter, so the one chapter teaches every term from zero | Total beginner; add a primer chapter (Chapter 0) teaching the vocabulary | Request (one chapter only) |
| Length and split | One chapter, about 60-75 seconds | About 5 min per chapter for dense material, 2-3 for light | Request |
| Chapter outline | What a hash is (fixed-size fingerprint, same input same output, one letter changes everything), one-way and password logins, collisions and SHA-1 | The source's own order; titles and minutes proposed | Default (no source document; ordered from definition to use to failure) |
| Characters (LEAD, CHECK) | LEAD: Whizz, an overeager teal blender who blends any input into a fingerprint. CHECK: Latch, a calm purple padlock who guards the login and checks fingerprints | An original pair that fits the topic, drawn from simple shapes | Default |
| Flavor | Generic student life (group chat, smoothies, logging in) | The viewer's own school or campus life if known; otherwise generic student life | Default, generic version: this project is committed to a public repo as a demo, so no personal or school details |
| Fresh research | Yes: NIST glossary definitions (hash function, collision, collision and preimage resistance), OWASP and a university security office on password storage, and one incident (the 2017 SHA-1 collision) plus NIST retiring SHA-1 | Yes: verified background definitions and 1-3 real, well-documented examples with sources | Default |
| Checkpoint | None | Two or more chapters: build the first, send it, wait for a reaction, then the rest | Request (and only one chapter) |
| Extras | None beyond MP4 + .srt + script | None beyond MP4 + .srt + script | Default |

## Outline

| Chapter | Title | Minutes (target) | Main ideas |
|---|---|---|---|
| ch1 | What's a hash function? | 1.0-1.25 | Hook (sites check passwords they never store); any input in, fixed-size fingerprint out; same input same output, one letter changes everything (real SHA-256 values); one-way, so sites store the hash and compare at login (real sites use slow password hashes); collisions, the 2017 SHA-1 collision, NIST retiring SHA-1; two recall questions; sign-off |

## Sources

One `.md` per source in `sources/` (extracted text), so `vg.py <project> claims` can read it.

| File | What it is | Where it came from | Date |
|---|---|---|---|
| nist_glossary_hash_function.md | NIST glossary definitions of hash function | https://csrc.nist.gov/glossary/term/hash_function | retrieved 2026-11-14 |
| nist_glossary_collision.md | NIST glossary: collision, collision resistance | https://csrc.nist.gov/glossary/term/collision | retrieved 2026-11-14 |
| nist_glossary_preimage_resistance.md | NIST glossary: preimage resistance (one-way) | https://csrc.nist.gov/glossary/term/preimage_resistance | retrieved 2026-11-14 |
| owasp_password_storage.md | OWASP Password Storage Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html | retrieved 2026-11-14 |
| wustl_password_authentication.md | WashU Information Security, "Password-based Authentication" | https://informationsecurity.wustl.edu/?p=5802 | Oct 27, 2022 |
| google_sha1_collision_2017.md | Google Security Blog, "Announcing the first SHA1 collision" | https://security.googleblog.com/2017/02/announcing-first-sha1-collision.html | Feb 23, 2017 |
| nist_retires_sha1_2022.md | NIST news, "NIST Retires SHA-1 Cryptographic Algorithm" | https://www.nist.gov/news-events/news/2022/12/nist-retires-sha-1-cryptographic-algorithm | Dec 15, 2022 |
| sha256_demo.md | SHA-256 of cat, cats and a long text, computed with Python hashlib | computed locally | 2026-11-14 |

## Notes

- Defaults taken without an answer: viewer level (beginner), outline, characters, flavor (generic), fresh research, extras.
- The build machine's network refused direct downloads of every source site, so `sources/` holds exact excerpts read through a web-fetch tool rather than full page text.
- Names the voice may mispronounce: "SHA-1" (written "S H A one" in `say`), "SHA-256" (written "S H A two fifty-six"), "Whizz", "Latch".
