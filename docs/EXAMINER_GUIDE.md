# Examiner review entry

Start with [submission instructions](SUBMISSION.md), [current engineering Gate](final-remediation/09_P1_FINAL_GATE.md), and [evidence index](EVIDENCE_INDEX.md). The isolated candidate is not yet deployed to the examiner server; existing server runs must not be represented as this source's acceptance.

Review product code and tests alongside source-linked findings. COMPLETE is a workflow state, not proof of security. Positive conditional-code claims are not unconditional remote exploitation claims. Historical incomplete/partial/failed runs remain in the evidence index.

For local verification: install requirements-dev.txt in a fresh virtual environment, run `python -m pytest -q -p no:cacheprovider`, then `python scripts/validate_schemas.py`. Build with `docker build --build-arg BUILD_SHA=$(git rev-parse HEAD) --platform linux/amd64 -t codeaudit-review .` and run `python scripts/docker_smoke.py codeaudit-review`. These commands do not call a paid model. A working Docker daemon and sufficient disk space are prerequisites.
