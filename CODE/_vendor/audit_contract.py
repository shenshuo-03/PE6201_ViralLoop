"""Check declared contract/manifest evidence. Does not independently verify logs."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def load(path):
    raw = Path(path).read_bytes()
    text = raw.decode('utf-8-sig')
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml
        except ImportError as exc:
            raise ValueError('Use JSON-compatible YAML or an existing PyYAML runtime') from exc
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError('Root must be an object')
    return value, hashlib.sha256(raw).hexdigest()


def get(obj, key):
    for part in key.split('.'):
        if not isinstance(obj, dict) or part not in obj:
            return None
        obj = obj[part]
    return obj


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def audit(contract, manifest, contract_hash, prior=()):
    issues = []
    def issue(level, field, detail):
        issues.append({'level': level, 'field': field, 'detail': detail})
    cfg = contract.get('audit')
    if not isinstance(cfg, dict):
        cfg = {}
        issue('FAIL', 'audit', 'Missing audit configuration')
    for field in ('expected', 'required_fields', 'required_checks', 'allowed_phases', 'allowed_variants', 'per_run_limits', 'cycle_limits'):
        if not cfg.get(field):
            issue('FAIL', field, 'Missing or empty contract rule')
    for field in cfg.get('required_fields', []):
        if get(manifest, field) is None or get(manifest, field) == '':
            issue('UNKNOWN', field, 'Required evidence missing')
    for field, expected in cfg.get('expected', {}).items():
        if expected is None:
            issue('FAIL', field, 'Unresolved contract expectation')
        elif get(manifest, field) != expected:
            issue('FAIL', field, 'Expected/actual mismatch')
    if manifest.get('contract_sha256') != contract_hash:
        issue('FAIL', 'contract_sha256', 'Contract hash mismatch')
    for field, rule in [('phase', 'allowed_phases'), ('variant_id', 'allowed_variants')]:
        if manifest.get(field) not in cfg.get(rule, []):
            issue('FAIL', field, 'Value not allowed')
    checks = manifest.get('integrity_checks', {})
    if not isinstance(checks, dict):
        checks = {}
    for name in cfg.get('required_checks', []):
        value = checks.get(name)
        if value is False or value == 'FAIL':
            issue('FAIL', name, 'Integrity check failed')
        elif value is not True and value != 'PASS':
            issue('UNKNOWN', name, 'Integrity check not established')
    events = manifest.get('access_events')
    if not isinstance(events, list) or not events:
        issue('UNKNOWN', 'access_events', 'No complete access evidence')
        events = []
    for event in events:
        if not isinstance(event, dict) or any(not event.get(k) for k in ('split', 'purpose', 'time', 'evidence')):
            issue('UNKNOWN', 'access_events', 'Incomplete access event')
            continue
        split, purpose = event['split'], event['purpose']
        if split in cfg.get('forbidden_splits', []) or purpose in cfg.get('forbidden_purposes_by_split', {}).get(split, []):
            issue('FAIL', 'access_events', 'Forbidden split/purpose accessed')
        if split == cfg.get('final_split', 'final'):
            if manifest.get('phase') != 'final' or manifest.get('freeze_verified') is not True or manifest.get('final_unexposed_before_run') is not True:
                issue('FAIL', 'final', 'Final access lacks final phase/freeze/unexposed evidence')
    totals = {}
    runs = list(prior) + [manifest]
    ids = set()
    for run in runs:
        if not run.get('run_id') or run['run_id'] in ids:
            issue('FAIL', 'run_id', 'Missing/duplicate cycle run ID')
        ids.add(run.get('run_id'))
        if run.get('cycle_id') != manifest.get('cycle_id') or run.get('currency') != manifest.get('currency'):
            issue('FAIL', 'cycle', 'Prior runs have different cycle/currency')
    for field, limit in cfg.get('per_run_limits', {}).items():
        value = get(manifest, field)
        if not number(limit):
            issue('FAIL', field, 'Unresolved/invalid contract cap')
        elif not number(value):
            issue('UNKNOWN', field, 'Invalid/missing actual usage')
        elif value > limit:
            issue('FAIL', field, 'Per-run cap exceeded')
    for field, limit in cfg.get('cycle_limits', {}).items():
        values = [get(run, field) for run in runs]
        if not number(limit):
            issue('FAIL', field, 'Invalid cycle cap')
        elif any(not number(v) for v in values):
            issue('UNKNOWN', field, 'Incomplete cycle usage')
        else:
            totals[field] = sum(values)
            if totals[field] > limit:
                issue('FAIL', field, 'Cycle cap exceeded')
    verdict = 'FAIL' if any(i['level'] == 'FAIL' for i in issues) else 'WARN' if issues else 'PASS'
    return {'verdict': verdict, 'usable_for_claims': verdict == 'PASS', 'contract_sha256': contract_hash,
            'run_id': manifest.get('run_id'), 'issues': issues, 'cycle_totals': totals,
            'scope': 'Logged conformance only; raw evidence checks remain harness responsibilities'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('contract')
    parser.add_argument('manifest')
    parser.add_argument('--prior-manifest', action='append', default=[])
    parser.add_argument('--output')
    args = parser.parse_args()
    try:
        contract, contract_hash = load(args.contract)
        manifest, manifest_hash = load(args.manifest)
        prior = [load(p)[0] for p in args.prior_manifest]
        result = audit(contract, manifest, contract_hash, prior)
        result['manifest_sha256'] = manifest_hash
    except (ValueError, OSError, TypeError, AttributeError) as exc:
        result = {'verdict': 'FAIL', 'usable_for_claims': False, 'error': str(exc)}
    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output + '\n', encoding='utf-8')
    print(output)
    return 0 if result['verdict'] == 'PASS' else 2 if result['verdict'] == 'FAIL' else 1


if __name__ == '__main__':
    raise SystemExit(main())
