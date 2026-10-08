# P1 ACCEPTANCE

P1_GATE: **CONDITIONAL — not release-ready**. Completed bounded implementation, tests and18 real evaluation runs. Docker/CI verification is blocked locally; the finite runtime matrix does not establish generalized semantic reliability. No deployment, server changes, push or P2.

## P0 status (operator Gate Review)

P0_STATUS: **PASS_WITH_LIMITATION**.

P0_ENGINEERING_REMEDIATION=PASS; P0_REAL_MODEL_PROACTIVE_EVIDENCE_COMPLETION=PASS; P0_REAL_MODEL_POST_REJECTION_RECOVERY=INCONCLUSIVE.

P0_LIMITATION (permanent):

> Deterministic post-rejection recovery is covered by automated tests, while direct real-model post-rejection recovery was not observed in the bounded three-run acceptance campaign because the tested model proactively completed missing evidence before settlement.

Earlier P0 FAIL/INCONCLUSIVE artifacts remain untouched; this is the user's later overall Gate decision, not a rewrite of experiments.

## Release hygiene

Audited baseline0733933113faee3121b2c5d692ef4ee1400d4d0d to a7cf6e46a87f6b0089cc962ed95c0dceeb2914e7:187 files,44963 insertions,2 deletions.

- Release-required classification:40 files (2 product,4 test,30 concise acceptance evidence,4 docs).
- Generated model traces:81 files,37100 insertions,2788847 bytes (82.5% of all insertions).
- Redundant audit output:50 files,2420 insertions; temporary fixture copies:16 files,1470 insertions.
- Cache/build/unknown:0 classified paths.
- Full path/category/size index: [06_RELEASE_HYGIENE_AUDIT.md](06_RELEASE_HYGIENE_AUDIT.md).
- No files deleted, no Git history rewrite. Existing traces indexed; new P1 raw requests/responses archived outside Git. Docker context excludes evaluation/final-remediation.
- SECURITY_BLOCKERS: none found by pattern checks and reviewed provenance; this is not a proof no possible secret exists. Scans cover original187 changed files and new private model JSON. No credentials serialized in requests or published summaries. No push performed.

## P1 semantic reliability

P1_SEMANTIC_RELIABILITY: **PASS for the bounded implemented constraints and regression set**, not a guarantee of arbitrary-platform/version judgment correctness.

Existing assumption schema reused: state/references are preserved; verified/supported/unknown/contradicted correspond to VERIFIED/SUPPORTED/UNKNOWN/CONTRADICTED. Supported and contradicted claims require read references; material unsupported deployment claims cannot retain decisive unconditional verdicts. Explicit conditional_code claims must keep unresolved premises and unknown deployment exposure. Material contradicted assumptions require revision or abstention. Evidence Gate still validates references/constraints, not semantic truth.

PLATFORM_TESTS: ntpath/POSIX differences, mixed separators, UNC-like paths and absolute paths pass using local Python path libraries. These are reference semantics, not Windows-host execution or multi-CPython historical integration tests.

VERSION_TESTS: two actual isolated runtime combinations pass: Werkzeug2.3.8 + urllib3 1.26.20, and Werkzeug3.0.6 + urllib3 2.2.3, both Python3.9.6/POSIX. scripts/p1_runtime_matrix.py records traversal/absolute/mixed-separator/UNC-like path behavior and userinfo/hostname URL boundaries using the installed packages. Exact versions, outputs and installation logs are retained under p1-preflight/runtime-matrix. Finite-observation/non-extrapolation checks and assumption constraints also pass. This is neither all intervening versions nor historical affected/fixed exploit reproduction, and not proof that the LLM can independently infer every version boundary.

GUARD_TESTS:6 trusted synthetic reference scenarios pass: unreachable, effective, partial input, after sink, another layer, inappropriate sanitizer. The real path case additionally tests model analysis of a working containment guard. Reference unit tests alone do not prove model discrimination across all six cases.

DATA_FLOW_TESTS: a controller→service→worker→sink fixture passes with effectful subprocess replaced by a recording sink; changing route linkage prevents any sink call. Real command case traverses all4 files. No third-party target code was executed by the Agent. Source/sink citation validity still cannot guarantee complete semantic flow by itself.

## Critic

CRITIC: **PASS for bounded advisory contract and evaluator-metadata isolation**, not independent truth verification.

Status-specific prompt challenges cover CONFIRMED guards/platform/version/reachability, REJECTED bypasses, LIKELY decisive missing links, INSUFFICIENT_EVIDENCE possible next tools. Critic receives fresh bounded evidence context, never writes a verdict. Explicit finding/evaluator keys are allowlisted/filtered, including nested expected/ground_truth/answer metadata; tests verify canaries are absent and input finding is not mutated. This does not sanitize every imaginable answer encoded in free text; harness isolation of evaluator labels remains necessary.

Existing engine does not force review for every INSUFFICIENT_EVIDENCE finding; the critic supports that status when invoked, but exhaustive automatic invocation is not newly claimed. Real r02 project/generic runs reveal repeated revision/critique cycles and iteration exhaustion; these failures are retained as a reliability limitation, not repaired mid-campaign or hidden by larger budgets.

