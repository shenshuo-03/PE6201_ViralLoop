# SUBMISSION_INDEX — Requirement → File → Status

Two requirement sources are used together: the **official PE6201 Assessment Timeline** and the **Problem Statement Watch-outs** companion. Where the packaging brief asked for something the course does not require, it is marked as *requested by author, not by the course*.

Legend — **Verified** means the file exists and its content was checked during packaging. **Not re-run** means the artefact is a frozen record and was deliberately not re-executed.

---

## Part A · Official course requirements

| # | Course requirement (source) | Submitted file | Status | Verified |
|---|---|---|---|---|
| A1 | **Problem Statement** — mandatory milestone, ~1 page, provided template (Timeline §1) | `REPORT/Problem_Statement_EN.md` | Complete — English rendering of the Week-3 submission, with a provenance note | ✅ content checked |
| A2 | **Business & technical trade-off analysis, ≤1,200 words** (Timeline §4) | `REPORT/Final_Report_EN.md` (~1,240 words) | Complete | ✅ word count checked |
| A3 | **Working code in a GitHub repository** (Timeline §4; Watch-outs check 4) | `CODE/` — all three rounds' real source | Complete and packaged — **public repo upload pending (see F1)** | ✅ files present |
| A4 | **Recorded video presentation / demo, face + screen visible** (Timeline §4) | `DEMO/Video_Script_EN.md` (script only) | **Script complete. Video NOT recorded** — author action required | ⚠️ see F1 |
| A5 | Repository must **run on someone else's machine** (Watch-outs check 4) | `CODE/README.md` | Documented; see honest verification note below | ⚠️ partially verified |
| A6 | Named dataset, named baseline, named number (check 2) | `DATA/DATA_README.md`, `REPORT/Final_Report_EN.md` §3–4 | Complete | ✅ |
| A7 | First person throughout (check 3) | `REPORT/` | Complete | ✅ |
| A8 | Read once for typos — communication is 25% (check 5) | all `REPORT/` documents | **Not done by the author yet** | ⚠️ see F1 |
| A9 | Submit to **NTULearn** (Timeline: "Submit to NTULearn unless a brief says otherwise") | — | **Author action required** | ❌ see F1 |

**On A5's honest verification note.** The commands in `CODE/README.md` were read from the actual scripts — nothing was guessed. They were **not re-executed against live APIs** during packaging, because the experiments are frozen and re-running them would consume paid budget and could mutate frozen outputs. `CODE/README.md` marks each such command **[NOT RE-RUN]** rather than claiming it was tested.

---

## Part B · Items the packaging brief asked for

| # | Brief item | Delivered as | Status |
|---|---|---|---|
| B1 | Final English project report, ~1200 words, specified storyline | `REPORT/Final_Report_EN.md` | ✅ |
| B2 | Data → `DATA_README.md` with source, cleaning, 36–38h window, labels, splits, leakage control, per-round usage, raw vs processed | `DATA/DATA_README.md` | ✅ |
| B3 | Evals → `EVALS_README.md` with what/why/IO/metric/result/limitations, including failed or stopped evals | `EVALS/EVALS_README.md` | ✅ |
| B4 | Code → `README.md` with setup, deps, API config, run/demo/repro commands, output locations | `CODE/README.md` | ✅ documented, ⚠️ not re-run |
| B5 | `CODE_MODULE_GUIDE.md` — file/module level | `CODE/CODE_MODULE_GUIDE.md` | ✅ |
| B6 | `PRODUCT_DOCUMENTATION.md` — persona, problem, IO, both architectures, external intelligence, metrics targeted vs reached, cost, limitations, final decision | `PRODUCT_DOCUMENTATION/PRODUCT_DOCUMENTATION.md` | ✅ |
| B7 | `ViralLoop_Demo.html` — all English, opens and pages correctly in a browser | `DEMO/ViralLoop_Demo.html` | ✅ self-contained, no server needed, 8 pages, arrow-key navigation |
| B8 | English video script (video recorded by the author, not faked) | `DEMO/Video_Script_EN.md` | ✅ script only — **video not recorded** |
| B9 | Round 1/2/3 explainers | `REPORT/Round1_Explainer.md`, `Round2_Explainer.md`, `Round3_Explainer.md` | ✅ |
| B10 | `SUBMISSION_INDEX.md` | this file | ✅ |
| B11 | `FINAL_SUBMISSION_CHECKLIST.md` | `FINAL_SUBMISSION_CHECKLIST.md` | ✅ |
| B12 | Clean submission folder: no keys, no secrets, no unrelated caches, no duplicate raws, no obsolete reports causing confusion, English filenames, clear structure | see §D | ✅ with three disclosed exceptions |
| B13 | Final submission audit | §A–§E of this file | ✅ |

---

## Part C · Round-by-round evidence coverage

Every item below points at a **real** artefact. "Planned" is never presented as "result".

### Round 1 — `REPORT/Round1_Explainer.md`

