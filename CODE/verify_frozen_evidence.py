"""Frozen-evidence integrity check for the PE6201 ViralLoop submission package.

Why this exists
---------------
The report, the explainers and every figure in them cite artefacts that live
under ``DATA/`` and ``EVALS/``.  Those artefacts are the *frozen evidence*: they
are the output of the three rounds as they were actually run.

Reproducing a round is a different activity from submitting it.  If a
reproduction ever wrote into ``DATA/`` or ``EVALS/``, the numbers the report
cites would silently stop matching the files on disk.  This script makes that
failure impossible to miss.

Usage
-----
    python CODE/verify_frozen_evidence.py --check      # default: verify
    python CODE/verify_frozen_evidence.py --write      # (re)build the manifest
    python CODE/verify_frozen_evidence.py --check --quiet

Exit status is 0 when the evidence matches the manifest and 1 when anything was
added, removed or changed, so it can be used as a pre-commit or CI gate.

Deliberate exclusions
---------------------
``__pycache__`` / ``*.pyc`` (interpreter build output) and the manifest itself.
Everything else under the two evidence roots is covered -- including the
``api_cache`` call caches and the embedding vectors that make an offline
reproduction possible, so that a later cache refresh cannot pass unnoticed.
The append-only provenance logs listed in ``EXTRA_FILES`` are covered too, even
though they live under ``CODE/``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOTS = ("DATA", "EVALS")
MANIFEST = REPO / "EVALS" / "FROZEN_EVIDENCE_MANIFEST.json"
SKIP_DIRS = {"__pycache__"}
SKIP_SUFFIXES = {".pyc", ".pyo"}

# Append-only provenance logs that sit under CODE/ rather than DATA/ or EVALS/.
# They record the original run, so a reproduction must not append to them either:
# CODE/_packaged_paths.reproduction_copy() continues them in the round's own
# reproduced_run/logs/ folder.  They are covered here so a stray append is caught.
EXTRA_FILES = (
    "CODE/round2_v002/events_v002.jsonl",
    "CODE/round2_v002/process_archive_v002.md",
    "CODE/round3_v003/events_v003.jsonl",
    "CODE/round3_v003/process_archive_v003.md",
    "CODE/round3_v004/events_v004.jsonl",
    "CODE/round3_v004/process_archive_v004.md",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk() -> dict:
    """sha256 of every frozen evidence file, keyed by repo-relative POSIX path."""
    out = {}
    for root in ROOTS:
        base = REPO / root
        if not base.is_dir():
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = [d for d in dn if d not in SKIP_DIRS]
            for name in fn:
                if Path(name).suffix in SKIP_SUFFIXES:
                    continue
                p = Path(dp) / name
                if p.resolve() == MANIFEST.resolve():
                    continue
                out[p.relative_to(REPO).as_posix()] = sha256(p)
    for rel in EXTRA_FILES:
        p = REPO / rel
        if p.is_file():
            out[rel] = sha256(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", default=True,
                      help="verify the evidence against the manifest (default)")
    mode.add_argument("--write", action="store_true",
                      help="rebuild the manifest instead of verifying against it")
    ap.add_argument("--quiet", action="store_true", help="only print problems")
    args = ap.parse_args()

    current = walk()

    if args.write:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps({
            "purpose": "SHA-256 of every frozen evidence file under DATA/ and EVALS/",
            "scope": "the artefacts the submitted report cites; not reproducible output",
            "how_to_verify": "python CODE/verify_frozen_evidence.py --check",
            "note": "a reproduction writes to <round>/reproduced_run/ and can never "
                    "change these hashes",
            "file_count": len(current),
            "files": dict(sorted(current.items())),
        }, indent=1), encoding="utf-8")
        print(f"WROTE {MANIFEST.relative_to(REPO)}  ({len(current)} files)")
        return 0

    if not MANIFEST.exists():
        print("NO MANIFEST: run with --write first", file=sys.stderr)
        return 1

    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
    added = sorted(set(current) - set(expected))
    removed = sorted(set(expected) - set(current))
    changed = sorted(k for k in set(current) & set(expected) if current[k] != expected[k])

    if not (added or removed or changed):
        if not args.quiet:
            print(f"FROZEN EVIDENCE INTACT: {len(current)} files match "
                  f"{MANIFEST.relative_to(REPO)}")
        return 0

    print("FROZEN EVIDENCE DRIFT DETECTED", file=sys.stderr)
    for label, rows in (("ADDED", added), ("REMOVED", removed), ("CHANGED", changed)):
        if rows:
            print(f"  {label} ({len(rows)}):", file=sys.stderr)
            for k in rows[:40]:
                print(f"    {k}", file=sys.stderr)
            if len(rows) > 40:
                print(f"    ... and {len(rows) - 40} more", file=sys.stderr)
    print("\nIf this drift is intentional, rebuild the manifest with --write and "
          "update the documents that cite the affected artefacts.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
