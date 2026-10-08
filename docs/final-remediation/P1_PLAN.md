# P1 execution plan / worklog

P0 accepted by operator as PASS_WITH_LIMITATION. Permanent limitation: Deterministic post-rejection recovery is covered by automated tests, while direct real-model post-rejection recovery was not observed in the bounded three-run acceptance campaign because the tested model proactively completed missing evidence before settlement.

1. Classify all187 baseline-diff paths, inspect sensitive data, retain existing history, index evidence. DONE: no high-confidence credential matches.
2. Run new225-test preflight with pinned Semgrep. IN_PROGRESS.
3. Extend existing assumption state enum to supported/contradicted while preserving legacy verified/unknown. Reject unconditional material unsupported deployment claims; preserve explicit conditional-code scope. Critic remains advisory; whitelist finding fields and explicit status-specific challenges, no evaluator metadata.
4. Add platform/version/guard/data-flow semantic reference cases and tests. These validate oracle behavior/prompt constraints, not prove LLM semantic correctness.
5. Freeze six newly authored holdout-style cases before model runs: command, authorization, path, deserialization, SSRF, framework FP. Evaluator manifest outside copied source. No new knowledge tuning. At most18 model audits (6x3 arms), one each, bounded iterations/calls; stop on provider errors. Developer-authored cases are not independent blind evaluation.
6. Run semantic, critic, harness, full tests; schema check; Docker build and local CI equivalent. Ordinary CI has no model calls. No deployment/server changes/push/P2.
7. Archive private raw evidence outside Git; publish adjudication summaries, action sequence/hashes and limitations. Conclude Gate only from observed results.