| Evidence | Location |
|---|---|
| Cleaned dataset / split information | `DATA/round1_dataset/` (`processed_posts.parquet`, `labels.parquet`, `splits/*.parquet`, `cleaning_log.csv`, `content_types.csv`) |
| Evaluator results (E0–E4) | `EVALS/round1_historical_and_generator/evaluator_results.csv`, `evaluator_dev_results.csv`, `evaluator_bootstrap.json` |
| Generator ladder results | `EVALS/round1_historical_and_generator/generator_results.csv`, `generator_summary.csv`, `generator_candidate_results.csv` |
| Feedback vs resampling result | `generator_paired_comparisons.csv`, `independent_generation_audit_summary.json`, `independent_generation_audit_comparisons.csv` |
| Cost / audit evidence | `cost_summary.json`, `cost_results.csv`, `api_ledger.jsonl`, `integrity_checks.json`, `failure_cases.csv` |
| Pattern cards | `EVALS/round1_historical_and_generator/pattern_cards/` |
| Round-1 human review status (not a result) | `EVALS/round1_historical_and_generator/human_review_package/` |
| Round-1 explainer | `REPORT/Round1_Explainer.md` |

### Round 2 — `REPORT/Round2_Explainer.md`

| Evidence | Location |
|---|---|
| Frozen configs | `CODE/round2_v002/configs/`, `DATA/round1_dataset/configs/` |
| V0 / V1 / V2 / O1 definitions | `REPORT/Round2_Explainer.md` §"Version definitions"; `CODE/round2_v002/generation.py` |
| Judge calibration / validation | `EVALS/round2_judge_and_final/controlled_pairs_*.json`, `challenge_summary_*.json`, `judge_validation_cases/`, `evaluator_admission_v002.json` |
| Final comparison results | `final_comparison_results_v002.csv`, `final_comparisons/`, `final_summary_v002.json` |
| Generation metrics | `final_generation_metrics_v002.json` |
| Token / cost / integrity audit (**FAIL**) | `contract_manifest_audit_v002.json`, `final_integrity_audit_v002.json`, `cost_summary_v002.json`, `api_ledger_v002.jsonl` |
| Real human naturalness feedback | `human_naturalness_submissions/`, `human_naturalness_revision_acceptance_v002.json`, `naturalness_user_review_v002.json` |
| Round-2 explainer | `REPORT/Round2_Explainer.md` |

### Round 3 — `REPORT/Round3_Explainer.md`

| Evidence | Location |
|---|---|
| Executed Dev configuration | `CODE/round3_v003/configs/`, `CODE/round3_v004/configs/`, `*_freeze_v00*.json` |
| Content-archetype / engagement redesign | `REPORT/Round3_Explainer.md` §Attempt 2; `CODE/round3_v004/configs/brief_schema_v004.json`, `archetype_routes_v004.json` |
| Actual generated Dev evidence | `EVALS/round3_dev_and_termination/v003/dev_cases/`, `v004/dev_cases/` |
| Real human feedback that exists | `EVALS/round3_dev_and_termination/v00*/` (naturalness/preview records); **no formal 8-group human Final exists** |
| Identity / ownership audit | `v003/identity_supplement/`, `identity_supplement_summary_v003.json` |
| Selector challenge | `v003/selector_challenge/`, `selector_challenge_summary_v003.json` |
| JEV connectivity probe | `v003/jev_preflight_v003.json` |
| Termination / why Final was not run | `v004/process_archive_v004.md`, `v004/dev_process_audit_v004.json`, `REPORT/Round3_Explainer.md` §Execution stop point |
| Round-3 explainer | `REPORT/Round3_Explainer.md` |

---

## Part D · Clean-folder compliance

| Rule | Status | Note |
|---|---|---|
| No API keys | ✅ | Automated secret scan over the whole package: **0 hits** |
| No secrets / tokens | ✅ | Keys are read from environment only; nothing hard-coded |
| No unrelated caches | ✅ | API caches, `__pycache__`, vendored libraries excluded |
| No bulk duplicate raw responses | ✅ | Per-call caches excluded; the run record (`runs/`) is kept because it is the provenance chain |
| No obsolete reports causing confusion | ✅ | Chinese in-progress drafts are **not** copied; each round has one English explainer |
| Key experiment evidence **not** deleted | ✅ | Frozen results, ledgers, audits and failure records are all preserved |
| English filenames | ⚠️ **three exceptions** — see below | All *new* files are English |
| Clear directory structure | ✅ | `REPORT/ DEMO/ CODE/ DATA/ EVALS/ PRODUCT_DOCUMENTATION/` + 2 index files |

**Disclosed filename exceptions.** Three items keep their original names because renaming them would break the provenance chain to the frozen experiment artefacts and to the parent report's evidence index:

1. Round-3 source folders retain `v003` / `v004` (these are version identifiers, already Latin).
2. A small number of copied evidence JSON files carry `_v002` / `_v003` / `_v004` suffixes — these are the **actual filenames written at run time**, and the report's audit trail references them.
3. `REPORT/source/` holds the original Chinese Problem Statement submission, preserved unchanged as provenance.

No raw experimental evidence was translated, rewritten, or truncated. Where Chinese content had to be preserved, an English specification accompanies it.

---

## Part E · The three submission claims, precisely stated

The report makes exactly these claims and no more:

1. **Historical relative high score is predictable** on this dataset and split — AP 0.552 (E2) and 0.585 (E4) against a 0.247 lazy baseline, with an author-clustered bootstrap interval of roughly [0.219, 0.405] for E2's increment.
2. **That predictability did not translate into a stable generation gain** — the feedback-vs-resampling difference is +0.0001395 with a CI containing zero, independently corroborated by an audit also containing zero.
3. **Round 3 terminated at Dev with no valid G1-vs-G0 conclusion** — because real content quality, not the experiment's schedule, was the reason to stop.

Anything beyond these three — virality, engagement lift, production readiness, commercial ROI — is explicitly **not** claimed anywhere in this submission.
