# ViralLoop Product Description

## Persona / input / output

User: an author writing a technical discussion post about local large language models. The first version covers only the English r/LocalLLaMA setting and is not generalized into an all-platform viral tool.

Input: topic, audience, content type, fact material (F1/F2...); the current live prototype explicitly treats the material as a hypothetical scenario. Output: a draft, a relative performance-potential score, quality and rejection reasons, positive/negative soft-pattern diagnostics, one revised version and the extra call cost. It must not display a real viral probability or promise an engagement gain.

```text
Historical posts -> source-record recovery -> fixed observation window -> time partitions
                     |-- Train -> local model / real embeddings / pattern statistics
                     `-- Dev   -> choose parameters and thresholds -> Freeze -> Historical Test

Topic + fact ledger -> Train-only retrieval -> Gemini generates candidates
                                  |
                     local hard rules + independent GPT quality check
                                  |
                     qualified candidates ranked by the local text model
                                  |
                     soft-pattern diagnostics -> one feedback rewrite
                                  |
                     re-check / re-rank -> best qualified draft or the original
                                  |
                     real logs + harness + genuine human blind review
```

## External intelligence and build vs buy

Built in-house: data audit, labels, frozen partitions, TF-IDF/logistic regression, hard quality rules, case retrieval, pattern statistics, the experiment harness, the cost ledger and the interface. Bought: Gemini generation, GPT quality and exploratory historical classification, and real OpenAI embeddings; all via OpenRouter, under the authorized US$5 cap.

Why no agent: the task order is fixed, and adaptive tool planning has no evidence of adding value yet. Why no fine-tuning: samples and time are limited, so the historical learnable signal and the benefit of simple methods are verified first.

## Metric targets and actual values

The goal is not to force F1 to some number, but to: compare against lazy/context baselines; make generation hard constraints auditable; compare feedback against multi-sampling at the same per-topic budget; and retain negative results. Actual metrics are in `results/experiment_1_0_results_and_conclusions.md` and the raw CSV files; the product description does not hard-code unfinished experiment numbers.

## Operating boundaries

Only pre-publication fields may enter the model; score, comment count and retrieval-age outcome features are not inputs. The network only accesses the data source and the authorized model APIs. Retrieved posts are untrusted data and cannot become system instructions. The model quality check will misjudge sometimes; a human still has to check facts before publication. Abstaining and retaining the original are acceptable outputs.
