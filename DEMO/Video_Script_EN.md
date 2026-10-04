# Video Script (English) — ViralLoop Demo

**Target length: ~5 minutes.** Recording, face and screen are the author's own; this file is the script only.
Sections marked **[SCREEN]** show the screen, **[FACE]** are to camera.

---

### 0:00 – 0:25 · Hook and claim **[FACE]**

> "I built a system to turn an engineer's raw notes into a post a technical community would actually read. I spent three rounds of experiments trying to make it work with retrieval, feedback loops, planning agents and automatic judges.
>
> And what I found is the honest headline: **I could predict which historical posts performed well — but I could not turn that prediction into a better post.** This is the story of that negative result, and why it is the most useful thing I built."

### 0:25 – 1:00 · The problem **[FACE] + [SCREEN: slide — persona]**

> "This is Wei. He's an engineer who just found something surprising in a benchmark. He reads r/LocalLLaMA every day. He has never posted.
>
> Not laziness — he genuinely doesn't know whether his result is the headline or a footnote. The closest existing tools write fluent summaries. Fluency is easy. **Postability is not**, and nothing measures it."

### 1:00 – 1:50 · Why AI, and what I actually built **[SCREEN: architecture diagram]**

> "I chose prompting a rented foundation model, and climbed no higher than the evidence justified. I tested each rung: prompt engineering, retrieval over historical examples, pattern cards, a feedback loop, and multi-sample selection.
>
> The data: r/LocalLLaMA, a hundred thousand posts, cleaned down to two thousand three hundred and thirty-six. A single community, so platform and domain stay constant. I recovered observation age from the archive and fixed a thirty-six to thirty-eight hour window, so a post couldn't win just by being older.
>
> My label is **relative high score within month and content type** — not clicks, not impressions. And I froze the splits: train on January to July, and never touch the November–December Final set until the end."

### 1:50 – 2:45 · The result **[SCREEN: evaluator table + figures]**

> "Round one. Two questions, deliberately separated.
>
> First: can history be predicted? Yes. TF-IDF got an Average Precision of zero point five five two; a semantic embedding got zero point five eight five. Against a lazy baseline of zero point two four seven, that's real signal. I checked accuracy separately — and my lazy baseline scored seventy-five percent accuracy by never predicting the positive class. That's exactly the trap the brief warns about, and AP is what exposes it.
>
> Second: does that prediction make generated posts better? **No.**
>
> Here's the key number. Feedback versus equal-budget resampling: plus zero point zero zero zero one three nine five. The bootstrap interval runs from minus zero point zero zero zero nine to plus zero point zero zero one. **It contains zero.** My independent auditor agreed: minus zero point zero one five, also containing zero.
>
> And here is the most interesting part. The automatic scores barely moved — but the human reaction was completely different. A reviewer said, and I quote, *'information density is too high, it doesn't look like something a real user would post.'*
>
> **My automatic ruler rewarded clear, complete, compliant text. The human was asking whether anyone would post it.** Those are different questions."

### 2:45 – 3:35 · What went wrong, and how I found out **[SCREEN: judge admission table, Round 3 evidence]**

> "Round two, I stopped trusting my judge and tested it. Thirty controlled comparison pairs. Gemini Flash failed outright. Gemini Lite passed overall but **failed the information value dimension specifically** — two out of five. So I closed the feedback arm. That was the protocol working, not failing.
>
> Round three, I found the deepest problem. I built a brief that assumed every author is a community member asking for help. The result: **all eight tasks collapsed into help-seeking posts** — including material that was plainly a release, a tutorial, or a personal test.
>
> The schema was the bug. So I rebuilt it around four archetypes — finding, opinion, resource, question — and changed the question I was asking, from *'which would make you reply?'* to *'would you open this in your feed?'* That fixed the type collapse. It did not fix the summary tone."

### 3:35 – 4:20 · Limitations, said out loud **[FACE] + [SCREEN: limitations]**

> "I want to be explicit about what this project does **not** establish.
>
> I never measured real exposure or engagement. There is no online result here at all.
>
> Round two's protocol audit **failed** — I exceeded my own token cap by twenty-two percent, and sixty-eight raw responses were never saved. I'm reporting that rather than hiding it.
>
> Round three **terminated early at the development stage**. I did not run the Final, and I did not reconstruct the human feedback. So there is no valid conclusion about the planner versus the baseline.
>
> And the deepest limitation is statistical: with ten to twelve tasks, my experiment could only ever detect an enormous effect. I did not compute that up front. **I was underpowered by construction.**"

### 4:20 – 5:00 · The decision **[FACE]**

> "So here is what I ship: a fact-constrained drafting assistant. Real author intent in. A complete brief. Simple generation. Deterministic fact, identity and date checks. And mandatory human confirmation before anything is published.
>
> The closed loop — retrieval, patterns, feedback, planner — I keep as research assets, not as the product.
>
> Total API cost, all three rounds: one dollar thirty-two. Cheaper than I expected. The cost that actually held me back was never money — it was reconciling confounds, checking identity, and getting a human to judge technical content in their second language.
>
> The lesson I'd carry forward is not *'complexity is bad.'* It's that **I put calibrating the measuring stick last, when it should have been first.** On an uncalibrated target, a positive result and a negative result are equally uninterpretable.
>
> That's the project. Thank you."

---

## Recording notes

- Total runtime target ~5:00. Camera and screen both visible throughout, per the brief.
- Have these open before recording: `REPORT/figures/historical_evaluator_AP.png`, `REPORT/figures/generator_proxy_and_quality.png`, the evaluator table from `REPORT/Round1_Explainer.md`, and the judge admission table from `REPORT/Round2_Explainer.md`.
- Deliver the limitation section (§3:35) without hedging — the brief explicitly asks the demonstration to articulate limitations out loud.
- Do not say "viral", "boosted engagement", or any percentage that implies measured online performance. None of that was measured.
