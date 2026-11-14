"""Check script/claims.md: every quoted source phrase must appear in the source file it names.

claims.md holds a markdown table with a "Source" column. Each Source cell holds either
    sources/<file>.md: "exact quote"           (one or more quotes; several files may follow each other)
or a URL (listed for the main session to open; not checked here). Both the quote and the source text
are normalised before matching: markdown links become their text, emphasis marks and brackets are
dropped, dashes become "-", quote marks are ignored (write a quote inside a quote as \" or '),
whitespace collapses, case is ignored, and "..." inside a quote stands for omitted words.

Exit status 1 when any quote is not found, a source file is missing, or a row has no source.
"""
import re
import unicodedata

import project

DASHES = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"
QUOTE_MAP = {"\u201c": '"', "\u201d": '"', "\u201e": '"', "\u00ab": '"', "\u00bb": '"',
             "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u2032": "'", "\u2033": '"'}


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)        # [text](url) -> text
    s = re.sub(r"<(https?://[^>]+)>", r"\1", s)
    for k, v in QUOTE_MAP.items():
        s = s.replace(k, v)
    for d in DASHES:
        s = s.replace(d, "-")
    s = s.replace("\u2026", "...").replace("\u00a0", " ")
    s = re.sub(r"[\[\]{}()]", "", s)                          # brackets, e.g. editorial [sic] marks
    s = re.sub(r"(\*\*|__|\*|`)", "", s)                      # markdown emphasis and code marks
    s = re.sub(r"[\"']", "", s)                               # quote marks (so quotes inside quotes match)
    s = re.sub(r"\s*-\s*", "-", s)                            # "a - b" == "a-b" == "a — b"
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def found(q, text):
    """q in text, where "..." in q stands for omitted words (the pieces must appear in order)."""
    pos = 0
    for piece in [x.strip() for x in q.split("...") if x.strip()]:
        i = text.find(piece, pos)
        if i < 0:
            return False
        pos = i + len(piece)
    return True


def split_row(line):
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def parse_table(text):
    """Yield (line_no, row dict keyed by lower-case header) for every table in the file."""
    hdr = None
    lines = text.splitlines()
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if not s.startswith("|"):
            hdr = None
            continue
        if re.match(r"^\|[\s:|-]+\|?$", s):
            continue
        cells = split_row(s)
        if hdr is None:
            hdr = [c.lower() for c in cells]
            continue
        yield i, dict(zip(hdr, cells))


def source_cell(row):
    for k, v in row.items():
        if "source" in k:
            return v
    return None


def parse_cell(cell):
    """-> (list of (file, quote), list of urls). Curly quotes are straightened first."""
    c = cell.replace("\\|", "|")
    c = re.sub(r"\[([^\]]*)\]\(([^)]*)\)", lambda mm: mm.group(1) if mm.group(1).startswith("sources/") else mm.group(2), c)
    for k, v in QUOTE_MAP.items():
        c = c.replace(k, v)
    pairs = []
    parts = re.split(r"(?=\bsources/)", c)
    for p in parts:
        mm = re.match(r"(sources/[^\s:\"]+)\s*:?\s*(.*)", p, re.S)
        if not mm:
            continue
        quotes = [q.replace('\\"', '"') for q in re.findall(r'"((?:[^"\\]|\\.)+)"', mm.group(2))]
        if not quotes:
            pairs.append((mm.group(1), None))
        for q in quotes:
            pairs.append((mm.group(1), q))
    urls = re.findall(r"https?://[^\s)>\]|\"]+", c)
    return pairs, urls


def run():
    root = project.root()
    f = root / "script" / "claims.md"
    if not f.exists():
        raise SystemExit(f"{f} is missing")
    cache, problems = {}, []
    n_rows = n_quotes = n_found = 0
    url_rows = []
    for line_no, row in parse_table(f.read_text()):
        cell = source_cell(row)
        if cell is None:
            continue
        n_rows += 1
        claim = next((v for k, v in row.items() if "claim" in k), None) or next(iter(row.values()), "")
        pairs, urls = parse_cell(cell)
        if not pairs and not urls:
            problems.append((line_no, claim, "no source: give sources/<file>.md: \"quote\" or a URL"))
            continue
        for path, q in pairs:
            if q is None:
                problems.append((line_no, claim, f"{path}: no quote given"))
                continue
            n_quotes += 1
            sp = root / path
            if path not in cache:
                cache[path] = norm(sp.read_text(errors="replace")) if sp.exists() else None
            if cache[path] is None:
                problems.append((line_no, claim, f"{path}: file not found"))
            elif not found(norm(q), cache[path]):
                problems.append((line_no, claim, f'{path}: quote not found: "{q}"'))
            else:
                n_found += 1
        if urls and not pairs:
            url_rows.append((line_no, claim, urls))
    print(f"{f}: {n_rows} claims, {n_quotes} quotes checked, {n_found} found, {len(url_rows)} cite only URLs")
    if url_rows:
        print("\nURL-only rows (open these yourself):")
        for line_no, claim, urls in url_rows:
            print(f"  line {line_no}: {claim[:70]}  ->  {' '.join(urls)}")
    if problems:
        print(f"\n{len(problems)} PROBLEM(S):")
        for line_no, claim, msg in problems:
            print(f"  line {line_no}: {claim[:70]}\n      {msg}")
        return 1
    print("all quotes found")
    return 0
