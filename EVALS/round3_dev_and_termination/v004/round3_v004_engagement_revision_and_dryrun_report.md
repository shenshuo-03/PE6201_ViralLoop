# ViralLoop Round 3: task-definition revision and zero-cost check report

> Status: **paused by the user; no posts were regenerated, no new paid API call was made, and Final was not entered.**
> Old batch: `Dev Attempt 1 / engagement-diversity failure`.
> New batch: Round 3 `Dev Attempt 2 / Engagement Objective Pivot`. The engineering directory is `loops/v004`, used to isolate the new objective and evidence from the old; it does not mean the work expanded into a fourth experiment round.

## 1. Root cause: the problem was in the task definition, the sampling and the evaluation objective

The eight briefs already executed, the original sources, the generation code, the Planner and the Chinese form were all inspected. **8/8 briefs contained non-empty `current_user_goal` / `current_decision` / `desired_help`; 8/8 posting identities were specified as seeking help.** This 8/8 count comes from the actual brief fields, not from a machine re-scoring of a "mode-collapse rate". The help-seeking tendency in the generated drafts matches the user's observation; no separate gold-standard taxonomy of post types was built.

| Stage | Actual evidence | How it caused the drift |
|---|---|---|
| Task template | `v003/experiment_contract_v003.yaml:58`: `A community member is considering a specific practical decision... Define goal, decision and desired help` | Manufactured a personal decision and a help need for every piece of material |
| Brief | `v003/code/round3_runner.py:67-68`: identity fixed to `community member seeking help...`, with the three help-seeking fields emitted globally | New discoveries, showcases and opinions had no task entry point of their own |
| G0/G1 common generation | Same file, line 70: `addressing current_user_goal, current_decision and desired_help` | Both arms were required to write around help-seeking |
| G1 Planner | Line 71: `organize but never change its user goal`; `current_goal/central_purpose/desired_response` | The Planner could only reinforce the wrong premise and could not restore the material's original propagation angle |
| Selector | Line 74: `current user goal`, `concretely motivated`, `worth_replying` | The evaluation favoured a clear purpose and replyability and never explicitly optimised reading interest, discovery value, or save/share |
| Human form | `v003/code/human_review.py`: showed goal/decision/desired help and asked primarily "if you could publish only one"; secondarily asked about motivation/replies | The review task's own anchor was help-seeking, so it could not detect the gain from other engagement mechanisms |
| Original sampling | `round3_bootstrap.py:23-25`: only Question, Experience, Discussion, using the old labels directly | Showcase/Resource were never independently covered; the old labels themselves misclassified |

Specific misclassifications: the old D05 Qwen3 technical report release was labelled Experience; the D08 Sigil application showcase was labelled Discussion. **There was no logical requirement that fact safety force help-seeking form; it was my implementation that over-restricted the user purpose to a decision-help request.**

The following English text was appended to the old process archive; the old contract, prompts and generation results were not rewritten:

> Dev Attempt 1 revealed a task-formulation mode collapse: heterogeneous source materials were systematically reframed as advice-seeking decision posts. This over-optimized for explicit motivation and replyability while underrepresenting novelty, discovery, opinion, showcase, and other engagement mechanisms.

## 2. Files changed and the reuse boundary

The old `v003` had only the following appended: the process archive, events, the user-pause file, and the Attempt 1 classification note. The pause file reuses the existing cost-request interception mechanism. The old Chinese blind-review service was stopped to avoid continuing to collect evaluations of invalid tasks.

The main new `v004` files:

| File | Purpose of change |
|---|---|
| `experiment_contract_v004.yaml` | Forward-looking contract, parent version, pause state, shared cost/request caps, metrics and admission rules |
| `configs/brief_schema_v004.json` | Four task categories; help-seeking fields mandatory only for A |
| `configs/archetype_routes_v004.json` | Shared writing route across the four categories, identical for G0/G1 |
| `prompts/BRIEF/AUDIT/BASEPROMPT/PLAN/QUALITY/TRANSLATE/JUDGE_v004.txt` | Task definition, engagement planning, hard constraints, faithful translation and evaluation objective |
| `code/round3_runner.py` | Copied from the old runner and modified in place; retains cache, threads, ledger, manifest, budget reservation; adds paid-call disablement and native JEV interface adaptation |
| `code/selector_v004.py` | AB/BA comparison on the same objective, five-label conversion and the old thresholds; requires new human labels first |
| `code/human_review.py` | Reuses the old form; changes the questions and diagnostic multi-select, without building a new service framework |
| `inputs/source_assignment_v004.json`, `sources/` | The 8 new sources and full bodies; no generated output |
| `results/source_shape_review_v004.json` | Archetype check after actually reading the full texts; does not masquerade as scientific fact verification |
| `code/offline_validate_v004.py` | No-network interception and checks on fields / routing / form / source isolation / old evidence |
| `results/attempt1_preservation_baseline_v004.json` | Per-file hash baseline of the old evidence |

