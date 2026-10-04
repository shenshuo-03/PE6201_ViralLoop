"""Deployment repair: avoid machine-reserved port 8765; experiment outcomes unchanged."""
from common import *
def main():
    for name in ['src/server.py','run.ps1','README.md','submission/demo_script.md']:
        p=ROOT/name;s=p.read_text(encoding='utf-8').replace('8765','8877');p.write_text(s,encoding='utf-8')
if __name__=='__main__':main()
