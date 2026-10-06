# PE6201 ViralLoop Experiment 1.1: Practical Execution Plan v4.1 (revised execution edition)

Date: 4 October 2026. Status: design complete, the second paid experiment has not been executed. This document replaces the v4 execution arrangements; all original files for v3, v4 and Experiment 1.0 are retained. Only the protocol is updated; Round 2 has not been started.

Revisions in this edition: the external judge does not take part in generator Tune/Selection; the headline result separates wins, ties, uncertain outcomes and failures; at most two pre-declared internal candidates for the evaluator, with model shopping stopped after freeze; nothing is tied to Jev.

## 1. Final goal: the generator is the product, the evaluator is a tool

Build a content generator that, from a real topic, audience and factual material, produces a natural, specific, informative English post suitable for r/LocalLLaMA, and that supports one optional rewrite.

The ultimate aim is to raise the production rate of genuinely high-performing content. Round 2 first tests two checkable questions:

1. Compared with a simple generation by the same model, does the system more reliably produce copy worth publishing?
2. Did the extra cost of RAG and feedback buy an improvement recognised by independent review and by a genuine human?

The historical high-performance association evaluation is retained, but neither it nor any judge probability may be read directly as a probability of going viral. Proving real propagation requires later prospective publishing evidence; this document designs that as a separate stage and does not pretend the offline experiment has already delivered that validation.

**The delivery decision is allowed to favour the simple option.** If Strong Prompt is the most effective, deliver that; if feedback adds nothing, switch default feedback off. A complex method must not be adopted merely to display a closed loop.

## 2. Product inputs and outputs

Inputs: topic, target audience, posting purpose, real facts/material, necessary conditions, optional tone.

Outputs:

- A recommended draft and an alternative, both editable by the user.
- Fact provenance, and which statements are advice or inference.
- Diagnostics for community fit, specificity and information value.
- One optional rewrite round with a before/after difference.
- Uncertainty, cost and latency; when facts are insufficient, ask for the key missing condition or emit an explicit placeholder.

It does not output an unverified "69% virality probability", does not invent measurements or personal experience, and does not post automatically. The original interface was Chinese and the published draft English; Chinese translations for the user's reading were shown side by side with the English original. This submitted package is English-only.

## 3. Reuse from Round 1, and isolation

Reuse the original data, the 36-38 hour window, the 2,336 cleaned records, the temporal splits, E2/E4, the retrieval index, the twelve pattern cards, the API cache and the ledger. The historical models are not retrained and the historical Final is not re-run.

Round 1 result constraints: historical prediction carries signal; the complex generator configurations and feedback showed no reliable advantage; the hypothetical material made the posts abstract. Round 2 must not continue to use a hypothetical experiment as the main task.

Round 2 creates its own directory and run_ids; 1.0 is read-only. Shared cache entries must be located by the full model, request and configuration hash, and an old cached result must never be recorded as a new call.

Final posts already exposed in Round 1, and the final generation topics, are known historical evidence only: they may not enter a new prompt, retrieval, calibration or a new independent Final. The data split for new generation tasks is registered separately from the historical classification split.

## 4. The evaluator is not tied to a model: Jev as an investigated candidate

Candidates may come from a structured decision model, a dedicated evaluation model, or a general LLM judge. Pre-check task suitability, existing access, price and call stability first, then write at most two internal candidates into the contract; not all three categories must be run, and popularity is not a reason to prefer one. Jev is only one candidate. The investigation below is a snapshot from earlier checking and does not mean it was wired up at run time.

### 4.1 Verification findings

Jev is TypeSafe's structured decision model, supporting Choice, Score and Noul (boolean judgement probability). It does not generate prose explanations and suits narrow judgements over given material. The vendor recommends splitting a complex judgement into independent questions. [Official capability notes](https://docs.typesafe.ai/introduction)

