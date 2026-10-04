# Problem Statement (English version)

**PE6201 · End-of-Course Project · Milestone 1**
Name: Shen Shuo · Individual · Formative (not graded) — maps to Rubric criteria 1 & 2

> **Provenance note.** This is the English rendering of the Problem Statement submitted in Week 3 (`Shen_Shuo_B.txt`). The original Chinese submission text is preserved unchanged in `REPORT/source/Shen_Shuo_B_original.txt`. Where the project changed direction after instructor feedback, the change is noted rather than back-dated into the original wording.

---

## 1 · Working title

**ViralLoop — a fact-constrained community post drafting and evaluation prototype for technical communities.**

## 2 · The problem, and why it matters

People who work on AI products have things worth sharing — a test that contradicted the received wisdom, a config that fixed a latency problem, a resource nobody has packaged well. Most of them cannot turn that into a post that a technical community will read, because the judgement about *what the hook is* and *what to leave out* is tacit and hard-won.

**The closest existing tools** are generic AI writing assistants (ChatGPT, Jasper, Copy.ai) and community-specific drafting helpers. They optimise for fluency and completeness. None of them can tell an author whether a draft is something a real community member would actually post, and none of them is grounded in verifiable source material — so the failure mode is a confident, well-written, unpostable summary.

**The gap:** nobody measures whether historical engagement signal transfers into *generation quality*. Fluency is cheap; postability is not.

**Out of scope:** automated publishing, cross-platform virality prediction, commercial launch, model fine-tuning.

## 3 · Who it's for, and the domain

**Primary user:** Wei, an engineer at an early-stage AI startup. He has just finished an internal benchmark and found something surprising. He has 40 minutes between meetings, a scratch note of raw numbers, and no idea whether "we cut p99 from 480ms to 90ms" is the headline or a footnote. He reads r/LocalLLaMA and Hacker News daily but has never posted on either. He does **not** know what a scoring model is, and would not trust one if he did.

**What changes when the system works:** Wei gets a draft he recognises as *his own point, better organised*, and can post it in ten minutes instead of abandoning it.

**Domain:** developer tooling and applied AI — a domain I already know, which the course watch-out explicitly recommends.

## 4 · Why AI — and which kind

**Yes, AI is the right tool, and the right kind is prompting a rented foundation model.** The task is open-ended natural-language generation with no fixed answer set; there is no rule or lookup table that drafts a post.

I will climb the ladder only as far as the evidence justifies, testing each rung:
- **Zero-shot / few-shot prompting** — the cheapest thing that often works.
- **RAG** — only if grounding in retrieved examples demonstrably helps.
- **Narrow ML** — a TF-IDF logistic regression as the *measurement* tool for historical engagement signal, not as the generator.
- **Agents** — not without a task that genuinely needs a multi-step tool loop.

**Non-AI baseline:** a lazy classifier (always predict the minority-majority class) plus a constant prior. Any accuracy claim will be reported against it.

**What stays rules:** fact, identity and date validation are deterministic checks, together with mandatory human confirmation. Neither is delegated to the model.

## 5 · Proposed approach — build vs buy

| Layer | Own / rent | Reason |
|---|---|---|
| Data processing, split, labels | Own | Control leakage, observation age, traceability |
| Historical classifier | Own (off-the-shelf ML libs) | Cheap, freezable comparison baseline |
| Semantic representation | Rent (embedding API) | Avoid training cost |
| Generation, diagnosis, auto-judge | Rent (LLM APIs) | Fast to implement |
| Retrieval, orchestration, cache, ledger | Own | Project-specific control and auditability |
| Human review interface | Own (local service) | Lower the cost of real feedback |
| Final selection and publishing | Human | Automatic evaluation is not yet trustworthy |

**Cost per use** is tracked per call rather than estimated: each API call logs provider, model, input/output tokens and price, and the ledger is reconciled against the pricing table in `configs/model_prices.json`. The declared budget ceiling for the project is US$5.

## 6 · Data

**Named source:** [`pszemraj/LocalLLaMA-posts`](https://huggingface.co/datasets/pszemraj/LocalLLaMA-posts) — a Reddit r/LocalLLaMA archive, **100,679 rows**, ODC-BY.

The dataset measures **net vote score within one community over time**, which is *not* impressions, clicks or unique readers. The target is therefore defined as **relative high score within month × content type**, not "viral".

Additional fields (`score`, `retrieved_on`) are recovered from the same upstream archive so that observation age can be held roughly constant. Splits are temporal to prevent leakage.

**Constraints:** ODC-BY covers the dataset licence but Reddit author text may carry separate rights — so the repository ships processed artefacts and a download script, not a commercial redistribution of author content.

## 7 · Success metric and how I will evaluate it

**One metric:** Average Precision on a held-out set of historical posts, **target AP ≥ 0.40 and clearly above the lazy baseline (0.247)**, measured on a Final split of ~348 posts that is never used for tuning.

**The eval I will actually run:**
1. **Historical evaluation** — E0 lazy/prior through E4 semantic, reported with P/R/F1/AP, plus author-clustered bootstrap intervals.
2. **Leakage check** — report AP before and after removing any post-publication field.
3. **Judge admission** — an automatic judge is a *component*, not an oracle: it must pass a controlled comparison set with a declared agreement threshold per dimension before it may select anything.
4. **Abstention** — the system declines and reports when material is insufficient, and I measure how often it declines and whether those cases were the ones it would have got wrong.
5. **Human check** — real reviewers rate both *relative preference* and *absolute postability*.

## 8 · Risks, limitations and responsible use

| Risk | Mitigation |
|---|---|
| Confident fabrication of facts | Prompt-level fact red-lines + deterministic source/date checks + abstain when material is insufficient |
| Third-party experience written as the author's own | Mandatory `speaker_role` field; independent identity audit |
| Silent failure — a plausible but wrong post is shipped | **Mandatory human confirmation**; no automated publish path is built |
| Over-claiming virality | No probability is ever shown to the user |
| Community norms against generated text | The tool drafts for review; it does not post |

**Non-use:** no automated posting, no engagement farming, no inferences about individuals. Frameworks: IMDA Model AI Governance Framework (human accountability) and OWASP Top 10 for LLM Applications 2025 (prompt injection — source material is treated as data, never instructions).

## 9 · Smallest first version

**One end-to-end path:** one brief in → one model call → one draft out, with the fact red-lines in the prompt.

**The sentence that tells me it worked:** *given a real author's brief, the system returns a draft the author would be willing to publish under their own name.* Tested on real briefs, not synthetic ones.

---

## Instructor feedback that changed the direction

The written feedback on this statement recommended reviewing the **Precision, Recall and cost specifically for the high-performing class**, since a widely-cited "80% agreement" can be achieved by a system that never predicts high performance at all. That directly shaped §7: the lazy baseline became a first-class comparison, and AP was chosen over accuracy because AP rewards ranking the minority positive class correctly.

A later, second direction change came from the project's own evidence rather than from feedback: after Round 1 showed that historical predictability did not transfer into generation gains, the deliverable narrowed from "a loop that optimises posts" to "a fact-constrained drafting assistant with honest evaluation limits". That change is documented in `Round1_Explainer.md`.
