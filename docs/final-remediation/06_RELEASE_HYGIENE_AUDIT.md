# Release hygiene audit

Frozen audit head: `a7cf6e46a87f6b0089cc962ed95c0dceeb2914e7`. Baseline `0733933113faee3121b2c5d692ef4ee1400d4d0d`. All187 changed paths classified below; no files deleted or history rewritten.

| Category | Files | Insertions | Deletions | Bytes |
|---|---:|---:|---:|---:|
|A. PRODUCT_CODE|2|138|2|67924|
|B. TEST_CODE|4|385|0|26889|
|C. REQUIRED_ACCEPTANCE_EVIDENCE|30|3312|0|139433|
|D. REQUIRED_DOCUMENTATION|4|138|0|18334|
|E. GENERATED_MODEL_TRACE|81|37100|0|2788847|
|F. TEMP_FIXTURE|16|1470|0|32614|
|H. DUPLICATE / REDUNDANT|50|2420|0|105188|

G/CACHE and I/UNKNOWN:0 files. Largest volume is repeated prompts/raw responses and observation snapshots, not product implementation. Byte sizes are current UTF-8/on-disk file sizes, insertion counts from git numstat.

High-confidence secret alerts: 0. Keyword hits are retained as counts; API headers in source, authentication examples, and token accounting are not themselves leaked credentials. Review raw trace data and tool payload origins; no API credentials are intentionally included. No push is authorized.

## Release evidence policy

Keep product/tests, concise result summaries, actual action sequences, test logs, audit IDs and hashes in the review entry points. Preserve committed historical raw evidence without rewriting/deleting it; provide an index instead of repeatedly embedding payloads. New P1 raw paid-model requests/responses will stay in a private external evidence directory with a local archive/hash, while public summaries disclose private-artifact accessibility limits. Docker build context must exclude final-remediation raw evaluation traces; build image should not copy prior paid runs. No deletion is performed.

## P0 formal Gate Review

P0_ENGINEERING_REMEDIATION=PASS; P0_REAL_MODEL_PROACTIVE_EVIDENCE_COMPLETION=PASS; P0_REAL_MODEL_POST_REJECTION_RECOVERY=INCONCLUSIVE; P0_OVERALL=PASS_WITH_LIMITATION.

> Deterministic post-rejection recovery is covered by automated tests, while direct real-model post-rejection recovery was not observed in the bounded three-run acceptance campaign because the tested model proactively completed missing evidence before settlement.

## Complete path index

