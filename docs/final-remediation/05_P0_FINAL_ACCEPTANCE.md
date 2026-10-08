# P0 FINAL ACCEPTANCE

P0_FINAL_GATE: **INCONCLUSIVE**. Three real-model attempts completed normally, but none triggered incomplete-evidence settlement rejection. This is not FAIL_PRODUCT, and is not proof of recovery after rejection.

BASELINE_SHA: `0733933113faee3121b2c5d692ef4ee1400d4d0d`

CURRENT_SHA (tested harness/source): `75996c6` (full SHA in result.json). The subsequent evidence-only commit records this report; no product code changes.

REAL_MODEL_PROVIDER: api.deepseek.com

REAL_MODEL_NAME: deepseek-flash. These observations concern only the tested model, not all LLMs or model-independent behavior.

ATTEMPTS: **3 / 3 maximum**, all REAL_MODEL=true, total430491 tokens. Every attempt preserved separately. No further model calls after the cap.

| Attempt | Fixture | audit_id / conversation run id | Actual first supplementary read | Workflow | Model tool calls | Tokens |
|---|---|---|---|---|---:|---:|
| 1 | A: single catalogue,180 lines | f14017882f5b48b28fe67ca5baffa4be | catalog.py151–180 | COMPLETE | 13 | 132125 |
| 2 | B: controller/service/security configuration | 5d6d348f529447839aa1d8586ac00181 | security_config.py151–180 | COMPLETE | 13 | 130491 |
| 3 | C: same cross-file task, interior gap | dd7dbb9e29ae4aae920e74932dc09d19 | security_config.py83–95, closing84–89 gap | COMPLETE | 14 | 167875 |

SUCCESSFUL_AUDIT_ID: none for the required post-rejection recovery path.

FIRST_SETTLEMENT: In every attempt, the model read missing scope before its first settlement. A submitted feature_absent; B/C submitted decision-linked reviewed settlements after examining the real authorization guard. All first settlements were accepted.

GATE_RESPONSE: No NEEDS_MORE_EVIDENCE response. Other validation errors, where present, are preserved in the trace and are not counted as incomplete-scope recovery.

MISSING_EVIDENCE: Initial actual read caches lacked A151–180, B151–180, C84–89. These coordinates were not injected as an instruction or expected answer into prompts. The model received truthful actual read payloads and total-lines metadata. Initial state files include evaluator-observed gaps and are not themselves passed as a new prompt.

RECOVERY_ACTION: No post-rejection action exists. The observed actions were proactive supplementation. The model chose when to read and when to settle freely; no instruction to err/settle early, forced tool choice, fake model call, Gate mutation or replay was used.

EVIDENCE_PROGRESS: Actual read-cache gaps changed from the initial missing ranges to empty before settlement. Harness observation recorded dispatch before/after state, and asserted each non-seed dispatch matched a real provider response tool call. All actions within each trial used the same audit/context. No combining rejection from one run with reads from another.

SECOND_SETTLEMENT: Not applicable; no rejected first settlement requiring recovery.

FINAL_SURFACE_STATUS: reviewed in all three. A feature_absent for SQL persistence; B/C decision-linked REJECTED unauthorized-read hypotheses after actual guard inspection. These are useful proactive counter-evidence observations, **not** evidence of an absence judgment being overturned after a coverage rejection.

WORKFLOW_STATUS: COMPLETE for all three. Workflow completion does not establish recovery acceptance, whole-repository safety or generalized vulnerability accuracy.

FULL_PYTEST: Not rerun in P0.5, because the instruction makes rerun conditional on real recovery success, which did not occur. Product code is unchanged. Previous P0 result remains225 passed /0 failed /0 skipped; it is not relabeled as a new run. Harness syntax was checked before experiments.

HISTORICAL_EVIDENCE_MODIFIED: **NO**. Round19 archive SHA256 reverified as e02f2a6c2ef55364c2e2aa0816e6f5260542162b37c50edae25e5473fd3f62cb. Prior P0 evidence and product tree have no diff from393a6e0. Each new run's artifact checksums verified.

PRODUCT_CODE_CHANGED_DURING_P0.5: **NO**.

FIXTURE_SPECIFIC_PRODUCT_LOGIC: **NO**. Fixture controls exist solely in acceptance.py, outside product code.

## Evidence and stop

[Machine result](../../evaluation/final-remediation/p0-real-recovery/result.json) contains per-run settlement arguments, actual gap transitions, provenance, usage and final outcomes. Each run directory contains initial-state, normal task prompt, source fixture, all API request messages/tool schemas (no credentials), actual model responses, state-transitions.jsonl, original Engine tool trace and final report. Evidence uses Local tools; no OctoBus E2E claim.

- [Run01](../../evaluation/final-remediation/p0-real-recovery/run-01/result.json)
- [Run02](../../evaluation/final-remediation/p0-real-recovery/run-02/result.json)
- [Run03](../../evaluation/final-remediation/p0-real-recovery/run-03/result.json)
- [Previous-trigger analysis](04_REAL_MODEL_TRIGGER_ANALYSIS.md)

NEXT_TASK: Await next Gate Review. If further testing is authorized, agree on an additional natural scenario or scope boundary before spending more; do not silently expand beyond three attempts or manufacture a rejection. No deployment, P1/P2, release, push or new fix commit. Current P0 implementation remains deterministically tested; real post-rejection fallback remains unproven.