Workspace helper files: `engagement_pivot_dryrun.py`, `engagement_pivot_finalize.py`, `engagement_pivot_patch.py`, `engagement_pivot_report.py`. These are one-off offline migration and reporting tools and **are not new agents or experiment components**.

## 3. The four archetypes and the 8 new tasks

| Category | Core value | Suggested development |
|---|---|---|
| A Troubleshooting / Advice | Help solve a specific problem | problem -> environment -> limitations -> an answerable question |
| B Finding / Benchmark / Result | A notable result, contrast or discovery | finding -> minimum evidence -> significance -> limits/optional discussion |
| C Opinion / Debate / Trade-off | A defensible position and a genuine trade-off | position -> evidence -> trade-off -> optional dissent |
| D Showcase / Release / Resource | The use value of a capability, tool or resource | what it is -> capability -> who it suits -> limits |

These are directional constraints and **not a uniform sentence pattern or mandatory closing template**. B and D may overlap; the main writing purpose for a task is fixed in advance and the category is not changed on the fly according to which version reads better.

The 8 new task sources are below, 2 per category; seed `v004-engagement-6201305`, ordered by a fixed hash, with no filtering by score, upvotes or generation result:

| Task | Category | Original title | Date |
|---|---|---|---|
|E01|A|Help Needed|2025-04-15|
|E02|A|Can someone help verify these speeds I'm getting from an LLM run on my phone? |2025-01-13|
|E03|B|Cerebras brings instant inference to Mistral Le Chat (Mistral Large 2 @ 1100 tokens/s)|2025-02-07|
|E04|B|I tested 10 LLMs locally on my MacBook Air M1 (8GB RAM!) – Here's what actually works-|2025-06-28|
|E05|C|Recent models really make me think attention is all we need|2025-03-25|
|E06|C|Comment on The Illusion of Thinking: Recent paper from Apple contain glaring flaws in the original study's experimental design, from not considering token limit to testing unsolvable puzzles.|2025-06-14|
|E07|D|Step-by-step GraphRAG tutorial for multi-hop QA - from the RAG_Techniques repo (16K+ stars)|2025-06-05|
|E08|D|Local Open Source VScode Copilot model with MCP|2025-06-16|

Sampling excluded sources already used in Round 2 as well as Round 3's old 14 Dev/Final sources and their duplicate groups; TF-IDF similarity to any old source had to be below 0.45. That rule reduces duplication risk but cannot prove there is no semantic overlap. The new sources are all new **writing tasks** drawn from the historical Train, and no claim is made that they are also unseen data for the old predictor.

Offline work found that keyword rules still misclassify. The initial candidates and the failure reasons are retained in `sampling_draft1..4`; the rule fix happened **before any new generation, preference or engagement result**. Finally the full texts were read to confirm each task's dominant archetype.

One unresolved Final limitation must be flagged: the strict rule currently yields only 2 type-C sources, and both were used in Dev. **They cannot be reused as the independent Final C tasks.** The Final target is provisionally A1/B2/C2/D1 but has not been allocated; before entering Final, the remaining unexposed material must undergo a source-level suitability check and be sealed, otherwise the conclusion must be narrowed. Help-seeking sources must not be relabelled as opinion to make up the numbers. This check needs no model generation and no paid call.

## 4. The new brief/scenario schema

Required: topic, audience, content_archetype, speaker_role, source_relationship, source_date, posting_intent, current_context, core_value, core_hook, facts, limitations, allowed_claims, forbidden_claims.

`decision`/`desired_help` are **mandatory only for A**; B/C/D default to null. "Having a purpose" must not be interpreted as "having a personal help-seeking decision". posting_intent may be: ask_for_help, share_finding, discuss_result, challenge_assumption, share_resource, showcase_project, compare_options, invite_debate; the current mis-conversion of B/C/D into ask_for_help is rejected by validation.

