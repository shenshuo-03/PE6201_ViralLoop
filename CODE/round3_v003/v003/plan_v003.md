# PE6201 ViralLoop Round 3 Experiment Execution Plan v1.2

> Positioning: a lightweight, human-calibrated content optimization experiment.
> Core product: from a topic, target readers and real material, generate natural, credible community posts worth publishing.
> This round's task: test whether motivation planning and title optimization improve publishing value, and whether an automatic selector can assist candidate ranking.
> Status: a plan to be executed; all quantities, thresholds and costs in this document are presets, not results already obtained.
> This document does not start the experiment or add spending; execution reuses the project's existing US$5 total authorization and checks the actual remaining budget.

## Notes on this update

v1.2 is the latest plan for this round. It keeps v1.1's samples, versions, human title acceptance, selector admission and budget rules, and adds only three corrections:

1. Make explicit the two input layers, "current user task" and "historical evidence material"; historical posts do not automatically serve as posting motivation.
2. Call the Selector result a "new-task generalization check", not an independent selector accuracy validation.
3. Add lightweight usage warnings and task anomaly monitoring; do not set a 750k cumulative-token automatic pause.

Only G0/G1 and the optional title module are still executed; GEPA, RAG or an agent are not expanded. This document is the complete replacement plan; the old v1/v1.1 are retained for traceability and versions are not mixed.

## 1. The most important judgment

Round 3 does not keep adding RAG, feedback loops or agents. It first solves two problems:

1. Does the generated post look like content a real user posted for a clear purpose?
2. Does the automatic selector's judgment come close to the user's own publishing preference?

Keep only components that add value. A simple baseline may win in the end; negative results should also be recorded in full.

Conclusions this round can support are "offline publishing-preference improvement" or "the automatic selector is preliminarily usable". They cannot be used to claim a higher real viral rate, upvote rate, comment rate or community recognition.

## 2. Evidence from the first two rounds and this round's hypotheses

### 2.1 Existing observations

- Round 1 has 2,336 cleaned historical records and the E2/E4 historical association models.
- Round 2 V1 added a focusing prompt and reduced facts at the same time, so the result cannot be attributed to prompt tuning alone.
- Round 2 external comparison: V1/V0 was 1 win, 7 losses, 3 uncertain, 1 failure; V2/V1 was 3 wins, 2 losses, 7 uncertain.
- The Round 2 internal evaluator did not pass the information-value admission, so the feedback version was not executed.
- O1 actually retained the original, so identity Ties cannot prove that multi-sampling itself is ineffective.
- The automated quality score and a small amount of genuine naturalness feedback were misaligned, but there is still no complete genuine human Final result.
- Round 2's token-budget block failed, with a known cumulative 1,225,228 tokens exceeding the original internal limit. Round 3 must reserve budget before requests and block overruns.

All of the above retain the original evidence; the first two rounds' results are not rewritten. It must not be presupposed that "a strong LLM is already near-optimal" or that "motivation is the main cause"; these are judgments to be tested.

### 2.2 Only three hypotheses are tested this round

| Hypothesis | Comparison | What it can answer |
| --- | --- | --- |
| H1: the automatic selector is preliminarily usable | machine judgment vs human labels | whether it can assist draft selection within this round's scope |
| H2: motivation planning adds value | G1 vs G0 | with the same full material, whether an explicit posting purpose improves the content |
| H3: title optimization adds value | same body, optimized title vs original title | whether changing only the title is worth the extra cost |

GEPA, RAG, feedback rewriting, multi-agent and large-scale model search are all excluded from this round. Future explicit bottlenecks warrant a separate experiment.

## 3. Data and stage isolation

### 3.1 Data source

Continue using r/LocalLLaMA historical material and the existing source-group isolation tooling. Reuse the data and tools, but do not use old evaluation results as new evidence for this round.

From source groups that never entered the first two rounds' development, Selection, Final, controlled evaluator items, human previews or manual edits, draw:

- 8 new Dev source groups: human calibration and component exploration.
- 6 new Final source groups: independent comparison after the product freeze.

This round's 8 Dev groups are used both for selector screening and generator development and are explicitly exploratory data, not claimed as independent validation. There is no extra independent Selection set; selection bias is constrained by the new Final and conservative conclusions.

### 3.2 Allocation rules

