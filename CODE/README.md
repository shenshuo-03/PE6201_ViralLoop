# CODE/README — Environment, Setup and Reproduction

> **Verification status.** Two tiers, kept separate on purpose.
>
> **Verified — actually executed on 5 Oct 2026, in a clean virtual environment:** dependency installation (`pip install -r CODE/requirements.txt`), import of all ten third-party libraries, and a full syntax compile of all 50 Python files under `CODE/`. Cost US$0.00, no model API contacted. Raw output and its honest limits: **[`CODE/INSTALL_LOG.txt`](INSTALL_LOG.txt)**.
>
> **Not re-run — marked `[NOT RE-RUN]` below:** the experiment commands that call model APIs. These were deliberately not re-executed, because the experiments are frozen and must not be re-run: a live re-run would consume paid API budget and could mutate the frozen outputs that the report's numbers come from. Every command name, flag and output path was read from the actual source — nothing is guessed — but the flag is honest about what was executed.
>
> The end-to-end counts reported in the report are internally consistent with the frozen JSON/CSV artefacts in this repository.

---

## 1. Environment

| Item | Value |
|---|---|
| OS used | Windows 11 (commands below use PowerShell) |
| Python | 3.13 |
| Key libraries | `numpy`, `pandas`, `scikit-learn`, `scipy`, `pyarrow`, `matplotlib`, `requests`, `reportlab`, `pypdf`, `Pillow` (see `CODE/requirements.txt`) |
| Model access | **OpenRouter** (single gateway for all LLM and embedding calls) |

Round 1 shipped a vendored dependency directory (`vendor/`) so it could run without a global install. That directory is **excluded** from this repository as bundled third-party code; use `requirements.txt` instead.

## 2. Dependency installation

```bash
# All three rounds — one consolidated file
pip install -r CODE/requirements.txt
```

`CODE/requirements.txt` is the union of what the three rounds actually import; `round1_generation_pipeline/requirements.txt` is the same set as declared for Round 1, and `requirements.lock.txt` is the frozen resolution used for the Round 1 run. Round 2 and Round 3 add **no** third-party packages — their human-review web interfaces use only the Python standard library (`http.server`).

> **Install command status: [VERIFIED]** — `pip install -r CODE/requirements.txt` was executed in a clean virtual environment on 5 Oct 2026 and completed with exit code 0, installing 27 packages. All ten imported libraries then loaded, and all 50 Python files under `CODE/` compiled without syntax errors. See `CODE/INSTALL_LOG.txt` for the recorded output, including the limits of what this does and does not prove.

## 3. API configuration

All model access goes through OpenRouter with a bearer token read from the environment:

```bash
# PowerShell
$env:OPENROUTER_API_KEY = "<your-key>"
```

```bash
# bash
export OPENROUTER_API_KEY="<your-key>"
```

**No key, token or secret is stored anywhere in this repository.** Keys live only in the environment.
Model identifiers and unit prices used for the cost ledger are recorded declaratively in:

- `round1_generation_pipeline/configs/model_prices.json`
- `round2_v002/configs/model_prices_v002.json`
- `round3_v003/configs/model_prices_v003.json`
- `round3_v004/configs/model_prices_v004.json`

## 4. Key experiment commands

### Round 1 — historical evaluation and generation ladder

```powershell
cd CODE/round1_generation_pipeline

# Full pipeline driver (data → evaluators → generation → audit → report)
.\run.ps1

# Individual stages
python data_pipeline.py            # clean, recover observation age, build splits
python performance_evaluator.py    # E0–E4 historical evaluator ladder
python semantic_evaluator.py       # E4 semantic embedding variant
python pattern_miner.py            # pattern cards from Train only
python run_generation_final.py     # G0–G4 / O1 / O2 generation arms
python audit_generated_performance.py   # independent E4 audit of generated text
python verify_integrity.py         # integrity checks
python render_report.py            # figures + report tables
```

Stage-to-artefact mapping:

| Script | Output |
|---|---|
| `data_pipeline.py` | `DATA/round1_dataset/` |
| `performance_evaluator.py` | `EVALS/round1_historical_and_generator/evaluator_results.csv` |
| `run_generation_final.py` | `EVALS/.../generator_results.csv`, `generator_candidate_results.csv` |
| `audit_generated_performance.py` | `EVALS/.../independent_generation_audit_summary.json` |
| `verify_integrity.py` | `EVALS/.../integrity_checks.json` |

**[NOT RE-RUN]**

### Round 2 — judge admission and Final

```powershell
python CODE/round2_v002/preparation_checks.py     # offline preparation checks
python CODE/round2_v002/evaluator.py              # judge admission (Calibration + Validation)
python CODE/round2_v002/generation.py             # V0 / V1 / V2 / O1
python CODE/round2_v002/final_experiment.py       # 12 Final tasks
python CODE/round2_v002/conformance_audit.py      # contract/manifest + token cap audit
```

Human review interface:

```powershell
python CODE/round2_v002/review_server.py          # serves the blind review pages
python CODE/round2_v002/product_server.py         # serves the product UI
```

**[NOT RE-RUN]**

### Round 3 — v003 (Attempt 1) and v004 (Attempt 2)

```powershell
python CODE/round3_v003/round3_runner.py          # v003 dry-run + Dev execution
python CODE/round3_v003/human_review.py           # Dev review interface

python CODE/round3_v004/offline_validate_v004.py  # 27 offline checks (no paid calls)
python CODE/round3_v004/round3_runner.py          # v004 8 Dev tasks
python CODE/round3_v004/selector_v004.py          # selector admission attempt
python CODE/round3_v004/human_review.py           # Dev review interface
```

**[NOT RE-RUN]**

### Demo

Open `DEMO/ViralLoop_Demo.html` directly in a browser — it is self-contained and needs no server.
The original local product UI is served with:

```powershell
python CODE/round2_v002/code_product/product_server.py
```

## 5. Output locations

| Artefact type | Location |
|---|---|
| Per-call API ledger (JSONL) | `EVALS/*/api_ledger*.jsonl` |
| Frozen configs | `CODE/round*/configs/`, `DATA/round1_dataset/configs/` |
| Evaluator results | `EVALS/round1_historical_and_generator/` |
| Judge admission | `EVALS/round2_judge_and_final/` |
| Round 3 Dev evidence | `EVALS/round3_dev_and_termination/` |
| Figures | `REPORT/figures/` |
| Split data | `DATA/round1_dataset/splits/` |

## 6. Things that will not reproduce byte-for-byte

Stated plainly rather than hidden:

1. **LLM outputs are non-deterministic.** Temperature > 0 was used. The frozen outputs in `EVALS/` are the actual run records; a fresh run will differ.
2. **Round 2's protocol audit FAILED** (token cap exceeded ~22.5%; 11 manifests and 68 raw responses missing). Reproducing Round 2 exactly is therefore **not possible for those units** — the gap is part of the record.
3. **Round 3's Final was never run.** There is nothing to reproduce.
4. **Raw corpora and embeddings are excluded** for size. `data_pipeline.py` regenerates them from the documented upstream source.
5. **`vendor/` was excluded**, so Round 1 needs `pip install -r requirements.txt` instead of the vendored path.

## 7. Safety

- Source material is treated as **data, never as instructions** (prompt-injection handling).
- Fact and identity checks are deterministic rules, not model judgements.
- There is **no automated publishing path** — human confirmation is required by design.
- No secrets are committed. `.gitignore` excludes caches, virtualenvs and credential files.
