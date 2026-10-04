"""Resume after development numeric-guard amendment, without repeating historic test."""
from common import *
from run_remaining import freeze_generators,execute
def main():
    for p in [ROOT/'results/FINAL_TEST_COMPLETED.json',ROOT/'results/judge_classifier/FINAL_COMPLETED.json']:
        if not p.exists():raise RuntimeError('Historical frozen tests must finish first')
    freeze_generators()
    execute('harness.py','--stage','final_test')
    execute('upworthy_transfer.py')
    write_json(ROOT/'results/RUN_STATE.json',{'at':now(),'status':'automated_experiments_completed','human_review':'pending genuine user input','face_video':'pending user recording'})
if __name__=='__main__':main()
