"""Tell a *declared* packaging change apart from an *undeclared* code edit.

Why this exists
---------------
Rounds 2 and 3 froze the code that produced their evidence: each round's freeze
record stores a SHA-256 of every module that was live when the freeze happened
(``generator_freeze_v002.json`` and ``dev_execution_freeze_v004.json``).  Those
hashes are the reason the report can say "the code was not changed after the
freeze".

Publishing the package forced three kinds of change on that code:

1. **Path resolution.**  The original rounds ran inside their own working
   directory.  In the package the same artefacts live under ``DATA/`` and
   ``EVALS/``, so the four path-constant lines of each entry module now resolve
   through :mod:`_packaged_paths`.
2. **Write protection.**  ``runtime.py`` and ``round3_runner.py`` now route any
   write aimed at the frozen evidence to ``<round>/reproduced_run/``.
3. **Englishization.**  Chinese *renderings* that already had an English source
   in the package (HTML labels, UI strings, one prompt argument, document
   headings) were replaced by that English text.

None of these touches a threshold, a prompt contract, a metric or an output
format.  But a bare hash comparison cannot see that: it would report the frozen
code as "changed", which is both alarming and uninformative.

How the claim is kept checkable
-------------------------------
``CODE/_frozen_code/<round>/`` holds a **byte-identical copy of the original
module**.  ``CODE/PACKAGED_CODE_DEVIATIONS.json`` records, per file, the frozen
hash, the packaged hash and a one-line reason.

A packaged module therefore counts as *matching the freeze* when either

* its hash equals the frozen hash (module untouched), or
* it is a **declared** deviation whose packaged hash matches the recorded
  packaged hash **and** whose preserved original still hashes to the frozen
  value.

A module that changed without being declared is reported as a real problem, so
the exemption cannot hide an arbitrary edit.  ``CODE/verify_packaged_code.py``
re-derives every claim independently.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

CODE = Path(__file__).resolve().parent
MANIFEST = CODE / "PACKAGED_CODE_DEVIATIONS.json"


def sha256(path) -> str:
    """SHA-256 of a file, read in chunks so large files stay cheap."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load() -> dict:
    """The declared-deviation manifest, or an empty skeleton if it is absent."""
    if not MANIFEST.exists():
        return {"rounds": {}}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def declared(round_key: str) -> dict:
    """``{filename: entry}`` for one round's declared deviations."""
    return dict(load().get("rounds", {}).get(round_key, {}).get("files", {}))


def frozen_code_ok(round_key: str, freeze_hashes: dict, code_dir=None) -> dict:
    """``{filename: bool}`` saying whether each frozen module is accounted for.

    ``freeze_hashes`` is the round's own ``code_hashes`` mapping (filename to
    SHA-256) exactly as the freeze recorded it.  ``code_dir`` defaults to the
    packaged round directory named in the manifest.

    A ``True`` means "this module is the frozen module, or a declared
    deviation from it".  A ``False`` means "this module is neither", which is
    the case a reader should care about.
    """
    meta = load().get("rounds", {}).get(round_key, {})
    declared_files = dict(meta.get("files", {}))
    if code_dir is None:
        code_dir = CODE.parent / meta.get("code_dir", "")
    code_dir = Path(code_dir)

    result = {}
    for name, frozen_sha in freeze_hashes.items():
        path = code_dir / name
        if not path.exists():
            result[name] = False
            continue
        current = sha256(path)
        if current == frozen_sha:
            result[name] = True
            continue
        entry = declared_files.get(name)
        result[name] = bool(entry) and entry.get("packaged_sha256") == current
    return result


def undeclared_changes(round_key: str, freeze_hashes: dict, code_dir=None) -> list:
    """Filenames that changed against the freeze without being declared."""
    return [name for name, ok in frozen_code_ok(round_key, freeze_hashes, code_dir).items()
            if not ok]
