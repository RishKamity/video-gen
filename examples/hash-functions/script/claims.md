# Claims check: What is a hash function?

Every factual or numeric claim in the narration (`N3` = said in segment 3) and in the planned on-screen text (`S3` = shown during segment 3), one row each. Analogies, jokes and plain-language definitions written for the video are not listed.

- **Source** holds either `sources/<file>.md: "a short exact quote"` (one or more quotes; `...` inside a quote stands for omitted words) or the URL that was opened. `vg.py <project> claims` checks every quote against the file and lists URL-only rows for the main session to open.
- **Label** is how the video presents the claim on screen: `verified`, `secondhand`, `a guess`, `unverified` or `estimate` (docs/STYLE.md). Keep the source's own labels.

**Fact-check edits (main session, before narration):** "Websites" became "Good websites" (not every site hashes); "Change one letter, cat to cats" became "Add one letter" (cats adds a letter); "no practical way back to the input" became "no practical way to run it backwards", the one-way screen shows a generic input instead of "cat" (anyone can hash "cat" and compare), and the login screen notes that guessable passwords can still be guessed; "two inputs" became "two different inputs"; "always 64 characters long" became "SHA-256: always 64 characters" (the length is SHA-256's, not every hash's).

**Label changes from the source (for the main session to confirm):** none. All sources are primary or reliable (NIST, OWASP, a university security office, the researchers' own announcement, a local computation), so every claim is `verified`.

| Ch | Seg | Claim | Label | Source |
|---|---|---|---|---|
| ch1 | N1 | Good websites can check your password without storing it (they store a hash and compare) | verified | sources/wustl_password_authentication.md: "A system will store the "hashed password" in its database" "compute the "hashed password" again and compare it to the one in the database" |
| ch1 | N2 | A hash function turns input of any length into a code of fixed length | verified | sources/nist_glossary_hash_function.md: "A function that maps a bit string of arbitrary length to a fixed-length bit string." |
| ch1 | N2 | The output is short (a condensed representation) | verified | sources/nist_glossary_hash_function.md: "The output often serves as a condensed representation of the input." |
| ch1 | S2 | SHA-256 of "cat" begins 77af778b51abd4a3 | verified | sources/sha256_demo.md: "77af778b51abd4a3c51c5ddd97204a9c3ae614ebccb75a606c3b6865aed6744e" |
| ch1 | S2 | A SHA-256 output is always 64 characters long (on screen: "SHA-256: always 64 characters") | verified | sources/sha256_demo.md: "Every SHA-256 output above is 64 hex characters long, whether the input is 3 characters or 110,000 characters." sources/nist_glossary_hash_function.md: "A function on bit strings in which the length of the output is fixed." |
| ch1 | N3 | Same input gives the same code every time | verified | sources/sha256_demo.md: "The input cat hashed twice gives the same output both times" |
| ch1 | N3 | A hash is like a fingerprint for data | verified | sources/nist_glossary_hash_function.md: "A hash function can be considered to be a fingerprint of the file or message." |
| ch1 | N3, S3 | Adding one letter, cat to cats, totally changes the code (77af778b... vs d936608b...) | verified | sources/sha256_demo.md: "Changing cat to cats changes the output completely: cat starts 77af778b, cats starts d936608b." |
| ch1 | N4, S4 | A hash is one-way: no practical way to run it backwards | verified | sources/nist_glossary_preimage_resistance.md: "it is computationally infeasible to find a preimage" sources/owasp_password_storage.md: "hashing is a one-way function" |
| ch1 | N5 | Sites store only the password's hash, hash each login attempt and compare | verified | sources/wustl_password_authentication.md: "A system will store the "hashed password" in its database beside the respective user ID and salt value." "the system will compute the "hashed password" again and compare it to the one in the database." |
| ch1 | S5 | Guessable passwords can still be guessed (brute force), so sites should use slow password hashes like bcrypt | verified | sources/owasp_password_storage.md: "strong, slow hashing algorithms such as Argon2id, bcrypt, or PBKDF2" "Using slow, memory-hard algorithms makes brute-force attacks significantly more difficult" |
| ch1 | N6 | A collision is two different inputs with the same output | verified | sources/nist_glossary_collision.md: "An event in which two different messages have the same message digest." |
| ch1 | N6, S6 | Good hash functions make collisions practically impossible to find | verified | sources/nist_glossary_collision.md: "An expected property of a hash function whereby it is computationally infeasible to find a collision" |
| ch1 | N7 | In 2017 researchers found a SHA-1 collision | verified | sources/google_sha1_collision_2017.md: "Date: February 23, 2017" "we are announcing the first practical technique for generating a collision" |
| ch1 | N7, S7 | Two different PDFs had the same SHA-1 hash | verified | sources/google_sha1_collision_2017.md: "two PDFs that have identical SHA-1 hashes but different content" |
| ch1 | S7 | NIST says SHA-1 should be phased out by Dec 31, 2030 (announced Dec 15, 2022) | verified | sources/nist_retires_sha1_2022.md: "SHA-1 should be phased out by Dec. 31, 2030" "Date: December 15, 2022" |
| ch1 | N9 | A site cannot reverse a hash; it compares hashes | verified | sources/owasp_password_storage.md: "it is impossible to "decrypt" a hash" sources/wustl_password_authentication.md: "compare it to the one in the database" |
| ch1 | N11 | A collision is two different inputs with the same hash | verified | sources/nist_glossary_collision.md: "Two or more distinct inputs produce the same output." |