- Use a fixed random seed and pre-recorded eligibility rules; do not pick tasks by upvotes, predicted score or a method's performance.
- Exclude source groups by similar original post, same project/event, or near-duplicate content, not just by post ID.
- Final reserves 2 tasks in each of three categories: troubleshooting help, experience/test discussion, opinion/decision discussion.
- Dev should cover these three categories as much as possible, not concentrate all tasks in one writing style.
- Before freezing, eligibility and grouping may be verified; Final bodies, briefs and generation results do not enter design, examples, retrieval, tuning or human previews. Content access used for eligibility verification is recorded separately.
- When a source needs exclusion, keep the reason and substitute in the predetermined backup order; do not exclude it because generation performed poorly.

### 3.3 Brief fields

Each task generates the same full brief shared by all versions, in two layers.

**Layer 1: current user task.**

- current_user_goal: what the user hopes to accomplish.
- current_decision: the specific decision or problem under consideration.
- desired_help: what kind of help the user wants from the community.
- scenario_origin: real_user_input or controlled_hypothetical.
- experimental_user_scenario: controlled experimental scenario description; do not fabricate a scenario when it is real user input.
- scenario_id, scenario_version: scenario identity and version.

**Layer 2: historical evidence and constraints.** The existing fact ledger is retained, with source_facts clearly distinguished from the scenario setup:

- topic: the topic.
- audience: target readers.
- posting_intent: help-seeking, discussion, sharing, decision, etc.
- speaker_role: poster identity and material ownership.
- problem_or_goal: the actual problem.
- context: necessary background.
- source_facts: a real historical fact ledger with IDs; engineering may keep the facts-compatible field, but the content and IDs of the two must be exactly identical.
- source_url, source_date: provenance and date.
- limitations: sample, scope of applicability, uncertainty.
- allowed_claims: judgments that may be expressed.
- forbidden_claims: identities, experiences, results or currency that must not be fabricated.

Interaction outcomes are used only for historical auditing and are not fed into the generator or the draft selector. Source text and brief must be checked against each other; automatically extracted facts are not inherently correct.

### 3.4 Construction and freezing of the user scenario

When there is no real user need this round, use a controlled hypothetical product input and label it clearly. The AI constructs the scenario from pre-locked task templates and material scope, and does not modify the scenario based on G0/G1 outputs, preference labels or historical popularity.

- Dev scenarios are locked before any generation request, and G0/G1 inputs are exactly identical.
- Final scenario construction rules, templates and eligibility conditions are locked before the product freeze; the concrete scenario is constructed and locked when the new sources are opened after the freeze, and then both systems' outputs are generated. Scenarios must not be tailored to a method.
- A scenario may set "currently comparing deployment options" or "needs to troubleshoot a certain class of problem", but must not fabricate existing tests, purchases, job titles, hardware ownership or results.
- When device or budget parameters are needed, label them explicitly as hypothetical parameters rather than user facts, and do not cite them as historical evidence.
- The same scenario and material are given to the generator, fact checker, Selector, translation and human background card so that the task definition stays consistent.
- Whether historical data can help a current decision is an open question; old results must not be automatically inferred to be the current model's, version's or hardware's performance.

Report usage: Current user goals are controlled hypothetical product inputs, while factual claims remain grounded in archived sources.

This improves the realism of the product task but cannot prove the need has been validated by real target users. Scenario design, single-user preference and the timeliness of historical evidence remain limitations.

## 4. Posting identity: a real problem this round must solve

Historical posts are other people's experiences and cannot be passed off directly as the new poster's first-hand testing.

Two clear input modes:

1. **User's own material**: the user explicitly provides their own experience, data and identity, and first-person expression is allowed within scope.
2. **Historical third-party material**: writing may only be done as discussion, quotation or posing a question; necessary attribution is retained and a 2025 test is not written up as current first-hand testing.

This round's historical-data experiment defaults to the second mode, but the posting purpose is determined by current_user_goal/current_decision/desired_help and must not automatically become "I read an old post so let's discuss it". Historical material is decision evidence, not necessarily a posting reason.

For example:

- Historical fact: a certain author reported in 2025 that Qwen3-8B was slower under specific hardware and configuration.
- Controlled user task: assume the user is comparing local document Q&A options and wants to understand the expected speed and troubleshooting methods for different configurations.
- Help wanted: comparable data from the community for similar configurations, settings that need checking, and applicability limits.
- Forbidden: writing the hypothetical user as having already tested that hardware first-hand, or claiming an old test as a current general conclusion.

The generated draft is a hypothetical product draft with a clear task, not a post a real user has already published, nor current news. First-person need expression is limited to the explicitly given hypothetical goal; first-person experience must not be fabricated.

