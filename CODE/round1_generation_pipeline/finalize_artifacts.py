"""Summarize executed evidence only; generate review package and course report.

PDF creation is separate (render_report.py). This script never invents human votes,
real user traffic, measured benchmarks or unobserved model experiments.
"""
from common import *
from harness import summarize
from model_api import entries,spent
import pandas as pd,numpy as np,re,random,importlib.metadata

def table(df,columns,decimals=3):
    # Avoid optional tabulate dependency.
    lines=['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']
    for _,r in df.iterrows():
        cells=[]
        for c in columns:
            v=r[c];cells.append(f'{v:.{decimals}f}' if isinstance(v,(float,np.floating)) else str(v))
        lines.append('| '+' | '.join(cells)+' |')
    return '\n'.join(lines)
def write_md(path,content):Path(path).write_text(content,encoding='utf-8')
def blind_package():
    cases=[];keys=[];rng=random.Random(SEED)
    comparisons=[(f'T{i:02d}','G0_generic','G4_both','G4_vs_G0') for i in range(1,9)]+[(f'T{i:02d}','O1_resample','O2_feedback','Feedback_vs_resample') for i in range(7,11)]
    for tid,a,b,comparison in comparisons:
        ra=json.loads((ROOT/'results/generator_runs'/f'{tid}__{a}.json').read_text(encoding='utf-8'));rb=json.loads((ROOT/'results/generator_runs'/f'{tid}__{b}.json').read_text(encoding='utf-8'))
        xa=ra['selected'] or max(ra['results'],key=lambda x:x['performance_score']);xb=rb['selected'] or max(rb['results'],key=lambda x:x['performance_score'])
        swap=bool(rng.getrandbits(1));A,B=(xb,xa) if swap else (xa,xb);cid=f'H{len(cases)+1:02d}'
        cases.append({'id':cid,'topic_id':tid,'topic':ra['topic']['topic'],'facts':ra['topic']['facts'],'A':{'title':A['draft']['title'],'body':A['draft']['body']},'B':{'title':B['draft']['title'],'body':B['draft']['body']}})
        keys.append({'id':cid,'topic_id':tid,'comparison':comparison,'A_variant':b if swap else a,'B_variant':a if swap else b,'A_qualified':A['constraint_pass'],'B_qualified':B['constraint_pass'],'fallback_raw_candidate':ra['selected'] is None or rb['selected'] is None})
    write_json(ROOT/'evals/human_blind_cases.json',cases);write_json(ROOT/'results/HUMAN_UNBLINDING_KEY_DO_NOT_READ_DURING_REVIEW.json',keys)
    template='case_id,clarity,usefulness,credibility,clickbait,overall\n'+'\n'.join(c['id']+',,,,,' for c in cases)+'\n'
    (ROOT/'evals/human_review_template.csv').write_text(template,encoding='utf-8-sig')
    write_json(ROOT/'evals/human_review_status.json',{'at':now(),'status':'pending genuine human submission','planned_pairs':12,'distinct_topics':10,'G4_vs_G0_pairs':8,'feedback_vs_resample_pairs':4,'note':'Different comparison families must not be pooled into one headline win rate; repeated topics are clustered. If a method abstains, blind review shows best raw candidate and the key records that fact.'})

