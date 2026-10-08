# P0 RECOVERY GATE REPORT

P0_RECOVERY_GATE: **FAIL — required real-model post-rejection recovery was not exercised**.

BASELINE_SHA: 0733933113faee3121b2c5d692ef4ee1400d4d0d

Tested code SHA: fd175be8dd4577682a9a2d26d574e911b341e0e2. Subsequent evidence-only commit records this result; no deployment or release push.

ROOT_CAUSE: see [02_P0_ROOT_CAUSE.md](02_P0_ROOT_CAUSE.md). Actual incomplete-read rejection is correct. Baseline lacks machine-readable gaps and persistent recovery priority. Generic failure counting ignores coverage progress and can be reset by irrelevant successful actions. Model claimed all1464 lines read while25 were missing. Compaction does not erase the read cache; its causal role remains unproven.

FILES_CHANGED: agent/v2/engine.py; new agent/v2/recovery.py; tests/test_v2_recovery.py; these two phase documents; evaluation/final-remediation/p0-recovery evidence and validation scripts. Existing uncommitted candidate implementation/docs/knowledge remain untouched in original checkout.

GATE_CHANGED: **NO** (acceptance criteria). Existing _validate_surface logic remains intact; the wrapper classifies incomplete negative evidence and adds recovery metadata. Partial, missing, changed, empty and truncated source cannot establish complete negative coverage. No finding/status promotion is synthesized.

RECOVERY_DESIGN: typed NEEDS_MORE_EVIDENCE; exact missing ranges from actual snapshot/cache; pending_evidence persisted to disk, investigation_state, execution checkpoint and compacted memory; deterministic recovery priority, model-selected actions. Three same-action/arguments/reason/coverage failures stop without progress. Evidence progress changes fingerprint; irrelevant reads/state actions do not reset stalls. Per-surface24-rejection cap and existing segment/iteration/tool/time limits bound changing-argument loops. Exhaustion yields INCOMPLETE, never a generated CONFIRMED.

NEW_TESTS:14 passed. Covers strict rejection, metadata, generic ledger.py121–127 supplementation, successful recovery and finish, no-progress retries including irrelevant success, compaction/disk state, unavailable/changed/empty/truncated source, round/call exhaustion, partial progress, recovery cap, segment checkpoint, same-response batch accounting.

FULL_PYTEST: passed225 / failed0 / skipped0,46.94s. [unit log](../../evaluation/final-remediation/p0-recovery/unit-tests.txt), [full log](../../evaluation/final-remediation/p0-recovery/full-pytest.txt). Initial synthetic fault tests failed because snapshot files are intentionally read-only; explicit chmod was added only to test fault injection. Initial failure log retained. No production permission policy changed.

SEMGREP_DECISION: required scanner integration/functional tests. Installed pinned requirements-dev.txt into isolated p0-test-venv, including semgrep1.99.0; all four previously failing tests passed. No skips or relaxed assertions. Fresh clone must install the declared development requirements or use the supplied test image workflow.

HISTORICAL_REPRODUCTION: **PASS**, meaning expected rejection/no-progress stop and scripted supplementation reproduced, not model acceptance. [Minimal result](../../evaluation/final-remediation/p0-recovery/historical-reproduction.json), [historical final-action replay](../../evaluation/final-remediation/p0-recovery/historical-replay.json). New recovery counts the initial direct dispatch rejection, so two subsequent scripted rounds produce the third failure; the adapted harness accounts for this. Original harness mismatch log retained. Historical missing1440–1464 recovered as metadata; scripted補读 then settlement accepted. Private archive required for historical replay; no claim of public fresh-clone reproducibility.

HISTORICAL_EVIDENCE_MODIFIED: **NO**. Round19 archive hash remains e02f2a6c2ef55364c2e2aa0816e6f5260542162b37c50edae25e5473fd3f62cb. Original tracked dirty patch byte-identical. Integrity record under new evidence directory.

## Real-model result — stop condition reached

REAL_MODEL_VALIDATION: **FAIL** (protocol acceptance unmet; not evidence that the model cannot recover).

REAL_MODEL: true; provider api.deepseek.com; model deepseek-flash; audit_id892583c225bd4ea6a0161ca36cbbad55. Tested SHA fd175be8dd4577682a9a2d26d574e911b341e0e2.

Harness seeded a plan and an actual partial read of inventory_constants.py1–120/173, then explicitly requested a first settlement attempt before further reads. Every later tool action was selected by real model calls. The model instead complied with the stronger complete-read requirement and read the tail first. This is an induced protocol experiment, not a blind vulnerability benchmark or OctoBus E2E.

RECOVERY_SEQUENCE:

1. Harness: plan + real partial read1–120; incomplete scope available to model.
2. Model call1: repo.read_range121–173, successful. **No initial settle attempt/rejection occurred.**
3. Model call2: settle_surface(feature_absent), accepted with full reads.
4. Model call3: finish, workflow COMPLETE. This does not prove recovery after rejection.

Three model-selected tool calls;25577 total tokens; no provider error. Required Gate response/missing feedback/second settlement sequence is absent, so strict validator correctly returns REAL_MODEL_RECOVERY=FAIL. Full requests, responses, action sequence, run summary and actual tool trace retained in [real-model](../../evaluation/final-remediation/p0-recovery/real-model/result.json). Credentials were read from existing configuration into process memory only, never stored in evidence. No server mutation.

GENERIC_RECOVERY: **PASS, deterministic only**. Real-model post-rejection recovery remains unproved.

REMAINING_RISKS: real acceptance fixture did not reach rejection; exact same frozen recovered state needs a better controlled continuation test. Unit/scripted success cannot substitute for real recovery. Complete-file reads may consume significant budget; blocked long lines require honest deferral. Source/server mismatch remains unchanged. Pending-state file is durable evidence, but process-crash resumption is not a newly implemented capability.

NEXT_RECOMMENDED_PHASE: **Continue P0 after next Gate Review**, improve fault-injection validation setup so the model actually receives a genuine rejected settlement; preserve this failed trial. Do not begin P1/P2/deployment/release. Stopped immediately after real validation result, with no extra paid retry.