It is allowed to write naturally "saw a small-sample test, want to discuss its scope of applicability"; it is not required to say "The source reports" in every paragraph. But sources, dates and key limitations must not be deleted for the sake of naturalness, and "I tried it yesterday" must not be invented out of thin air.

## 5. Generator versions

### 5.1 Shared settings

- The generation model continues to be Round 2's GPT-4.1-mini; before execution verify the exact model ID, availability, price and context limit and lock them.
- Same sources, full brief, identity rules and fact-check rules.
- Body target 90-180 English words, up to 220 words; title up to 160 characters. Overrunning is an output-format failure, and a long draft of one version must not be trimmed after the fact.
- temperature defaults to 0.5; planning, fact checking and the selector default to 0.
- Dev generates 1 draft per task per version; Final generates 2 candidates per task per version, with both drafts returned in the same request.
- The candidate count is the same, but G1's planning and title components add cost; record every extra request and do not claim a fully cost-matched comparison.
- No per-draft human polishing, and no rerunning after seeing Final results to pick a good draft.

### 5.2 G0: Minimum Safe Baseline

Reuse Round 2's V0 base prompt and unify this round's shared identity, length and fact rules. Record the differences from the old V0; this round's G0 is not a direct reuse of the old output.

Core prompt:

```text
Write a natural r/LocalLLaMA post for the specified audience and posting intent.
Address current_user_goal, current_decision and desired_help.
Use archived source facts as evidence; do not treat reading an old post as the default posting motivation.
Respect scenario_origin: hypothetical goals do not authorize invented lived experience.
Use the complete brief as evidence, but do not turn it into a source summary.
Preserve facts necessary for readers to understand and respond.
Respect speaker ownership, source dates and limitations.
Do not invent personal experience, measurements or unsupported claims.
Return title, body and fact_refs.
```

G0 has no extra motivation-planning step and no RAG or feedback rewriting. It is the minimum usable system with fact, identity and format constraints, and is not called a raw LLM or "bare LLM".

### 5.3 G1: full material plus grounded motivation planning

Do not delete brief fields, do not set Top-2 Facts, and do not force only two facts to be cited.

Add one short planning request:

```text
Who can legitimately be posting this, given speaker_role and scenario_origin?
What current_user_goal and current_decision have been explicitly supplied?
What desired_help should this post seek?
How can source_facts inform that goal without becoming a source summary?
What decision or problem is central?
What response would be useful from readers?
Which context, source attribution and limitations must be preserved?
Which facts are necessary, and which are optional?
Which proposed motivations or experiences lack evidence and must not be used?
```

Structured output: identity, scenario origin, the explicitly given current goal, one central purpose, the desired response, relevant historical evidence, information that must be preserved, and content additions that are forbidden. Planning must not replace the given goal or fabricate a "more dramatic" experience.

The writing request reads both the full brief and the planning result. Planning only offers organizational advice; it cannot modify the fact ledger or authorize first-person experience. If planning conflicts with the sources, that task's G1 is recorded as a failure and is not quietly rewritten by a human into a success sample.

This is a component experiment of "adding a motivation-planning step". It cannot further claim to have separated the causal contribution of "one extra call" from "planning semantics"; this round adds no extra irrelevant planning control.

### 5.4 T: independent title module

- The body stays verbatim identical, verified by a body hash.
- Each draft generates at most 2 new titles, forming at most 3 candidates together with the original title.
- No new facts, first-hand implications, exaggerated results or change of the post's purpose.
- The selector compares the original title with each of the two new titles one by one with AB/BA swapped; at most one candidate that clearly beats the original is kept.
- If both new titles beat the original, pick the first by a pre-fixed candidate order, with no extra repeated contest.
- Tie, Uncertain or rejection all keep the original title; without selector admission the title module is switched off.

The title comparison supplies the full same body so the model does not compare titles out of context. Each AB request returns two independent results, "original/T1" and "original/T2", and the BA request maps them back separately; this is not a direct swapped-free three-way ranking. New titles that fail the fact or misleading check do not enter selection.

Whole-post calibration cannot prove title-selection ability. The Dev human verification is of the whole "generated titles plus machine title selection" module, not of the human standing in for the machine to pick the best title. Final keeps the same machine rules and then has humans verify the whole product effect; no claim of improved click-through rate is made.

## 6. Fact and quality checks

Reuse the existing check code, but this round reports "conditions the program can check directly" and "model-assisted judgment" separately.

