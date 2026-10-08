# Evidence index

| Group / purpose | Source commit | Audit / model | Result | Path | Limitation |
|---|---|---|---|---|---|
| Historical failures: Round19 missing scope |22cda54; baseline0733933|4c6f4521861746e4bd3c6581c5f90025; deepseek-flash|INCOMPLETE|evaluation/evidence-remediation-19/result.json|Historical implementation; full archive private|
| P0 deterministic recovery |fd175be|scripted, no LLM|14 tests passed; expected no-progress rejection|evaluation/final-remediation/p0-recovery/|Not real model recovery|
| P0 first real acceptance |fd175be|892583c225bd4ea6a0161ca36cbbad55; api.deepseek.com/deepseek-flash|Required rejection path not triggered|evaluation/final-remediation/p0-recovery/real-model/result.json|COMPLETE does not prove recovery|
| P0 real campaign |75996c6|f14017882f5b48b28fe67ca5baffa4be;5d6d348f529447839aa1d8586ac00181;dd7dbb9e29ae4aae920e74932dc09d19; api.deepseek.com/deepseek-flash|3 proactive completions; post-rejection INCONCLUSIVE|evaluation/final-remediation/p0-real-recovery/result.json|Bounded3 runs; no all-model claim|
| P1 semantic tests |4a8aefc; final reference test66e04e5|No LLM|252 full tests pass; finite runtime vectors pass|evaluation/final-remediation/p1-preflight/|Not universal semantics or actual Windows-host certification|
| P1 knowledge ablation |4a8aefc|18 audit ids in result; api.deepseek.com/deepseek-flash|NOT_ESTABLISHED benefit; completed13/18|evaluation/final-remediation/p1-heldout/result.json|Developer-authored6 cases; one run/cell; private raw archive hash indexed|
| Docker / CI |90586134ec701b4ec605c3536675f4e647b37965|No LLM; audit id N/A|252 tests, build + smoke + local CI PASS|evaluation/final-remediation/p1-5/verified/result.json; docs/final-remediation/09_P1_FINAL_GATE.md|Hosted GitHub Actions NOT_RUN until actual push/run|
| Final Release (reserved) |NOT_CREATED|N/A|NOT_RUN|Future P2/Final Release|No deployment or push authorized this phase|

Paths are repository-relative. [History index](HISTORY_INDEX.md) and [release policy](RELEASE_TREE_POLICY.md) define retention. Full committed historical traces remain intact; summaries are the primary examiner path. A private archive hash requires the actual archive for independent review.

P0_STATUS=PASS_WITH_LIMITATION. REAL_MODEL_POST_REJECTION_RECOVERY=INCONCLUSIVE permanently for the existing campaign. UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED.

> Deterministic post-rejection recovery is covered by automated tests, while direct real-model post-rejection recovery was not observed in the bounded three-run acceptance campaign because the tested model proactively completed missing evidence before settlement.

Docker / CI attempt history: original daemon-unavailable records remain at p1-5 root; continuation/ preserves recovered-daemon build and the first failed smoke on 764e1cb. verified/ records the complete successful clean run on 9058613. Root build/smoke/CI logs contain chronological attempts. No previous failure is overwritten.
