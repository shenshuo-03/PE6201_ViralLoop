"""Offline evidence synthesis after actual runs; never completes missing human or publishing data."""
from runtime import *
from _packaged_code import frozen_code_ok
import pickle,collections
import pandas as pd

def summarize():
    summary=read(LOOP/'results/final_summary_v002.json');freeze=read(LOOP/'configs/generator_freeze_v002.json');ledger=rows(LEDGER);events=rows(LOOP/'events_v002.jsonl')
    groups=read(LOOP/'inputs/source_assignment_v002.json')+read(LOOP/'inputs/dev_assignment_correction_v002.json')['new_selection']
    ids=[g['source_group_id'] for g in groups]
    original=read(LOOP/'inputs/parent_artifacts_v002.json')['files']
    external=[r for r in ledger if r['model']==EXTERNAL]
    final_records=[read(p) for p in (LOOP/'results/generator_runs').glob('F*_v002.json')]
    metrics={}
    for variant in ['V0','V1','V2','O1']:
        records=[r for r in final_records if r['variant']==variant];candidates=[c for r in records for c in r['candidates']]
        metrics[variant]={'topics':len(records),'candidates':len(candidates),'selected':sum(bool(r['selected']) for r in records),'hard_pass':sum(c['quality']['hard_pass'] for c in candidates),'quality_pass':sum(c['quality']['quality_pass'] for c in candidates),'mean_words':sum(c['quality']['body_words'] for c in candidates)/len(candidates) if candidates else None,'original_retained':sum(r.get('original_retained',False) for r in records),'generation_cost_usd':sum(r['generation_usage']['budget_charge_usd'] for r in records),'quality_cost_usd':sum(r['quality_usage']['budget_charge_usd'] for r in records)}
    write(LOOP/'results/final_generation_metrics_v002.json',metrics)
    # Historical predictor is an association audit only, never generation feedback.
    texts=[];keys=[]
    for r in final_records:
        if r['selected']:
            p=r['selected']['draft'];texts.append(p['title']+'\n'+p['body']);keys.append({'brief_id':r['brief_id'],'variant':r['variant']})
    with (OLD/'results/models/E2_tfidf.pkl').open('rb') as f:model=pickle.load(f)
    scores=model.predict_proba(pd.DataFrame({'text':texts}))[:,1]
    audit_scores=[dict(k,E2_historical_association_score=float(s)) for k,s in zip(keys,scores)]
    write(LOOP/'results/historical_E2_association_audit_v002.json',{'model_retrained':False,'used_for_selection':False,'scores':audit_scores,'interpretation':'Association with retrospective high-score labels, not actual viral probability; E4 independently recorded in historical_E4_association_audit_v002.json'})
    missing_manifest=[r['run_id'] for r in ledger if not (LOOP/'runs'/r['run_id']/f'manifest_{r["run_id"]}.json').exists()]
    missing_raw=[r['run_id'] for r in ledger if not (LOOP/'runs'/r['run_id']/'raw_response.json').exists()]
    frozen_ok=frozen_code_ok('round2_v002',freeze['code_hashes'],LOOP/'code')
    reads=[e for e in events if e['stage']=='access' and e['evidence'].get('split')=='final']
    product_hash=sha(LOOP/'product_contract_v002.yaml') if (LOOP/'product_contract_v002.yaml').exists() else None
    total_tokens=sum((r.get('input_tokens') or 0)+(r.get('output_tokens') or 0) for r in ledger if r.get('contract_sha256')!=product_hash)
    isolation={'source_groups_unique':len(set(ids))==len(ids),'first_round_snapshot_unchanged':{p:sha(OLD/p)==h for p,h in original.items()},'frozen_code_unchanged':frozen_ok,'external_generator_tune_selection_calls':sum(r['phase'] in ['tune','selection','naturalness'] for r in external),'final_source_reads_all_after_freeze':all(e['time']>=freeze['at'] for e in reads),'no_feedback_calls_after_failed_admission':not any(r['tag'].startswith(('O2:','diagnosis:','preservation:')) for r in ledger),'missing_per_run_manifest':missing_manifest,'missing_per_run_raw':missing_raw,'archive_status':'FAIL on internally declared token cap; WARN on incomplete early archives. Raw observed comparisons retained with protocol-deviation caveat.','known_tokens':total_tokens,'internal_token_cap':1000000,'token_control_failed':total_tokens>1000000,'budget_charge_usd':sum(costs()),'within_user_USD5_cap':sum(costs())<=5,'human_final_complete':False,'actual_publishing_performed':False}
    write(LOOP/'results/final_integrity_audit_v002.json',isolation)
    byphase=collections.defaultdict(float)
    for r in ledger:byphase[r['phase']]+=r['budget_charge_usd']
    write(LOOP/'results/cost_summary_v002.json',{'prior_usd':costs()[0],'round_usd':costs()[1],'total_usd':sum(costs()),'cap_usd':5,'round_cap_usd':2,'ledger_rows':len(ledger),'by_phase_usd':dict(byphase),'unknown_cost_conservatively_reserved_rows':[r['run_id'] for r in ledger if r.get('actual_cost_usd') is None]})
    lines=[]
    for k,s in summary['comparisons'].items():
        c=s['counts'];rate='no decisive outcome' if s['decisive_win_rate'] is None else f'{100*s["decisive_win_rate"]:.1f}%'
        lines.append(f'| {k} | {c["Win"]} | {c["Loss"]} | {c["Tie"]} | {c["Uncertain"]} | {c["Failure"]} | {rate} | {100*s["decisive_coverage"]:.1f}% |')
    doc=f'''# PE6201 ViralLoop: Round 2 Experiment Process and Results

## Conclusions first

Round 2 automated generation and independent offline comparison have been actually run. Before Final, the product was frozen by preset rules as **{freeze['selected_product']}**: full brief from real material, simple generation prompt, two candidates, quality screening, fixed-order selection. The internal evaluator did not pass admission, so feedback rewriting and preference-based selection were switched off.

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
'''+ '\n'.join(lines)+f'''

Each comparison covers only 12 tasks. The Wilson intervals are stored in `final_summary_v002.json`; they are conditional intervals for the decisive subsample, not an overall success probability or a real viral rate.

## Generation checks and cost

'''+ '\n'.join(f'- {v}: {m["topics"]} topics, {m["candidates"]} candidates; {m["hard_pass"]}/{m["candidates"]} passed the engineering hard checks, {m["selected"]}/{m["topics"]} qualified drafts selected, candidates average {m["mean_words"]:.1f} English words.' for v,m in metrics.items())+f'''

As of this report, the Round 2 accounted budget is **US${costs()[1]:.6f}**, Round 1 is **US${costs()[0]:.6f}**, and the project total is **US${sum(costs()):.6f}**, below the authorized US$5. The detailed ledger includes failed requests and conservative reservations for unknown costs.

The hard checks and quality scores in the report are still model-engineering screening, not fact certification or genuine user acceptance. E2 and the frozen E4 only perform a historical association audit on new drafts and are not used for selection; their scores are not to be interpreted as real viral probabilities. E4 re-obtained same-specification embeddings for the new drafts, and that cost is written into Round 2 without altering the Round 1 ledger.

## Limitations and critical analysis

- **Popularity confounding has not disappeared.** Posting time, trending events, author, exposure and recommendation distribution can all affect the historical score; the offline text comparison isolates task material and generation conditions but cannot estimate the causal gain of an actual post.
- **Controlled items are not a human gold standard.** The 15/15 external result only means the engineered differences were identified; it must not be written as "100% accuracy in community judgment". The internal information-value failure shows that an overall 12/15 must not mask a single ineffective key dimension.
- **The automated quality score once conflicted with the human opinion.** A dense draft accepted by the automated check was rejected by the author. The simplification goal was set by a human, and automated-generation effects must be read from independent results and must not be replaced by the human-edited draft.
- **Fair comparison has boundaries.** V1 adds a focusing step and V2 adds retrieval, so their cost must be counted; an equal number of candidates does not mean identical call cost. O1's stop strategy of retaining the original produced identity Ties, so the conclusions are limited to this implementation with preference selection switched off.
- **An independent reviewer is not the same as an unbiased one.** The external model is from a different family from the generator and did not take part in selection, but stylistic preference and human construction of the items still have an influence. The 12 genuine human blind-review pairs are not yet complete.
- **Historical material is not current news.** The source is archived author self-reports, so the necessary dates and uncertainties must be retained. Someone else's measurement must not be passed off as first-hand experience, and the model's current performance must not be claimed.
- **There are archive-completeness warnings.** Early on, {len(missing_manifest)} records lacked a complete per-run manifest and {len(missing_raw)} lacked a per-run raw response file. The cost ledger is retained, but the cache does not guarantee every retry can be rebuilt; record gaps must not be written up as "all audits passed".
- **Token control failed.** This round's known cumulative total is {total_tokens:,} tokens, exceeding the internal protocol limit of 1,000,000 tokens. The execution program omitted a pre-call token block; this is not an overspend of the user's US$5 cost cap, but it is a genuine protocol deviation. This round cannot be labelled a confirmatory experiment that fully observed the pre-registered budget, and the old cap will not be rewritten to retroactively legitimize it. Follow-up product controls open a separate version, while the original frozen experiment code and records are retained.

## Deliverables and next steps

The desktop Experiment 1.1 package contains the protocol, real material, briefs, generated candidates, the selection path, the original AB/BA outputs, the cost ledger, grouping and freeze reviews, and a runnable generation page. The product is a fact-constrained community writing assistant and currently does not claim a verified viral outcome.

Remaining evidence: the 12 genuine human Final blind-review pairs; if real interaction improvement is to be tested in the future, this requires separately pre-registering posting-time/topic stratification and random assignment, a fixed observation window, and an actual publish. No real publishing has been performed.
'''
    (LOOP/'round2_experiment_full_process_and_results.md').write_text(doc,encoding='utf-8')
    pd.DataFrame([{'comparison':r['comparison'],'brief_id':r['brief_id'],'outcome':r['outcome']} for p in (LOOP/'results/final_comparisons').glob('*_v002.json') for r in [read(p)]]).to_csv(redirect_write(LOOP/'results/final_comparison_results_v002.csv'),index=False,encoding='utf-8-sig')
    (LOOP/'PROJECT_STATE.md').write_text('# Round 2 status\n\nloop_version: v002\nstate: AUTOMATED_FINAL_COMPLETE_HUMAN_FINAL_PENDING\n\nAutomated generation, Selection freeze and external Final comparison are complete; feedback is switched off. The product is frozen at V0 and was not re-chosen based on Final. There is no genuine human Final or real publishing evidence yet.\n',encoding='utf-8')
    print(json.dumps({'final_metrics':summary['comparisons'],'cost':costs(),'archive_warnings':len(missing_manifest),'all_frozen_code_unchanged':all(frozen_ok.values())}))

if __name__=='__main__':summarize()
