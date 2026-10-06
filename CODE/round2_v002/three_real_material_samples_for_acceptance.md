# Round 2: three real-material samples for naturalness acceptance

This is not a formal blind review. Judge only whether each sample reads like something worth posting in a real community, and name the one that most needs work. The sources are archived 2025 user reports, not your own first-hand testing.

## Sample 1: Clarifying the llama.cpp HTTP server file upload button and reproducibility when querying file contents

Type: Question / Troubleshooting; source date: 2025-05-14

Task: Understanding the functionality of the file upload button in llama.cpp's HTTP server and achieving reproducible results when querying file contents.

I've been reading about the file upload feature in llama.cpp's HTTP server and its behavior when used to ask questions about uploaded files. The original poster, using llama 3.2 3B Q4_K_S, noted that sometimes the model answers questions about the file content correctly, but other times it seems to interpret the file content itself rather than the query. They speculate the file upload might concatenate the file with the prompt, but this isn't confirmed. Their goal is to get reproducible answers—meaning the same prompts in a new conversation produce consistent results—but this hasn't been reliably achieved in their tests. Given this variability and the unclear mechanism behind the upload button, has anyone figured out how exactly the file upload interacts with the prompt? Also, are there known strategies or settings to improve reproducibility when querying uploaded file contents through this interface? Any insights or shared experiences would be helpful to understand this feature's intended use and limitations.

[Source post](https://www.reddit.com/r/LocalLLaMA/comments/1kmd9f9/what_does_llamacpps_http_servers_fileupload/)

## Sample 2: What do DeepSeek R1 perplexity results tell us about expert count and distilled model comparisons?

Type: Experience / Benchmark; source date: 2025-01-30

Task: To understand the performance of DeepSeek R1 models with varying numbers of experts and compare them to distilled models, based on a limited perplexity test.

A short perplexity test on DeepSeek R1 models with different numbers of experts offers some tentative insights but comes with major caveats. The test covered only 8 blocks out of about 560, used a block size of 512, and included distilled models plus Virtuoso-Medium-v2 for comparison. The source notes that the full DeepSeek R1 model, even with aggressive quantization, generally outperformed the distilled versions unless limited to 2 experts. Virtuoso Medium V2’s distill performance fell between DeepSeek R1 with 3 and 4 experts. Attempts to test with 10 and 12 experts failed due to NaN errors. Also, perplexity may not be a fair metric for chain-of-thought models since they don’t get to "think." Given these limitations and missing details like hardware and dataset specifics, how useful do you find perplexity as a metric for evaluating MoE models like DeepSeek? Would other benchmarks or test setups better clarify the impact of expert count on performance?

[Source post](https://www.reddit.com/r/LocalLLaMA/comments/1idi5cr/i_did_a_very_short_perplexity_test_with_deepseek/)

## Sample 3: Using Local LLMs to Improve HTML-to-Markdown Conversion: Challenges with Media-Heavy and JS-Only Sites

Type: Discussion / Opinion; source date: 2025-06-20

Task: Discussing methods and challenges for enhancing HTML-to-Markdown conversion using local LLMs, aiming to outperform traditional tools on complex websites.

A project shared on r/LocalLLaMA describes converting HTML web pages to high-quality Markdown using local LLMs like Qwen2.5-7B/8B with llama.cpp on consumer GPUs (e.g., 4070/4080/4090), running fully offline. It combines heuristic HTML analysis via BeautifulSoup to detect content focus and framework fingerprints with LLM-generated JSON extraction strategies and AI-based quality scoring. While results on standard article or blog pages often score good to excellent, the tool struggles with media-heavy or JavaScript-only sites without browser rendering. Processing a single page takes about 10–20 seconds on a 4070 GPU, but batch processing hundreds of pages may require optimization. Given these constraints, how do others handle dynamic or media-rich sites relying solely on local LLMs without browser engines? Are there practical methods to improve extraction quality or speed, such as pre-rendering, hybrid heuristics, or model fine-tuning? Also, what evaluation approaches beyond AI scoring have you found effective for benchmarking Markdown extraction quality?

[Source post](https://www.reddit.com/r/LocalLLaMA/comments/1lftz5s/open_discussion_improving_htmltomarkdown/)

## Please respond

Are these three natural, concrete and worth posting? If not, just name the sample number and the most obvious problem. Do not accommodate the system merely because it produced something. Until acceptance is received, no formal generation comparison or Final is started.
