# Round 3 Explainer — Task Realism Failed, and the Round Was Stopped at Dev

Working directories: `实验1.2版/v003` and `v004` → packaged as `CODE/round3_v003`, `CODE/round3_v004`, `EVALS/round3_dev_and_termination`.

## What Round 3 asked

A narrow question: **with the same full-fact input, does one explicit motivation/expression planning step beat a minimal safe baseline?** A secondary question: can a selector be found that agrees with real human preference?

Deliberately excluded from the main line: RAG, GEPA, multi-agent, feedback loops, and any new predictor. Explicitly allowed outcomes included "the baseline wins" and "no enhancement component shows a gain" — pre-declaring that a negative result was acceptable.

**Planned but not executed:** 8 Dev tasks and 6 new Final tasks; an optional title module requiring separate human validation; JEV integration within time and candidate limits.

## Attempt 1 (v003) — all eight tasks collapsed into help-seeking

G0 and G1 shared the same real source and full brief; G1 added one Motivation Planner call. The planner captured `current_user_goal`, `current_decision` and `desired_help`.

**The failure was structural, not incidental.** Those fields were applied to *every* task type, and the unified identity was set to "a community member currently making a decision and asking for help". Material that was plainly an experience report, an opinion or a resource was rewritten as *"I saw some old material and now I'd like your help"*.

| Source topic | What it became |
|---|---|
| Multilingual TTS and Anki | A request for help comparing technical options |
| M40/M60 hardware | A configuration help request |
| OpenRouter conversation export | Author identity blurred with source author |
| Long-context reasoning comparison | An unequal test recast as a discussion request |
| Qwen3 tech report | A release news item mislabelled as an experience post |
| Qwen3 multi-size model tests | Historical tests forced into a present-tense decision |
| SOCAMM technical analysis | An analysis piece turned into an advice request |
| Sigil local application | A resource/product showcase turned into a help request |

16 drafts were generated; the independent ownership/identity check passed **14/16**. D03's two drafts incorrectly inherited the source author's first-person experience. An earlier record described this as a translation problem; a faithful read-back clarified that the **Chinese translation preserved the English original's identity error** — it is a *generation ownership* bug, and it must not be papered over by quietly polishing the translation.

Claude ran AB/BA over the 8 pairs and reached **swap consistency of only 3/8**, below the planned 7/8. That number is *swap stability*, not accuracy against humans — human labels were never collected.

The user's substantive objection: nearly all 8 tasks were asking for advice, and the community's normal mix of discovery, opinion and resource posts was missing. That "all 8 dominated by a help-seeking frame" claim comes from schema and content inspection — it is **not** a completed 8-item human preference statistic.

Attempt 1 is preserved as a failed development attempt. No task was deleted, no label was swapped, no translation was retouched to improve the result.

## JEV — what was actually proven

An earlier check of the OpenRouter chat-model catalogue suggested JEV was hard to reach. It was later found that the **decision-output** model must be queried via the native `/api/v1/systemone` endpoint, not the ordinary chat route.

One genuine connectivity probe used `typesafe/jev-1.13-20260917`: 389 input tokens, 62 output tokens, **US$0.000016338**, latency ≈ **0.677 s**, returning a structured narrow judgement with confidence.

**Proven:** the JEV native judgement interface was reachable from the existing environment at that moment.

**Not proven:** that JEV agrees with real community preference, selects higher-value posts, is more reliable than Claude, or produces useful rewrite explanations. It never passed Dev admission or ran a Final. No JEV-class model was locally loaded, trained or validated.

"Successfully connected" must not be written as "the project used JEV to validate content".

## Attempt 2 (v004) — separating engagement from replyability

After the pause, the task taxonomy was rebuilt as four archetypes, 2 each: **A question, B finding/experience, C opinion, D resource.** Help-seeking ceased to be the default template; historical sources became *material*, not a mandatory posting reason.

The new brief schema used `content_archetype`, `speaker_role`, `source_relationship`, `posting_intent`, `current_context`, `core_value` and `core_hook`, with `decision`/`desired_help` required **only** for archetype A. G0 and G1 shared full material, the type route and fact constraints.

The **primary evaluation question also changed** — from *"which post would make you more likely to reply?"* to *"would you open this in your feed and keep reading?"* — with information value, like/save/share intent, naturalness and single-post publishability recorded separately, and explicit "I would not read either" and "cannot tell" options.

This is a genuine research-goal correction, not cosmetic: **comment-thread replyability is not the same as reading value.** It fixed the type collapse. It did not automatically fix language naturalness or the technical-community comprehension gap.

### The 8 new Dev sources

