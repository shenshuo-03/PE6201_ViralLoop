"""Readable course report PDF from the actual Markdown, with evidence figures."""
from common import *
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from xml.sax.saxutils import escape
import re
def main():
    p=ROOT/'submission/report.md';text=p.read_text(encoding='utf-8')
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='VLTitle',fontName='Helvetica-Bold',fontSize=19,leading=23,textColor=colors.HexColor('#143b6b'),spaceAfter=14));styles.add(ParagraphStyle(name='VLHead',fontName='Helvetica-Bold',fontSize=12,leading=16,spaceBefore=13,spaceAfter=6));styles.add(ParagraphStyle(name='VLBody',fontName='Helvetica',fontSize=10.5,leading=14.3,spaceAfter=8));styles.add(ParagraphStyle(name='VLSource',fontName='Helvetica',fontSize=8.5,leading=11.5,spaceAfter=5))
    story=[]
    for block in text.split('\n\n'):
        block=block.strip()
        if not block:continue
        block=block.replace('–','-').replace('—','-').replace('’',"'")
        if block.startswith('# '):story.append(Paragraph(escape(block[2:]),styles['VLTitle']))
        elif block.startswith('## '):story.append(Paragraph(escape(block[3:]),styles['VLHead']))
        elif block.startswith('- '):
            for line in block.splitlines():story.append(Paragraph(escape(line[2:]),styles['VLSource']))
        else:story.append(Paragraph(escape(block),styles['VLBody']))
    wc=json.loads((ROOT/'submission/report_word_count.json').read_text(encoding='utf-8'))
    story.append(Spacer(1,10));story.append(Paragraph(f"Main report: {wc['main_words']} words (references excluded). Draft pending genuine human review and author verification.",styles['VLSource']))
    story.append(PageBreak());story.append(Paragraph('Appendix: executed evidence',styles['VLHead']))
    for name,caption in [('historical_evaluator_AP.png','Historical evaluation: 348 held-out posts.'),('generator_proxy_and_quality.png','Generation: 10 frozen hypothetical briefs; scores are proxies.')]:
        path=ROOT/'results/figures'/name
        if path.exists():
            from PIL import Image as PILImage
            w,h=PILImage.open(path).size;story.append(Image(str(path),width=480,height=480*h/w));story.append(Paragraph(caption,styles['VLSource']));story.append(Spacer(1,8))
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#657381'));canvas.drawString(48,27,'PE6201 - ViralLoop experiment 1.0 | No real platform uplift claimed');canvas.drawRightString(A4[0]-48,27,str(doc.page))
    pdf=ROOT/'submission/report.pdf';SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=45,bottomMargin=44,title='PE6201 ViralLoop experimental report',author='Shen Shuo (draft for review)').build(story,onFirstPage=footer,onLaterPages=footer)
    print('PDF',pdf,flush=True)
if __name__=='__main__':main()
