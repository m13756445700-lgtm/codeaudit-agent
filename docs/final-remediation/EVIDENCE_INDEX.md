# Evidence index and publication boundary

P0 user Gate decision: PASS_WITH_LIMITATION. The historical FAIL/INCONCLUSIVE run records are unchanged. Current interpretation does not relabel any run as a successful post-rejection model recovery.

> Deterministic post-rejection recovery is covered by automated tests, while direct real-model post-rejection recovery was not observed in the bounded three-run acceptance campaign because the tested model proactively completed missing evidence before settlement.

Review entry points:

- 02_P0_ROOT_CAUSE.md: mechanical recovery defect and design.
- 03_P0_RECOVERY_GATE_REPORT.md: first real trial missed target rejection.
- 04_REAL_MODEL_TRIGGER_ANALYSIS.md and05_P0_FINAL_ACCEPTANCE.md: bounded three-run natural-scope results.
- 06_RELEASE_HYGIENE_AUDIT.md: all187 baseline-diff paths, raw trace/required evidence classification and sensitive-data review.
- 07_P1_ACCEPTANCE.md: current P1 conclusions and explicit limits.
- evaluation/final-remediation/p1-preflight/: fresh regression, schemas, Semgrep, CI/build evidence.

Existing committed raw P0 evidence remains available in Git history and tree; no history rewrite/deletion. Reviewers should start with summaries and request/action indices rather than repeated full model prompts. New P1 full raw requests/responses/audit workspaces are archived privately outside the repository; public campaign summary includes artifact hash and audit IDs. A hash verifies a supplied archive but does not make an inaccessible archive independently reviewable. Evidence portability remains a release limitation.

Docker build context excludes evaluation/final-remediation (past campaign outputs), reducing sensitive/unneeded runtime image contents. Heldout source fixtures and evaluator manifest remain developer testing material. Engine snapshots copy only each case/source subtree; neither investigator nor critic receives expected labels from the manifest. Do not benchmark by pointing the agent at the whole evaluation directory.