| ID | Type | Source content | Fact boundary that must hold |
|---|---|---|---|
| E01 | A question | Qwen2.5 LoRA output garbling, ~3k data and config | Must not impersonate the original author's training run |
| E02 | A question | S22 Ultra local inference speed vs a GPU-less device | Different conditions cannot be used to infer cause |
| E03 | B finding | Cerebras/Mistral ~1,100 tokens/s claim | A vendor/third-party claim, not a first-party measurement |
| E04 | B finding | Informal 10-model test on an M1 8GB MacBook Air | A small subjective test, not an unbiased benchmark |
| E05 | C opinion | A judgement on recent models and attention | Must stay an opinion, not become an empirical conclusion |
| E06 | C opinion | Criticism of Apple's "Illusion of Thinking" paper | The criticism's allegations are not verified facts |
| E07 | D resource | GraphRAG / multi-hop tutorials and RAG_TECHNIQUES | One tutorial's implementation ≠ the whole GraphRAG category |
| E08 | D resource | Local VS Code/Copilot, MCP, Continue/HF settings | Historical config cannot be described as currently available without a date |

Sources were drawn from Train by fixed hash and rule, excluding earlier-round sources and near-duplicates. Multiple sampling drafts were retained and the rules were adjusted before generation to correct type misclassification — so this must **not** be described as fully pre-registered sampling with an unchanging semantic classifier. Under the strict rule, type C had very few usable sources; both went into Dev, and the 6 new Final sources were never frozen or tested.

### Free-of-charge repair and the paid run

An offline dry-run passed 27 checks (type, source isolation, prior-evidence hash, schema, no-paid-calls). That supports **process constraints only** — it does not demonstrate generation quality.

On resume, 16 calls tried to generate and audit 8 briefs. All were initially rejected by enumeration validation: intent written as free text, missing required fields for archetype A, a few non-contiguous quotations and over-strong claims. The assistant applied **manual, no-new-API repairs grounded in the original material**, retaining the original responses and a repair log — and the repair happened **before any G0/G1 draft existed**, so both arms received identical repaired briefs.

A further 48 calls then produced 16 G0/G1 drafts with quality, independent identity/fact checks and faithful Chinese translation. Attempt 2 totalled **64 calls, US$0.0975549**.

Process audit status: `PASS_WITH_DOCUMENTED_BRIEF_REPAIR`. Old evidence, contract linkage, sources, ledger and Final isolation were preserved. This is **not** "zero-deviation execution" and **not** a fully automatic product flow.

### Generation quality and audit disagreement

Original automatic checks passed **7/16**. After supplementary checks, only **2/16** met both the original label and had no listed publication blocker — both from E01 (G0 and G1).

Main failure classes:

- E02/E06 bodies carried **internal fact numbering**. The old rule only caught uppercase `F` and missed lowercase `f`.
- E04's two drafts and one E05 draft described 2025 material as "recently" without a date.
- Both E07 drafts generalised a specific tutorial's scope to a broader technology category.
- One E06 draft stated the source's criticism too definitively.
- A junior judge flagged already-attributed and already-uncertain vendor claims and opinions as `unverified`, while the independent reviewer passed them — the two disagree on rule execution.
- Several drafts were no longer all help-seeking, but still read as **summaries of third-party material** rather than natural community expression.

**7/16 and 2/16 are process labels — not content accuracy, hallucination rates, or real publishability.** The original judge over-blocked; the supplementary check covered only some risks. The remaining 14 drafts must not be called "14 pieces of false content". Faithful translation did not rewrite these problems away, and a numeric-format change must not be mistaken for a translation error.

## Execution stop point

| Round 3 item | Actual status |
|---|---|
| Attempt 1: 8 Dev tasks, 16 drafts | Generated and archived |
| Attempt 1: Claude AB/BA | Run — swap consistency 3/8 |
| JEV native connectivity | One successful probe |
| Attempt 2: new 8 Dev tasks, 16 drafts | Generated, audited, translated, archived |
| Formal 8-group human preference statistic | **Not completed — not reconstructed** |
| JEV / alternative selector human admission | **Not completed** |
| 4 title-module human validations | **Not run** |
| 6 Final tasks after freezing P* | **Not run** |
| Online publication, engagement, virality | **Not run** |

At termination the new Dev interface was ready, but no formal complete Round 3 human evaluation submission exists. The user stopped the round based on the observed content quality and the problems above.

**Required framing:** *Round 3 terminated early at the Dev stage due to poor real-human quality feedback; no valid conclusion about G1 versus G0 can be given.*

"Terminated early" is neither dressing up an incomplete experiment as a success, nor silently converting missing data into a failure win-rate. It is a documented product and resource decision.