### 6.1 Programmatic checks

- JSON and required fields valid.
- fact_refs exist in the ledger.
- Title and body lengths conform to the agreement.
- The title-experiment body hash is unchanged.
- Source, version, generated candidate, cost and raw response are all recorded.
- The existing mechanical copy detection runs under the frozen rules.

### 6.2 Model-assisted fact review

Read the full source and brief, and check for:

- Unsupported facts or numbers.
- Fabricated first-hand testing, identity or experience.
- Historical results written as current results.
- Deleted key limitations or background.
- Title-body contradiction, misleading or exaggeration.

The above review is not fact certification. Do not continue to treat Gemini 4/5 as independent quality evidence. Model-rejected drafts keep the original and the rejection reason.

### 6.3 Human fact verification

The AI assistant checks the Final selected drafts one by one against sources and fact references and produces a reviewable table; this is assistant source review, not labelled as independent human expert certification. When a technical dispute cannot be resolved, record Unverified rather than forcing a verdict.

The user mainly evaluates naturalness and publishing value and is not required to judge technical facts.

## 7. Human Dev evaluation

8 tasks, 1 G0 and 1 G1 draft each, 16 drafts and 8 pairs in total.

- Anonymous randomized A/B, hiding model, version, score and system description.
- Both drafts use the same fact background card, stating source dates and poster identity.
- Faithful consistent translation, keeping tone, paragraphs, numbers and uncertainty; no polishing during translation.
- Chinese by default, English expandable.
- After translation, check fact, number and identity consistency; errors fix only the translation, not the English draft.

### 7.1 Primary label

"If you could publish only one, how would you choose?"

- A is more worth publishing.
- B is more worth publishing.
- Tie: the two are about the same.
- Both unacceptable: neither is worth publishing.
- Uncertain: missing background, incomprehensible, or cannot judge.

Also record separately for each draft "publishable / not publishable / cannot judge", to avoid mistaking "the better of the two" for "already usable".

### 7.2 Supplementary questions

- Which is more natural?
- Which expresses the posting purpose more clearly?
- Which is more worth reading or replying to?
- Does it read like a material summary, seem too verbose, lack background, or have an unclear question?
- Optionally, one sentence on the main problem.

State the conclusion accurately as "this user's preference as presented in the Chinese translation". The single reviewer, the Chinese translation and the technical-background limitation must all be disclosed and cannot substitute for English-community audience evidence.

## 8. Automatic Selector calibration and freeze

### 8.1 Candidate limit

The main candidate uses the exact locked ID of Round 2's external Claude model; no large-scale search is started.

Jev is allowed only one connection pre-check of no more than 15 minutes: there must be usable authorization, a stable interface, clear output and an upper-bounded cost. Otherwise it is closed. At most two candidates; no searching for a third.

The pre-check is not evidence of successful integration; failures and costs incurred are recorded as they are.

### 8.2 The same 8 human pairs

- Each candidate judge does AB/BA, 16 requests per model in total.
- Do not put human answers or version identity into the machine prompt.
- Do not modify the judge prompt per task based on human answers; compare only the pre-locked candidates.
- Also support A, B, Tie, Both unacceptable, Uncertain.
- Conflicts after AB/BA mapping back to the same content are merged into Uncertain; request failures are recorded separately as Failure.

### 8.3 Engineering admission

Check simultaneously:

1. At least 6 of 8 tasks with fully consistent labels.
2. At least 4 tasks where the human has a clear A/B preference; otherwise ranking ability cannot be validated this round.
3. On these human-clear tasks, the machine gives a consistent A/B at least 75% of the time; abstentions and failures do not count as correct.
4. AB/BA content mapping consistent on at least 7/8; also report decisive coverage, since passing by abstaining on everything is not allowed.
5. Display length-bias, position-bias and similar checks, but 8 tasks cannot prove the absence of systematic bias.

Admission is only a preliminary threshold for this round's limited scope and does not mean a stable replacement for humans. When both candidates pass, 6/8 and 7/8 cannot be used for a precise ranking. Pre-fix the selection order:

1. First exclude candidates with an unstable interface, an unreliable price upper bound, or unusable structured results.
2. Among the remaining stable and usable candidates, prefer the one with higher machine decisive coverage on human-clear tasks; also list the number of misjudgments, since coverage is not accuracy.
3. If coverage is equal, choose the one with the lower estimated call cost at the same input scale; if cost is also equal, choose the one already integrated with fewer dependencies.
4. If still tied, use the pre-fixed main candidate Claude without adding model search.

