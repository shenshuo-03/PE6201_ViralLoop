# ViralLoop Experiment 1.0: Real Results and Conclusions

## Scope actually completed

The full audit, cleaning/deduplication/type rules, the 400-record upstream audit, 2,800 limited recoveries, the 2,336-record data freeze, the complete evaluator ladder, twelve positive/negative pattern cards, the generator ladder/ablations, one feedback comparison, the cost and failure ledger, and a runnable local interface were all actually executed. Final generation experiment: **10 topics, 180 candidates**; development topics and final topics are kept separate.

**Not completed and not fabricated**: the 12 genuine human blind-review pairs, the face-visible video recording, and real-platform randomized A/B and propagation outcomes. The English report is currently a reviewable draft and must keep these boundaries.

## 1. Data and controlled variables

All 400 audit records were returned, 95.75% within 36-38 hours; score and observation time come from the same source record. 100,679 raw posts, 20,019 rule-eligible candidates; 2,800 stratified random recoveries, 2,336 final. Train 1396 / Tune 398 / Selection 194 / Test 348.

Low, zero and negative scores were retained. There is no exposure data, so textual association cannot be treated as causation. Usable author history is only 324/2336; the missing rate is high. Median first-capture age is 17.0 seconds, 13 records exceed one hour, maximum 10.82 hours; the state of the body at the moment of posting remains uncertain. Labels are a retrospective relative ranking within the same month and content type, not an absolute engagement threshold knowable in real time.

## 2. Historical evaluator: full 348-record final test

| model | precision | recall | f1 | average_precision | brier |
| --- | --- | --- | --- | --- | --- |
| E0_lazy | 0.000 | 0.000 | 0.000 | 0.247 | 0.247 |
| E0_prior | 0.000 | 0.000 | 0.000 | 0.247 | 0.186 |
| E1_context_only | 0.291 | 0.500 | 0.368 | 0.305 | 0.185 |
| E1b_context_structure | 0.381 | 0.593 | 0.464 | 0.420 | 0.170 |
| E2_tfidf | 0.510 | 0.605 | 0.553 | 0.552 | 0.180 |
| E3_text_context | 0.468 | 0.686 | 0.557 | 0.500 | 0.160 |
| E4_lsa | 0.392 | 0.674 | 0.496 | 0.540 | 0.154 |
| E4_semantic | 0.451 | 0.698 | 0.548 | 0.585 | 0.148 |

Text-only E2 has AP=0.552, strict-context E1 0.305, showing that historical text does carry incremental predictive signal; **this cannot prove the effect comes from wording rather than topic, news and implicit author factors**. The real semantic model has AP=0.585, Brier=0.148; the serving-side local E2 still has the advantages of no API calls, speed and interpretability. E3 performed well in development but its final AP did not exceed E2, showing that adding context does not necessarily improve cross-time generalization.

Author-clustered bootstrap: E2 minus prior AP interval [0.2187349245374035, 0.4050082634270958]; E3 minus E1 interval [0.10398960624329404, 0.2980778819269875]. The intervals are conditional on the retained months and cannot cover all future variation.

## 3. LLM Judge: the same 80-record subsample

| model | n | precision | recall | f1 | average_precision |
| --- | --- | --- | --- | --- | --- |
| E5a_zero_shot | 80 | 0.273 | 0.818 | 0.409 | 0.421 |
| E5b_few_shot | 80 | 0.178 | 0.727 | 0.286 | 0.322 |
| E5c_retrieval | 80 | 0.151 | 1.000 | 0.262 | 0.404 |
| E0_lazy | 80 | 0.000 | 0.000 | 0.000 | 0.138 |
| E0_prior | 80 | 0.000 | 0.000 | 0.000 | 0.138 |
| E1_context_only | 80 | 0.158 | 0.545 | 0.245 | 0.321 |
| E1b_context_structure | 80 | 0.265 | 0.818 | 0.400 | 0.545 |
| E2_tfidf | 80 | 0.350 | 0.636 | 0.452 | 0.599 |
| E3_text_context | 80 | 0.333 | 0.818 | 0.474 | 0.478 |
| E4_lsa | 80 | 0.212 | 0.636 | 0.318 | 0.448 |
| E4_semantic | 80 | 0.290 | 0.818 | 0.429 | 0.505 |

That random 80-record set contains only 11 positives (13.75%), different from the full test's 24.71%; therefore it is compared within the same subsample shown above and must not be pooled with the full 348. The zero-shot / few-shot / RAG judges were all genuinely executed; no specific model was provided for "Jev", and no independent reward model is claimed to have been deployed. Small samples and threshold drift limit the conclusions.

## 4. Generators and quality constraints

With the same model and fact material, G0/G1/G2/G3/G4-positive/G4-both produced 2 drafts per topic; O1 added 3 drafts without feedback, O2 revised 3 drafts using local scores/pattern feedback; with the same 3600-token output cap, actual tokens and cost were recorded separately.

