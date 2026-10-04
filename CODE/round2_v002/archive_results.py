"""Offline evidence synthesis after actual runs; never completes missing human or publishing data."""
from runtime import *
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
    frozen_ok={name:sha(LOOP/'code'/name)==h for name,h in freeze['code_hashes'].items()}
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
        c=s['counts'];rate='无决定性结果' if s['decisive_win_rate'] is None else f'{100*s["decisive_win_rate"]:.1f}%'
        lines.append(f'| {k} | {c["Win"]} | {c["Loss"]} | {c["Tie"]} | {c["Uncertain"]} | {c["Failure"]} | {rate} | {100*s["decisive_coverage"]:.1f}% |')
    doc=f'''# PE6201 ViralLoop：第二轮实验过程与结果

## 先看结论

第二轮自动生成和独立离线比较已实际运行。产品在Final前按预设规则冻结为 **{freeze['selected_product']}**：真实素材完整Brief、简单生成提示、两篇候选、质量筛查、固定顺序选稿。内部评测器未通过准入，反馈改写和偏好选稿关闭。

当前证据只支持判断离线写作偏好，**不能证明能生成真实爆款**。真人Final盲评与实际发布结果尚缺；三篇自然度验收不是正式真人效果评测。

## 问题、实验对象与控制

目标是把真实素材写成有具体问题、值得社区讨论的内容，并检验强提示、结构RAG及增加采样是否带来增益。平台为r/LocalLLaMA，素材来自第一轮已清洗的2025年历史Train。第一轮模型不重训，历史Final不重跑。

按来源组隔离：4Tune、2Selection、12Final；另有自然度预览和评测器受控题。两个原Selection来源曾被预览，因此先降级为开发用途，再机械补选两条新Selection来源。Final预分配不变，源文本进入生成过程均发生在产品冻结后。

生成器均使用GPT-4.1-mini，同一任务使用同一完整事实来源，输入不含点赞、评论、score。各方法：

- V0：完整Brief、简单提示，2候选。
- V1：先选一个发帖目的、最多2条必要事实，再用强提示，2候选。事实审核仍读取完整来源。
- V2：V1加历史结构参考，2候选；检索库排除所有已分组来源，只提取写作结构。
- O1：同一V2起稿额外采样3篇，保留原稿。由于偏好选稿器未准入，合格原稿优先保留，不能据此声称增加采样无效。
- O2/V3：按评测器失败停止规则未执行，不能声称反馈优化有效或无效。

## 实际执行过程

1. Jev无可用直连凭证、目录价格无法可靠上界，没有进行付费接入。预先限定两个内部候选，随后没有继续找模型。
2. 生成6篇来源明确的自然度预览，翻译3篇给本人检查。实际反馈：第1篇认可；第2篇因信息密度大拒绝；第3篇认可但注明技术背景难以判断。
3. 两次自动简化仍堆积细节。助手做了一版直接编辑，本人回复“会”，认可其更像正常帖子。该编辑稿不纳入自动生成效果样本。
4. 30对受控题按来源组分成15Calibration和15Validation，每对交换AB/BA。内部Gemini Flash Lite校准较好，但Validation信息价值仅2/5，未达逐维门槛，停止反馈及偏好选稿。外部Claude Haiku在15对受控Validation上符合全部设计预期。
5. 正式Tune做两轮，第一轮输出完整保留。第二轮改为先聚焦再生成，没有使用外部裁判。随后Selection各方案合格任务数均2/2，按并列时优先简单方案的规则冻结V0。两个Selection任务很少，不能把这解释为V0普遍最好。
6. 冻结后在12条新任务生成候选，再由外部Claude做独立比较。AB/BA不同意见合并为Uncertain；相同文本直接记身份Tie并明确不是Judge投票。没有从Final结果反向修改产品。

## Final独立比较结果

Win表示新方法优于旧方法。决定性胜率仅以Win+Loss为分母；覆盖率为(Win+Loss)/12。Uncertain不计半胜。

| 比较 | Win | Loss | Tie | Uncertain | Failure | 决定性胜率 | 决定性覆盖率 |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
'''+ '\n'.join(lines)+f'''

每项只有12个任务。Wilson区间保存在`final_summary_v002.json`，它是决定性子样本的条件区间，不是全体成功概率或真实爆款率。

## 生成检查与成本

'''+ '\n'.join(f'- {v}：{m["topics"]}题、{m["candidates"]}候选；工程硬检查通过{m["hard_pass"]}/{m["candidates"]}，选出合格稿{m["selected"]}/{m["topics"]}，候选平均{m["mean_words"]:.1f}英文词。' for v,m in metrics.items())+f'''

截至此报告，第二轮预算计入 **US${costs()[1]:.6f}**，第一轮 **US${costs()[0]:.6f}**，项目累计 **US${sum(costs()):.6f}**，低于本人授权US$5。详细流水包括失败请求和未知费用的保守预留。

报告中的硬检查和质量分仍是模型工程筛查，不是事实认证或真实用户验收。E2与冻结E4仅对新稿做历史关联审计，不用于选型；其分数不解释为真实爆款概率。E4重新取得新稿的同规格嵌入，费用写入第二轮而不改第一轮流水。

## 局限与批判性分析

- **热度混杂没有消失。** 发布时间、热点、作者、曝光、推荐分发等均可能影响历史score；离线文案比较隔离了任务素材与生成条件，无法估计真实发帖后的因果增益。
- **受控题不是真人金标准。** 15/15外部结果只代表识别了工程设计的差异，不能写“社区判断准确率100%”。内部信息价值失败说明不能把总体12/15掩盖某一关键维度无效。
- **自动质量分与人意见曾冲突。** 自动检查认可的密集稿被本人拒绝。简化目标经人工确定，自动生成效果必须看独立结果，不能用人工编辑稿替代。
- **公平比较有边界。** V1增加聚焦步骤、V2增加检索，费用需计入；候选数相同不等于调用成本完全相同。O1保留原稿的停止策略导致身份Tie，结论限于这套关闭偏好选择的实现。
- **评审独立不等于无偏。** 外部与生成器模型家族不同且未参与选型，但仍会有风格偏好和题目人工构造影响。真人12对盲评尚未完成。
- **历史素材不等于当前新闻。** 来源是归档作者自述，必要日期和不确定性必须保留。不能把别人的测量冒充亲测，不能声称模型当前表现。
- **档案完整性有警告。** 早期{len(missing_manifest)}条缺完整单次manifest、{len(missing_raw)}条缺单次原始响应文件。费用流水保留，缓存不保证重建每次重试；不把记录缺口写成全部审核通过。
- **Token控制失败。** 本轮已知累计{total_tokens:,} Token，超过内部协议100万Token限额。执行程序漏掉调用前Token阻断；不是用户US$5费用上限超支，但属于真实协议偏差。本轮不能标为完全遵守预注册预算的确认性实验，不改写旧上限来追认。后续产品控制另开版本，原冻结实验代码与记录保留。

## 可交付与下一步

桌面实验1.1版含协议、真实素材、Brief、生成候选、选择路径、AB/BA原输出、费用流水、分组与冻结审核，以及可运行的生成页面。产品为事实约束社区写作辅助，当前不宣称已验证爆款。

剩余证据：由真人完成12对Final盲评；若未来检验真实互动提升，需另外预注册发布时间/主题分层与随机分配、固定观察窗口并进行真实发布。当前没有执行真实发布。
'''
    (ROOT/'第二轮实验_完整过程与结果.md').write_text(doc,encoding='utf-8')
    pd.DataFrame([{'comparison':r['comparison'],'brief_id':r['brief_id'],'outcome':r['outcome']} for p in (LOOP/'results/final_comparisons').glob('*_v002.json') for r in [read(p)]]).to_csv(LOOP/'results/final_comparison_results_v002.csv',index=False,encoding='utf-8-sig')
    (ROOT/'PROJECT_STATE.md').write_text('# 第二轮状态\n\nloop_version: v002\nstate: AUTOMATED_FINAL_COMPLETE_HUMAN_FINAL_PENDING\n\n自动生成、Selection冻结与外部Final比较完成；反馈关闭。产品冻结V0，未据Final改选。尚无真人Final和真实发布证据。\n',encoding='utf-8')
    print(json.dumps({'final_metrics':summary['comparisons'],'cost':costs(),'archive_warnings':len(missing_manifest),'all_frozen_code_unchanged':all(frozen_ok.values())}))

if __name__=='__main__':summarize()
