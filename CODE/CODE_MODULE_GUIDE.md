# CODE_MODULE_GUIDE — File and Module Level Documentation

Scope: file/module level, as required by the brief. This is **not** a line-by-line commentary.
Every entry states: what it does · input · output · dependencies · role in the experiment.

---

## Round 1 — `round1_generation_pipeline/`

| Module | What it does | Input | Output | Depends on | Role |
|---|---|---|---|---|---|
| `data_pipeline.py` | Cleans the raw archive, recovers observation age, builds labels and temporal splits | Raw archive (`data/raw/`) | `processed_posts.parquet`, `labels.parquet`, `splits/*.parquet`, `cleaning_log.csv` | pandas, pyarrow | **Stage 0** — everything downstream depends on this frozen split |
| `common.py` | Shared paths, config loading, hashing, JSON/CSV helpers | `configs/*.json` | In-memory configs | stdlib | Infrastructure |
| `model_api.py` | Single choke point for all LLM/embedding HTTP calls; retries; **per-call ledger append** | Prompt + model id | Response + usage record | `requests` | The only place network calls happen — the cost ledger and cache depend on it |
| `retrieval.py` | TF-IDF retrieval over **Train only** for RAG arms | Query text, Train corpus | Retrieved example indices | scikit-learn | Prevents Final leakage into retrieval |
| `pattern_miner.py` | Tests 10 measurable pattern hypotheses by content type, with multiple-testing handling | Train labels + text | `patterns/*.json`, `pattern_statistics.csv` | scipy, sklearn | Produces the 12 pattern cards (8 positive, 4 negative) used in G4 |
| `performance_evaluator.py` | Historical evaluator ladder **E0–E4** (lazy, prior, context, context+structure, TF-IDF, text+context, LSA) | Splits | `evaluator_results.csv`, `E*_final_predictions.csv` | sklearn | **The only layer with real held-out labels** |
| `semantic_evaluator.py` | E4 semantic-embedding variant | Splits + embedding API | `E4_semantic_final_predictions.csv` | OpenRouter | Independent historical auditor used to cross-check E2 |
| `generator.py` | Generation arms G0–G4 (prompt, few-shot/planning, RAG, pattern cards) | Brief + retrieved examples + pattern cards | Candidate drafts | `model_api` | The treatment under test |
| `run_generation_final.py` | Runs the generation ladder on the frozen Final briefs | Frozen topic bank | `generator_results.csv` | `generator` | Produces the 180-candidate record |
| `quality_evaluator.py` | Automatic quality scoring of candidates | Drafts | Quality scores | `model_api` | Supporting metric — **not** a product acceptance signal |
| `quality_calibration.py` | 30 controlled quality cases (24 invalid, 6 valid) for the fact-checker | Drafts | `quality_calibration_cases.json` | `model_api` | Tests the checker on *pre-designed narrow* anomalies only |
| `judge_evaluator.py` | LLM historical classification (E5a zero-shot / E5b few-shot / E5c retrieval) | 80-post subset | `judge_classifier_results.csv` | `model_api` | Compares LLM judgement against E2/E4 **on the same subset** |
| `audit_generated_performance.py` | Independent E4 audit of generated text; never feeds back into generation | Generated drafts | `independent_generation_audit_summary.json` | sklearn | **The independent check on the feedback-vs-resampling claim** |
| `upworthy_transfer.py` | Title transfer experiment | Upworthy pairs | `upworthy_transfer_metrics.json` | pandas | Transfer test — result ≈ chance, reported as such |
| `verify_integrity.py` | 13 process integrity checks | All artefacts | `integrity_checks.json` | stdlib | Process constraints only — **not** content quality |
| `harness.py` | Orchestrates staged runs and run-state bookkeeping | Config | `RUN_STATE.json` | stdlib | Reproducibility scaffolding |
| `finalize_artifacts.py` | Aggregates results into final tables and figures | Result CSV/JSON | `report.md`, figures | matplotlib | Reporting |
| `render_report.py` | Renders report tables and figures | Results | `figures/*.png` | matplotlib | Reporting |
| `server.py` | Local human-review / product UI server | Cases JSON | HTML pages | stdlib http.server | Lowers the cost of collecting real feedback |
| `translate_blind.py`, `update_blind_language.py` | Chinese translation of blind cases for the reviewer | Case JSON | `*_zh.json` | `model_api` | Reviewer accessibility; translation did **not** alter the English source |
| `topic_bank.py` | Defines the experimental generation topics | `configs/topic_bank.json` | Brief list | stdlib | Separate from the 348 history evaluation set |
| `model_attribution.py` | Records selected model attribution | Ledger | `selected_model_attributions.json` | stdlib | Audit trail |
| `smoke_test_ui.py` | UI smoke test | — | `ui_smoke_test.json` | stdlib | Engineering only |

---

## Round 2 — `round2_v002/`