These are engineering selection rules only and do not constitute a model reliability ranking. Write them into the contract before the freeze; do not change them after seeing Final.

If all fail, switch off the key automatic ranking and title module, and Final uses fixed candidate rules and human evaluation, without continuing to fix the judge until it passes.

## 9. Dev component screening and product freeze

### 9.1 G1 retention rule

Based on the 8 human Dev pairs:

- G1 gets a clear preference on at least 5 tasks.
- No newly confirmed serious fact or identity error.
- Do not substitute one content type's effect for an all-domain conclusion.
- Report the publishable rate, Tie, rejection, abstention and extra cost.

This is a directional development threshold, not statistical significance. If not met, baseline B = G0; if met, B = G1.

### 9.2 Title exploration

After selector admission, test B+T on 4 pre-designated Dev tasks. The 4 tasks cover the existing three categories and are not chosen by whether G1 won.

At most 4 drafts, 2 new titles each. Both mechanical and model checks are recorded. The machine picks one title using the rules frozen in 5.4; if the original is retained, that result is also kept, and tasks are not swapped to assemble 4 "optimization success" cases.

Then add **4 human title blind-review pairs**:

- Anonymously show the original title and the machine's final pick, A/B randomized, version identity hidden.
- Both titles share the same body or accurate Chinese background beneath them, so the judgment is not made out of context on which is more eye-catching; expand the full body when needed.
- Faithful translation, no title polishing; English viewable.
- Labels are A better / B better / Tie / both unsuitable / cannot judge; plus whether it is exaggerated, misleading or mismatched with the body.
- The human only accepts the machine's already-chosen result, and does not pick a different one from the two new titles.
- Identical titles are recorded as Identity Tie and are not counted as an optimization win; tasks whose human answer has not been received must not automatically enter Final.

Only if at least 3/4 tasks show a clear human preference for the machine-chosen new title, with no newly confirmed fact or misleading problem, does B+T become the Final challenger product. The calculation is over all 4 tasks; tasks with abstention, failure or a retained original title are not deleted.

This validates the title module's preliminary value on development tasks; it does not mean the title judge independently passed comprehensive validation, nor does it mean an improved click-through rate. Final strictly reuses the same machine title-selection rule and does not let humans take part in title selection, avoiding swapping the system.

### 9.3 Final product P*

- B = G1, title passes: P* = G1+T.
- B = G1, title fails or is off: P* = G1.
- B = G0, title passes: P* = G0+T.
- B = G0, title fails or is off: P* = G0.

If P* = G0, the conclusion is "this round found no enhancement component worth adding", not "G0 is proven best or near-optimal". If it is exactly the same as the baseline, stop the "improvement effect" Final comparison; do not generate two identical systems and exploit random differences to claim improvement. A separate single-system usability check may be run, but it does not serve as the planned comparison.

Freeze: code, model, all prompts, generation parameters, selector, labels, candidate budget, fact rules, translation pipeline, Final task allocation, failure handling and reporting metrics. Save hashes and times.

## 10. Final: 6 new tasks

### 10.1 Fixed comparison

G0 baseline vs frozen P*, without testing the full component matrix.

6 tasks x 2 systems x 2 candidates = 24 base candidates. The title module only changes the title of the selected product draft and does not generate extra bodies.

### 10.2 Candidate selection

- Fact and format checks first, then select from qualified drafts.
- Selector admitted: do AB/BA on the two qualified candidates of the same system, and the clear winner is selected.
- Tie or Uncertain: select the first qualified draft in the fixed order. Both unacceptable is recorded as a selector rejection and this system's output for that task stops; a rejection must not be automatically downgraded to a Tie and then forced into a selection.
- Selector not admitted: the first qualified draft in the fixed order.
- If only 1 is qualified, select it; 0 qualified is recorded as a system failure and is not rewritten on the spot into a success.

The candidate counts compared between systems are the same. Selector, planning and title requests are all counted in the product's total cost and latency.

### 10.3 Machine Final

If admitted, the Selector does AB/BA on P*/G0, 12 requests in total.

It has already taken part in product selection, so it cannot serve as an independent generation-effect judge. Here it is used to analyse consistency with humans, abstentions and preference differences.

A judge that is not admitted may keep a "diagnostic reference" status, but is not called an effective Selector and its results do not retain the product; it may be skipped to save budget.

### 10.4 Human Final