## Knowledge ablation

6 newly authored frozen cases: command injection, authorization, path handling, unsafe deserialization, SSRF/URL trust, fixed-template framework false positive. They were authored for this run, not copied from prior case files; no claim of independent authorship or blind external evaluation. Expected labels remain outside each source snapshot. No knowledge tuning after freeze.

18 real audits: api.deepseek.com / deepseek-flash, one per case/arm; same case bytes and budgets, real advisory critic enabled in all arms. Tested product/case commit4a8aefc. Later changes before reporting only add a trusted reference test/docs/evidence; product hashes remain the tested ones.

| Arm | TP/TN/FP/FN | Abstentions | COMPLETE/PARTIAL/INCOMPLETE | Tool calls | Tokens | Decisive reference cited |
|---|---|---:|---|---:|---:|---|
| Project knowledge |3/3/0/0|0|4/1/1|106|721434|6/6|
| No project knowledge |3/3/0/0|0|5/1/0|94|493057|6/6|
| Generic knowledge |3/3/0/0|0|4/1/1|101|644812|6/6|

TP counts CONFIRMED **or LIKELY** as positive detection. Project/generic have2 CONFIRMED+1 LIKELY; off has3 CONFIRMED. No claim that these certainty levels are equivalent. All18 had valid reference gates and cited the targeted decisive line; this is limited evidence-quality measurement, not independent semantic adjudication. Same development Agent reviewed conclusions against frozen source and task; not an independent reviewer.

Known outcomes/limitations:

- r01: all arms identify the4-file shell command flow, with conditional-code scope.
- r02: all identify missing tenant checks; project/generic retain LIKELY, then exhaust iteration budget in review/revision. Off finishes conditional CONFIRMED under supplied business policy. Positive target detection does not erase workflow failure.
- r03: all reject traversal within the stable-POSIX/no-concurrent-symlink scope. Project/generic additionally plan unused_adapter and defer it, producing PARTIAL even though the target verdict is correct.
- r04: all identify base64→pickle unsafe decoding, conditional to supplied input premise.
- r05: all reject user-selected key as arbitrary URL control under the frozen URL/DNS/redirect premises; off additionally defers dormant_fetch and produces PARTIAL. Generic records an extra INSUFFICIENT_EVIDENCE for dormant_fetch, distinct from target-level abstention0; project records an additional scoped REJECTED. Target metrics do not imply identical whole-report judgments.
- r06: all reject template-source injection for fixed template with variable data, scoped to that property.

UNIQUE_KNOWLEDGE_BENEFIT: **NOT_ESTABLISHED**. No measurable target-correctness improvement in this small campaign; project knowledge did not improve completion or cost. One run per cell cannot establish statistical equivalence, infer overall model accuracy, or conclude knowledge never helps.

Total1859303 tokens. No additional paid retries. Summary, findings, key action hashes, usage and archive identity: [result.json](../../evaluation/final-remediation/p1-heldout/result.json). Raw archive is private/local and must be supplied separately for full independent inspection. New main-tree payload omits repeated raw prompts/responses.

## Regression, Docker and CI

Fresh P0 preflight:225 passed /0 failed /0 skipped,35.60s.

P1 order: semantic20 then critic2 then harness4; full251 passed32.43s; added explicit cross-file/broken-route reference test, reran semantic21 and full252 passed37.26s. Initial and final logs retained.

FULL_PYTEST: **passed252 / failed0 / skipped0**.

Semgrep1.99.0 freshly checked, installed through pinned requirements-dev.txt; no optional skips. Persisted and V2 tool schema validation pass.

DOCKER_BUILD: **FAIL/BLOCKED**. Local Docker build returned no output before60-second bound. Direct daemon `_ping` also timed out after10s, exit28. No new image exists; no remote-server build used. No Docker restart or server changes attempted.

CI: **FAIL / incomplete local equivalent**. New .github/workflows/ci.yml includes Python3.11 setup, pinned dependency install, pytest, schema validation and Docker build. No paid-model calls, no `|| true`/`continue-on-error` core bypass. Local test/schema steps passed; Docker step blocked. GitHub-hosted Actions has not run because pushing is prohibited. This is configuration plus partial local verification, not a green hosted CI claim.

## Remaining risks and next_task

1. Docker daemon/build and actual hosted CI remain unverified; resolve before release.
2. Only two framework/dependency combinations on Python3.9.6/POSIX were observed. Historical affected/fixed exploit reproduction, a multi-CPython matrix and actual Windows host remain unverified; no whole-version-range or deployment claims are supported.
3. Model critique/revision may exhaust bounded iterations; scoped tasks may become PARTIAL from model-added out-of-scope surfaces.
4. Knowledge uniqueness remains unproved; externally authored blind cases and repeated measurements would require a separately authorized campaign.
5. Full raw evidence is locally archived, not publicly retrievable from hashes alone.
6. Server/GitHub mismatch remains unchanged for P2/final release; do not advertise current server as this tested branch.

Stop at P1 Gate Review. Keep codex/p0-evidence-recovery isolated. No deployment, main push, final release or P2.
