"""Packaged-layout path resolver for the PE6201 ViralLoop submission package.

Why this module exists
----------------------
Each experiment round was originally executed inside its own working directory,
so the frozen code addresses its inputs and outputs with short relative paths:
``configs/model_prices.json``, ``data/splits/train.parquet``,
``results/api_ledger_v003.jsonl``, ``inputs/source_assignment_v004.json`` and so
on.

The submission package reorganises those artefacts into the reader-facing
``DATA/`` and ``EVALS/`` folders so that a marker can find the evidence without
reading through a working tree.  Doing that moved files away from the paths the
frozen code expects, which would have made the packaged copy unrunnable.

``RoundPaths`` restores the original addressing **without moving, duplicating,
rewriting or regenerating a single frozen artefact**.  It only answers the
question "where is this logical path actually stored in the packaged layout?".

Scope and honesty
-----------------
* It changes *where files are found*.  It never changes *what any number means*.
* Reads resolve to the packaged evidence; writes to a path that does not exist
  yet resolve to the round's own directory, so the frozen ``DATA/`` and
  ``EVALS/`` evidence is never overwritten by a stray run.
* Only the four path-constant lines in the round entry modules use it.  No
  experiment logic, prompt, threshold, contract or output format is touched.

A round's working directory is still discovered the way the original code did,
so the same file runs unchanged in the original tree and in this package.
"""

from pathlib import Path

__all__ = ["RoundPaths", "repo_root", "repo_paths", "round1_root",
           "round2_root", "round3_v003_root", "round3_v004_root",
           "redirect_write", "reproduction_copy"]

# Every RoundPaths built in this process, so redirect_write() can translate a
# resolved evidence path back into the logical path that produced it.
_REGISTRY = []


def _is_evidence(path):
    """True when ``path`` sits inside the frozen DATA/ or EVALS/ evidence tree."""
    parts = Path(path).parts
    return any(p in RoundPaths._EVIDENCE_TOP for p in parts)


def _evidence_write_allowed():
    """Whether a script may write into the archived evidence folders.

    Off by default.  Reproducing a round is expected to write its *own* outputs,
    not to overwrite the artefacts the submitted report cites.  Set
    ``VIRALLOOP_ALLOW_EVIDENCE_WRITE=1`` to opt in to writing frozen evidence
    (for example when deliberately regenerating a round from scratch).
    """
    import os

    return os.environ.get("VIRALLOOP_ALLOW_EVIDENCE_WRITE") == "1"


class RoundPaths:
    """A drop-in stand-in for the ``ROOT`` / ``LOOP`` / ``L`` Path constants.

    Supports the only operation the frozen code performs on those constants:
    ``ROOT / "configs/x.json"``.  The result is always a real :class:`Path`, so
    ``.exists()``, ``.read_text()``, ``.glob()``, ``.mkdir()`` and friends behave
    exactly as before.

    Write protection
    ----------------
    The submitted package stores round outputs under ``DATA/`` and ``EVALS/`` as
    frozen evidence.  When a mapped directory inside those folders does **not**
    yet contain the requested leaf, a run is almost always trying to create a new
    output.  Rather than let a stray reproduction overwrite the cited artefacts,
    such writes are redirected to ``<round>/reproduced_run/`` unless
    ``VIRALLOOP_ALLOW_EVIDENCE_WRITE=1`` is set.  Reads always resolve to the
    packaged evidence, unchanged.
    """

    _EVIDENCE_TOP = ("EVALS", "DATA")

    def __init__(self, workdir, mapping):
        self._work = Path(workdir).resolve()
        self._work.mkdir(parents=True, exist_ok=True)
        self._map = {k: Path(v).resolve() for k, v in mapping.items()}
        _REGISTRY.append(self)

    @property
    def workdir(self):
        return self._work

    def match(self, path):
        """Best (logical_path, base_length) for ``path`` under this mapping.

        Returns ``None`` when the path is not reachable through this mapping.
        The base length lets callers prefer the most specific mapping.
        """
        try:
            target = Path(path).resolve()
        except OSError:
            return None
        best = None
        for key, base in self._map.items():
            try:
                rel = target.relative_to(base)
            except ValueError:
                continue
            if best is None or len(str(base)) > best[1]:
                best = (str(Path(key) / rel).replace("\\", "/"), len(str(base)))
        return best

    def logical_for(self, path):
        """Reverse-map a resolved packaged path back to its logical path.

        ``EVALS/round2_judge_and_final/x.json`` becomes
        ``results/x.json`` when this instance is the round-2 resolver.  Returns
        ``None`` when the path is not reachable through this mapping.
        """
        hit = self.match(path)
        return hit[0] if hit else None

    @property
    def out(self):
        """Root for newly produced outputs.

        Existing frozen evidence is always *read* through ``ROOT / 'results/...'``.
        Code that produces a new artefact should write through ``ROOT.out`` so a
        reproduction never overwrites the submitted evidence.  Set
        ``VIRALLOOP_ALLOW_EVIDENCE_WRITE=1`` to make ``out`` an alias of the round
        working directory instead.
        """
        return self._work if _evidence_write_allowed() else self._work / "reproduced_run"

    def __truediv__(self, other):
        s = str(other).replace("\\", "/").lstrip("./")
        best_key, best_len = None, -1
        for key in self._map:
            if (s == key or s.startswith(key + "/")) and len(key) > best_len:
                best_key, best_len = key, len(key)
        if best_key is not None:
            base = self._map[best_key]
            rest = s[best_len:].lstrip("/")
            if base.exists():
                target = base / rest if rest else base
                # A missing leaf inside a frozen evidence folder means the run is
                # creating a new output: redirect it away from the cited
                # artefacts unless the caller explicitly opted in.
                if (rest and not target.exists() and _is_evidence(base)
                        and not _evidence_write_allowed()):
                    redirected = self._work / "reproduced_run" / s
                    # The frozen code follows this with ``mkdir(exist_ok=True)``,
                    # which does not create intermediate folders.  Create the
                    # redirect's parent chain here so a run that produces a brand
                    # new artefact cannot fail on a missing directory.  This only
                    # ever touches the scratch folder, never the evidence tree.
                    redirected.parent.mkdir(parents=True, exist_ok=True)
                    return redirected
                return target
        # Unknown prefix, or a mapped directory that is absent (for example the
        # raw corpus, which is deliberately not redistributed): address it inside
        # the round's own directory.
        return self._work / s

    def __fspath__(self):
        return str(self._work)

    def __str__(self):
        return str(self._work)

    def __repr__(self):
        return "RoundPaths(%r)" % str(self._work)

    def __getattr__(self, name):
        # .exists(), .name, .glob(), .iterdir(), ... fall through to the workdir
        return getattr(self._work, name)


