"""List every shipped file that still contains CJK text, with its character count.

The package is English.  Three deliberate categories keep Chinese (see
``EVALS/RAW_EVIDENCE_NOTE.md``):

* the verbatim per-call API records under ``**/api_cache/`` and ``**/runs/``,
* verbatim source text inside the frozen dataset,
* the byte-identical originals of the frozen round code under ``CODE/_frozen_code/``.

(That note itself contains Chinese, because it quotes the text it is describing.)

This script exists so the claim can be checked rather than believed:

    python CODE/scan_cjk.py            # list every file, worst first
    python CODE/scan_cjk.py --summary  # counts per category only

Exit status is 0 when the only hits are in those three categories, and 1 when a
file outside them contains Chinese.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CJK = re.compile("[\u4e00-\u9fff]")
TEXT_SUFFIXES = {".md", ".py", ".json", ".txt", ".yaml", ".yml", ".html", ".js",
                 ".csv", ".jsonl", ".toml", ".ps1", ".bat", ".sh", ".mjs", ".ts"}
SKIP_PARTS = {".git", "reproduced_run", "__pycache__", ".pytest_cache"}


def category(rel: str) -> str:
    """Which declared exception, if any, this path belongs to."""
    if rel == "EVALS/RAW_EVIDENCE_NOTE.md":
        # The note quotes the Chinese it is describing; it cannot avoid doing so.
        return "D · this note (quoted examples)"
    if "/api_cache/" in rel or "/runs/" in rel:
        return "A · verbatim per-call API record"
    if rel.startswith("CODE/_frozen_code/"):
        return "C · preserved original of frozen round code"
    if rel.startswith("DATA/"):
        return "B · verbatim dataset text"
    return "UNDECLARED"


def scan():
    for p in sorted(REPO.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(REPO).as_posix()
        if any(part in SKIP_PARTS for part in rel.split("/")):
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        n = len(CJK.findall(text))
        if n:
            yield n, len(text), rel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--summary", action="store_true", help="counts per category only")
    args = ap.parse_args()

    hits = sorted(scan(), reverse=True)
    counts: dict[str, int] = {}
    undeclared = []
    for n, size, rel in hits:
        cat = category(rel)
        counts[cat] = counts.get(cat, 0) + 1
        if cat == "UNDECLARED":
            undeclared.append(rel)
        if not args.summary:
            print(f"  {n:7d} cjk  {size:9d} bytes  {rel}")

    print(f"\nfiles containing CJK: {len(hits)}")
    for cat in sorted(counts):
        print(f"  {counts[cat]:5d}  {cat}")
    if undeclared:
        print("\nUNDECLARED Chinese outside the three documented categories:")
        for rel in undeclared:
            print(f"  {rel}")
        return 1
    print("\nEvery hit is inside a category declared in EVALS/RAW_EVIDENCE_NOTE.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
