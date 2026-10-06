"""Deployment-only UI defaults from the already frozen practical model choice."""
from common import *
def main():
    p=ROOT/'web/index.html';s=p.read_text(encoding='utf-8')
    s=s.replace('Generate','<label>Generation method<select id="liveVariant"><option value="G0_generic" selected>G0 generic generation (practical default)</option><option value="G1_prompt">G1 Prompt</option><option value="G3_rag">G3 RAG</option><option value="G4_both">G4 positive and negative pattern RAG</option></select></label><label><input type="checkbox" id="doOptimize" style="width:auto"> Add one feedback rewrite (experiments have not shown it beats extra sampling)</label><br><button id="live">Generate</button>')
    s=s.replace("content_type:$('newType').value,facts:","content_type:$('newType').value,variant:$('liveVariant').value,optimize:$('doOptimize').checked,facts:")
    s=s.replace("text('h3',r.original_retained?'Original retained':'Revised',$('liveResult'));draftCard(r.final,$('liveResult'));","if(r.optimization_requested){text('h3',r.original_retained?'Original retained':'Revised',$('liveResult'));draftCard(r.final,$('liveResult'));}")
    p.write_text(s,encoding='utf-8')
if __name__=='__main__':main()
