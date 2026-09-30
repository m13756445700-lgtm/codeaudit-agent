"""Offline adjudication template and paired summaries; never fabricates reviewer labels."""
import argparse
import json
from collections import defaultdict
from pathlib import Path


def review_campaign(directory, reviews=None):
    plan = json.loads((directory/'plan.json').read_text())
    path = directory/'results.jsonl'
    records = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    by_job = {r['job_index']: r for r in records}
    if len(by_job) != len(records):
        raise ValueError('Duplicate job index')
    labels = {c['id']: c['target'] for c in plan['cases']}
    template = [{'job_index': r['job_index'], 'case': r['case'], 'arm': r['arm'],
                 'audit_id': r['summary']['audit_id'], 'target': labels[r['case']],
                 'target_outcome': 'PENDING', 'additional_false_positives': 0,
                 'reviewer': '', 'rationale_with_references': ''} for r in records]
    template_path = directory/'review-template.json'
    if not template_path.exists():
        template_path.write_text(json.dumps(template, indent=2)+'\n')
    judgments = {}
    if reviews:
        for item in json.loads(reviews.read_text()):
            index = item['job_index']
            if index in judgments or index not in by_job:
                raise ValueError('Unknown or duplicate reviewed job')
            if item['target_outcome'] not in ('TP', 'TN', 'FP', 'FN', 'UNRESOLVED'):
                raise ValueError('Review still pending or invalid')
            if not item.get('reviewer', '').strip() or not item.get('rationale_with_references', '').strip():
                raise ValueError('Reviewer and evidence rationale required')
            fp = item.get('additional_false_positives')
            if type(fp) is not int or fp < 0:
                raise ValueError('Additional false positives must be a nonnegative integer')
            record = by_job[index]
            target = labels[record['case']]
            expected = target.get('expected', target.get('status'))
            allowed = ('TP', 'FN', 'UNRESOLVED') if expected == 'CONFIRMED' else ('TN', 'FP', 'UNRESOLVED')
            if item['target_outcome'] not in allowed:
                raise ValueError('Outcome conflicts with frozen ground truth')
            if record['summary'].get('failure') and 'Model HTTP error' in record['summary']['failure'] and item['target_outcome'] != 'UNRESOLVED':
                raise ValueError('Provider-refused run must not become a semantic accuracy label')
            judgments[index] = item
    groups = defaultdict(lambda: {'runs': 0, 'complete': 0, 'reviewed': 0, 'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0, 'UNRESOLVED': 0})
    snapshots = defaultdict(set)
    for record in records:
        key = record['case'] + '/' + record['arm']
        group = groups[key]; group['runs'] += 1
        group['complete'] += record['summary']['status'] == 'COMPLETE'
        snapshots[record['case']].add(record['summary']['snapshot_sha256'])
        item = judgments.get(record['job_index'])
        if item:
            group['reviewed'] += 1
            group[item['target_outcome']] += 1
            group['FP'] += item['additional_false_positives']
    if any(len(values) != 1 for values in snapshots.values()):
        raise ValueError('Cannot compare knowledge arms on different snapshots')
    result = {'planned_runs': len(plan['jobs']), 'attempted_runs': len(records),
              'reviewed_runs': len(judgments), 'groups': dict(groups),
              'all_runs_complete': len(records) == len(plan['jobs']) and all(r['summary']['status'] == 'COMPLETE' for r in records),
              'all_runs_adjudicated': len(judgments) == len(plan['jobs']),
              'knowledge_unique_gain': 'NOT_AUTOMATICALLY_ESTABLISHED',
              'notice': 'Compare on/off/generic per case with matched snapshots and repeat counts. Small development samples are not blind validation or proof of statistical significance. Full release requires documented independent acceptance.'}
    (directory/'adjudicated-summary.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--reviews', type=Path)
    args = parser.parse_args()
    print(json.dumps(review_campaign(args.campaign, args.reviews), indent=2))


if __name__ == '__main__':
    main()
