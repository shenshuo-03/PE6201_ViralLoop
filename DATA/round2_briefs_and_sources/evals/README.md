# Round 2 evaluation materials

**`controlled_pairs_calibration` / `controlled_pairs_validation`** — 30 pairs in total, isolated by original source group. Each pair removes a useful feature along one design dimension and includes exact-text ties and minor-formatting ties. The `expected` labels come from constructed engineering cases, not from a gold standard of human preference; they are not used to claim real popularity or community-level accuracy.

**`brief_*`** — the writing brief produced by material extraction and source review. Quotations are checked by contiguous characters, which does not prove that a semantic inference is correct. The source file remains the basis for factual review.

**`naturalness_user_review`** — naturalness checks on three posts, carried out in Chinese. `genuine submissions` preserves the reviewer's actual assessments; revision D03 received an affirmative conversational reply, which only fixes the direction of expression. Assistant-edited drafts do not count as an automatically generated result. The note that S01's technical background was hard to judge is retained.

**`final_human_public_pairs`** — the blind Chinese random A/B comparison of V1 against V0. `private_mapping` is stored separately and not shown on the page. Reviewers could answer "Uncertain" when technical understanding was insufficient. A mechanical check of the numbers in the translation is not proof of full semantic quality. Where no human result was submitted this is explicitly marked pending.

**`final_comparisons`** — after freezing, an external model compared newly generated drafts on fresh material using AB/BA ordering. Disagreements are recorded as Uncertain and are not counted as a half win. Where the two items are identical the original is retained as a Tie, explicitly noted as not being a model-judge vote.

Product-test material (identifiers beginning with **L**), its generation and its translation must not be mixed into the Final effect sample.
