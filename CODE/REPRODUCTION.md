# REPRODUCTION — what re-runs, what is frozen, and how that is enforced

This package ships the real output of three experiment rounds. Those outputs are
**frozen evidence**: the report cites specific numbers, and those numbers have to
keep matching the files on disk.

Reproducing a round is a different activity from submitting it. This document
explains the mechanism that keeps the two apart, so a marker can run the code
without silently overwriting the evidence it is checking.

---

## 1. One command

```bash
python CODE/run_all_checks.py          # everything, no paid calls (~2 min)
python CODE/run_all_checks.py --quick  # skip the two slowest stages
```

It compiles every module, runs every offline entry point with
`OPENROUTER_API_KEY` removed from the environment, re-derives Round 1's one-shot
final test and compares it with the frozen results, re-runs Round 3's Attempt-2
validator, and finishes by re-verifying that **nothing it ran touched the
archive**. Exit status is 0 only if every stage passes.

Current state on the packaging machine:

```
14/14 stages passed — no paid calls, archive untouched
```

---

## 2. Where a reproduction writes

The original rounds ran inside their own working directory and addressed their
inputs with short relative paths (`configs/x.json`, `results/y.csv`). The
submission package reorganises those artefacts under `DATA/` and `EVALS/` so a
marker can find them. `CODE/_packaged_paths.py` restores the original addressing
without moving or rewriting a single frozen file.

On top of that, three rules keep writes away from the archive:

| Rule | What it does | Where |
|---|---|---|
| `RoundPaths` redirect | A write to a path that does not yet exist *inside* `DATA/` or `EVALS/` lands in `<round>/reproduced_run/` instead | `CODE/_packaged_paths.py` |
| `redirect_write()` | A write aimed at an existing frozen artefact — e.g. regenerating a report or a validator output — is redirected the same way | `CODE/_packaged_paths.py` |
| `reproduction_copy()` | Append-only provenance (ledgers, event logs, process archives) is continued in `reproduced_run/logs/`, seeded from the archive so reads still see the whole history | `CODE/_packaged_paths.py` |

Reads always resolve to the packaged evidence, unchanged. A round therefore still
sees every frozen input it needs — including the caches that make a re-run
cost-free.

To regenerate a round **in place** on purpose, set
`VIRALLOOP_ALLOW_EVIDENCE_WRITE=1`. That is a deliberate opt-out, not the
default.

Scratch output is excluded from version control:

```
**/reproduced_run/
```

---

## 3. How the claim is checked

Two independent verifiers ship with the code. Both are plain scripts with an exit
status, so they can gate a commit as well as a reading.

### `CODE/verify_frozen_evidence.py` — the evidence has not moved

`EVALS/FROZEN_EVIDENCE_MANIFEST.json` holds the SHA-256 of every file under
`DATA/` and `EVALS/` — 5,370 files, including the `api_cache` call caches, the
final-test embedding vectors, and the append-only run logs under `CODE/`.

```bash
python CODE/verify_frozen_evidence.py --check   # verify
python CODE/verify_frozen_evidence.py --write   # rebuild after an intended change
```

It reports anything added, removed or changed, and exits 1 if there is any. A run
of `run_all_checks.py` finishes by calling it, so a leak would be caught
immediately.

### `CODE/verify_packaged_code.py` — the code is what it claims to be

Rounds 2 and 3 froze the SHA-256 of the modules that were live when their
freezes were taken (`generator_freeze_v002.json`, `dev_execution_freeze_v004.json`).
Publishing forced three kinds of change on that code:

1. **Path resolution** through `_packaged_paths` — the four path-constant lines of
   each entry module.
2. **Write protection** — `runtime.py` and `round3_runner.py` route writes to
   `reproduced_run/`.
3. **Englishization** — labels and prompt strings that had a Chinese rendering
   were replaced by the English text already present in the package.

None of those touches a threshold, a prompt contract, a metric or an output
format. But a bare hash comparison cannot see the difference, so the package
declares the changes instead of hiding them:

* `CODE/_frozen_code/<round>/` holds a **byte-identical copy of every original
  module** whose hash the freeze records.
* `CODE/PACKAGED_CODE_DEVIATIONS.json` records, per file, the frozen hash, the
  packaged hash and the reason.

`verify_packaged_code.py` then proves three things: the preserved originals still
hash to the frozen values, every packaged difference is declared, and nothing is
undeclared. A module that changed without an entry is reported as a failure.

```
PACKAGED CODE OK: every frozen module is preserved byte-identical;
9 declared deviation(s) account for every packaged difference
```

---

## 4. What genuinely cannot be re-derived

Stated plainly, as in `REPORT/`:

1. **LLM outputs are non-deterministic.** Temperature > 0 was used, so a fresh
   API call returns different text. The frozen outputs are the actual run record.
2. **Round 2's protocol audit FAILED** — the internal token cap was exceeded by
   ~23%, and 11 manifests and 68 raw responses are missing. Those units cannot be
   reconstructed; the gap is part of the record.
3. **Round 3's Final was never run.** There is nothing to reproduce, by design.
4. **The raw Reddit corpus is not redistributed.** `data_pipeline.py` rebuilds it
   from the documented upstream dataset.
5. **Vendored third-party libraries are not committed.** Install from
   `CODE/requirements.txt`.

What *is* fully reproducible offline, at zero cost, is the Round 1 final-test
result: the packaged embedding vectors and the API caches carry it, and the
reproduction matches the frozen numbers **exactly** (max absolute difference
0.0 across all nine evaluator rows and all six per-model prediction files).
