"""Shared paths, deterministic IO and reproducibility helpers; no credentials saved."""
import sys, json, hashlib, datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _packaged_paths import round1_root, redirect_write
# ROOT is this round's working directory.  _packaged_paths.RoundPaths maps each
# logical sub-path ("data/...", "configs/...", "results/...") onto wherever this
# submission package stores that artefact, so the frozen code runs from the
# package unchanged.  See CODE/_packaged_paths.py for the exact mapping.
ROOT=round1_root()
WORK=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor_runtime'))
sys.path.insert(0,str(WORK/'experiment_libs'))
sys.path.insert(1,str(WORK/'audit_libs'))
SEED=6201
RAW_FILE=ROOT/'data/raw/LocalLLaMA.parquet'
if not RAW_FILE.exists():RAW_FILE=WORK/'LocalLLaMA.parquet'
def write_json(path,obj):
    # A reproduction must not overwrite the frozen evidence this report cites;
    # redirect_write sends any such write into the round's reproduced_run/ folder.
    path=redirect_write(Path(path));path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(x):return hashlib.sha256(x.encode()).hexdigest()