| variant | topics | coverage | mean_selected_performance | mean_selected_quality | mean_selected_clickbait |
| --- | --- | --- | --- | --- | --- |
| G0_generic | 10 | 1.000 | 0.244 | 4.100 | 1.000 |
| G1_prompt | 10 | 1.000 | 0.242 | 4.150 | 1.000 |
| G2_fewshot_planning | 10 | 1.000 | 0.242 | 4.050 | 1.000 |
| G3_rag | 10 | 1.000 | 0.241 | 4.075 | 1.000 |
| G4_both | 10 | 1.000 | 0.240 | 4.000 | 1.000 |
| G4_positive | 10 | 1.000 | 0.242 | 4.050 | 1.000 |
| O1_resample | 10 | 1.000 | 0.242 | 4.100 | 1.000 |
| O2_feedback | 10 | 1.000 | 0.242 | 4.050 | 1.000 |

These are proxy metrics on explicitly hypothetical material; no potential score may be read as a probability of going viral. For abstaining topics, the mean selected score includes only qualified outputs, so coverage must be read alongside it. The independent judge did not give the rewriter its scoring rationale; it may still share bias with the generator and needs genuine human checks.

The feedback O2 minus multi-sample O1 difference on jointly qualified topics averages **+0.00014**, topic-bootstrap 95% interval [-0.00089, +0.00099], n=10. The interval spans 0, so feedback cannot yet be considered better than multi-sampling.

The positive-plus-negative pattern G4-both minus positive-only difference is -0.00224, interval [-0.00400, -0.00072]; more rules must not be assumed better by default. Pattern cards were BH-corrected on Train and only direction-checked on Tune; no claim is made that all development p-values are significant.

## 5. Best and most cost-effective

Before the final test, Selection Dev was frozen: the proxy-performance candidate was **G1_prompt**; the actually adopted candidate was **G0_generic**. Selection had only 2 topics, so the choice itself is very unstable and cannot be packaged as a large-scale optimal conclusion. All final full-version results are retained as-is, and the selection rule was not re-chosen to suit the final outcome.

The product should currently center on factual fidelity and clear expression; advanced RAG, patterns and closed loops are only optional experimental paths. Only when genuine human review and real published experiments provide further support can the product promise around "content performance optimization" be raised.

## 6. Cost and failures

All accounted call budget is **US$0.34423 / US$5**; the total of explicit usage.cost charges actually paid is **US$0.34423**; 0 requests lacking a cost field are charged against the budget at a conservative upper bound, and estimates must not be dressed up as exact settlement. The ledger covers development calls, failures and fixes; see api_ledger/cost_results.

Quality control detected Precision=1.000/Recall=1.000 on 30 controlled mutations (6 groups of the same material, not 30 independent open-world samples). This only shows that these preset factual errors were caught, not that the quality judge is 100% accurate.

Real failures included: out-of-material numbers, fabricated advice miswritten as fact, truncated JSON, HTTP 200 with an internal provider error, fact-reference false positives, and over-constraining soft patterns. Development rule fixes and old results were fully archived. No retained original or failing topic was deleted in order to showcase closed-loop improvement.

## 7. Optional Upworthy external transfer

A real run ranked the Reddit title model against Upworthy with identical experiment/image/lede/excerpt CTR: 1913 experiments, 1866 non-tied, accuracy 0.510, random baseline 0.5. No Upworthy data was used for tuning; officially flagged non-random periods were excluded. Observed CTR still carries sampling noise and the domain/time/genre gaps are large; this is not evidence about full Reddit posts or real viral hits.

## 8. What the user still needs to add

1. Open the local `/blind` page and complete 12 genuine A/B/Tie evaluations (8 pairs G4 vs G0, 4 pairs feedback vs multi-sampling, summarized separately).
2. Review the hypothetical material, negative results and conclusion boundaries in the report.
3. Record a roughly 5-minute face-visible plus screen video following the demo script and submit it yourself.

This has reached the experimental execution threshold. The next version should prioritize real material and genuine human/platform feedback rather than piling on more agents, fine-tuning and multi-platform complexity.

## 9. Independent re-check with a second performance model (exploratory post-hoc analysis)

The frozen E4 semantic model was used for auditing only and never supplied feedback to generation or rewriting. After re-checking 178 independent texts (2 of the 180 candidates shared cached text), the feedback minus multi-sampling independent potential-score difference is -0.01462, 95% topic interval [-0.04148, +0.00746]. Neither the optimizer nor the auditor shows feedback to be better; a tiny score gain under this single model must not be written up as an engagement gain, and disagreement between the two models is not by itself proof of reward hacking. See the independent_generation_audit files.

selected_model_attributions.json separately stores the true logit contributions of the linear model; the coefficients reflect term/topic associations, not causal editing advice.

## 10. Applicability correction after user feedback

The genuine human blind review was deferred at the user's request. The user pointed out that the generated posts were too abstract; the check confirmed that the uniform hypothetical material and the disclaimer requirement reduced community realism. The generation experiment is therefore only a proxy comparison on controlled hypothetical material and cannot prove that real community content optimization works. See `REPORT/Round1_Explainer.md`. The historical real-post prediction experiment is interpreted separately from this issue.