6 tasks, 12 drafts, reusing anonymity, consistent translation and the same background card. Across the whole round the user needs to read at most 28 Chinese posts, plus 4 title comparisons (8 titles; the bodies are already-seen Dev material and can be expanded on demand). The added title validation does not require reading 8 new bodies.

If the title module did not run, there are only 8 Dev pairs and 6 Final pairs; if P* = G0 and the improvement comparison stops, do not force an extra 6 same-system Final pairs.

Reuse A/B/Tie/Both unacceptable/Uncertain and the per-draft publication-eligibility label.

Final answers are used only for validation and reporting, and do not retroactively change prompts, swap the judge, re-choose the product or rerun draft selection.

## 11. Metrics, thresholds and conclusions

### 11.1 Primary generator metrics

- Raw counts of W/L/Tie/Both unacceptable/Uncertain/Failure.
- The proportion of all tasks obtaining a clear preference, W/6.
- Decisive win rate W/(W+L), together with decisive coverage (W+L)/6.
- Each version's publishable-task proportion, confirmed fact errors, and number of unresolved facts.
- If a system has no qualified draft, record it as a system failure; report the effect not only on the remaining successful tasks.

Uncertain must not be counted as half a win. Report small-sample intervals and counts, and do not use decimals to manufacture a sense of precision.

### 11.2 Engineering positive signal

P* obtains a clear human preference on at least 4/6 tasks, with 0 confirmed serious fact/identity errors, and at least 4/6 tasks judged publishable by the user.

If met, the write-up is only "preliminary positive signal observed in this round's 6 tasks". If not met, write that no gain was proven; the threshold must not be changed by deleting abstention tasks or swapping topics.

If the product cost exceeds G0 by about 2x with only a weak gain, continue to use the simple baseline by default. This decision rule is written down before the freeze, and the product is not re-searched after Final.

### 11.3 Selector new-task generalization check (Final Generalization Check)

Using the 6 new Final human labels, report: the number of fully consistent labels, the consistency rate on human-clear tasks, machine decisive coverage, AB/BA consistency, and rejection/abstention differences.

The Final drafts have partly been filtered by this Selector, so this is a check of system-level preference versus humans on new tasks, not an independent, filter-unbiased Selector benchmark. Write it accurately as "on the system outputs for the new Final tasks, X/6 consistent with human labels", not "external validation proves the Selector's accuracy is X%".

An overall consistency of at least 4/6 that does not rely on many abstentions can count as preliminary support; if there are too few clear tasks, the conclusion is insufficient information. Consistency with the selected drafts cannot be extrapolated to all unfiltered candidates, let alone claimed as community-judgment accuracy.

### 11.4 Other results

- Naturalness, motivation clarity, reply-worthiness: diagnostic results.
- API requests, all tokens, cost, retries, end-to-end latency, model service time: operability.
- E2/E4: historical association audit only, not used for generation, screening or reward, and not called viral probability; unnecessary embedding requests are switched off by preference.

## 12. Calls and budget: calculate clearly before executing

This round does not reuse the unaccounted "main line <= 120 requests". The table below is a per-stage upper-bound plan, and the actual must be verified against existing batch-processing capacity and caching.

| Stage | Request upper bound | Note |
| --- | ---: | --- |
| 14 new brief extraction and source verification | 28 | at most 2 per source, after the Final-stage freeze |
| Dev G0/G1 generation | 16 | 8 tasks x 2 versions |
| Dev G1 motivation planning | 8 | once per task |
| Dev fact check | 8 | batch both drafts of a task |
| Dev Chinese translation | 8 | batch both drafts of a task |
| Main Selector challenge | 16 | 8 pairs x AB/BA |
| 4-task title exploration | 16 | 1 generation, 2 swapped comparisons, 1 fact check per task; one comparison request can return structured results for both new titles separately |
| Dev faithful title translation | 4 | batch the original and the machine selection per task, for the added human validation |
| Final two-system body generation | 12 | returns 2 candidates per request |
| Final motivation planning | 6 | called only when P* includes G1 |
| Final candidate fact check | 12 | batch 2 candidates per system |
| Final internal draft selection | 24 | 6 tasks x 2 systems x AB/BA |
| Final title generation, selection, check | 24 | called only when P* includes T, 4 times per task |
| Final selected-draft translation | 6 | batch two drafts per task |
| Final machine comparison | 12 | 6 tasks x AB/BA |
| **Maximum main-line total** | **200** | not the number of calls every path necessarily makes |