| Module | What it does | Input | Output | Role |
|---|---|---|---|---|
| `runtime.py` | Shared runtime, config, ledger and cache handling for v002 | `configs/*_v002.json` | Ledger entries | Infrastructure |
| `preparation_checks.py` | Offline preparation checks before any paid call | Briefs, sources | `offline_preparation_checks_v002.json` | Gate before spending |
| `evaluator.py` | **Judge admission** — Calibration then Validation over 30 controlled pairs | `controlled_pairs_*.json` | `challenge_summary_*.json` | The ruler is tested before being trusted |
| `generation.py` | Generation of **V0 / V1 / V2 / O1** | Brief + structure retrieval | Candidates | The four arms under comparison |
| `final_experiment.py` | Runs the 12 Final tasks and external-judge comparisons | Frozen configs | `final_comparison_results_v002.csv`, `final_summary_v002.json` | Main Round 2 output |
| `conformance_audit.py` | Contract/manifest + token-cap audit | Manifests, ledger | `contract_manifest_audit_v002.json`, `final_integrity_audit_v002.json` | **This audit FAILED** — the failure is part of the record |
| `archive_results.py` | Windows the development archive | Results | `development_archive/` | Housekeeping |
| `final_human_review.py` | Serves the planned 12-group human Final comparison | Final pairs | `final_human_pairs/` | Prepared — **the human Final was never completed** |
| `preview.py` | Naturalness preview generation | Drafts | `naturalness_previews_v002.json` | Produced the 3-preview real feedback sample |
| `revise_naturalness.py` | Automatic simplification attempts | Drafts | `naturalness_repair_*` | Failed twice on D03; a manual edit was what worked |
| `semantic_posthoc_audit.py` | Post-hoc E2/E4 association audit on v002 | Generated text | `historical_E2/E4_association_audit_v002.json` | Independent check on proxy validity |
| `review_server.py` | Blind review web server | Cases | HTML | Feedback collection |
| `product_server.py` | Product UI server | Brief | HTML draft | The user-facing slice |

---

## Round 3 — `round3_v003/` (Attempt 1)

| Module | What it does | Role |
|---|---|---|
| `round3_runner.py` | v003 dry-run then Dev execution (G0 + G1 with Motivation Planner) | Attempt 1 — **failed structurally**: all 8 tasks collapsed into help-seeking |
| `human_review.py` | Dev review interface | Prepared; formal human statistics never completed |
| `prompts/{BRIEF,BASEPROMPT,PLAN,JUDGE,QUALITY,AUDIT,TRANSLATE}_v003.txt` | The actual prompts used | The schema defect that caused the collapse lives here |

## Round 3 — `round3_v004/` (Attempt 2)

| Module | What it does | Role |
|---|---|---|
| `offline_validate_v004.py` | 27 offline checks: archetype, source isolation, prior-evidence hash, schema, no-paid-calls | Gate before spending; process constraints only |
| `round3_runner.py` | v004 execution — 8 archetype-typed Dev tasks, G0 vs G1 (Engagement Planner) | Attempt 2 — type collapse fixed, summary tone remained |
| `selector_v004.py` | Selector admission attempt | **Never completed human admission** |
| `human_review.py` | Dev review interface | Ready at termination; no formal submission exists |
| `configs/brief_schema_v004.json` | The archetype-typed brief schema (4 archetypes, A-only required fields) | The fix for Attempt 1's defect |
| `configs/archetype_routes_v004.json` | Type routing rules | Keeps help-seeking from being the default |
| `configs/dev_execution_freeze_v004.json` | Frozen dev execution config | Prevents post-hoc drift |

---

## Cross-cutting modules

| Concern | Where it lives | Note |
|---|---|---|
| **Cost ledger** | `*/api_ledger*.jsonl`, written by `model_api.py` / `runtime.py` | Every call logs provider, model, in/out tokens, price |
| **Model prices** | `*/configs/model_prices*.json` | Declarative; used to reconcile the ledger |
| **Freezing** | `configs/*_freeze*.json`, `experiment_contract_*.yaml` | Thresholds and configs frozen before Final |
| **Provenance** | `runs/*/manifest_*.json`, `prompt.txt`, `raw_response.json`, `request_config.json` | Per-call record — **68 raw responses are missing from Round 2, and that gap is disclosed** |
| **Archiving** | `process_archive_*.md` | Narrative record of what was run and what was not |
| **Packaged-layout path resolution** | `_packaged_paths.py` | Restores the rounds' original relative addressing for the `DATA/`+`EVALS/` layout, and redirects every write away from the frozen evidence |
| **Packaging-change declaration** | `_packaged_code.py`, `PACKAGED_CODE_DEVIATIONS.json`, `_frozen_code/` | Byte-identical originals of every frozen module the packaging had to touch, plus the per-file reason |
| **Verification** | `verify_frozen_evidence.py`, `verify_packaged_code.py`, `run_all_checks.py` | Exit-status checks for evidence integrity, code provenance and end-to-end runnability |
| **Vendored helper** | `_vendor/audit_contract.py` | The contract-audit helper `conformance_audit.py` needs, vendored so the round runs without the author's machine |

## Where to look for the failures

This codebase deliberately keeps its own failure evidence:

| Failure | Where to find it |
|---|---|
| Feedback loop had no measurable effect | `EVALS/round1_historical_and_generator/generator_paired_comparisons.csv` |
| Judge failed on information value | `EVALS/round2_judge_and_final/challenge_summary_validation_google_gemini-2.5-flash-lite_v002.json` |
| Protocol audit FAILED | `EVALS/round2_judge_and_final/contract_manifest_audit_v002.json` |
| Help-seeking collapse | `EVALS/round3_dev_and_termination/v003/` |
| Identity inheritance bug | `EVALS/round3_dev_and_termination/v003/identity_supplement/` |
| Quality still blocking release | `EVALS/round3_dev_and_termination/v004/` |
| Round 3 never ran Final | `EVALS/round3_dev_and_termination/v004/process_archive_v004.md` |
