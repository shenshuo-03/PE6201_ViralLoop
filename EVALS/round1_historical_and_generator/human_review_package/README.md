# Evaluations (Round 1 package)

**Historical classification.** A frozen month × type relative-score label. Parameter and threshold selection uses Dev; Final is evaluated once. The expensive E5 judge runs on a pre-fixed 80-item subsample, and every local model is scored on the same 80 items. The full 348-item table is stored separately and must not be merged into a combined ranking.

**Generation comparison.** 10 frozen topics with hypothetical facts; 2 candidates per variant. Extra sampling and feedback rewriting each produce 3 drafts, from the same starting draft, with the same model and the same output cap. Retrieval and pattern material are supplied only from Train and Tune-validated sources. All candidates, refusals, final selections and costs are recorded.

**Quality control.** Numeric, fact-ID, hypothetical-status, length and copy rules, plus an independent model. The 30 controlled positive cases and mutated counter-examples test only a narrow factual constraint; they do not establish open-world discrimination accuracy.

**Human review.** `human_blind_cases.json` hides version and score; the browser route `/blind` offers A/B/Tie. Records appear under `human_review_submissions/` only after a real person submits; AI must not fill them in. Anything not submitted is never written up as "human-verified". The unblinding mapping is stored separately and is not opened during review.

**Real platform.** There was no randomised platform A/B test, no exposure data and no actual engagement with the generated drafts, so any claim of a "real virality lift" cannot be treated as verified.
