# FINAL_SUBMISSION_CHECKLIST

**Everything in this file is something only the author can do.** Nothing here has been done on your behalf, and nothing here was faked.

---

## 1. Must do before submitting

| # | Action | Why only you can do it | Done? |
|---|---|---|---|
| 1 | **Upload the repository to GitHub and confirm it is PUBLIC** | Requires your GitHub account and credentials. No valid token, SSH key or `gh` CLI was present on this machine. | ☐ |
| 2 | **Record the video presentation** (~5 min, face **and** screen visible) | The brief requires your own face and screen. The script is ready at `DEMO/Video_Script_EN.md`. | ☐ |
| 3 | **Check your name and matriculation number** appear correctly | Identity fields are placeholders in `REPORT/Problem_Statement_EN.md` | ☐ |
| 4 | **Submit to NTULearn** | Course requirement; only you have access | ☐ |
| 5 | **Convert the report to PDF** if NTULearn requires PDF rather than Markdown | NTULearn's accepted-format setting is not visible from here | ☐ |
| 6 | **Read the report once for typos** | The brief's fifth submit-check is "read it once for typos — communication is 25% of the project mark" | ☐ |
| 7 | **Confirm the deadline** in your email | The official timeline PDF in `work/` states the End-of-Course Project was due **Sun 20 Sep 2026**, while later correspondence referenced a different date. Verify which applies to you. | ☐ |
| 8 | **Open `DEMO/ViralLoop_Demo.html` once in a browser yourself** | It was verified as self-contained and English, but the final visual check should be on your machine | ☐ |

## 2. Recommended, not required

| # | Action | Note |
|---|---|---|
| 9 | Add a repository description and topic tags on GitHub | Helps a marker find it |
| 10 | Add the repo link into `REPORT/Final_Report_EN.md` | One line under the title |
| 11 | Record a 30-second screen-only clip of `ViralLoop_Demo.html` as a backup | If the live demo has issues during the video, you have a fallback |
| 12 | Delete or archive the working folders (`实验1.0版`, `实验1.1版`, `实验1.2版`) from any folder you share | They are the raw workspace; the submission package is self-contained |
| 13 | Double-check that `build_final_package.py` is not accidentally committed with a local path in it | It contains absolute Windows paths; harmless, but it is a build tool, not part of the submission |

The **one thing you must not do** is re-run the experiments. They are frozen. Re-running would consume paid budget, could mutate frozen outputs, and would create numbers that contradict the report.

---

## 3. What is already complete

| Deliverable | Status |
|---|---|
| Final English report (~1,240 words) | ✅ |
| Problem statement (English) | ✅ |
| Round 1 / 2 / 3 explainers | ✅ |
| `DATA_README.md` | ✅ |
| `EVALS_README.md` | ✅ |
| `CODE/README.md` + `CODE_MODULE_GUIDE.md` | ✅ |
| `PRODUCT_DOCUMENTATION.md` | ✅ |
| `ViralLoop_Demo.html` (English, 8 pages, self-contained) | ✅ |
| English video script | ✅ |
| `SUBMISSION_INDEX.md` | ✅ |
| Data, evals, code from all three rounds packaged | ✅ 429 files, 23.3 MB |
| Secret scan | ✅ 0 hits |
| Git repository initialised and committed locally | ✅ |

---

## 4. Honest caveats you should know before you present this

These are deliberate design decisions in the package, not oversights.

1. **The code was not re-executed.** Every command in `CODE/README.md` was read from the real scripts, but marked **[NOT RE-RUN]** where it was not executed. The experiments are frozen; re-running them would be wrong. If a marker asks "does this run?", the honest answer is: the pipeline ran end-to-end during the project and the artefacts are the record — but the live re-run was deliberately not performed during packaging.

2. **Round 2's protocol audit FAILED.** Token cap exceeded by ~22.5%; 11 manifests and 68 raw responses missing. This is disclosed in the report and in the explainers. Do not let it be discovered rather than stated — stating it first is a strength.

3. **Round 3's Final does not exist.** It was never run. The report says so explicitly. Do not fill it in under deadline pressure.

4. **The human evaluation is one reviewer, in Chinese.** It is real, and it is not representative. Both are stated.

5. **Raw corpora and embeddings are excluded** (65 MB + 108 MB) because they regenerate from the documented source. If a marker wants them, `data_pipeline.py` regenerates them.

6. **Three filenames are not English** — Round 3's `v003`/`v004` identifiers and the preserved original Chinese Problem Statement. Both are provenance, and the reasons are documented in `SUBMISSION_INDEX.md` §D.

---

## 5. The single sentence that matters most if you are asked the hard question

> **"The bottleneck was never how much machinery to add. It was whether the task was real and whether the measuring stick was calibrated — and I put calibrating the stick last, when it should have been first. On an uncalibrated target, a positive result and a negative result are equally uninterpretable."**
