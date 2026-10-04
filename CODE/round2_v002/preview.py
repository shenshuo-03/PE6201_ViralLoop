"""Real naturalness audit, Chinese review artifact and genuine response collection."""
from evaluator import *
def main():
    cases=read(LOOP/'results/naturalness_previews_v002.json');checked=[]
    for row in cases:
        b=row['brief'];p=row['draft'];file=LOOP/'results'/f'naturalness_quality_{b["id"]}_v002.json'
        if file.exists():q=read(file)
        else:
            js,u=quality(b,[p],'naturalness:'+b['id'],'naturalness');q={'judgment':js[0],'usage':u};write(file,q)
        text=p['title']+' '+p['body']
        manual_flags=[]
        if re.search(r"\b(?:I've found|I have found|I haven't located|I tested|I've tested|my tests|my measurements|I measured)\b",text,re.I):manual_flags.append('First-person source-author research/testing cannot be attributed to reader speaker')
        if '2025' in b.get('source_date','') and re.search(r'\brecent\b',text,re.I) and '2025' not in text:manual_flags.append('2025 archive cannot be described as a recent test in 2026')
        if manual_flags:
            q['judgment']['hard_pass']=False;q['judgment']['unsupported_claims']+=manual_flags
        if not q['judgment']['hard_pass']:
            repair=LOOP/'results'/f'naturalness_repair_{b["id"]}_v002.json'
            if repair.exists():fixed=read(repair)
            else:
                prompt=BASE_PROMPT+STRONG+'Produce exactly ONE draft. Repair factual/identity issues in the current draft; preserve real source facts, do not fabricate new evidence.\n'+json.dumps({'brief':b,'source':read(LOOP/'sources'/f'{b["id"]}_v002.json'),'current_draft':p,'audit':q['judgment']},ensure_ascii=False)
                ans=complete(prompt,GEN,'naturalness:'+b['id']+':fact_repair',1100,'naturalness',.2);fixed={'draft':ans['value']['drafts'][0],'usage':ans['usage']};write(repair,fixed)
            p=fixed['draft'];js,u=quality(b,[p],'naturalness:'+b['id']+':repaired','naturalness');q={'judgment':js[0],'usage':u};write(LOOP/'results'/f'naturalness_quality_repaired_{b["id"]}_v002.json',q)
            event('naturalness','fact repair made before human gate; original preserved',{'id':b['id'],'pass':q['judgment']['hard_pass']})
        checked.append({'brief':b,'draft':p,'quality':q['judgment'],'human_accepted':False})
    write(LOOP/'results/naturalness_checked_v002.json',checked)
    automatic=all(x['quality']['hard_pass'] for x in checked) and sum(x['quality']['quality_pass'] for x in checked)>=5
    write(LOOP/'results/naturalness_gate_v002.json',{'automatic_pass':automatic,'hard_pass_count':sum(x['quality']['hard_pass'] for x in checked),'quality_pass_count':sum(x['quality']['quality_pass'] for x in checked),'n':len(checked),'human_pass':False,'formal_generator_stage_allowed':False,'rule':'All hard pass and at least 5/6 fit,specificity,information>=3; real user acceptance required','source_based_not_human_ground_truth':True})
    # One per type: these are a usability gate, never formal final human results.
    chosen=[next(x for x in checked if x['brief']['id']==bid) for bid in ['D01','D03','S01']]
    translated=[]
    for row in chosen:
        b=row['brief'];p=row['draft'];out=LOOP/'results'/f'naturalness_zh_{b["id"]}_v002.json'
        if out.exists():zh=read(out)
        else:
            prompt='''Translate this real draft into clear simplified Chinese for user review. Do not improve, add or remove claims. Preserve all numbers/model names, source attribution and uncertainty. Return JSON {"title_zh":"...","body_zh":"...","brief_goal_zh":"..."}. No invented experiences or additional advice.\n'''+json.dumps({'title':p['title'],'body':p['body'],'brief_goal':b['problem_or_goal']},ensure_ascii=False)
            ans=complete(prompt,INTERNALS[0],'translate:naturalness:'+b['id'],1800,'naturalness');zh=ans['value'];write(out,zh)
        nums=lambda t:sorted(re.findall(r'\d+(?:\.\d+)?',t))
        translation_numbers_preserved=nums(p['title']+' '+p['body'])==nums(zh['title_zh']+' '+zh['body_zh'])
        translated.append({'id':b['id'],'type':b['content_type'],'brief_goal_zh':zh['brief_goal_zh'],'source_url':b['source_url'],'source_date':b['source_date'],'title_zh':zh['title_zh'],'body_zh':zh['body_zh'],'title_en':p['title'],'body_en':p['body'],'numeric_check':translation_numbers_preserved})
    write(LOOP/'evals/naturalness_user_review_v002.json',translated)
    doc='# 实验1.1：三篇真实素材样例，请验收自然度\n\n这不是正式盲评。只需判断是否像真实社区里值得发布的内容；可指出哪一篇最需要改。来源是2025年归档用户报告，不是你本人的实测经历。中文是忠实翻译，英文是发布稿。\n'
    for i,x in enumerate(translated,1):
        doc+=f'\n## 样例{i}：{x["title_zh"]}\n\n类型：{x["type"]}；来源日期：{x["source_date"]}\n\n任务：{x["brief_goal_zh"]}\n\n{x["body_zh"]}\n\n[素材原帖]({x["source_url"]})\n\n<details><summary>英文原文</summary>\n\n{x["title_en"]}\n\n{x["body_en"]}\n\n</details>\n'
    doc+='\n## 请反馈\n\n这三篇是否自然、有具体信息、值得发布？若不满意，指出样例编号和最明显的问题即可。不要因为系统已生成就迁就它。未收到你的验收前，不启动正式生成比较或Final。\n'
    (ROOT/'三篇真实素材样例_请验收.md').write_text(doc,encoding='utf-8')
    write(LOOP/'results/cost_summary_v002.json',{'prior_usd':costs()[0],'round_usd':costs()[1],'total_usd':sum(costs()),'cap_usd':5,'round_cap_usd':2,'calls':len(rows(LEDGER))})
    event('naturalness','Chinese review package ready; gate pending real user',{'automatic_pass':automatic,'numeric_translation_checks':[x['numeric_check'] for x in translated]})
if __name__=='__main__':main()
