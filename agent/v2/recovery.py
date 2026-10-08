"""Evidence navigation only. Never supplies findings or relaxes validation."""
import hashlib
import json
from agent.v2.repository import safe_path, digest


class NeedsMoreEvidence(ValueError):
    def __init__(self, message, feedback):
        super().__init__(message)
        self.feedback = feedback


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def coverage_gaps(engine, paths):
    gaps = []
    for path in dict.fromkeys(paths):
        entry = {'path': path, 'missing_ranges': [], 'blocked_reason': None}
        try:
            source = safe_path(engine.audit / 'repo', path)
            if path not in engine.metadata['files'] or digest(source) != engine.metadata['files'][path]:
                entry['blocked_reason'] = 'SNAPSHOT_UNAVAILABLE_OR_CHANGED'
            else:
                lines = source.read_text(errors='replace').splitlines()
                observed = engine.read_cache.get(path, {})
                if not lines:
                    entry['blocked_reason'] = 'EMPTY_FILE_NO_QUOTABLE_EVIDENCE'
                for number, code in enumerate(lines, 1):
                    if observed.get(number) == code:
                        continue
                    if entry['missing_ranges'] and entry['missing_ranges'][-1][1] == number - 1:
                        entry['missing_ranges'][-1][1] = number
                    else:
                        entry['missing_ranges'].append([number, number])
                    if len(code) > 2000:
                        entry['blocked_reason'] = 'LINE_EXCEEDS_TOOL_OUTPUT_LIMIT'
        except (OSError, ValueError):
            entry['blocked_reason'] = 'FILE_UNAVAILABLE'
        if entry['missing_ranges'] or entry['blocked_reason']:
            gaps.append(entry)
    return gaps


def actions(gaps, segment_calls):
    result = []
    if segment_calls >= 12:
        result.append({'action': 'investigation_note', 'instruction':
                       'Save a new note with already-read evidence, unresolved scope and next read before more tools. If no valid evidence is available, defer honestly.'})
    for gap in gaps:
        if gap['blocked_reason']:
            result.append({'action': 'defer_surface', 'path': gap['path'], 'reason': gap['blocked_reason']})
            continue
        for start, end in gap['missing_ranges']:
            # First bounded chunk per gap. Refresh state after every read.
            result.append({'action': 'use_tool', 'tool': 'repo.read_range',
                           'arguments': {'path': gap['path'], 'start': start, 'end': min(end, start + 119)}})
    return result