The following is a structural illustration, **not an actually generated brief, and the single fact shown is only illustrative; the real requirement is 4-8 facts**:

```json
{
  "content_archetype": "B",
  "speaker_role": "community analyst, not source author",
  "source_relationship": "third_party_archive",
  "source_date": "<original date>",
  "posting_intent": "share_finding",
  "current_context": "Controlled product input: share an archived finding relevant to a local-inference choice; no claim that it happened today",
  "core_value": "The concrete informational value a reader can take away",
  "core_hook": {
    "text": "A contrast or finding supported by the source",
    "fact_refs": [
      "F1"
    ]
  },
  "facts": [
    {
      "id": "F1",
      "text": "What the original author or vendor reported; not independently confirmed",
      "evidence_quote": "A contiguous short quote from the source",
      "status": "author_report | vendor_claim | opinion | verified_fact"
    }
  ],
  "limitations": [
    "Conditions not fully comparable, publication date, not independently verified, and so on"
  ],
  "allowed_claims": [
    "Attributed, bounded statements that are allowed"
  ],
  "forbidden_claims": [
    "Personal testing, fabricated data, presenting an old release as a release made today"
  ],
  "decision": null,
  "desired_help": null
}
```

`current_context` may carry the controlled product input of "why this finding or resource is worth sharing"; it must not invent a new development that happened today. The old content's dates, third-party attribution and conditions are retained. `core_hook.fact_refs` may only reference existing facts.

A source quotation only proves "the source said this"; it does not prove the conclusion is scientifically correct. For example: the E03 speed figure is a vendor/reposted claim; the E04 quality scores include model self-evaluation bias; E05 is speculation; the criticism in E06 has not been independently verified. The corresponding attribution and uncertainty must be preserved at generation time.

## 5. G0/G1 and the full Engagement Planner prompt

G0 = Minimum Safe Baseline. G1 = the same G0 generation flow + one short Engagement Planner call. Both arms use **the same frozen brief, sources, identity, common category route, fact constraints, generation model and body/title length limits**. Only G1 receives the plan result; G1 is not given more real material or looser safety constraints.

G1 output: content_archetype, primary_value, strongest_grounded_hook, why_readers_should_care, recommended_angle, essential_context, facts_to_emphasize, facts_optional, natural_opening_strategy, natural_ending_strategy, engagement_risk, safety_constraints.

The actual English prompt is below, and has been written into the file the runner reads:

```text
You are a short Engagement Planner for a complete grounded brief, not a universal help/motivation planner. Preserve the assigned content_archetype and posting_intent. Return JSON {content_archetype,primary_value,strongest_grounded_hook,why_readers_should_care,recommended_angle,essential_context,facts_to_emphasize,facts_optional,natural_opening_strategy,natural_ending_strategy,engagement_risk,safety_constraints}. primary_value is novelty|utility|surprise|contrast|debate|discovery|resource. facts_to_emphasize/facts_optional contain existing fact IDs. Hook must be supported by those facts, with source date, attribution and limitations. A may center a specific answerable issue; B centers a reported finding and its limits; C centers a defensible position and genuine trade-off; D centers a resource/capability and who can use it. Do not impose a personal decision, question opening or advice-seeking ending on B/C/D. Do not invent firsthand ownership, expertise, tests, newness, conflict or causality. Choose a natural ending, which may be a takeaway, limit or invitation; a question is not mandatory. No new facts. Explain what would make THIS archetype dull, generic or AI-written.
```

The observation can at most support "whether the Engagement Planning pipeline helps"; it cannot on its own demonstrate the causal effect of any one abstract psychological mechanism.

## 6. The new human Dev evaluation

Still 8 G0/G1 groups, with no increase in task count and no model identity or score given to the user. Faithful Chinese translation, with the English expandable. Per group:

1. **Main question: if both posts appeared in your feed at the same time, which one would you be more willing to open and keep reading?**
2. Which one leaves you feeling afterwards that it "had something in it, was valuable"?
3. Which one is more likely to make you upvote, save or share?
4. Which one is more likely to prompt a substantive comment or discussion from you?
5. Which one feels more natural, more like a real person posting rather than an AI compiling material?
6. Is each of A and B worth publishing: Yes / No / Uncertain.