A second Selector adds at most 16 more; pre-checks, embeddings, format repairs and failure retries also count against the quota and must not be missed.

If the existing interface cannot batch as in the table above, it must be recalculated rather than pretending to finish in one go. No complex new framework is added just to compress the number of requests.

### 12.1 This round's limits

- Main-line request budget cap 220, or 240 with at most two Selectors; retries do not automatically add quota.
- Tokens continue to be estimated, with all failures, translations, reviews and retries recorded, but per the user's latest view this round sets no 500k cumulative-token hard stop, and necessary checks are not skipped to reduce tokens. Each request still has a model context and maximum-output limit, cost is reserved at a safe upper bound, and the already-frozen previous-round token limit is not retroactively modified.
- This round's cost soft target is US$0.75 and the hard cap is US$1.25.
- The project's US$5 total cap remains in force; check the latest ledger before execution and do not treat the old cumulative amount in the Round 2 report as the current balance.
- Execution stops when either the request-count or the dollar hard cap is reached first; tokens serve as a diagnostic and cost-estimation basis, without a separate cumulative hard stop this round.

US$1.25 is only a limit and does not guarantee that all main-line calls can complete. Calculate first using frozen model prices and actual input tokens; if insufficient, cancel Jev, title exploration or unnecessary historical audits before execution, keeping core G0/G1 and the human Final. Do not secretly change thresholds midway or cut one version's candidates.

### 12.2 Concurrency and budget reservation

- At most 4 API workers; reduce concurrency when the service rate-limits, and do not retry endlessly for speed.
- Different sources may run in parallel; the dependency order of planning -> generation -> review -> draft selection -> title is kept.
- Before each request, reserve the call count and cost upper bound in the same atomic budget ledger; also estimate the input-token safe upper bound and maximum output tokens, for cost and context feasibility.
- Spent + in-flight reserved + Final-reserved budget must not exceed the request-count or dollar hard cap; do not treat a healthy token balance as if cost could grow without limit.
- Settle after real usage is obtained; keep a conservative reservation when usage is unknown and do not charge it as zero.
- A timed-out request may already be billed; book it at real or conservative cost, and re-apply for quota before retrying.
- At most 1 retry per request; a format failure may be repaired once for a charge, but it is still subject to the total quota.

The Final budget is reserved separately in advance and Dev must not overdraw it. The budget block must first pass a local simulation: concurrency-critical balance, unknown usage, failure retries, overrun rejection; verified before paid requests begin.

### 12.3 Lightweight anomaly monitoring

When cumulative tokens reach 500k, log one warning and have the AI check usage and task progress; normal growth continues running without asking the user to confirm repeatedly. A cumulative usage of 750k or higher does not automatically trigger a new hard stop. Cost and call caps still block as usual.

Before execution, lock the following checks in the configuration:

- The request key includes source, stage, version, candidate and attempt number; a completed request must not be accidentally re-sent, and retries are allowed separate accounting.
- At most one retry per request; format repair must not retry recursively.
- If a stage's actual call count exceeds the preset maximum workload, pause the related tasks and check for a loop.
- If a request exceeds the preset timeout, or the completed-task count does not grow for a long time, log a diagnostic; for a timeout, first clarify billing and in-flight status rather than immediately re-sending many times.
- If a single request's tokens clearly exceed the input estimate, or usage is abnormal for tasks of the same length, record the estimated/actual deviation and check it; do not judge it a bug merely because complex material is longer.

Prefer to pause the affected tasks on an anomaly, have the AI repair within the existing scope, preserve the failure evidence and resume; only go to the user for insufficient budget, a change in experimental meaning, or a need for user permission. Real anomalies must not be silently ignored, and normal cumulative token growth must not become a new manual approval step.

## 13. Engineering scope and archive

Reuse the existing harness, brief, fact review, translation and blind-review pages. New configuration and a lightweight runner are enough; the UI, database or agent framework are not rebuilt.

"Write less code" is a scope principle, not a limit on the number of patches for necessary fixes. Budget, fact, logging and grouping bugs must be fixed, and execution must not proceed while broken just because it has already been edited three times.

At execution, create the next round's loops/v003 and keep v001/v002 as they are. Save at least:

```text
loops/v003/
  plan_v003.md
  experiment_contract_v003.yaml
  process_archive_v003.md
  events_v003.jsonl
  artifact_index_v003.json
  configs/
  code/
  inputs/
  runs/
  results/
  review_v003.md
  decision_v003.md
```

