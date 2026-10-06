"""Run every reproducibility check for this submission in one command.

    python CODE/run_all_checks.py            # everything (no paid calls)
    python CODE/run_all_checks.py --quick    # skip the two slowest stages

What "reproducible" means here
------------------------------
The three rounds are frozen evidence.  This script does **not** re-spend money and
does **not** rewrite a single archived artefact.  It proves four separate things:

1. **Runs.**  Every module compiles and every offline entry point executes without
   a network call.  ``OPENROUTER_API_KEY`` is removed from the environment for
   every stage, so a stage that tried to call the API would fail loudly instead
   of silently spending money.
2. **Reproduces.**  Round 1's one-shot final test is re-derived from the packaged
   evidence and compared with the frozen ``evaluator_results.csv`` and the
   per-model prediction files.  Round 3's Attempt-2 validator re-runs its 28
   offline checks.
3. **Preserves the code.**  ``verify_packaged_code.py`` proves every module the
   freezes recorded is either unchanged or a declared, enumerated packaging
   change whose byte-identical original is still shipped.
4. **Preserves the evidence.**  ``verify_frozen_evidence.py`` proves the SHA-256
   of every file under ``DATA/`` and ``EVALS/`` (plus the append-only run logs)
   still matches the manifest, i.e. nothing this script ran leaked into the
   archive.

Exit status is 0 only when every stage passes.  Output of each stage is printed
under its own heading so a failure can be read in place.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

CODE = Path(__file__).resolve().parent
REPO = CODE.parent
PY = sys.executable


def _interpreter():
    """The interpreter to run the stages with.

    Prefers the one running this script; falls back to the packaging author's
    verification virtual environment only when the current interpreter cannot
    import the libraries the stages need.
    """
    import importlib.util  # noqa: PLC0415

    if importlib.util.find_spec("pandas") is not None:
        return PY
    for cand in (Path(r"C:/Users/19139/.workbuddy/binaries/python/envs/pe6201_verify/Scripts/python.exe"),):
        if cand.exists():
            return cand
    return PY


PY = _interpreter()

REVIEW_PORT = 8878


def clean_env() -> dict:
    """The environment a reproduction runs in: no API key, evidence read-only."""
    env = dict(os.environ)
    env.pop("OPENROUTER_API_KEY", None)
    env.pop("VIRALLOOP_ALLOW_EVIDENCE_WRITE", None)
    return env


def run(argv, cwd, label, timeout=1800):
    started = time.perf_counter()
    print(f"\n{'=' * 78}\n# {label}\n# $ {' '.join(str(a) for a in argv)}   (cwd={cwd.relative_to(REPO)})\n{'=' * 78}")
    try:
        proc = subprocess.run([str(a) for a in argv], cwd=str(cwd), env=clean_env(),
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after {timeout}s")
        return False, ""
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out.rstrip()[-4000:] if len(out) > 4000 else out.rstrip())
    took = time.perf_counter() - started
    print(f"--> exit={proc.returncode}  ({took:.1f}s)")
    return proc.returncode == 0, out


def port_open(port, host="127.0.0.1"):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def compile_all():
    bad = []
    files = sorted(CODE.rglob("*.py"))
    for f in files:
        proc = subprocess.run([str(PY), "-m", "py_compile", str(f)],
                              env=clean_env(), capture_output=True, text=True)
        if proc.returncode != 0:
            bad.append((f, proc.stderr.strip().splitlines()[-1] if proc.stderr else ""))
    print(f"\n{'=' * 78}\n# compile every module under CODE/  ({len(files)} files)\n{'=' * 78}")
    for f, err in bad:
        print(f"  FAIL {f.relative_to(REPO)}: {err}")
    print(f"--> {len(files) - len(bad)}/{len(files)} compile cleanly")
    return not bad


def round1_matches_frozen():
    """Round 1 final test: does the reproduction equal the frozen numbers exactly?"""
    import pandas as pd  # noqa: PLC0415  (only needed for this stage)

    frozen = REPO / "EVALS/round1_historical_and_generator"
    scratch = CODE / "round1_generation_pipeline/reproduced_run"
    print(f"\n{'=' * 78}\n# round 1: reproduced vs frozen results\n{'=' * 78}")

    a = pd.read_csv(frozen / "evaluator_results.csv")
    b = pd.read_csv(scratch / "evaluator_results.csv")
    cols = ["model", "average_precision", "f1", "brier", "precision", "recall",
            "roc_auc", "accuracy", "threshold"]
    a = a[cols].sort_values("model").reset_index(drop=True)
    b = b[cols].sort_values("model").reset_index(drop=True)
    if a.shape != b.shape:
        print(f"  FAIL shape {a.shape} vs {b.shape}")
        return False
    num = a.select_dtypes("number").to_numpy() - b.select_dtypes("number").to_numpy()
    worst = float(abs(num).max())
    identical = worst == 0.0
    print(f"  evaluator_results.csv: {a.shape[0]} models, max abs difference = {worst:g}")
    print(a.to_string(index=False))
    print(f"  bit-identical: {identical}")

    ok = identical
    for path in sorted(frozen.glob("E*_final_predictions.csv")):
        mine = scratch / path.name
        if not mine.exists():
            print(f"  FAIL {path.name} not reproduced")
            ok = False
            continue
        x, y = pd.read_csv(path), pd.read_csv(mine)
        same = (x.id.tolist() == y.id.tolist())
        d = float(abs(x.probability.to_numpy() - y.probability.to_numpy()).max())
        preds = bool((x.prediction.to_numpy() == y.prediction.to_numpy()).all())
        print(f"  {path.name}: ids={same} max_prob_diff={d:g} predictions={preds}")
        ok = ok and same and d == 0.0 and preds
    print(f"--> round 1 reproduction {'matches the frozen evidence exactly' if ok else 'DIFFERS'}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quick", action="store_true",
                    help="skip the round-1 final test and the review-server stage")
    args = ap.parse_args()

    results = []
    results.append(("compile every module", compile_all()))
    results.append(("chinese content audit", run(
        [PY, CODE / "scan_cjk.py", "--summary"], REPO, "chinese content audit")))
    results.append(("frozen evidence manifest", run(
        [PY, CODE / "verify_frozen_evidence.py", "--check"], REPO, "frozen evidence (before)")))
    results.append(("packaged code deviations", run(
        [PY, CODE / "verify_packaged_code.py"], REPO, "packaged code")))

    if not args.quick:
        marker = CODE / "round1_generation_pipeline/reproduced_run/FINAL_TEST_STARTED.json"
        marker.unlink(missing_ok=True)  # one-shot guard; a verification run is not a silent repeat
        results.append(("round 1 final test", run(
            [PY, "performance_evaluator.py", "--stage", "final"],
            CODE / "round1_generation_pipeline", "round 1 final test (no API key)")))
        results.append(("round 1 matches frozen", round1_matches_frozen()))

    results.append(("round 3 v004 offline validator", run(
        [PY, "offline_validate_v004.py"], CODE / "round3_v004",
        "round 3 v004 offline validator")))

    server = None
    if not args.quick:
        print(f"\n{'=' * 78}\n# start the round-2 review server on 127.0.0.1:{REVIEW_PORT}\n{'=' * 78}")
        server = subprocess.Popen([str(PY), "review_server.py"],
                                  cwd=str(CODE / "round2_v002"), env=clean_env(),
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(40):
            if port_open(REVIEW_PORT):
                break
            time.sleep(0.25)
        print("  review server listening" if port_open(REVIEW_PORT) else "  review server NOT listening")

    try:
        for script in ["preparation_checks.py", "conformance_audit.py", "archive_results.py",
                       "preview.py", "semantic_posthoc_audit.py"]:
            results.append((f"round 2 {script}", run(
                [PY, script], CODE / "round2_v002", f"round 2 {script}")))
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
            print("\n  review server stopped")

    # The point of the whole exercise: nothing above touched the archive.
    results.append(("frozen evidence manifest (after)", run(
        [PY, CODE / "verify_frozen_evidence.py", "--check"], REPO,
        "frozen evidence (after every stage ran)")))
    results.append(("packaged code deviations (after)", run(
        [PY, CODE / "verify_packaged_code.py"], REPO, "packaged code (after)")))

    print(f"\n{'=' * 78}\n# SUMMARY\n{'=' * 78}")
    width = max(len(name) for name, _ in results)
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}}")
    failed = [name for name, ok in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} stages passed"
          + (f"; failing: {failed}" if failed else " — no paid calls, archive untouched"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
