"""Deployment-only UI defaults from the already frozen practical model choice."""
from common import *
def main():
    p=ROOT/'web/index.html';s=p.read_text(encoding='utf-8')
    s=s.replace('<button id="live">真实生成并优化</button>','<label>生成方法<select id="liveVariant"><option value="G0_generic" selected>G0 通用生成（实用默认）</option><option value="G1_prompt">G1 Prompt</option><option value="G3_rag">G3 RAG</option><option value="G4_both">G4 正负模式 RAG</option></select></label><label><input type="checkbox" id="doOptimize" style="width:auto"> 附加一次反馈改写（实验尚未证明优于多采样）</label><br><button id="live">真实生成</button>')
    s=s.replace("content_type:$('newType').value,facts:","content_type:$('newType').value,variant:$('liveVariant').value,optimize:$('doOptimize').checked,facts:")
    s=s.replace("text('h3',r.original_retained?'保留原稿':'优化结果',$('liveResult'));draftCard(r.final,$('liveResult'));","if(r.optimization_requested){text('h3',r.original_retained?'保留原稿':'优化结果',$('liveResult'));draftCard(r.final,$('liveResult'));}")
    p.write_text(s,encoding='utf-8')
if __name__=='__main__':main()