Comparison options: A / B / Tie / Both unacceptable / Uncertain. "Both are not worth publishing" and "neither is attractive to read" are related but not identical judgements, so per-draft publishability is retained separately.

Diagnostic multi-select: reads too much like a material summary, reads too much like a help-seeking template, too ordinary / no hook, information too dense, not enough information, title unattractive, position or result not prominent, over-clickbait, posting motivation feels unreal, other. Fact checking is the responsibility of the system and the source review; the user is not required to become a technical expert.

No new 8 groups were generated and no new blind-review service was started. Placeholder text on the offline page is explicitly marked as a structure check and **is not experiment output or a human evaluation**.

## 7. Selector rubric and hard gates

Hard gates first: no fabricated results/numbers, third-party identity truthful, dates and key conditions preserved, not seriously misleading, no large-scale copying, basically natural and comprehensible, title consistent with the body. A hard-gate failure still counts as a task failure: it is not deleted, the task is not swapped, and it is not offset by a high engagement score.

Only after passing are these compared: attention, information_gain, novelty_or_interest, utility, genuine tension/contrast, comment_potential, save_share_potential, naturalness. The primary label is overall_engagement_preference, aligned with a real reader's willingness to read in a feed.

The actual rubric:

```text
Compare two same-brief community posts after hard factual/identity gates. Primary: if both appear in a reader's feed, which would the reader click and continue reading? Assess attention, information_gain, novelty_or_interest, utility, genuine tension_or_contrast, comment_potential, save_share_potential and naturalness, considering the assigned archetype. Clear help requests are not inherently better than findings, opinions or showcases. Do not reward fabrication, clickbait, fake controversy, verbosity, position or model identity. A/B/Tie/Both unacceptable/Uncertain: Tie is similar appeal, Both unacceptable means neither worth reading/publishing, Uncertain means insufficient basis. Return JSON {overall_engagement_preference,attention,information_gain,novelty_or_interest,comment_potential,save_share_potential,naturalness,evidence}. The same five labels apply to each comparison. evidence is a short grounded reason; Jev returns narrow structured decisions instead of pretending to explain.
```

Only the two candidates JEV and Claude are retained; no third will be sought. JEV did connect successfully in the previous stage, but **a successful connection does not mean the new objective has passed calibration**. JEV was not called again in this pass. The native `systemone` interface has been adapted to the shared cost ledger and cache; the new interface path has not yet been executed and verified on a real new task.

Admission on 8 tasks: overall label agreement >= 6/8, at least 4 tasks with a clear human A/B, machine agreement >= 75% on the clear tasks, and AB/BA agreement >= 7/8; passing must not rely on a large number of abstentions. When all pass, coverage, cost and simplicity are considered, and a one-vote gap is not used to force a ranking. Claude's old 3/8 position-consistency failure is retained; the new objective may not inherit an old conclusion or claim it has been admitted.

If fact failures leave fewer than 8 valid calibration pairs, the Selector does not pass on a denominator with the hard problems deleted; it stays unadmitted and sources are not replaced. A human may rate the appeal of an actual draft, but an unsafe draft cannot become a deployable winner. After that, Final only performs a generalisation check on new tasks and does not claim a fully independent Selector accuracy test.

## 8. One example per category from the old sources: the angle changes, not the facts

The following is **design expectation, not a new generation result or effect data**:

| Category / old material | Old actual task or old flow tendency | Angle the new flow should preserve | Must not cross the line |
|---|---|---|---|
| A / D01 multilingual TTS and Anki | Choosing a local TTS and asking the community for advice | A concrete help request may be kept: language coverage, stability, distribution/voice-licensing constraints, narrowed into an answerable question | Do not claim the new poster already built a plugin or personally tested XTTS |
| B / D06 Qwen3 multi-model tests | Turned multi-model results into "which Qwen3 should I choose?" | On some tasks, reported scores for smaller/MoE models contrast with the large model; lead with the finding, then give the task and language limits | Do not turn a small test into small models generally winning, and do not invent test conditions |
| C / D07 SOCAMM analysis | Turned a technical analysis into the poster's own hardware choice / deployment help request | The trade-off among bandwidth, power and volume raised by the source; state clearly that it is the source's argument and an assumption to be checked | The material may contain technical misstatements; do not treat it as verified engineering principle, and drop the assertion if necessary |
| D / D08 Sigil application | The old brief actually became "I am building a local LLM app, should I choose tabs or a single chat view?" | Show what Sigil's per-tab prompt/parameters, persistent chats and offline capability are worth to someone trying many models | Do not impersonate the developer, do not call an old update a release made today, and do not invent trial experience or repository links |