def repo_root():
    """Absolute path of the submission package root (the folder holding README.md)."""
    return Path(__file__).resolve().parents[1]


def round_workdir(name):
    """Retained for compatibility with the original helper name."""
    return Path(__file__).resolve().parent / name


def repo_paths():
    """Repository-relative logical prefixes.

    Rounds 2 and 3 read the *earlier* rounds' ledgers through repository-level
    paths (``experiment_1_0/results/...``, ``loops/v002/results/...``).  This
    mapping keeps those budget-accounting reads working in the packaged layout.
    """
    r = repo_root()
    return RoundPaths(r, {
        "experiment_1_0/results": _p("EVALS", "round1_historical_and_generator"),
        "experiment_1_0/data": _p("DATA", "round1_dataset"),
        "experiment_1_0/configs": _p("DATA", "round1_dataset", "configs"),
        "loops/v002/results": _p("EVALS", "round2_judge_and_final"),
        "loops/v002/inputs": _p("DATA", "round2_briefs_and_sources", "inputs"),
        "loops/v002/sources": _p("DATA", "round2_briefs_and_sources", "sources"),
        "loops/v003/results": _p("EVALS", "round3_dev_and_termination", "v003"),
        "loops/v003/runs": _p("EVALS", "round3_dev_and_termination", "v003", "runs"),
        "loops/v004/results": _p("EVALS", "round3_dev_and_termination", "v004"),
    })


def _p(*parts):
    return repo_root().joinpath(*parts)