def make_figures(e,gs):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figdir=ROOT/'results/figures';figdir.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(9,4.8));order=e.sort_values('average_precision');ax.barh(order.model,order.average_precision,color=['#bcc4ce' if x.startswith('E0') else '#225bc1' for x in order.model]);ax.axvline(float(e.prevalence.iloc[0]),color='#b45b10',linestyle='--',label='Test class prevalence');ax.set_xlabel('Average Precision on 348 held-out historical posts');ax.set_xlim(0,.7);ax.legend(loc='lower right');fig.tight_layout();fig.savefig(figdir/'historical_evaluator_AP.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.5));order=gs.sort_values('variant');axes[0].barh(order.variant,order.mean_selected_performance,color='#225bc1');axes[0].set_xlabel('Mean selected proxy score (NOT actual virality)');axes[0].set_xlim(0,.35);axes[1].barh(order.variant,order.mean_selected_quality,color='#198166');axes[1].set_xlabel('Independent model quality (1-5)');axes[1].set_xlim(0,5);fig.suptitle('10 frozen hypothetical briefs; report abstention coverage separately');fig.tight_layout();fig.savefig(figdir/'generator_proxy_and_quality.png',dpi=180);plt.close(fig)

def main():
    summarize();blind_package()
    e=pd.read_csv(ROOT/'results/evaluator_results.csv');match=pd.read_csv(ROOT/'results/judge_classifier_results.csv');summary=pd.read_csv(ROOT/'results/generator_summary.csv');gs=summary[summary.partition.eq('final_test')].copy();candidate=pd.read_csv(ROOT/'results/generator_candidate_results.csv');fc=candidate[candidate.partition.eq('final_test')]
    comparisons=pd.read_csv(ROOT/'results/generator_paired_comparisons.csv');cost=json.loads((ROOT/'results/cost_summary.json').read_text(encoding='utf-8'));data=json.loads((ROOT/'configs/data_freeze.json').read_text(encoding='utf-8'));freeze=json.loads((ROOT/'configs/generator_freeze.json').read_text(encoding='utf-8'));boot=json.loads((ROOT/'results/evaluator_bootstrap.json').read_text(encoding='utf-8'));up=json.loads((ROOT/'results/upworthy_transfer_metrics.json').read_text(encoding='utf-8'));cal=json.loads((ROOT/'results/quality_calibration_metrics.json').read_text(encoding='utf-8'))
    by={r.model:r for _,r in e.iterrows()};cg={r.variant:r for _,r in gs.iterrows()}
    o=comparisons[comparisons.a.eq('O2_feedback')&comparisons.b.eq('O1_resample')&comparisons.metric.eq('selected_performance')].iloc[0]
    pn=comparisons[comparisons.a.eq('G4_both')&comparisons.b.eq('G4_positive')&comparisons.metric.eq('selected_performance')].iloc[0]
    observations=pd.read_parquet(ROOT/'data/processed_posts.parquet');first_age=(observations.first_retrieved_at-observations.created_at)/3600
    versions={x:importlib.metadata.version(x) for x in ['pandas','numpy','pyarrow','scikit-learn','scipy','matplotlib']}
    write_json(ROOT/'configs/runtime_versions.json',{'at':now(),'python':sys.version,'packages':versions});(ROOT/'requirements.lock.txt').write_text('\n'.join(k+'=='+v for k,v in versions.items())+'\n',encoding='utf-8')
    ledger=pd.DataFrame(entries());ledger.drop(columns=['cache_key','request_id'],errors='ignore').to_csv(ROOT/'results/cost_results.csv',index=False)
    status={'automated_completed':True,'human_review_completed':False,'face_video_completed':False,'real_platform_experiment_completed':False,'final_generated_candidates':len(fc),'formal_topics':10,'api_budget_accounted_usd':spent(),'known_actual_api_cost_usd':cost['known_actual_cost_usd']};write_json(ROOT/'results/DELIVERY_STATUS.json',status)
    md=f'''# ViralLoop Experiment 1.0: Real Results and Conclusions

## Scope actually completed

The full audit, cleaning/deduplication/type rules, the 400-record upstream audit, 2,800 limited recoveries, the 2,336-record data freeze, the complete evaluator ladder, twelve positive/negative pattern cards, the generator ladder/ablations, one feedback comparison, the cost and failure ledger, and a runnable local interface were all actually executed. Final generation experiment: **10 topics, {len(fc)} candidates**; development topics and final topics are kept separate.

**Not completed and not fabricated**: the 12 genuine human blind-review pairs, the face-visible video recording, and real-platform randomized A/B and propagation outcomes. The English report is currently a reviewable draft and must keep these boundaries.

## 1. Data and controlled variables

All 400 audit records were returned, 95.75% within 36-38 hours; score and observation time come from the same source record. 100,679 raw posts, 20,019 rule-eligible candidates; 2,800 stratified random recoveries, 2,336 final. Train 1396 / Tune 398 / Selection 194 / Test 348.

Low, zero and negative scores were retained. There is no exposure data, so textual association cannot be treated as causation. Usable author history is only {int((observations.author_prior_missing==0).sum())}/{len(observations)}; the missing rate is high. Median first-capture age is {first_age.median()*3600:.1f} seconds, {int(first_age.gt(1).sum())} records exceed one hour, maximum {first_age.max():.2f} hours; the state of the body at the moment of posting remains uncertain. Labels are a retrospective relative ranking within the same month and content type, not an absolute engagement threshold knowable in real time.

## 2. Historical evaluator: full 348-record final test

{table(e,['model','precision','recall','f1','average_precision','brier'])}

Text-only E2 has AP={by['E2_tfidf'].average_precision:.3f}, strict-context E1 {by['E1_context_only'].average_precision:.3f}, showing that historical text does carry incremental predictive signal; **this cannot prove the effect comes from wording rather than topic, news and implicit author factors**. The real semantic model has AP={by['E4_semantic'].average_precision:.3f}, Brier={by['E4_semantic'].brier:.3f}; the serving-side local E2 still has the advantages of no API calls, speed and interpretability. E3 performed well in development but its final AP did not exceed E2, showing that adding context does not necessarily improve cross-time generalization.

Author-clustered bootstrap: E2 minus prior AP interval {boot['ci95']['E2_minus_prior']}; E3 minus E1 interval {boot['ci95']['E3_minus_E1']}. The intervals are conditional on the retained months and cannot cover all future variation.

## 3. LLM Judge: the same 80-record subsample

{table(match,['model','n','precision','recall','f1','average_precision'])}

That random 80-record set contains only 11 positives (13.75%), different from the full test's 24.71%; therefore it is compared within the same subsample shown above and must not be pooled with the full 348. The zero-shot / few-shot / RAG judges were all genuinely executed; no specific model was provided for "Jev", and no independent reward model is claimed to have been deployed. Small samples and threshold drift limit the conclusions.

## 4. Generators and quality constraints

With the same model and fact material, G0/G1/G2/G3/G4-positive/G4-both produced 2 drafts per topic; O1 added 3 drafts without feedback, O2 revised 3 drafts using local scores/pattern feedback; with the same 3600-token output cap, actual tokens and cost were recorded separately.

{table(gs,['variant','topics','coverage','mean_selected_performance','mean_selected_quality','mean_selected_clickbait'])}

These are proxy metrics on explicitly hypothetical material; no potential score may be read as a probability of going viral. For abstaining topics, the mean selected score includes only qualified outputs, so coverage must be read alongside it. The independent judge did not give the rewriter its scoring rationale; it may still share bias with the generator and needs genuine human checks.

The feedback O2 minus multi-sample O1 difference on jointly qualified topics averages **{o.mean_delta:+.5f}**, topic-bootstrap 95% interval [{o.ci95_low:+.5f}, {o.ci95_high:+.5f}], n={int(o.paired_topics)}. {'The interval spans 0, so feedback cannot yet be considered better than multi-sampling.' if o.ci95_low<=0<=o.ci95_high else 'The interval does not span 0 in this small sample, but this is still an exploratory proxy result and does not represent a real engagement gain.'}

The positive-plus-negative pattern G4-both minus positive-only difference is {pn.mean_delta:+.5f}, interval [{pn.ci95_low:+.5f},{pn.ci95_high:+.5f}]; more rules must not be assumed better by default. Pattern cards were BH-corrected on Train and only direction-checked on Tune; no claim is made that all development p-values are significant.

## 5. Best and most cost-effective

Before the final test, Selection Dev was frozen: the proxy-performance candidate was **{freeze['best_performance_selection']}**; the actually adopted candidate was **{freeze['best_practical_selection']}**. Selection had only 2 topics, so the choice itself is very unstable and cannot be packaged as a large-scale optimal conclusion. All final full-version results are retained as-is, and the selection rule was not re-chosen to suit the final outcome.

The product should currently center on factual fidelity and clear expression; advanced RAG, patterns and closed loops are only optional experimental paths. Only when genuine human review and real published experiments provide further support can the product promise around "content performance optimization" be raised.

## 6. Cost and failures

All accounted call budget is **US${cost['budget_accounted_usd']:.5f} / US$5**; the total of explicit usage.cost charges actually paid is **US${cost['known_actual_cost_usd']:.5f}**; {cost['unknown_charge_calls']} requests lacking a cost field are charged against the budget at a conservative upper bound, and estimates must not be dressed up as exact settlement. The ledger covers development calls, failures and fixes; see api_ledger/cost_results.

Quality control detected Precision={cal['precision_invalid']:.3f}/Recall={cal['recall_invalid']:.3f} on 30 controlled mutations (6 groups of the same material, not 30 independent open-world samples). This only shows that these preset factual errors were caught, not that the quality judge is 100% accurate.

Real failures included: out-of-material numbers, fabricated advice miswritten as fact, truncated JSON, HTTP 200 with an internal provider error, fact-reference false positives, and over-constraining soft patterns. Development rule fixes and old results were fully archived. No retained original or failing topic was deleted in order to showcase closed-loop improvement.

## 7. Optional Upworthy external transfer

A real run ranked the Reddit title model against Upworthy with identical experiment/image/lede/excerpt CTR: {up['n_experiments']} experiments, {up['non_tie_n']} non-tied, accuracy {up['pairwise_accuracy']:.3f}, random baseline 0.5. No Upworthy data was used for tuning; officially flagged non-random periods were excluded. Observed CTR still carries sampling noise and the domain/time/genre gaps are large; this is not evidence about full Reddit posts or real viral hits.

## 8. What the user still needs to add

1. Open the local `/blind` page and complete 12 genuine A/B/Tie evaluations (8 pairs G4 vs G0, 4 pairs feedback vs multi-sampling, summarized separately).
2. Review the hypothetical material, negative results and conclusion boundaries in the report.
3. Record a roughly 5-minute face-visible plus screen video following the demo script and submit it yourself.

This has reached the experimental execution threshold. The next version should prioritize real material and genuine human/platform feedback rather than piling on more agents, fine-tuning and multi-platform complexity.
'''
    write_md(ROOT/'results/experiment_1_0_results_and_conclusions.md',md)
    audit_path=ROOT/'results/independent_generation_audit_comparisons.csv'
    if audit_path.exists():
        audit=pd.read_csv(audit_path)
        ar=audit[audit.a.eq('O2_feedback')&audit.b.eq('O1_resample')&audit.metric.eq('audit_score')].iloc[0]
        addon=f'\n## 9. Independent re-check by a second performance model (exploratory post-hoc analysis)\n\nThe frozen E4 semantic model was used for auditing only and never fed scores back into generation or rewriting. Re-checking 178 independent texts (2 of the 180 candidates shared cached text) gave a feedback-minus-multi-sampling independent potential-score difference of {ar.mean_delta:+.5f}, with a 95% topic interval [{ar.ci95_low:+.5f},{ar.ci95_high:+.5f}]. Neither the optimizer nor the auditor demonstrated that feedback is better; a tiny score gain from this model must not be written up as an engagement benefit, and disagreement between two models must not be taken as proof of reward hacking. See the independent_generation_audit files.\n\nselected_model_attributions.json separately stores the linear model\'s actual logit contributions; the coefficients reflect term/topic associations, not causal editing advice.\n'
        write_md(ROOT/'results/experiment_1_0_results_and_conclusions.md',md+addon)
    make_figures(e,gs)
    report=f'''# ViralLoop: Constraint-Aware Content Generation and Independent Evaluation

## Problem and intended outcome

ViralLoop asks whether historical technical-community posts contain reusable performance signals, and whether those signals help generate and improve content without sacrificing factual fidelity. Its intended user is a writer preparing an English r/LocalLLaMA post from a topic, audience and supplied facts. The prototype returns candidate drafts, model-relative potential scores, quality diagnostics and one revision. It does not predict a guaranteed viral outcome. Reddit score, generated-content proxy scores, independent model quality ratings and real reader reactions represent different evidence. No generated post was published in a randomized platform experiment.

The practical question is not whether the largest pipeline wins. It is what extra quality or performance potential is purchased by Prompt engineering, examples, retrieval, pattern guidance and feedback, relative to their cost and implementation complexity. The project implements an auditable end-to-end path and keeps negative outcomes rather than optimizing a demonstration narrative.

## Data and evaluation design

The public LocalLLaMA archive contained 100,679 posts. Free rules selected 20,019 eligible 2025 text posts without consulting score. Deleted bodies, link-only or media-dominant posts, explicit promotions and obvious release news were excluded. Zero and negative scores remained. Sampling was stratified by month and rule-based content type, not performance. A 400-post upstream audit recovered every requested record; 95.75% had second-observation ages between 36 and 38 hours. This fixed the primary window before model evaluation. Only 2,800 candidates were restored, rather than the entire archive.

After window checks, deletion handling and near-duplicate removal, 2,336 posts remained. Score and observation time came from the same Arctic Shift record. Training covered January-July, tuning August-September, selection October, and final testing November-December: 1,396, 398, 194 and 348 posts respectively. Near duplicates were removed from later partitions. Author history used only sampled earlier outcomes whose observation had finished before the current post. Missing history was explicitly represented; it does not capture full author reputation.

The retrospective target was score strictly above the month/content-type 75th percentile. Outcome percentiles and feedback counts were never classifier inputs. This defines relative historical performance, not a deployable absolute engagement threshold. Initial archived text can differ from publication-time text, and unobserved exposure, breaking news and author effects remain confounders. Consequently, incremental text prediction cannot establish that wording caused higher engagement.

## Evaluator choices and historical results

The ladder included lazy and prior baselines, strict metadata, metadata plus structure, TF-IDF logistic regression, text plus context, local LSA, actual pretrained text embeddings plus classification, and generic LLM judges. LSA was labeled separately from pretrained semantic representation. Hyperparameters and classification thresholds were chosen on tuning data; selection data compared completed candidates. Frozen final tests were not used for further model tuning. Precision, recall, F1 and Average Precision were emphasized because a majority-class predictor can appear accurate while detecting no high-performing posts.

On all 348 held-out posts, positive prevalence was {by['E0_prior'].prevalence:.3f}. Strict context achieved AP {by['E1_context_only'].average_precision:.3f}; text-only achieved {by['E2_tfidf'].average_precision:.3f}, with precision {by['E2_tfidf'].precision:.3f}, recall {by['E2_tfidf'].recall:.3f} and F1 {by['E2_tfidf'].f1:.3f}. Pretrained embeddings achieved AP {by['E4_semantic'].average_precision:.3f} and Brier score {by['E4_semantic'].brier:.3f}. Text plus context achieved AP {by['E3_text_context'].average_precision:.3f}, showing that adding metadata did not automatically improve temporal generalization. These results support learnable historical signals, not a causal writing formula.

LLM zero-shot, few-shot and retrieval classifiers used the same fixed 80-post random subset, with local models evaluated on those exact IDs. That subset contained only 11 positives, so it was not ranked against the full-test table. The zero-shot judge achieved AP {float(match[match.model.eq('E5a_zero_shot')].average_precision.iloc[0]):.3f}; extra examples did not reliably improve it. No unspecified model called Jev or trained reward model was claimed to have been implemented. Small judge subsets limit confidence.

## Generation, patterns and feedback

The generator was Gemini 2.5 Flash Lite; independent quality review used GPT-4.1-mini. A local text-only classifier supplied optimization scores without requiring a hypothetical author's history. Retrieval searched training posts only. Ten predetermined measurable pattern hypotheses were compared within content type, with training multiple-testing correction and tuning-direction checks. Twelve cards survived, including eight positive and four negative associations. Cards retained sample sizes, counterexamples and limitations; negative stylistic patterns were soft advice rather than hard rejection rules.

Generation compared generic, structured Prompt, few-shot/planning, RAG, positive-pattern RAG and positive-plus-negative-pattern RAG. Each of ten frozen final briefs produced two candidates per version. Briefs explicitly used hypothetical facts, so no invented experimental numbers became personal experience. This isolates fidelity and rewriting but narrows applicability to real creator workflows. Hard rules checked numbers, references, length, scenario status and copying. A separate judge checked factual consistency, clarity, usefulness, credibility and clickbait. Its reasons were not supplied to the optimizer.

The feedback comparison started from the same draft. One arm generated three fresh alternatives without feedback; another made three targeted one-step revisions with local scores and pattern diagnostics. Model, candidate count and output cap were matched, while actual tokens and costs were recorded. Both arms could retain a qualified original. Final outputs were selected only after quality constraints; abstentions and every failed candidate were retained.

## Findings, critique and next steps

On the final generation topics, generic drafts had mean selected proxy score {cg['G0_generic'].mean_selected_performance:.3f} and independent quality {cg['G0_generic'].mean_selected_quality:.3f}; positive-plus-negative RAG had {cg['G4_both'].mean_selected_performance:.3f} and {cg['G4_both'].mean_selected_quality:.3f}. Feedback minus fresh sampling averaged {o.mean_delta:+.5f}, with a topic-bootstrap interval [{o.ci95_low:+.5f}, {o.ci95_high:+.5f}] on {int(o.paired_topics)} jointly qualified topics. Such a small, proxy-based comparison cannot establish real engagement improvement. Coverage must accompany conditional selected means; ten candidates from one topic are not ten independent observations.

Selection-stage choices were {freeze['best_performance_selection']} for potential and {freeze['best_practical_selection']} for practicality. Selection used only two briefs and is fragile. Additional architecture did not justify automatic preference for the complex pipeline. A title-only transfer test on {up['n_experiments']} Upworthy experiments achieved observed CTR-ordering accuracy {up['pairwise_accuracy']:.3f}; domain shift and noisy observed winners prevent broad conclusions.

Total budget-accounted API spend was ${cost['budget_accounted_usd']:.5f}, below the authorized $5 cap; known reported charges totaled ${cost['known_actual_cost_usd']:.5f}. Missing charge fields consumed conservative reservations. Failures and development fixes remained in the ledger. Engineering difficulties included mixed-type archive metadata, truncated JSON, provider errors and fact-reference false positives. The latter was corrected on development drafts before generator final testing; historical classifier tests were not rerun.

A controlled thirty-case fact-check probe detected its predefined mutations, but repeated variants of one scenario do not establish open-world quality accuracy. Genuine twelve-pair blind review and a face-visible demonstration remain for the author; neither was fabricated. The next valuable step is real creator material and prospective reader evidence, with randomized exposure if feasible. A fixed workflow, local models and purchased language APIs were sufficient; agents and fine-tuning were declined because their incremental value was unproven.

## Sources

- Dataset: https://huggingface.co/datasets/pszemraj/LocalLLaMA-posts
- Archive metadata: https://github.com/ArthurHeitmann/arctic_shift/blob/master/file_content_explanations.md
- Upworthy archive: https://upworthy.natematias.com/about-the-archive.html
'''
    if audit_path.exists():
        paragraph=f'A separate frozen semantic classifier audited generated drafts without feeding scores back into optimization. This was an explicitly post-hoc exploratory check, not another truth label. Feedback minus fresh sampling on this second proxy averaged {ar.mean_delta:+.5f}, with interval [{ar.ci95_low:+.5f}, {ar.ci95_high:+.5f}]. The audit therefore did not validate feedback superiority either. Linear-model token contributions were reconstructed exactly from coefficients, but can reflect topics and entities rather than effective edits. Two duplicated drafts shared cached generation; they were not counted as additional independent texts.\n\n'
        report=report.replace('## Sources',paragraph+'## Sources')
    write_md(ROOT/'submission/report.md',report);words=len(re.findall(r"\b[\w]+(?:['-][\w]+)*\b",report.split('## Sources')[0]));write_json(ROOT/'submission/report_word_count.json',{'main_words':words,'target':1200,'acceptable_teacher_range_15pct':[1020,1380],'references_excluded':True,'status':'draft pending genuine human review and author verification'})
    write_md(ROOT/'submission/demo_script.md',f'''# Demo script: about 5 minutes, genuine face-visible plus screen

The recording is done by the author; AI cannot stand in for the author\'s face. Do not show API keys. When only replaying real run records, say clearly "replay of experimental evidence"; when clicking to generate live, state clearly that a real model call is being made.

## 0:00-0:40 Problem and boundaries
Introduce writing technical-community content from fixed facts; the goal is to compare generation strategies and independent evaluation; no guarantee of a real viral rate can be made.

## 0:40-1:30 Data and historical models
Show the 2,336 frozen records, the 36-38h recovery evidence, the time partitions. Show the figure: text AP {by['E2_tfidf'].average_precision:.3f}, semantic AP {by['E4_semantic'].average_precision:.3f}, lazy positive-class F1 = 0. Explain that topic/exposure confounding remains.

## 1:30-3:15 Product loop
Open localhost:8765 and pick a genuinely completed T topic. Look at Facts first and explain that the material is hypothetical; compare G0, G4-both, O1, O2. Show all candidates, constraint failures, scores/quality and the retained original. If demonstrating live generation, prepare 2 short facts; do not exceed budget while waiting on camera or promise that scores will rise.

## 3:15-4:10 Experiment comparison
Show the 10-topic results and the feedback-vs-multi-sampling difference {o.mean_delta:+.5f} with its interval. Explain that "more complex is not necessarily better" and the practical reasons for choosing {freeze['best_practical_selection']}. If genuine human blind review is not finished, say clearly that it is still pending and do not invent results.

## 4:10-5:00 Trade-offs and limitations
Show the accounted cost ${cost['budget_accounted_usd']:.5f}, the failure categories, the reasons for not using agents/fine-tuning, and future real-reader validation. Close by explaining that the README is reproducible; reports/evals/data are transparently stored.
''')
    write_md(ROOT/'docs/reflection.md',f'''# Experiment reflection

Verified: historical text carries a relative-performance predictive signal, E2 AP={by['E2_tfidf'].average_precision:.3f} over the full retained months, real semantic={by['E4_semantic'].average_precision:.3f}.

Not verified: the causal benefit of phrasing, the real interaction of generated drafts, independent exposure normalization, full author reputation, multi-person blind review, and a large-scale stable strategy.

Complexity: context does not necessarily raise test AP; RAG/patterns did not guarantee better generation; feedback and multi-sampling must be compared from the same starting draft and the same budget. Putting many examples and statistics cards into the Prompt can also introduce facts, reduce diversity or confuse the objective.

Evaluation risk: quality rules that falsely flagged F-prefixed references were fixed during development; the unknown-number rule is still conservative and may reject legitimate quantity descriptions. Independent models may share bias. A narrow synthetic fact-check is not open-world 100% accuracy. The 10-topic bootstrap is exploratory only.

Next steps: real author material, genuine human review, and an editing comparison that only controls the input facts; run randomized exposure A/B only when real reader traffic exists. Do not expand agents/fine-tuning/multi-platform for now.
''')
    print('ARTIFACTS report words',words,'final drafts',len(fc),'budget',spent(),flush=True)
if __name__=='__main__':main()
