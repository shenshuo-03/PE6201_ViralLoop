"""Shared paths, deterministic IO and reproducibility helpers; no credentials saved."""
import sys, json, hashlib, datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parent/'work'
sys.path.insert(0,str(ROOT/'vendor_runtime'))
sys.path.insert(0,str(WORK/'experiment_libs'))
sys.path.insert(1,str(WORK/'audit_libs'))
SEED=6201
RAW_FILE=ROOT/'data/raw/LocalLLaMA.parquet'
if not RAW_FILE.exists():RAW_FILE=WORK/'LocalLLaMA.parquet'
def write_json(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(x):return hashlib.sha256(x.encode()).hexdigest()
