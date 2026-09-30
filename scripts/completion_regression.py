"""Repeat a declared development fixture; never substitute for held-out validation."""
import argparse
import json
from pathlib import Path
from scripts.v2_acceptance import ROOT, audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', default='go-shell')
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 10:
        parser.error('repeats must be 1..10')
    cases = json.loads((ROOT/'benchmark/ground_truth.json').read_text())
    case = next((c for c in cases if c['id'] == args.case), None)
    if case is None:
        parser.error('unknown ground truth case')
    if args.output.exists():
        parser.error('output already exists; preserve earlier results')
    records = []
    for _ in range(args.repeats):
        records.append(audit(case))
        args.output.write_text(json.dumps({'case': args.case, 'records': records}, indent=2))


if __name__ == '__main__':
    main()
