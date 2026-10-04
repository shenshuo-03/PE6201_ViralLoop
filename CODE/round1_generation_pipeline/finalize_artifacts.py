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
    md=f'''# ViralLoop 实验1.0：真实结果与结论

## 完成范围

全量审计、清洗/去重/类型规则、400条上游审计、2,800条有限恢复、2,336条数据冻结、完整评测器阶梯、12张正负模式卡、生成器阶梯/消融、一次反馈对照、成本与失败日志、可运行本地界面均已实际执行。最终生成实验：**10主题、{len(fc)}份候选**；开发主题与最终主题分开。

**尚未完成且未伪造**：真人12组盲评、露脸视频录制、实际平台随机A/B和传播表现。英文报告目前为可审阅草稿，必须保留这些边界。

## 1. 数据与控制变量

400条审计全返回，95.75%位于36–38小时；score与观察时间来自同一源记录。原始100,679条，规则候选20,019；分层随机恢复2,800，最终2,336。Train1396/Tune398/Selection194/Test348。

保留低、零、负分。没有曝光数据，不能把文本关联当因果。作者可用历史仅{int((observations.author_prior_missing==0).sum())}/{len(observations)}，缺失率较高。初次捕获中位{first_age.median()*3600:.1f}秒，{int(first_age.gt(1).sum())}条超过1小时，最大{first_age.max():.2f}小时；正文发布瞬间状态仍有不确定性。标签是同月同类型回顾性相对排名，不是实时可知的绝对热度阈值。

## 2. 历史评测器：完整348条最终测试

{table(e,['model','precision','recall','f1','average_precision','brier'])}

文本E2的AP={by['E2_tfidf'].average_precision:.3f}，严格上下文E1为{by['E1_context_only'].average_precision:.3f}，说明历史文本确有增量预测信号；**不能证明是表达而非主题、新闻和隐含作者因素造成**。真实语义模型AP={by['E4_semantic'].average_precision:.3f}，Brier={by['E4_semantic'].brier:.3f}；服务侧本地E2仍有无API调用、快和可解释的优势。E3开发表现好但最终AP未超过E2，说明增加上下文并非必然提升跨时间泛化。

作者聚类bootstrap：E2−先验AP区间{boot['ci95']['E2_minus_prior']}；E3−E1区间{boot['ci95']['E3_minus_E1']}。区间条件于保留月份，不能覆盖全部未来变化。

## 3. LLM Judge：相同80条子样本

{table(match,['model','n','precision','recall','f1','average_precision'])}

该随机80条只有11条正类（13.75%），与完整测试24.71%不同；因此用上表同一子样本比较，不能与完整348条混排。零样本/Few-shot/RAG Judge都真实执行；“Jev”未被提供具体模型，不冒称部署了独立奖励模型。小样本与阈值漂移限制结论。

## 4. 生成器与质量约束

相同模型与事实素材，G0/G1/G2/G3/G4-positive/G4-both每主题2稿；O1无反馈追加3稿，O2按本地评分/模式反馈改3稿；相同3600-token输出上限，实际tokens与费用分别记录。

{table(gs,['variant','topics','coverage','mean_selected_performance','mean_selected_quality','mean_selected_clickbait'])}

这是明确假设素材上的代理指标；潜力分都不能读作爆款概率。对拒答主题，平均选择分只包含合格输出，所以必须同时看coverage。独立Judge未向改写器提供评分理由；仍可能和生成器共享偏差，需要真人补检。

反馈O2−多采样O1的共同合格主题平均代理差值 **{o.mean_delta:+.5f}**，主题bootstrap95%区间 [{o.ci95_low:+.5f}, {o.ci95_high:+.5f}]，n={int(o.paired_topics)}。{'区间跨0，暂不能认为反馈优于多采样。' if o.ci95_low<=0<=o.ci95_high else '区间在该小样本内未跨0，但仍是探索性代理结果，不代表真实传播提升。'}

正负模式G4-both−仅正模式的代理差值{pn.mean_delta:+.5f}，区间[{pn.ci95_low:+.5f},{pn.ci95_high:+.5f}]；不能因为有更多规则就默认更好。模式卡在Train做BH校正，在Tune仅验证方向，不冒称所有开发p值显著。

## 5. 最强与最划算

最终测试之前，Selection Dev已冻结：代理效果候选 **{freeze['best_performance_selection']}**；实际采用候选 **{freeze['best_practical_selection']}**。Selection只有2主题，选择本身很不稳定，不能包装成大规模最优结论。最终全版本结果照实保留，不按最终成绩重新改选型规则。

目前产品应以忠实事实与清晰表达为核心；高级RAG/模式/闭环只是实验可选流程。只有真人评审和真实发布后实验进一步支持时，才能提高对“内容表现优化”的产品承诺。

## 6. 成本与失败

全部调用预算计入 **US${cost['budget_accounted_usd']:.5f} / US$5**；有明确usage.cost的实付合计 **US${cost['known_actual_cost_usd']:.5f}**；{cost['unknown_charge_calls']}次缺费用字段的请求按保守上限占用预算，不能把估计装成精确结算。台账含开发调用、失败和修正，详见api_ledger/cost_results。

质量控制在30条受控变异（6组同一素材，非30个独立开放世界样本）上检出Precision={cal['precision_invalid']:.3f}/Recall={cal['recall_invalid']:.3f}。这只能说明这些预设事实错误被抓到，不是证明质量Judge准确率100%。

真实失败包含：素材外数字、虚构建议被误写为事实、JSON截断、HTTP200内部provider error、事实引用误伤和软模式过度约束。开发规则修正及旧结果完整归档。没有为了展示闭环改善而删除保留原稿或失败主题。

## 7. 可选Upworthy外部迁移

真实跑了Reddit标题模型到Upworthy相同实验/图片/lede/excerpt的CTR排序：{up['n_experiments']}个实验，非并列{up['non_tie_n']}，准确率{up['pairwise_accuracy']:.3f}，随机基线0.5。未用Upworthy调参；排除官方指出的非随机时段。观察CTR仍有抽样噪声，域/时间/体裁差距大；不是完整Reddit帖或真实爆款证据。

## 8. 用户只需补什么

1. 打开本地 `/blind`，完成12组A/B/Tie真实评价（8组G4对G0，4组反馈对多采样，分开汇总）。
2. 审阅报告中的假设素材、负结果和结论边界。
3. 按Demo脚本录制5分钟左右本人露脸＋屏幕视频并自己提交。

这已经达到实验执行阈值。下一版优先补真实素材与真人/平台反馈，不继续堆Agent、微调和多平台复杂度。
'''
    write_md(ROOT/'results/实验结果与结论.md',md)
    audit_path=ROOT/'results/independent_generation_audit_comparisons.csv'
    if audit_path.exists():
        audit=pd.read_csv(audit_path)
        ar=audit[audit.a.eq('O2_feedback')&audit.b.eq('O1_resample')&audit.metric.eq('audit_score')].iloc[0]
        addon=f'\n## 9. 第二性能模型的独立复核（探索性后验分析）\n\n冻结的E4语义模型只做审计，没有向生成/改写提供反馈。对178份独立文本（180候选中有2份缓存共用文本）复核后，反馈−多采样的独立潜力分差值为{ar.mean_delta:+.5f}，95%主题区间[{ar.ci95_low:+.5f},{ar.ci95_high:+.5f}]。优化器和审计器均未证明反馈更优；不能把微小本模型升分写成传播收益，也不能凭两模型分歧就认定已经证明奖励投机。详见independent_generation_audit文件。\n\nselected_model_attributions.json另保存线性模型的真实logit贡献；系数体现词项/主题关联，不是因果修改建议。\n'
        write_md(ROOT/'results/实验结果与结论.md',md+addon)
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
    write_md(ROOT/'submission/demo_script.md',f'''# Demo脚本：约5分钟，真实本人露脸＋屏幕

视频录制由本人完成；AI不能代替本人露脸。不要展示API密钥。只播放真实运行记录时明确说“实验证据回放”；点击实时生成时明确说明真实调用模型。

## 0:00–0:40 问题与边界
介绍固定事实写技术社区内容，目标是比较生成策略和独立评测；不能承诺真实爆款率。

## 0:40–1:30 数据与历史模型
展示2336条冻结数据、36–38h恢复证据、时间分区。展示图：文本AP{by['E2_tfidf'].average_precision:.3f}、语义AP{by['E4_semantic'].average_precision:.3f}，lazy正类F1=0。解释主题/曝光混杂仍在。

## 1:30–3:15 产品闭环
打开localhost:8765，选一个真实完成的T主题。先看Facts，说明假设素材；比较G0、G4-both、O1、O2。展示全部候选、约束失败、分数/质量和保留原稿。若演示实时生成，准备2条简短事实；不要在录像里等待超过预算或保证会升分。

## 3:15–4:10 实验对比
展示10个主题结果与反馈对多采样差值{o.mean_delta:+.5f}及区间。解释“更复杂并非一定更好”，选择{freeze['best_practical_selection']}的务实理由。真人盲评未完成时明确说尚待补，不编结果。

## 4:10–5:00 取舍与局限
展示成本计入${cost['budget_accounted_usd']:.5f}、失败分类、没有Agent/微调的理由、未来真实读者验证。结尾说明README可复现；报告/evals/数据已透明保存。
''')
    write_md(ROOT/'docs/reflection.md',f'''# 实验反思

已验证：历史文本存在相对表现预测信号，完整保留月份E2 AP={by['E2_tfidf'].average_precision:.3f}，真实语义={by['E4_semantic'].average_precision:.3f}。

未验证：表达形式的因果收益、生成稿真实互动、独立曝光归一化、完整作者声誉、多人盲评、大规模稳定策略。

复杂度：上下文并不必然提高测试AP；RAG/模式未保证生成效果更好；反馈和多采样必须同一起稿同预算比。将大量例子和统计卡放进Prompt也可能引入事实、降低多样性或混淆目标。

评测风险：质量规则误伤F编号在开发阶段已修正；未知数字规则仍保守，可能拒绝合法数量描述。独立模型可能共有偏差。窄范围合成事实检查不是开放世界100%准确率。10主题bootstrap只作探索。

下一步：真实作者素材、真实人评审、只控制输入事实的编辑对照；具备读者流量才做随机曝光AB。暂不扩Agent/微调/多平台。
''')
    print('ARTIFACTS report words',words,'final drafts',len(fc),'budget',spent(),flush=True)
if __name__=='__main__':main()
