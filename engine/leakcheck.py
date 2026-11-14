"""Flag narration or on-screen text that shares wording or distinctive numbers with a file that must
not leak into the video (for example a sealed sample exam).

Checked: every segment's say and cap (script/chN_segments.py, all chapters in project.json) and every
quoted string in chapters/*.py (docstrings skipped). A string is flagged when it shares
  - any run of 6 words with the file (case, punctuation and quote style ignored), or
  - a distinctive number: 3+ digits, a decimal, a percentage or a money amount ("$1,240", "12.5%",
    "0.75", "2031"); numbers are compared by value, so "$1,240" in the file flags "1240 dollars" on screen.
The file may be .md/.txt (read as text), .json (all string values) or .html (tags stripped).
Exit status 1 when anything is flagged.
"""
import ast
import json
import pathlib
import re
from decimal import Decimal, InvalidOperation

import project

N = 6
QUOTES = {"‘": "'", "’": "'", "“": '"', "”": '"'}


def read_target(path):
    p = pathlib.Path(path)
    if not p.exists():
        raise SystemExit(f"{p} not found")
    raw = p.read_text(errors="replace")
    if p.suffix.lower() == ".json":
        out = []

        def walk(x):
            if isinstance(x, str):
                out.append(x)
            elif isinstance(x, dict):
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(json.loads(raw))
        return "\n".join(out)
    if p.suffix.lower() in (".html", ".htm"):
        return re.sub(r"<[^>]+>", " ", raw)
    return raw


def words(s):
    for k, v in QUOTES.items():
        s = s.replace(k, v)
    return re.findall(r"[a-z0-9]+", s.lower())


def grams(ws):
    return {tuple(ws[i:i + N]) for i in range(len(ws) - N + 1)}


NUM_RE = re.compile(
    r"(?P<money>[$€£]\s?\d[\d,]*(?:\.\d+)?)"
    r"|(?P<pct>\d[\d,]*(?:\.\d+)?\s?(?:%|percent\b))"
    r"|(?P<dec>\d[\d,]*\.\d+)"
    r"|(?P<big>\d{1,3}(?:,\d{3})+|\d{3,})")


def numbers(s):
    """Distinctive numbers in s, as {canonical value: original text}."""
    out = {}
    for mm in NUM_RE.finditer(s):
        text = mm.group(0)
        bare = re.sub(r"[^\d.]", "", text).rstrip(".")
        try:
            val = str(Decimal(bare).normalize()) if "." in bare else str(int(bare))
        except (InvalidOperation, ValueError):
            continue
        out.setdefault(val, text.strip())
    return out


def screen_strings(path):
    """(line, text) for every string constant in a chapter file, docstrings excluded."""
    tree = ast.parse(path.read_text())
    doc_ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                doc_ids.add(id(first.value))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in doc_ids:
            s = node.value
            if re.fullmatch(r"#[0-9a-fA-F]{3,8}", s) or not s.strip():
                continue
            out.append((node.lineno, s))
    return out


def run(target):
    root = project.root()
    text = read_target(target)
    tgrams = grams(words(text))
    tnums = numbers(text)
    items = []   # (where, text)
    for ch in project.chapters():
        f = root / "script" / f"{ch}_segments.py"
        if f.exists():
            for s in project.segments(ch):
                items.append((f"script/{f.name} id {s['id']} say", s["say"]))
                if s.get("cap") and s["cap"] != s["say"]:
                    items.append((f"script/{f.name} id {s['id']} cap", s["cap"]))
    for f in sorted((root / "chapters").glob("*.py")):
        for line, s in screen_strings(f):
            items.append((f"chapters/{f.name}:{line}", s))
    flags = []
    for where, s in items:
        shared = sorted(grams(words(s)) & tgrams)
        if shared:
            flags.append((where, s, "6 words: \"" + " ".join(shared[0]) + "\"" +
                          (f" (+{len(shared) - 1} more)" if len(shared) > 1 else "")))
        common = sorted(set(numbers(s)) & set(tnums))
        if common:
            flags.append((where, s, "number: " + ", ".join(f"{numbers(s)[v]} (file: {tnums[v]})" for v in common)))
    print(f"checked {len(items)} narration and on-screen strings against {target} "
          f"({len(tgrams)} 6-word runs, {len(tnums)} distinctive numbers)")
    if not flags:
        print("nothing shared")
        return 0
    print(f"\n{len(flags)} FLAG(S): reword these or change the numbers")
    for where, s, why in flags:
        short = s if len(s) <= 110 else s[:107] + "..."
        print(f"  {where}: {why}\n      {short!r}")
    return 1
