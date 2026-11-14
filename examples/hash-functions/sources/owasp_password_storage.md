# OWASP Cheat Sheet Series: Password Storage

- URL: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- Publisher: OWASP (Open Worldwide Application Security Project)
- Retrieved: 2026-11-14 (living document; no single publication date)

Exact excerpts read through a web-fetch tool (the build machine could not download the page directly).

## Excerpts

- "Because hashing is a one-way function (i.e., it is impossible to "decrypt" a hash and obtain the original plaintext value), it is the most appropriate approach for password validation."
- "Instead, they must be protected using strong, slow hashing algorithms such as Argon2id, bcrypt, or PBKDF2."
- "Fast hashing algorithms such as SHA-256 are not suitable for password storage"
- "Using slow, memory-hard algorithms makes brute-force attacks significantly more difficult, expensive, and time-consuming."
- "A salt is a unique, randomly generated string that is added to each password as part of the hashing process."
- "Passwords should be securely hashed using modern, adaptive hashing algorithms" (sentence continues; truncated by the fetch tool)
