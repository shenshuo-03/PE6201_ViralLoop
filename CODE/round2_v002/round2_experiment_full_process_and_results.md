# PE6201 ViralLoop: Round 2 Experiment Process and Results

## Conclusions first

Round 2 automated generation and independent offline comparison have been actually run. Before Final, the product was frozen by preset rules as **V0**: full brief from real material, simple generation prompt, two candidates, quality screening, fixed-order selection. The internal evaluator did not pass admission, so feedback rewriting and preference-based selection were switched off.

The current evidence only supports judgments about offline writing preference, and **cannot prove that it can produce a real viral hit**. Genuine human Final blind review and real publishing outcomes are still missing; the three-sample naturalness acceptance is not a formal human effectiveness evaluation.

## Problem, experimental subject and controls

The goal is to turn real material into content that raises a concrete problem and is worth community discussion, and to test whether strong prompting, structural RAG and extra sampling bring any gain. The platform is r/LocalLLaMA and the material comes from the 2025 historical Train set cleaned in Round 1. The Round 1 model was not retrained and the historical Final was not rerun.

Isolation by source group: 4 Tune, 2 Selection, 12 Final; plus naturalness previews and controlled evaluator items. Two original Selection sources had already been previewed, so they were first demoted to development use and two new Selection sources were mechanically added. The Final pre-allocation was unchanged, and every source text entered the generation process only after the product freeze.

All generators used GPT-4.1-mini, with the same full fact source for the same task, and the input contained no upvotes, comments or score. The methods:

- V0: full brief, simple prompt, 2 candidates.
- V1: first choose one posting goal and at most 2 necessary facts, then use the strong prompt, 2 candidates. Fact checking still reads the full source.
- V2: V1 plus a historical structure reference, 2 candidates; the retrieval library excludes all already-grouped sources and extracts writing structure only.
- O1: extra sampling of 3 more drafts from the same V2 starting draft, retaining the original. Because the preference selector did not pass admission, qualified originals are preferentially retained, so no claim that extra sampling is ineffective can be made from this.
- O2/V3: not executed due to the evaluator failure stop rule; no claim that feedback optimization is either effective or ineffective.

## What actually happened

1. Jev had no usable direct credentials and the catalogue price could not be reliably upper-bounded, so no paid integration was performed. Two internal candidates were fixed in advance, and no further model search followed.
2. Six naturalness previews with clear provenance were generated, and 3 were translated for the author to check. Actual feedback: sample 1 accepted; sample 2 rejected for high information density; sample 3 accepted with a note that the technical background was hard to judge.
3. Two automated simplifications still piled on detail. The assistant produced one directly edited version and the author replied "yes", accepting that it read more like a normal post. That edited draft is not counted as an automated-generation effect sample.
4. The 30 controlled pairs were split by source group into 15 Calibration and 15 Validation, with AB/BA swapped for each pair. The internal Gemini Flash Lite calibrated well, but the Validation information value was only 2/5 and did not reach the per-dimension threshold, so feedback and preference selection were stopped. The external Claude Haiku met all design expectations on the 15 controlled Validation pairs.
5. Formal Tune ran two rounds; the first round's outputs were fully retained. The second round was changed to focus first and then generate, without an external judge. Each Selection plan then qualified 2/2 tasks, and by the tie-break preference for the simpler plan, V0 was frozen. Two Selection tasks are very few, so this must not be interpreted as V0 being universally best.
6. After the freeze, candidates were generated for the 12 new tasks and then independently compared by the external Claude. Disagreements between AB and BA were merged into Uncertain; identical texts were recorded directly as an identity Tie, explicitly not as a judge vote. The product was not modified retroactively from the Final results.

## Final independent comparison results

Win means the new method was better than the old one. The decisive win rate uses only Win+Loss as its denominator; coverage is (Win+Loss)/12. Uncertain is not counted as half a win.

| Comparison | Win | Loss | Tie | Uncertain | Failure | Decisive win rate | Decisive coverage |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| V1_vs_V0 | 1 | 7 | 0 | 3 | 1 | 12.5% | 66.7% |
| V2_vs_V1 | 3 | 2 | 0 | 7 | 0 | 60.0% | 41.7% |
| O1_vs_V2 | 0 | 0 | 12 | 0 | 0 | no decisive outcome | 0.0% |

