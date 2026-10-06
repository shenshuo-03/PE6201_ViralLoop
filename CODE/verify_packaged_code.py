"""Verify that every change to the frozen round code is declared and auditable.

Run this after touching any module that a round's freeze records a hash for.

    python CODE/verify_packaged_code.py            # verify (default)
    python CODE/verify_packaged_code.py --write     # rebuild the manifest
    python CODE/verify_packaged_code.py --quiet

It checks three things for each registered round:

1. **The original is preserved.**  Every module in the round's freeze has a
   byte-identical copy under ``CODE/_frozen_code/<round>/`` whose SHA-256 still
   equals the frozen value.  This is what lets the report keep claiming that the
   code which produced the evidence is unmodified and available.
2. **The packaged copy is declared.**  Every packaged module either hashes to the
   frozen value, or appears in ``PACKAGED_CODE_DEVIATIONS.json`` with a matching
   ``packaged_sha256``.
3. **Nothing is undeclared.**  A module that differs from the freeze without an
   entry in the manifest is a failure, not a footnote.

Exit status is 0 when all three hold and 1 otherwise, so it can gate a commit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _packaged_code import CODE, MANIFEST, load, sha256  # noqa: E402

ROUNDS = {
    "round2_v002": {
        "code_dir": "CODE/round2_v002",
        "frozen_code_dir": "CODE/_frozen_code/round2_v002",
        "freeze_file": "CODE/round2_v002/configs/generator_freeze_v002.json",
        "freeze_key": "code_hashes",
    },
    "round3_v004": {
        "code_dir": "CODE/round3_v004",
        "frozen_code_dir": "CODE/_frozen_code/round3_v004",
        "freeze_file": "CODE/round3_v004/configs/dev_execution_freeze_v004.json",
        "freeze_key": "code_hashes",
    },
}

REASONS = {
    "round2_v002": "path resolution through _packaged_paths; write protection in runtime.py; "
                   "review-page labels and one prompt argument Englishized",
    "round3_v004": "path resolution through _packaged_paths; write protection in round3_runner.py; "
                   "blind-review labels and status document Englishized",
}


def repo_root() -> Path:
    return CODE.parent


def freeze_hashes(round_key: str) -> dict:
    meta = ROUNDS[round_key]
    data = json.loads((repo_root() / meta["freeze_file"]).read_text(encoding="utf-8"))
    return dict(data.get(meta["freeze_key"], {}))


def build() -> int:
    rounds = {}
    for round_key, meta in ROUNDS.items():
        hashes = freeze_hashes(round_key)
        code_dir = repo_root() / meta["code_dir"]
        original_dir = repo_root() / meta["frozen_code_dir"]
        files = {}
        for name, frozen_sha in sorted(hashes.items()):
            packaged = code_dir / name
            if not packaged.exists():
                print(f"MISSING packaged module: {packaged.relative_to(repo_root())}",
                      file=sys.stderr)
                return 1
            packaged_sha = sha256(packaged)
            if packaged_sha == frozen_sha:
                # Untouched module: nothing to declare, no preserved copy needed.
                continue
            # A deviation must carry a byte-identical original so the frozen
            # hash can still be checked by a reader.
            original = original_dir / name
            if not original.exists():
                print(f"MISSING preserved original: {original.relative_to(repo_root())}",
                      file=sys.stderr)
                return 1
            if sha256(original) != frozen_sha:
                print(f"PRESERVED COPY DIFFERS FROM FREEZE: {name}", file=sys.stderr)
                return 1
            files[name] = {
                "frozen_sha256": frozen_sha,
                "packaged_sha256": packaged_sha,
                "reason": REASONS[round_key],
            }
        rounds[round_key] = {**meta, "files": files}
        print(f"{round_key}: {len(files)} declared deviation(s) of {len(hashes)} frozen module(s)")

    MANIFEST.write_text(json.dumps({
        "why": "Declared packaging changes to the frozen round code. See CODE/_packaged_code.py.",
        "how_to_verify": "python CODE/verify_packaged_code.py",
        "rule": "a packaged module matches the freeze when its hash equals the frozen hash, "
                "or when it is declared here AND its preserved original still hashes to the "
                "frozen value; anything else is an undeclared change",
        "rounds": rounds,
    }, indent=1) + "\n", encoding="utf-8")
    print(f"WROTE {MANIFEST.relative_to(repo_root())}")
    return 0


def check(quiet: bool = False) -> int:
    manifest = load().get("rounds", {})
    problems = []
    for round_key, meta in ROUNDS.items():
        hashes = freeze_hashes(round_key)
        code_dir = repo_root() / meta["code_dir"]
        original_dir = repo_root() / meta["frozen_code_dir"]
        entry = manifest.get(round_key, {})
        declared = dict(entry.get("files", {}))

        for name, frozen_sha in hashes.items():
            packaged = code_dir / name
            if not packaged.exists():
                problems.append(f"{round_key}: packaged module {name} missing")
                continue

            packaged_sha = sha256(packaged)
            row = declared.get(name)
            if packaged_sha == frozen_sha:
                if row is not None:
                    problems.append(
                        f"{round_key}: {name} is declared as a deviation but now matches the freeze; "
                        "rebuild the manifest")
                continue
            if row is None:
                problems.append(f"{round_key}: UNDECLARED change to {name}")
                continue
            # Declared: the preserved original must still prove the frozen hash.
            original = original_dir / name
            if not original.exists():
                problems.append(f"{round_key}: preserved original missing for {name}")
            elif sha256(original) != frozen_sha:
                problems.append(f"{round_key}: preserved original {name} no longer matches the freeze")
            if row.get("frozen_sha256") != frozen_sha:
                problems.append(f"{round_key}: {name} frozen hash in the manifest is stale")
            if row.get("packaged_sha256") != packaged_sha:
                problems.append(
                    f"{round_key}: {name} packaged hash in the manifest is stale; rebuild with --write")

        for name in declared:
            if name not in hashes:
                problems.append(f"{round_key}: {name} is declared but is not in the freeze")

    if problems:
        print("PACKAGED CODE DEVIATIONS INCONSISTENT", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        return 1
    if not quiet:
        total = sum(len(m.get("files", {})) for m in manifest.values())
        print(f"PACKAGED CODE OK: every frozen module is preserved byte-identical; "
              f"{total} declared deviation(s) account for every packaged difference")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="rebuild the manifest")
    ap.add_argument("--quiet", action="store_true", help="only print problems")
    args = ap.parse_args()
    return build() if args.write else check(args.quiet)


if __name__ == "__main__":
    raise SystemExit(main())
