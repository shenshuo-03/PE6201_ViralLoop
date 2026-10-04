"""Faithful Chinese access version for genuine user review; original drafts frozen.

Chinese review is not validation of English fluency. Translate both sides with
identical instructions, no version/score information, preserve mistakes/hedges.
"""
from common import *
from model_api import complete,GENERATOR
import re,collections
def numeric(text):return collections.Counter(re.findall(r'\d+(?:\.\d+)?',text))
def main():
    cases=json.loads((ROOT/'evals/human_blind_cases.json').read_text(encoding='utf-8'))
    write_json(ROOT/'evals/human_blind_cases_en.json',cases);translations=[];checks=[]
    for case in cases:
        prompt='''Translate this blinded evaluation case into Simplified Chinese faithfully.
Do NOT improve, rewrite, shorten, correct mistakes, add facts, strengthen arguments,
or remove awkward repetition, uncertainty or caveats. Preserve paragraph structure,
all numeric expressions, units, fact IDs such as F1, and hypothetical status. Translate
both A and B using exactly the same standard. Keep technical terms understandable.
Do not infer model/version identities. Translate topic, each fact text, A/B titles
and bodies. Return the SAME JSON structure with id/topic_id and every fact id/status
unchanged. Output JSON only.\n'''+json.dumps(case,ensure_ascii=False)
        answer=complete(prompt,model=GENERATOR,max_tokens=3000,tag='human_blind_translation:'+case['id'],temperature=0)
        zh=answer['value'];zh['id']=case['id'];zh['topic_id']=case['topic_id']
        for side in ['A','B']:
            ok=numeric(case[side]['title']+' '+case[side]['body'])==numeric(zh[side]['title']+' '+zh[side]['body'])
            checks.append({'case_id':case['id'],'side':side,'numeric_and_reference_count_preserved':ok})
            if not ok:raise ValueError('Translation changed numeric expression for '+case['id']+side)
        if [f['id'] for f in zh['facts']]!=[f['id'] for f in case['facts']]:raise ValueError('Translation changed fact ids')
        zh['review_language']='zh-CN';zh['translation_note']='Faithful Chinese access translation; originals retained; no English-fluency validation'
        translations.append(zh);print('TRANSLATED',case['id'],flush=True)
    write_json(ROOT/'evals/human_blind_cases_zh.json',translations);write_json(ROOT/'results/blind_translation_checks.json',{'at':now(),'checks':checks,'not_checked':'numeric equality does not prove complete translation fidelity; user may compare original; translator instructed not to polish','review_language':'Chinese translated content, not original English fluency'})
    # Default public review package Chinese, immutable English counterpart kept.
    write_json(ROOT/'evals/human_blind_cases.json',translations)
if __name__=='__main__':main()
