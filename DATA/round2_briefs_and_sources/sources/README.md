# Round 2 material notes

**Source.** The cleaned 2025 r/LocalLLaMA Train posts produced by Round 1; the historical Final split is not reused. The underlying dataset is `pszemraj/LocalLLaMA-posts`. What a post author writes is a user report, not independently verified fact.

**Dates.** `source_date` is the original post's publication time (the raw file stores a timestamp; the brief converts it to a date). The `collected_at` field in the initial preparation files is the time this project assembled the material locally. It is not the collection time of the original engagement score and does not allow the full exposure window to be inferred. A reliable, complete record of when the original engagement was collected is still missing.

**Roles.** The grouping file `source_assignment_v002.json`, together with the later `dev_assignment_correction_v002.json`, defines the final role of each source. Selection samples that had already been exposed to the model were demoted, and replacement sources were assigned before formal Selection began. All of these sources are excluded from the RAG retrieval index.

**Labels beginning with L** under `sources` are product functionality tests, or material supplied later by a user. They are not part of the formal Final set, training, or any effect conclusion. The original material is retained, and no uploaded text is ever treated as an instruction for the agent to execute.