The fixed version the vendor currently lists is `jev-1.13.0`; direct-connection input is priced at US$0.042 per million tokens, output is free, and English is the main training language. The formal experiment pins the version and does not use the mutable `latest` alias. Price, response version and availability still need runtime verification. [Official model page](https://docs.typesafe.ai/models)

The public `jev-as-a-judge` project tests repeated judgements over five weather-agent records; it suggests low cost and repeat stability are worth verifying, but it is not 500 independent tasks and is not evidence of reliability for community writing. [Original project record](https://github.com/danielgshea/jev-as-a-judge)

MLflow has also published a technical-QA factuality evaluation case; that too cannot be extrapolated directly to copy preference. [MLflow experiment note](https://mlflow.org/blog/jev-llm-judge/)

### 4.2 Current integration status

This read-only check found: no `TYPESAFE_API_KEY` in the environment; the OpenRouter standard model catalogue lists only `typesafe/jev-router`, with a price field of `-1`, and it is unconfirmed whether it can be used through the existing standard calling method. No real Jev call was made, so integration must not be claimed as successful.

At execution time, read the official index and API documentation first and confirm the direct or gateway path, account permissions, actual billing and pinned version. Do not submit the existing OpenRouter key to an unofficial gateway. Do not treat a negative or missing price as free.

If a pre-declared candidate needs new credentials, proceed first through the channels already authorised; only when it is necessary and would affect the core task should the user be asked to configure an official key, and it must never be pasted into chat. All new evaluation interfaces together get at most 30 minutes of engineering investigation, not 30 minutes each. After pre-checking, pin at most two internal candidates and one external judge, and register the substitution rule for interface failures. Anything that cannot be connected is recorded as unavailable; do not install complex environments or keep searching for a third or fourth internal model.

### 4.3 Correct role

Jev is used for fact-support checks, narrow per-dimension judgements, A/B/Tie selection and candidate screening. The returned probability is the probability of the judgement option, not the post's real probability of going viral.

Jev does not carry the open-ended "weakness -> evidence -> edit suggestion" prose generation. The explanation module is implemented by another LLM, which forms suggestions from the brief and actual excerpts in the candidates and then checks whether a suggestion is fact-safe and whether it improves the draft. This is an additional LLM explanation and does not claim to expose Jev's internal reasoning.

## 5. Model roles and the default route

| Role | Preferred configuration | Authority |
| --- | --- | --- |
| Copy generator | GPT-4.1-mini, the same model for every variant | Generate and one rewrite |
| Internal decision model | One chosen from at most two pre-declared candidates; Jev may be a candidate but is not required | Narrow fact checks, draft selection, accept/reject a rewrite |
| Diagnoser | A cheap generative model; may be folded in when the internal judge reliably emits diagnostics | Name one problem and one action from the material only |
| External final judge | Pre-pinned, from a different family from the generator and the internal diagnosis/decision models | May run independent controlled admission checks; does not read the generator's Tune/Selection outputs and only evaluates generation outcomes at Final |
| Historical association audit | Frozen E2 and E4 | Supports the report; does not direct rewriting |
| Human | The user, possibly plus someone familiar with the target community | Independent preference and product acceptance |

The concrete gateway IDs, prices and availability are frozen once determined in the pre-check record; interfaces are never guessed from names. Candidate internal judges are chosen within Calibration under pre-declared criteria and then accepted at Validation; a model is not swapped for another and retried based on Validation results. Different model types sit the same item bank; a specialised name brings no admission exemption. If the budget cannot support an independent external judge, the "independent automatic validation" conclusion is dropped, and the internal judge may not be substituted for it.

Using a different family only reduces one kind of risk; it does not guarantee independent correctness. The external judge must also pass the controlled checks, and the human retains a non-substitutable acceptance role.

## 6. Real briefs and source management

Concentrate on three task types: troubleshooting questions, experience/benchmark summaries of real records, and discussion under a concrete choice pressure. Each type gets 2 Dev and 4 Final, giving 6 Dev and 12 Final.

Sources prefer publicly checkable technical material, real Train questions and user-run test records. When there is no real record, do not write an experience post saying "I tested it"; turn it into a question, a comparison discussion, or an explicit test plan.

Each brief contains:

```text
brief_id, source_group_id, source_urls, source_date, collected_at
content_type, persona, audience
problem_or_goal, context, motivation, desired_response
facts[{fact_id, claim, evidence_excerpt, source_url, status}]
speaker_relationship_to_source
allowed_claims, forbidden_claims, essential_limitations
```

State clearly whether the poster is a first-hand participant, a reader of public material, or a questioner. Another person's measured results may only be cited, never rewritten as the user's own experience. Reasonable advice, reasoning from existing facts, and questions are allowed; the nature must be labelled, and adding a disclaimer to every paragraph is not required.

The same issue, post, benchmark report and its near-duplicates form one source group and may not straddle Dev / calibration / Validation / Final. If a source comes from Train, the original post or its near-duplicate is forbidden from also being a RAG reference for that brief; the Train source group used to generate Final is likewise excluded from this round's RAG and example library.

Final briefs have their sources selected by a mechanical sampling rule before formal tuning and are sealed by the preparation process; only source validity and key facts are checked, and the Final generation output is never used to fix a prompt. Besides the 6 Dev briefs, a source-isolated evaluator control group is built.

## 7. First gate: first accept whether 6 drafts look like real posts

Use V1 to generate one draft for each of the 6 Dev briefs, then check: is the motivation clear, is the specific context sufficient, is the information useful, does it merely restate the material, does it pile up disclaimers, does it invent identity or experience?

Automatic behaviour scale 1-5: at least 5 of 6 must score >= 3 on community fit, specificity and information value, and no sample may have a critical fact violation. The threshold is an engineering gate, not a statistical proof.

Then provide three Chinese translations of different types together with the English originals so the user can make one quick judgement of "does this look like something a real user would post, is it valuable, and what is mainly wrong". This is not a formal blind review, only pre-freeze product acceptance, and AI may not fill it in. If the user is temporarily unavailable, continue other independent work, but the human naturalness acceptance must not be marked as passed.

## 8. Second gate: validate the evaluator

### 8.1 Controlled item bank

30 pairs in total: Calibration 15 and held-out Validation 15, divided as whole source/brief groups. Cover specificity, posting motivation, community fit, information value, opening, structure, clickbait and disclaimers; include identical-text pairs, slight-difference pairs and trade-off hard cases. Each pair records the expected relation and its reason; hard cases may be expected Tie/Uncertain.

Round 1 bad samples are used for Calibration, and a corrected version of the same source text may not also enter Validation. "Same facts" means the core claims are unchanged; changing how information is presented does not permit new measured values. The expected winner is a design label, not a community gold standard.

Calibration permits at most two rounds of rubric and Tie-rule adjustment and at most 4 few-shot examples. At most 2 internal judge candidates are pre-declared; Calibration selects one under the declared rule, which is then frozen and sits Validation once, avoiding repeated championship selection on Validation.

### 8.2 Order swapping and admission

The judge does not know the version, historical score, expected answer, or before/after identity. Each pair is run both AB and BA, mapped back to content and compared: a winner is declared only when the same side wins both times; two Ties give Tie; disagreement gives Uncertain. Position agreement is computed on the raw pre-merge judgements; the whole set of disagreements must not be converted to Tie and then called 100% agreement.

Admission: Validation accuracy > 0.70 and raw swap agreement >= 0.80; the three core dimensions are adequately covered with no obvious systematic failure; identical-text pairs must not consistently force one side. Output the exact numerator/denominator, confidence intervals, per-dimension results and effective coverage. 15 pairs at > 70% means at least 11 correct, still a small-sample engineering check.

Expected Ties also count as items, but directional-item accuracy is also reported separately; more Ties must not be used to inflate the result. Call errors count against failure coverage and may not be deleted so that only successful samples are reported. A model confidence threshold, if any, may only be set by Calibration; vendor probabilities may not simply be declared calibrated.

Before the generation experiment, the external judge passes a controlled Validation check under a pre-pinned rubric. This accepts the evaluation tool; it does not select the generator. Its results may not flow back into generation prompts, diagnostics or selection rules, and it may not access the generator's Tune/Selection outputs. If the internal judge's capability is inadequate, do not keep shopping for models until one passes; switch formal feedback off and V0/V1/V2 can still proceed. If the external judge is inadequate, do not use it to claim generation improvement: fall back to human evidence or state clearly that the result is unverified.

### 8.3 Preventing contamination

After admission, do not modify the judge rubric during generation Dev, and do not keep searching for a third or fourth model based on its results. Capability failures and interface failures are separated: a capability failure is not swapped away until it succeeds; interface failures such as 401/429/5xx may be retried a limited number of times under a pre-declared rule. If an interface or model must be changed, record the new contract/version, verify semantics and billing, and re-validate the affected tool; a substitution that was not pre-declared does not enter this round's formal comparison. If the rubric genuinely must change, close the affected strong conclusions for this round, open a separate development loop and a brand-new Validation group, and never quietly reuse an exposed item bank. If final human data is used to change the judge or choose the product, it too must be downgraded to selection data and must not keep masquerading as unused final evidence.

## 9. Quality constraints and content evaluation

Hard rules retained: out-of-material numbers, unsupported measurements, fabricated first-hand experience, critical contradictions, substantial copying, omitted critical limitations, and format failures. The number rule supports fact-unit-equivalent expressions; it may not mechanically ban every new number or keep producing false positives on an F1 reference.

A per-draft fact ledger and support check; the automatic tool only surfaces risk, and unknown evidence is not a PASS. A hard failure rejects the draft and is not outweighed by a high preference score.

Core behavioural standards:

- Community Fit: a specific posting purpose, necessary context, and a question or value the community can respond to.
- Specificity: make full use of the conditions, symptoms, devices, models or constraints already in the material, and do not invent missing information.
- Information Value: organise facts into a useful judgement, steps, comparison or explicit question, not into "more information" through length.
- Credibility: facts are traceable, and advice / inference / first-hand experience are clearly separated.
- Clarity/Usefulness: a reader can understand quickly and take something actionable away.
- Clickbait: the headline may not exceed what the body and evidence support.

Internal rule/judgement results, external pairwise preference and human preference are reported separately and are not combined into a single Viral Score.

## 10. Four generation variants: identical information, only the method changes

Every variant receives exactly the same brief, facts, audience, identity and hard constraints; the body length range (troubleshooting may use a necessary list), output limits and base model are identical. Length is not a quality target.

| Variant | The only added capability | Candidates |
| --- | --- | --- |
| V0 | Simple writing instruction + full brief | 2 |
| V1 | Structured prompt, typed writing rules | 2 |
| V2 | V1 + Structure-RAG | 2 |
| V3/O2 | One diagnosis on the selected V2 draft, then a targeted rewrite | 3 |

Structure-RAG retrieves only from usable Train references; summaries cover opening style, information order, evidence presentation, question structure and common weaknesses; a summary is generated once and cached, and original-post facts are not injected. Round 1 pattern cards serve only as soft diagnostic hints; if enabled together with Structure-RAG, V2 is a combined capability and the whole effect may not be attributed to the RAG summary alone.

Dev permits at most two major iterations, each mainly changing one factor, with old outputs and costs retained. Do not train more classifiers and do not add agents, fine-tuning or a cross-platform matrix.

## 11. A fair comparison of feedback and multi-sampling

Each topic uses the same selected V2 draft:

- O0: the original draft.
- O1: without seeing a diagnosis, regenerate 3 alternatives from the same brief and draft.
- O2/V3: the diagnoser gives one main weakness, an excerpt as evidence, one edit action, and the facts that may not be changed; then 3 versions are rewritten.

Even if the three drafts are produced within a single call, this is still one feedback round; no recursion to a high score. O1 and O2 use the same model, facts, reference material, candidate count and output cap; the only difference is the diagnostic feedback. Diagnosis cost is reported separately as part of the real product cost.

Both arms may retain the same original draft, and the hard screening and internal selection rules are identical. A pairwise tournament with a pre-pinned order may be used, checked by swapping each time; Tie or Uncertain retains the current draft. The candidate count is small, so order dependence is recorded and no claim of a global best ordering is made.

Rewrite acceptance conditions: facts and critical limitations preserved, the target dimension improved, credibility not reduced, and no obvious regression on other core dimensions. When the judgement is uncertain, keep the original draft. The external judge takes no part in these decisions and is not given their results.

Candidate count: per topic, V0/V1/V2 give 6 first drafts + 3 for O1 + 3 for O2 = 12 new texts; across 12 Final topics that is 144. V3 is O2, so no extra 2 drafts are produced, avoiding duplication and unfair budget. The 6 Dev topics produce at most 72 per round, not counting the initial 6 naturalness checks.

## 12. Dev, selection and freezing

The 6 Dev topics are pre-split by source group into 4 Tune and 2 Selection; Tune allows at most two iterations and Selection only chooses among already-formed configurations, with no callback. When type coverage is insufficient, the small-sample selection limitation is stated explicitly.

Pre-declared selection rule: Selection chooses the product on hard quality, the internal judge's community preference, coverage and cost alone; internal preference is explicitly labelled a development signal and not independent effectiveness evidence. If a complex option's benefit is unstable, adopt the simpler one. The external final judge may not read the generator's Tune or Selection outputs and may not give selection, rewrite or elimination advice; it only passes an admission check on the controlled item bank, and the formal evaluation of generation performance happens at Final after the freeze.

Freeze the model/interface versions, prompts, rubric, Tie rules, structure-summary logic, candidate selection, fact checks, topic/source-group hashes, metrics and budget; Final runs exactly once and topics are not swapped because a baseline won.

Evidence before and after selection is kept separate: Final verifies the frozen product against V0 and V1; having seen the Final winner, one may not retrospectively call it the pre-selected product.

## 13. Final: independent effectiveness validation

12 new source-group topics, 4 per task type, with all outputs and rejections retained automatically.

For each topic the external judge evaluates four core comparisons: V1 vs V0, V2 vs V1, V3 vs V2, and O2 vs O1; 48 pairs in total, all run with AB/BA swapping. If the frozen product is not a direct party to these adjacent comparisons, product-vs-V0 and product-vs-V1 comparisons are additionally pre-declared and budgeted in advance rather than picked afterwards.

The internal judge also emits its own preference for analysis, but external judge results are never fed back into rewriting or selection. E2/E4 only perform association audits: they neither adjust candidates nor set thresholds.

The headline result uses all 12 topics as a fixed base and reports simultaneously:

- Exact counts of Wins / Losses / Ties / Uncertain / Failures.
- Decisive win rate: `W / (W + L)`; NA when there is no decisive outcome, never 0% or 50%.
- Decisive coverage: `(W + L) / 12`.
- Tie Rate: `T / 12`; Uncertain Rate: `U / 12`; Failure Rate: `F / 12`.
- Output-qualified coverage and external-review success coverage are reported separately and not merged into one coverage figure.

Tie means the two contents are close in quality; Uncertain means the evidence is insufficient or the AB/BA judgements conflict; a call failure is listed separately and may not be counted as Tie or Uncertain. Hard quality results and content preference are separated: one side with no qualified draft is a one-sided failure, both sides with no qualified draft is a double failure; in the product-usability table the qualified side may be treated as ahead, but this is not mixed into the judge's preference wins over two qualified contents.

A secondary metric may report a preference score over decisive W/L/T only, `(W + 0.5*T)/(W+L+T)`, which must show its denominator and exclude U/F, and never assigns half a point to Uncertain. For topics where both sides have a qualified draft but the judgement is uncertain, sensitivity bounds treating Uncertain as a loss or a win may additionally be reported; the bounds are not observed results. All topics remain in the coverage table.

For comparisons where both sides have a qualified draft, report the conditional preference; overall accept/reject/coverage always stand alongside. The statistical unit is the Topic: bidirectional calls and multiple candidates do not increase the independent sample size. Bootstrap topic intervals and report the decisive-outcome sample size; samples without a decisive judgement after resampling are recorded as NA and disclosed, never manually filled with 50%. n=12 supports only exploratory conclusions. The best of the four comparisons must not be picked as a unified headline, and at low decisive coverage a high conditional win rate does not justify calling the optimisation effective.

Report the incremental rewrite cost and the end-to-end cost including the V2 parent draft, diagnosis, selection and failures/retries; report latency as both single-call time and user waiting time.

## 14. Human validation and tiered acceptance of "effectively usable"

### A. Engineering usability

At least 10 of the 12 topics produce a qualified, usable draft; no confirmed serious error of fact/copying/critical contradiction; failure reasons retained. This 10/12 is an engineering gate, not an observed result.

### B. Offline effectiveness support

Engineering target: with the frozen product against the same-model simple baseline, and provided at least 8 of 12 topics yield a decisive judgement, a decisive win rate >= 0.60 with fact quality not reduced; the exact win/loss counts, coverage over all topics and intervals must be reported. This threshold is not a significance criterion; an interval spanning 0.5 supports only directional evidence. If coverage is insufficient the conclusion is insufficient evidence, and a high conditional win rate still does not make it effective. Results for Strong Prompt are reported too; if it does not win and costs more, prefer the simple product. If the frozen product happens to be one of the baselines, a self-comparison is recorded only as identical draft/Tie and does not claim an improvement; the human sample must follow the pre-declared rule and be changed to a non-self comparison.

### C. Human publishability

Randomly draw 12 pairs by type from the pre-declared comparisons, not chosen by automatic score or disagreement. The main comparisons are frozen product vs V0 (6 pairs), vs V1 (3 pairs), and O2 vs O1 (3 pairs); if the product itself is V1, the second group becomes a pre-specified mechanism control with a clear name. Families are summarised separately and not merged into an overall win rate.

Chinese translations and the English originals are shown side by side with A/B identity hidden; numbers, facts and limitations are independently checked. A Chinese-language blind review can only validate content preference and cannot prove native-English naturalness; if possible, find a reviewer familiar with the target community who can read English to add a check. The reviewer's name, time, language, per-item choices and reasons are stored truthfully; AI may not fill them in.

A single user's feedback is single-reviewer acceptance and is not the community's overall preference. Agreement is split into directional preference, Tie and Uncertain, and a small-sample percentage may not be used to call one judge the most trustworthy. If review is postponed, the report states plainly that human external evidence is missing and does not substitute an AI simulation.

### D. Real viral effect

Only real publishing data can test interaction / high-performance rate. Passing A-C still delivers only "a high-performance content drafting aid with offline support" and may not claim a proven virality improvement.

The thresholds must not become tuning targets that guarantee passing; when they are not met, report the real result and the bottleneck.

## 15. Subsequent real-publishing validation: separate authorisation, separate protocol

This may be skipped during the course, but the product's final goal needs this layer.

Recommended prospective design: real users submit qualified posting tasks continuously; each task is first randomly assigned to the simple baseline or the frozen product and reviewed by the user under a uniform rule; revisions, rejections and unpublished tasks are recorded, not only the posts where the system did well. Community rules are respected and the same content is not posted repeatedly to manufacture a fake A/B.

Assignment of generation method is randomised within blocks allowed by content type, topic category, time period and author conditions; the creation time and the score/comments at a fixed 36-38 hours are recorded, with exposure reported separately if available. Editor review blind to the method reduces subjective publish-selection bias. The comparison is the full "generation + uniform review" process, not the pure causal effect of the text alone.

The real high-performance threshold can only be frozen from historical reference available before publishing; the Top-25% definition may not be changed based on experimental results. The task count needs a power analysis from the expected baseline and the minimum detectable improvement; a small course demo is only a feasibility trial and cannot guarantee a significant result. Actual publishing, account use, recruitment or extra spending needs separate user authorisation and is not executed automatically now.

## 16. Budget, stopping conditions and the human/AI split

The recorded Round 1 cumulative spend is US$0.34422535, leaving about US$4.65577465 of the project's existing US$5 cap; this is recomputed from the latest ledger before execution, includes any new calls, and is not reset by creating a new folder.

Round 2 targets US$1 of new spend, with a soft stop at US$1.50, an internal hard allocation of US$2, and never exceeding the project's remaining cap. Planning reference: integration/calibration 0.30, naturalness and Dev 0.35, Final and all external core comparisons 0.65, translation and retries 0.20; this is a hypothetical allocation, not a quote, and is frozen in the contract after the price pre-check. Final budget is preserved and Dev may not spend it early.

At the soft stop, save first and summarise the benefit; within the authorised range, an obviously necessary wrap-up may use the hard allocation, without adding a model matrix. Requests with an unknown unit price or an unbounded estimate are not executed. Any top-up of a new evaluation platform account or new paid commitment is not automatically authorised by the existing API budget.

AI handles source checking, brief building, integration, code, running, caching, logging, summarising, Chinese material and delivery. The user only needs to: configure the chosen interface credentials if necessary; give a quick naturalness acceptance; complete the final human blind review; authorise real publishing and record the face-visible video. This request asks only for a plan; this document is not an instruction to start all the paid experiments.

Stop: insufficient factual material, judge admission failure, naturalness failure, budget insufficient to preserve Final, source leakage, or Final exposure. Stop the affected conclusion rather than fabricating a PASS; other independent work continues.

## 17. The execution order I intend to actually follow

1. Create the independent 1.1 project, register the budget and the 1.0 evidence, and save the v3 and v4 inputs plus this v4.1.
2. Check sources and interfaces for free, choose real brief source groups, exclude cross-group leakage; run bounded small probes on paid interfaces.
3. Generate 6 Dev naturalness samples and give the user 3 with a Chinese counterpart for a quick acceptance; build the independent Calibration/Validation in parallel.
4. Pre-declare at most two internal judge candidates and one external judge; adjust once or twice from Calibration alone, select the internal judge, freeze it and run Validation once. A capability failure does not lead to swapping models until one passes.
5. Implement the structure-summary cache, single-problem diagnosis and fact preservation; run Tune, at most two rounds; Selection uses only the internal judge + hard quality + cost to choose the product, and the external judge does not read those generation drafts.
6. Freeze the full contract, code and source groups, then execute Final's 144 candidates and all external key comparisons.
7. Collect the 12 real blind-review pairs; if incomplete, give the automatic results first and mark the gap.
8. Produce one consolidated process audit and results review, keep or switch off RAG and feedback according to the evidence, and deliver the most practical version.

## 18. Files, reproduction and course delivery

Root directory: `Desktop/PE6201_ViralLoop/experiment_1_1/`. Continue the existing project structure; do not rebuild a complex orchestration platform. The execution loop is archived under `loops/v002/`; later complete loops increment and never overwrite an old loop.

Must be retained: the plan, the immutable contract and hashes, PROJECT_STATE, the source/fact ledger and grouping table, the access and call log, the judge item bank and raw judgements, all generation drafts, the selection path, version configurations, cost/latency/failures, the process audit, the result CSVs/MDs, and the product selection rationale.

The contract records the candidate count, evaluation rules, cost cap, model versions, split permissions and Final exposure state; an integrity audit PASS only shows the records follow the protocol, not that the judge is correct or that propagation effects hold.

Final delivery: README, PRODUCT (persona/input/output/architecture/target vs actual metrics), data/evals notes, a runnable interface, the experiment process and results MD, a ~1,200-word course report draft, and a ~5-minute face-visible + screen demo script. The course report explicitly retains Round 1's negative results, Round 2's fixes, and the unfinished real-propagation validation.

The most important deliverable is not "a more complex evaluator" but **a generator that passes acceptance on natural tasks, uses its material honestly, and has independent comparison evidence**. Whether it raises the real virality rate is left to prospective publishing validation.

## 19. v4.1 revision confirmation checklist

- [x] The generator is the product, the evaluator is a tool; Jev is not bound by default.
- [x] At most two internal candidates; selection uses Calibration alone; frozen before formal acceptance.
- [x] The external judge may run controlled admission but takes no part in generator Tune/Selection or rewriting.
- [x] Final reports wins, ties, uncertain and failures together with their coverage.
- [x] Uncertainty is never defaulted to half a win; a conditional win rate must carry its sample size and coverage.
- [x] A judge admission failure does not lead to more model shopping; failures and downgraded conclusions are retained.
- [x] The original 1.0 and v4 are retained; this new document is not a record of a new experiment having been run.

The execution threshold has been reached. Next, prioritise real briefs and a small sample acceptance, and do not keep enlarging the plan or the model matrix.