For example, the new D08 angle could be "each tab keeps its own system prompt and sampling settings, and this small feature solves context mixing when trying many models", without introducing a fictional personal UI decision. Whether it is genuinely more worth reading still needs a new blind review.

## 9. Old-data preservation and the offline check

A hash baseline was built over **578 existing files**: the old sources, the 16 drafts, translations, machine evaluations, raw requests/responses, ledger, contract, prompts and code. Every file was checked as unchanged; only the archive and events had explanatory text appended, plus the new pause and classification files.

This offline verification covered: 2 tasks in each of the four categories; source groups unique and isolated from the old Dev/Final; B/C/D not requiring help-seeking fields; A rejected when the help field is missing; non-A help-seeking collapse rejected; shared G0/G1 route; Selector rejects when no new human labels exist; the paid API entry point rejects before reaching the network; old evidence and the cost ledger unchanged; no automatic Final entry point; and the Chinese form's questions and diagnostic multi-select render.

**An offline check PASS covers configuration, source shape and interception logic only.** It does not mean the new generation quality has passed, that JEV is effective, that the generator's performance has improved, or that Final is ready. A new independent Final opinion-category source and a real run verification remain outstanding.

## 10. Request and cost estimates

| Stage | New requests |
|---|---:|
| 8 briefs + 8 source audits | 16 |
| G0/G1 x 8 drafts each | 16 |
| 8 Engagement Planner calls | 8 |
| Primary quality review + independent identity/fact review | 16 |
| 8 faithful Chinese translations | 8 |
| **Subtotal to regenerate 8 groups and hand them to a human** | **64** |
| After the human evaluation, JEV AB/BA calibration | 16 |
| Base-route total | **80** |
| Up to 8 error-correction/network retries reserved; not unlimited retries per request | 8 |
| **Attempt 2 main-line hard cap** | **88** |

If JEV is not admitted, Claude's 16 AB/BA calls may be run separately when the shared budget allows, **without automatically raising Attempt 2's cap of 88**; the stage budget must be rechecked. If both models turn out poor, seeking a third is forbidden.

Estimate: delivering the new 8 pairs costs about US$0.12-0.25; including JEV calibration and limited error correction, about US$0.15-0.35. This is a planned value, not an incurred cost. For reference, the equivalent 8-task base generation/translation in the old execution cost about US$0.089 and supplementary review about US$0.017; the new prompt length and output may differ. The JEV figure uses an existing price snapshot; before resuming, prices must be refreshed for free and each call intercepted with a conservative cost reservation, and an estimate must not replace the cap.

Round 3 has already spent **US$0.166365038 over 82 requests**, and v004 does not reset it to zero; Round 3's shared US$1.25 and the project's shared US$5 constraints continue to apply. After preserving Final's US$0.45, the currently available Dev budget is about **US$0.633635**. The worst-case 88 new calls would bring Round 3 to 170 requests, leaving 50, **which is not enough to promise that the whole original Final flow can be completed**. The Final call count and budget must therefore be rechecked, and progress must not be automatic.

## 11. Execution order after resuming, and the completion standard

The pause continues for now. After the user resumes: free price check / forward-looking contract and source-isolation confirmation -> freeze this pass's inputs/code/prompts -> generate only the new 8 pairs and complete the hard-gate review -> submit for genuine human blind review -> calibrate the established JEV/Claude -> decide whether to keep G1. The title module remains an optional 4 tasks, requiring at least 3/4 to show a clear preference for an optimised title, without exaggerating or altering body facts.

G1 needs at least 5/8 clear wins, with per-draft publishability and safety failures listed separately; a small sample supports only an exploratory choice and may not claim a significant improvement or a real virality rate. Tie and Uncertain are listed separately, and the report primarily gives W/L/Tie/Both unacceptable/Uncertain, the clear-task win rate, coverage and publishability, without halving Uncertain to produce a flattering headline.

The completion standard now: the task definition and evaluation objective have been corrected; the old evidence is preserved; the 8 new tasks are balanced and have passed the source-shape check; the zero-cost checks pass. **The new 8 pairs have not been run, Final has not run, and no new evidence exists on product effectiveness.**
