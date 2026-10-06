"""Review wording and per-response language metadata; no model-score reveal."""
from common import *
def main():
    p=ROOT/'web/blind.html';s=p.read_text(encoding='utf-8')
    s=s.replace('<h1>Human blind review</h1>','<h1>Human blind review</h1>')
    s=s.replace('Read the facts first, then compare A and B.','Read the facts first, then compare A and B.')
    s=s.replace('This is only a small-scale preference check.','This is only a small-scale content preference check and does not validate the fluency of the English original.')
    s=s.replace("['clickbait','More clickbait (fewer is better)']","['clickbait','Which is more clickbait (choose the riskier one)']")
    s=s.replace("({case_id:c.id,...Object.fromEntries", "({case_id:c.id,review_language:c.review_language||'en',...Object.fromEntries")
    p.write_text(s,encoding='utf-8')
if __name__=='__main__':main()