Each comparison covers only 12 tasks. The Wilson intervals are stored in `final_summary_v002.json`; they are conditional intervals for the decisive subsample, not an overall success probability or a real viral rate.

## Generation checks and cost

- V0: 12 topics, 24 candidates; 22/24 passed the engineering hard checks, 12/12 qualified drafts selected, candidates average 143.7 English words.
- V1: 12 topics, 24 candidates; 24/24 passed the engineering hard checks, 12/12 qualified drafts selected, candidates average 110.5 English words.
- V2: 12 topics, 24 candidates; 24/24 passed the engineering hard checks, 12/12 qualified drafts selected, candidates average 117.6 English words.
- O1: 12 topics, 36 candidates; 36/36 passed the engineering hard checks, 12/12 qualified drafts selected, candidates average 115.8 English words.

As of this report, the Round 2 accounted budget is **US$0.708653**, Round 1 is **US$0.344225**, and the project total is **US$1.052878**, below the authorized US$5. The detailed ledger includes failed requests and conservative reservations for unknown costs.

The hard checks and quality scores in the report are still model-engineering screening, not fact certification or genuine user acceptance. E2 and the frozen E4 only perform a historical association audit on new drafts and are not used for selection; their scores are not to be interpreted as real viral probabilities. E4 re-obtained same-specification embeddings for the new drafts, and that cost is written into Round 2 without altering the Round 1 ledger.

## Limitations and critical analysis

- **Popularity confounding has not disappeared.** Posting time, trending events, author, exposure and recommendation distribution can all affect the historical score; the offline text comparison isolates task material and generation conditions but cannot estimate the causal gain of an actual post.
- **Controlled items are not a human gold standard.** The 15/15 external result only means the engineered differences were identified; it must not be written as "100% accuracy in community judgment". The internal information-value failure shows that an overall 12/15 must not mask a single ineffective key dimension.
- **The automated quality score once conflicted with the human opinion.** A dense draft accepted by the automated check was rejected by the author. The simplification goal was set by a human, and automated-generation effects must be read from independent results and must not be replaced by the human-edited draft.
- **Fair comparison has boundaries.** V1 adds a focusing step and V2 adds retrieval, so their cost must be counted; an equal number of candidates does not mean identical call cost. O1's stop strategy of retaining the original produced identity Ties, so the conclusions are limited to this implementation with preference selection switched off.
- **An independent reviewer is not the same as an unbiased one.** The external model is from a different family from the generator and did not take part in selection, but stylistic preference and human construction of the items still have an influence. The 12 genuine human blind-review pairs are not yet complete.
- **Historical material is not current news.** The source is archived author self-reports, so the necessary dates and uncertainties must be retained. Someone else's measurement must not be passed off as first-hand experience, and the model's current performance must not be claimed.
- **There are archive-completeness warnings.** Early on, 11 records lacked a complete per-run manifest and 68 lacked a per-run raw response file. The cost ledger is retained, but the cache does not guarantee every retry can be rebuilt; record gaps must not be written up as "all audits passed".
- **Token control failed.** This round's known cumulative total is 1,225,228 tokens, exceeding the internal protocol limit of 1,000,000 tokens. The execution program omitted a pre-call token block; this is not an overspend of the user's US$5 cost cap, but it is a genuine protocol deviation. This round cannot be labelled a confirmatory experiment that fully observed the pre-registered budget, and the old cap will not be rewritten to retroactively legitimize it. Follow-up product controls open a separate version, while the original frozen experiment code and records are retained.

## Deliverables and next steps

The desktop Experiment 1.1 package contains the protocol, real material, briefs, generated candidates, the selection path, the original AB/BA outputs, the cost ledger, grouping and freeze reviews, and a runnable generation page. The product is a fact-constrained community writing assistant and currently does not claim a verified viral outcome.

Remaining evidence: the 12 genuine human Final blind-review pairs; if real interaction improvement is to be tested in the future, this requires separately pre-registering posting-time/topic stratification and random assignment, a fixed observation window, and an actual publish. No real publishing has been performed.
