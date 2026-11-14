# SHA-256 demo (computed)

Computed locally on 2026-11-14 with Python 3.13 `hashlib.sha256` (UTF-8 input). This is a primary computation, not a quote from a publication; anyone can re-run it.

```python
import hashlib
hashlib.sha256(text.encode()).hexdigest()
```

| Input | SHA-256 (hex) | Hex characters |
|---|---|---|
| `cat` | `77af778b51abd4a3c51c5ddd97204a9c3ae614ebccb75a606c3b6865aed6744e` | 64 |
| `cats` | `d936608baaacc6b762c14b0c356026fba3b84e77d5b22e86f2fc29d3da09c675` | 64 |
| `cat` | `77af778b51abd4a3c51c5ddd97204a9c3ae614ebccb75a606c3b6865aed6744e` | 64 |
| `Cat` | `48735c4fae42d1501164976afec76730b9e5fe467f680bdd8daff4bb77674045` | 64 |
| a 110,000-character text | `b7f1230468cbca4e4231566ba3b318af530e3575a1d6102b482b13a94358d560` | 64 |

Findings:

- The input cat hashed twice gives the same output both times: 77af778b51ab...
- Changing cat to cats changes the output completely: cat starts 77af778b, cats starts d936608b.
- Every SHA-256 output above is 64 hex characters long, whether the input is 3 characters or 110,000 characters.
