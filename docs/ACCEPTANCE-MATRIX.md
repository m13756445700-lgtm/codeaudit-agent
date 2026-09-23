# BRD Acceptance Matrix

Date: 2026-09-23. Environment: verified target-server Linux OctoBus container.

| Case | Expected | Actual | Result | Evidence |
|---|---|---|---|---|
| TC-01 | VERIFIED | VERIFIED | PASS | [JSON](../evidence/review/cases/TC-01.json) |
| TC-02 | REJECTED | REJECTED | PASS | [JSON](../evidence/review/cases/TC-02.json) |
| TC-03 | REJECTED | REJECTED | PASS | [JSON](../evidence/review/cases/TC-03.json) |
| TC-04 | VERIFIED | VERIFIED | PASS | [JSON](../evidence/review/cases/TC-04.json) |
| TC-05 | VERIFIED | VERIFIED | PASS | [JSON](../evidence/review/cases/TC-05.json) |
| TC-06 | REJECTED | REJECTED | PASS | [JSON](../evidence/review/cases/TC-06.json) |
| TC-07 | VERIFIED | VERIFIED | PASS | [JSON](../evidence/review/cases/TC-07.json) |
| TC-08 | REJECTED | REJECTED | PASS | [JSON](../evidence/review/cases/TC-08.json) |
| TC-09 | VERIFIED | VERIFIED | PASS | [JSON](../evidence/review/cases/TC-09.json) |
| TC-10 | REJECTED | REJECTED | PASS | [JSON](../evidence/review/cases/TC-10.json) |
| TC-11 | REJECTED | REJECTED | PASS | [JSON](../evidence/review/cases/TC-11.json) |
| TC-12 | Rule ON/OFF differs | REJECTED / NEEDS_REVIEW | PASS | [JSON](../evidence/review/cases/TC-12.json) |

TC-05 and TC-10 follow user-approved errata. TC-01 and TC-04 share the unconstrained MyBatis fixture and assert separate BRD requirements.

Each JSON contains a fixed commit and schema-validated finding. TC-12 also includes the disabled-rule finding. Scanner artifacts and committed fixture copies are retained alongside matrix.json.

Scope: static controlled fixtures, real Semgrep, independent Gate. This is not evidence of Java compilation, live exploitation, server reboot, or SSH acceptance.

The first macOS matrix attempt failed because the scanner was externally terminated. The complete Linux container run passed 12/12; failures are retained in runs/phase9-acceptance.log.