def redirect_write(path, workdir=None):
    """Return where a write aimed at the frozen evidence must actually land.

    ``RoundPaths`` can only redirect a write whose target does **not** exist yet,
    because it cannot tell a read from a write.  A script that *regenerates* an
    existing artefact therefore still points at the submitted file.  The round
    writers call this function so that, during a reproduction, any write aimed at
    ``DATA/`` or ``EVALS/`` is redirected to ``<round>/reproduced_run/<logical
    path>`` and the cited evidence stays byte-identical.

    Reads are never affected, and setting ``VIRALLOOP_ALLOW_EVIDENCE_WRITE=1``
    disables the redirect so a round can be regenerated in place on purpose.
    ``CODE/verify_frozen_evidence.py --check`` proves afterwards whether the
    evidence still matches its manifest.
    """
    p = Path(path)
    if _evidence_write_allowed():
        return p
    try:
        resolved = p.resolve()
    except OSError:
        return p
    if not _is_evidence(resolved):
        return p

    logical = None
    work = Path(workdir).resolve() if workdir else None
    # Several resolvers can reach the same evidence tree: a round resolver
    # (``results/*``) and the repository-level resolver (``loops/v002/results/*``)
    # often share a base.  Prefer the most specific mapping, and on a tie prefer
    # a round's own working directory over the repository root, so reproduction
    # output always lands next to the round that produced it.
    best = None
    for rp in _REGISTRY:
        hit = rp.match(resolved)
        if hit is None:
            continue
        score = (hit[1], 0 if rp.workdir == repo_root() else 1)
        if best is None or score > best[0]:
            best = (score, hit[0], rp.workdir)
    if best is not None:
        _, logical, rp_work = best
        if work is None:
            work = rp_work

    if logical is None:
        try:
            # Evidence that no round mapping reaches: keep the same relative
            # shape under the scratch folder.
            logical = resolved.relative_to(repo_root()).as_posix()
            if work is None:
                work = _REGISTRY[-1].workdir if _REGISTRY else repo_root()
        except (ValueError, IndexError):
            return p

    out = Path(work) / "reproduced_run" / logical
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def reproduction_copy(path, workdir=None):
    """A reproduction-local copy of an *append-only* archive file.

    Ledgers, event logs and process archives are append-only provenance.  A
    reproduction that appended to them would mix its own calls into the archived
    record and silently change a file the report cites.

    This returns a copy under ``<workdir>/reproduced_run/logs/``, seeded from the
    archive the first time it is requested, so reads still see the whole archived
    history and the reproduction's own log is complete as well.  Setting
    ``VIRALLOOP_ALLOW_EVIDENCE_WRITE=1`` returns the archive path unchanged.
    """
    src = Path(path)
    if _evidence_write_allowed():
        return src
    root = Path(workdir).resolve() if workdir else repo_root()
    out = root / "reproduced_run" / "logs" / src.name
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() and src.exists():
        out.write_text(src.read_text(encoding="utf-8", errors="replace"),
                       encoding="utf-8")
    return out


def round1_root(workdir=None):
    """Round 1 (``experiment_1_0``) logical paths."""
    w = Path(workdir) if workdir else Path(__file__).resolve().parent / "round1_generation_pipeline"
    return RoundPaths(w, {
        "configs": _p("DATA", "round1_dataset", "configs"),
        "data": _p("DATA", "round1_dataset"),
        "results": _p("EVALS", "round1_historical_and_generator"),
        "evals": _p("EVALS", "round1_historical_and_generator", "human_review_package"),
        "patterns": _p("EVALS", "round1_historical_and_generator", "pattern_cards"),
    })


def round2_root(workdir=None):
    """Round 2 (``loops/v002``) logical paths."""
    w = Path(workdir) if workdir else Path(__file__).resolve().parent / "round2_v002"
    return RoundPaths(w, {
        # ``LOOP/'code'/x.py`` addressed the round's own modules in the original
        # tree; in the package the modules sit directly in CODE/round2_v002/.
        "code": w,
        "results": _p("EVALS", "round2_judge_and_final"),
        "inputs": _p("DATA", "round2_briefs_and_sources", "inputs"),
        "sources": _p("DATA", "round2_briefs_and_sources", "sources"),
        "evals": _p("DATA", "round2_briefs_and_sources", "evals"),
        "runs": _p("EVALS", "round2_judge_and_final", "runs"),
    })


def round3_v003_root(workdir=None):
    """Round 3 Attempt 1 (``loops/v003``) logical paths."""
    w = Path(workdir) if workdir else Path(__file__).resolve().parent / "round3_v003"
    return RoundPaths(w, {
        "code": w,
        "results": _p("EVALS", "round3_dev_and_termination", "v003"),
        "runs": _p("EVALS", "round3_dev_and_termination", "v003", "runs"),
        "inputs": _p("DATA", "round3_briefs_and_sources", "v003_inputs"),
        "sources": _p("DATA", "round3_briefs_and_sources", "v003_sources"),
        "evals": _p("DATA", "round3_briefs_and_sources", "v003_evals"),
        # Documents that the reader-facing layout keeps in a v003/ subfolder.
        "experiment_contract_v003.yaml": w / "v003" / "experiment_contract_v003.yaml",
        "plan_v003.md": w / "v003" / "plan_v003.md",
        "process_archive_v003.md": _p("EVALS", "round3_dev_and_termination", "v003",
                                      "process_archive_v003.md"),
    })


def round3_v004_root(workdir=None):
    """Round 3 Attempt 2 (``loops/v004``) logical paths."""
    w = Path(workdir) if workdir else Path(__file__).resolve().parent / "round3_v004"
    return RoundPaths(w, {
        "code": w,
        "results": _p("EVALS", "round3_dev_and_termination", "v004"),
        "runs": _p("EVALS", "round3_dev_and_termination", "v004", "runs"),
        "inputs": _p("DATA", "round3_briefs_and_sources", "v004_inputs"),
        "sources": _p("DATA", "round3_briefs_and_sources", "v004_sources"),
        "evals": _p("DATA", "round3_briefs_and_sources", "v004_evals"),
    })
