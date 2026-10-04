"""Chinese review wording and per-response language metadata; no model-score reveal."""
from common import *
def main():
    p=ROOT/'web/blind.html';s=p.read_text(encoding='utf-8')
    s=s.replace('<h1>真人盲评</h1>','<h1>真人盲评 · 中文译文</h1>')
    s=s.replace('先看事实素材，再比较 A/B。','英文原稿已逐段翻译为中文，保留数字、限定和段落，不替任何版本润色。先看事实素材，再比较 A/B。')
    s=s.replace('结果只是小规模偏好检查。','结果只是小规模内容偏好检查，不用于验证原英文的语言流畅性。')
    s=s.replace("['clickbait','更标题党（越少越好）']","['clickbait','哪份标题党更严重（选风险更高的一份）']")
    s=s.replace("({case_id:c.id,...Object.fromEntries", "({case_id:c.id,review_language:c.review_language||'en',...Object.fromEntries")
    p.write_text(s,encoding='utf-8')
if __name__=='__main__':main()
