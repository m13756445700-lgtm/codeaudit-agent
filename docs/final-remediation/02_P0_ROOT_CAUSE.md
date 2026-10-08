# P0 root cause and minimal recovery design

Baseline: 0733933113faee3121b2c5d692ef4ee1400d4d0d. Phase 1 evidence is retained in the original checkout, docs/final-remediation/02_P0_REPRODUCTION.md and evaluation/final-remediation/p0-reproduction/result.json.

Baseline call chain: Model.complete -> Engine.run -> dispatch(settle_surface) -> validate_surface -> ValueError -> run exception handler -> tool message -> compact_context / investigation_checkpoint -> next Model.complete -> failure_rounds -> INCOMPLETE. Baseline engine.py lines 471–490 emit only `Feature absence requires fully read declared files; partial reads cannot establish absence`. Lines 645–677 return `{error, consecutive_same_failure, next_action}` with generic retry advice, no file/range, no NEEDS_MORE_EVIDENCE classification. The repeat key is (action name,error), shared even across differing surfaces. Any successful dispatch clears failures, whether or not it obtains new evidence.

Evidence: campaign19 read-cache reconstruction contains1439 of1464 exact lines of test.py; the model incorrectly claims full reading and omits1440–1464. Three final failed rounds produce INCOMPLETE. Engine retains read_cache during compaction; excerpts and receipts are bounded but there is no persistent pending gap state. The system prompt already requires complete reads and describes120-line ranges, but lacks a machine-readable recovery protocol. Therefore A (insufficient feedback), missing explicit recovery state/strategy (B/C), and observed model action failure (F) are supported. D is a coarse detector design risk, not proof that more retries would help. E is not established as the cause; cache is not cleared. No claim is made about the model's private reasoning.

## Selected design

A prompt-only change leaves the information gap and no-progress loop. Automatically reading entire files can spend unbounded scope and conceal model recovery. Instead keep validation strict and turn only incomplete negative coverage into a typed ValueError carrying structured gaps. Persist per-surface recovery state; recompute against actual bytes after reads; keep it in investigation_state, checkpoints and compacted memory. Orchestration deterministically makes pending evidence the next priority, but the model must select tools and resubmit/defer. No findings or safety judgments are synthesized.

Recovery fingerprints include action/arguments/reason/current evidence gaps. Three identical no-progress failures stop; actual read progress changes the fingerprint, while irrelevant successful calls do not erase recovery stalls. A generic per-surface24-rejection budget also bounds changing-argument loops; normal iteration/call/timeout limits remain unchanged. This is a denial-of-progress guard, not extra retry allowance. Blocked/missing/empty/truncated source never earns coverage. Recommend bounded120-line reads, checkpoint notes at exhausted segments, or honest deferral. Recovery metadata is navigation state, not evidence.

Existing dirty candidate engine/tests/knowledge/docs in /Users/bo/codeaudit-v2-final are preserved. This P0 change is isolated in a managed worktree from the frozen baseline; no unrelated candidate changes enter commits.

## Semgrep dependency decision

The four failures are required scanner integration/functional regression, not optional unit tests. requirements-dev.txt pins semgrep==1.99.0 and Dockerfile includes it. Do not skip or weaken assertions. Install pinned dev dependencies in a dedicated test environment and run all tests; fresh-clone testing must use requirements-dev.txt or tests/Dockerfile. No optional-skip policy introduced.
