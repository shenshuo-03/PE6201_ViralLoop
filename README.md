# ViralLoop — PE6201 End-of-Course Project · Final Submission

**Individual work · Shen Shuo**

**Submitted repository:** https://github.com/shenshuo-03/PE6201_ViralLoop (public)

ViralLoop is a research prototype that turns a real author's intent and dated source material into a
fact-constrained draft for technical communities, with rule-based checks and mandatory human
confirmation. It also contains three rounds of experiments testing whether historical engagement
signal can be turned into a generation advantage.

**The headline result is negative, and it is reported with the receipts attached:**
historical engagement is predictable, but that predictability did **not** transfer into a stable
generation gain. The bottlenecks were evaluator alignment, task realism, and complexity cost.

---

## Start here

| I want to… | Read |
|---|---|
| Understand the project and the result | [`REPORT/Final_Report_EN.md`](REPORT/Final_Report_EN.md) |
| See the original problem framing | [`REPORT/Problem_Statement_EN.md`](REPORT/Problem_Statement_EN.md) |
| Understand each round in detail | [`REPORT/Round1_Explainer.md`](REPORT/Round1_Explainer.md) · [`Round2`](REPORT/Round2_Explainer.md) · [`Round3`](REPORT/Round3_Explainer.md) |
| See the data and split logic | [`DATA/DATA_README.md`](DATA/DATA_README.md) |
| See every evaluation and its limits | [`EVALS/EVALS_README.md`](EVALS/EVALS_README.md) |
| Run the code | [`CODE/README.md`](CODE/README.md) |
| Understand the files and modules | [`CODE/CODE_MODULE_GUIDE.md`](CODE/CODE_MODULE_GUIDE.md) |
| Read the product documentation | [`PRODUCT_DOCUMENTATION/PRODUCT_DOCUMENTATION.md`](PRODUCT_DOCUMENTATION/PRODUCT_DOCUMENTATION.md) |
| Watch / read the demo | [`DEMO/`](DEMO/) — open `ViralLoop_Demo.html`, script in `Video_Script_EN.md` |
| Check what is submitted and what is outstanding | [`SUBMISSION_INDEX.md`](SUBMISSION_INDEX.md) · [`FINAL_SUBMISSION_CHECKLIST.md`](FINAL_SUBMISSION_CHECKLIST.md) |

---

## Repository layout

```
PE6201_ViralLoop_Final/
├── REPORT/          final report, problem statement, per-round explainers, figures
├── DEMO/            self-contained English demo page + English video script
├── CODE/            the real source of all three rounds + module guide
├── DATA/            the data actually used, split logic, provenance
├── EVALS/           every evaluation, its metric, result, and limitation
├── PRODUCT_DOCUMENTATION/  persona, architecture, metrics, cost, limitations
├── SUBMISSION_INDEX.md      requirement → file → status
└── FINAL_SUBMISSION_CHECKLIST.md   what only the author can still do
```

## Evidence discipline used throughout

Every number in this package is tagged with four things: **what it measured**, **on which sample**, **what it can support**, and **what it cannot**. In particular:

- A proxy score of 0.244 is **not** a 24.4% virality probability.
- "1 win in 8 comparisons" is **not** a 12.5% product success rate.
- "Round 3 terminated early" does **not** mean the planned Final was run.
- Automatic scores and human judgement are **different layers of evidence** and are never merged.
- Results from a run with a failed protocol audit are reported **with the failure attached**, not hidden.

Nothing in this repository was fabricated, back-filled, or reconstructed. Round 3's Final was never run, and no human feedback was invented.

## Cost

| Round | Ledger entries | Tokens | API cost (US$) |
|---|---:|---:|---:|
| Round 1 | 350 | 1,403,922 | 0.3442 |
| Round 2 (v002) | 500 | 1,230,780 | 0.7087 |
| Round 3 (v003 + v004) | 146 | 415,588 | 0.2639 |
| **Total** | **996** | **3,050,290** | **1.3168** |

This is experiment R&D cost, not a per-use production cost. It excludes Codex reasoning time, human effort, local compute and storage.

## Licence and data rights

The source dataset is ODC-BY, but the underlying Reddit author text may carry separate rights. This
repository ships processed artefacts and documentation rather than a commercial redistribution of
author content. See [`DATA/DATA_README.md`](DATA/DATA_README.md) §8.
