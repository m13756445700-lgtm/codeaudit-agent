# Release tree policy

Primary examiner paths: README.md; docs/EXAMINER_GUIDE.md; docs/SECURITY.md; docs/SUBMISSION.md; docs/final-remediation/09_P1_FINAL_GATE.md; docs/EVIDENCE_INDEX.md. Product code, tests, schemas, pinned dependency files, build/CI configuration, necessary fixtures, concise acceptance JSON, test results and historical failure indices remain tracked.

Raw model traces, repeated prompts/responses, temporary fixture outputs, caches, credentials, runtime workspaces and archives are not the primary review path. Historical committed true evidence is retained in tree/history; never rewrite commits or delete inconvenient failures. New raw model dumps should remain in private artifact storage, indexed by source commit, audit id and archive hash. A hash is not public access: disclose accessibility and provide archive separately when authorized.

.gitignore excludes future request/response/context dumps. Ignore rules do not untrack any existing artifact. .dockerignore excludes final-remediation campaign output from runtime image context. New temporary clean clones/venvs belong under ignored .internal or system temporary directories. No historical file was removed from the release tree in P1.5. No artifact is classified as expendable solely because it documents a failure.

All release checks refer to exact build SHA. OCI revision is supplied through BUILD_SHA, never hardcoded. A local image ID is not a registry RepoDigest. GitHub Actions remains NOT_RUN until an actual hosted workflow completes. A test-only clean local clone is not P2 GitHub fresh-clone acceptance.

P0 limitation: Deterministic post-rejection recovery is covered by automated tests, while direct real-model post-rejection recovery was not observed in the bounded three-run acceptance campaign because the tested model proactively completed missing evidence before settlement.

UNIQUE_KNOWLEDGE_BENEFIT=NOT_ESTABLISHED. No release document may upgrade this without new authorized evidence.