This document is a plan and does not replace the resolved execution contract. Before starting, lock the real source ID, model ID, price, prompts, code and input hashes, and the budget. Do not create a contract with placeholder fields and then claim it is pre-registered.

Record the raw response, structured output, error, retry, model/prompt version, duration, actual usage, cost, cache hit and contract hash every time. Record the planned-versus-actual difference per stage. Do one consolidated integrity review at the end of the loop; do not fabricate missing logs.

## 14. Execution order and completion criteria

1. **Prepare**: verify old assets, exclude already-exposed sources, pre-group, lock scenario templates and Dev current-user tasks, model prices and budget; pass the budget-control simulation.
2. **Dev**: generate 8 tasks of G0/G1, source review and faithful translation, hand to the user for 8 human label pairs.
3. **Selector**: up to two locked candidates take the challenge; freeze if it passes, otherwise switch off.
4. **Component selection**: choose G0/G1 from the Dev human results; only with a qualified Selector do the 4-task title exploration, then have the user complete 4 title acceptances, deciding by the 3/4 rule whether to include it.
5. **Freeze**: record P* and the whole protocol. If P* = G0, end the improvement-comparison route and honestly deliver a no-gain conclusion.
6. **Final**: after the freeze, open the 6 new material tasks, construct and freeze the current-user scenarios from the locked templates, generate 24 candidates, use fixed draft-selection and review rules, and prepare 6 human blind-review pairs.
7. **Close**: compute results and Selector consistency, cost, errors, budget and archive review, and form the report and product decision.

Completion criteria for this round: real outputs, real human labels, reviewable sources, complete budget records, freeze and Final isolation evidence, and a clear keep/close decision. If human labels have not yet been received, the status is HUMAN_PENDING and the experiment is not marked complete.

## 15. Stop conditions

- Insufficient sources or Final exposure: switch to the designated backups; if independent tasks cannot be obtained, stop the confirmatory conclusion.
- Selector failure: switch off the key ranking and title module and stop searching for models.
- G1 has no gain: keep G0; the title may be explored independently, and the body is not further complicated.
- Title has no gain: switch off.
- Neither version is worth publishing: record the real failure and do not treat a relative preference as a success.
- A fabricated fact or identity is found: reject that draft and record it; do not quietly rewrite it by hand into a model success.
- The request or dollar hard cap is reached: stop and report the incomplete stage; cumulative tokens continue to be recorded, without reusing this round's cancelled 500k hard stop.
- Wanting to adjust after Final: open a separate development round and keep the old Final in its exposed state.

## 16. Final deliverables

- A runnable simple generator: one of G0, G1 or its title-enhanced version.
- This round's full experiment report, with per-version prompts, topics, real examples and quality review.
- Raw human labels, anonymous mappings, machine AB/BA outputs and consistency results.
- The full candidate set, failed drafts, cost/token/call ledger and integrity review.
- A short product description: input, output, identity limits, applicable scenarios and current evidence boundaries.

The final research story is not pre-written as a "success":

> This round tested motivation planning and title optimization under full fact constraints, selected lightweight components using the project user's preference, and validated the frozen product on new tasks; the conclusions are limited to this offline test and do not represent real community propagation effects.

The execution threshold has now been reached. The next step is not to add more modules, but to run the 8 Dev tasks first and obtain the first batch of real preferences.

## 17. Quick alignment: what humans and AI each do this round

| Stage | AI responsible for | User responsible for | Completion criteria |
| --- | --- | --- | --- |
| Prepare | source screening, grouping, full brief, cost accounting, logging and checks | no extra research needed | real sources and execution contract verifiable |
| Dev bodies | generation, source verification, faithful translation, anonymous display | 8 post blind-review pairs | real labels received, not fabricated |
| Selector | up to two candidate challenges, selection by fixed rules and freeze | no model picking | admitted or switched off, results complete |
| Title exploration | generate and machine-select titles, translate, display anonymously | 4 title comparisons (only if the module runs) | at least 3 of all 4 tasks clearly prefer the new title with no misleading content |
| Final | freeze product, new-task generation, draft selection, source verification, translation | 6 final post blind-review pairs (when P* differs) | do not change the product or swap topics based on results |
| Wrap-up | full report, cost and integrity review, runnable product | final use and acceptance | conclusions are grounded, unfinished items clearly marked |

This v1.2 is a plan update and does not mean Round 3 has started running, nor that the title or Selector is already effective.