| Status | Category | Path | Insertions | Bytes |
|---|---|---|---:|---:|
|M|A. PRODUCT_CODE|agent/v2/engine.py|79|65246|
|A|A. PRODUCT_CODE|agent/v2/recovery.py|59|2678|
|A|D. REQUIRED_DOCUMENTATION|docs/final-remediation/02_P0_ROOT_CAUSE.md|19|3653|
|A|D. REQUIRED_DOCUMENTATION|docs/final-remediation/03_P0_RECOVERY_GATE_REPORT.md|48|6462|
|A|D. REQUIRED_DOCUMENTATION|docs/final-remediation/04_REAL_MODEL_TRIGGER_ANALYSIS.md|15|2955|
|A|D. REQUIRED_DOCUMENTATION|docs/final-remediation/05_P0_FINAL_ACCEPTANCE.md|56|5264|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/PHASE_SHA256SUMS.json|143|15616|
|A|B. TEST_CODE|evaluation/final-remediation/p0-real-recovery/acceptance.py|113|9270|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/result.json|246|8466|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-01/SHA256SUMS.json|45|4471|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/audit_plan.json|11|192|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/coverage.json|7|160|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/decision_reviews.json|27|1708|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/findings.json|86|4455|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/hypotheses.json|19|677|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/investigation_notes.json|24|976|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/knowledge_used.json|3|92|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/metadata.json|11|323|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/repo/catalog.py|180|4104|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/repo_profile.json|14|292|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/report.md|180|7328|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/run_summary.json|165|5829|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/surface_progress.json|35|1283|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/surface_reviews.json|15|637|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/audits/f14017882f5b48b28fe67ca5baffa4be/tool_calls.jsonl|15|28686|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/final-context.json|266|47420|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-01/initial-state.json|23|416|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-01/prompt.json|3|202|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/request-01.json|908|45363|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/request-02.json|942|48434|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/request-03.json|976|50133|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/request-04.json|996|51622|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/request-05.json|1016|53142|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/request-06.json|1036|54936|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/request-07.json|1056|58052|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/request-08.json|1076|62593|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/request-09.json|1096|64885|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/request-10.json|1116|69812|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/request-11.json|1136|71916|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/response-01.json|24|802|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/response-02.json|24|984|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/response-03.json|15|1270|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/response-04.json|15|1227|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/response-05.json|15|1541|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/response-06.json|15|2678|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/response-07.json|15|4024|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/response-08.json|15|494|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/response-09.json|15|4161|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/response-10.json|15|1814|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/response-11.json|15|2382|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-01/result.json|227|8394|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-01/source/catalog.py|180|4104|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-01/state-transitions.jsonl|16|53163|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-02/SHA256SUMS.json|45|4575|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/audit_plan.json|11|192|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/coverage.json|7|160|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/decision_reviews.json|47|2788|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/findings.json|195|10084|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/hypotheses.json|20|928|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/investigation_notes.json|47|1835|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/knowledge_used.json|3|84|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/metadata.json|13|506|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/repo/controller.py|4|131|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/repo/security_config.py|180|4498|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/repo/service.py|7|277|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/repo_profile.json|23|448|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/report.md|215|10965|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/run_summary.json|151|6234|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/surface_progress.json|17|828|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/surface_reviews.json|17|826|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/audits/5d6d348f529447839aa1d8586ac00181/tool_calls.jsonl|17|42198|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/final-context.json|254|64015|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-02/initial-state.json|23|424|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-02/prompt.json|3|426|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/request-01.json|908|47234|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/request-02.json|942|50915|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/request-03.json|990|54484|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/request-04.json|1024|59507|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/request-05.json|1044|68488|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/request-06.json|1064|73250|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/request-07.json|1084|83130|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/request-08.json|1104|86234|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/request-09.json|1124|87611|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/response-01.json|24|883|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/response-02.json|33|2191|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/response-03.json|24|4536|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/response-04.json|15|8464|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/response-05.json|15|483|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/response-06.json|15|8931|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/response-07.json|15|2814|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/response-08.json|15|1124|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/response-09.json|15|3258|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-02/result.json|195|8244|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-02/source/controller.py|4|131|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-02/source/security_config.py|180|4498|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-02/source/service.py|7|277|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-02/state-transitions.jsonl|18|57962|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-03/SHA256SUMS.json|49|4933|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/audit_plan.json|11|192|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/coverage.json|7|160|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/decision_reviews.json|41|2616|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/findings.json|217|10170|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/hypotheses.json|19|812|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/investigation_notes.json|48|2066|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/knowledge_used.json|3|84|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/metadata.json|13|506|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/repo/controller.py|4|131|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/repo/security_config.py|180|4510|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/repo/service.py|7|277|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/repo_profile.json|23|448|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/report.md|223|10308|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/run_summary.json|170|6270|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/surface_progress.json|17|788|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/surface_reviews.json|17|593|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/audits/dd7dbb9e29ae4aae920e74932dc09d19/tool_calls.jsonl|18|51622|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/final-context.json|280|72540|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-03/initial-state.json|23|422|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-03/prompt.json|3|426|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/request-01.json|908|48642|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/request-02.json|942|51174|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/request-03.json|990|54691|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/request-04.json|1010|57198|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/request-05.json|1030|58550|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/request-06.json|1050|67707|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/request-07.json|1070|72461|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/request-08.json|1090|82981|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/request-09.json|1110|92445|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/request-10.json|1130|95429|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/request-11.json|1150|96777|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/response-01.json|24|935|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/response-02.json|33|1594|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/response-03.json|15|2210|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/response-04.json|15|1133|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/response-05.json|15|8640|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/response-06.json|15|475|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/response-07.json|15|8805|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/response-08.json|15|8909|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/response-09.json|15|2694|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/response-10.json|15|1095|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/response-11.json|15|2669|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-real-recovery/run-03/result.json|214|8278|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-03/source/controller.py|4|131|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-03/source/security_config.py|180|4510|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-real-recovery/run-03/source/service.py|7|277|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-real-recovery/run-03/state-transitions.jsonl|19|67616|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/SHA256SUMS.json|42|6152|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/coverage-recovery.json|108|2707|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/credential-source-check.txt|1|74|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/dependency-install.txt|113|7494|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/full-pytest.txt|5|341|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/historical-replay.json|235|7760|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/historical-reproduction.json|102|3063|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/historical-reproduction.txt|18|342|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/integrity.json|12|633|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/real-model-validation.txt|2|857|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/real-model/action-sequence.json|85|3748|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/audit_plan.json|8|152|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/coverage.json|7|160|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/findings.json|1|2|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/hypotheses.json|1|2|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/knowledge_used.json|1|2|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/metadata.json|11|335|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/repo/inventory_constants.py|173|2379|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/repo_profile.json|14|304|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/report.md|46|3505|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/run_summary.json|103|3968|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/surface_progress.json|28|1019|
|A|H. DUPLICATE / REDUNDANT|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/surface_reviews.json|28|896|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-recovery/real-model/audits/892583c225bd4ea6a0161ca36cbbad55/tool_calls.jsonl|4|9044|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-recovery/real-model/conversation.json|78|23520|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-recovery/real-model/request-01.json|901|42372|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-recovery/real-model/request-02.json|921|45915|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-recovery/real-model/request-03.json|941|47535|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-recovery/real-model/response-01.json|15|664|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-recovery/real-model/response-02.json|15|1352|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-recovery/real-model/response-03.json|15|2346|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/real-model/result.json|899|22495|
|A|F. TEMP_FIXTURE|evaluation/final-remediation/p0-recovery/real-model/source/inventory_constants.py|173|2379|
|A|B. TEST_CODE|evaluation/final-remediation/p0-recovery/real_model_validation.py|47|4296|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/replay-harness-initial.txt|4|280|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-recovery/replay/historical-replay-trace.json|3|4270|
|A|E. GENERATED_MODEL_TRACE|evaluation/final-remediation/p0-recovery/replay/minimal-trace.json|640|13591|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/replay/result.json|338|11037|
|A|B. TEST_CODE|evaluation/final-remediation/p0-recovery/reproduce.py|92|6349|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/unit-tests-initial-fault-fixture.txt|104|7058|
|A|C. REQUIRED_ACCEPTANCE_EVIDENCE|evaluation/final-remediation/p0-recovery/unit-tests.txt|2|99|
|A|B. TEST_CODE|tests/test_v2_recovery.py|133|6974|
