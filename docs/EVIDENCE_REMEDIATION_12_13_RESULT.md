# Broad acceptance12/13 and implementation follow-up

Neither run authorizes release. Original results are preserved; remaining three jobs in each campaign were not attempted after review failure.

- Freeze12: INCOMPLETE after48 iterations,1,169,867tokens. Fifteen decision attempts repeated a structurally missing exact environment precondition. The gate retained its constraint but failed to explain the required literal value; Engine incorrectly returned a success-shaped next action.
- Fix: exact JSON-quoted correction hint and failed-decision next action. No automatic insertion or confidence promotion. Original proposal replay still fails without correction, passes after an explicit model-authored correction.
- Additional fix: operator business policy no longer disappears during context compaction; CLI exposes --policy-file and private audit records retain policy provenance.207isolatedLinux tests passed.
- Freeze13: COMPLETE,1,116,608tokens,1CONFIRMED/4REJECTED. The exact-precondition error recovered in one correction. Semantic review FAILED: module-wide absence claims were based on partial reads; runtime version range was broader than pinned evidence; original formparser scope absent from new plan.
- Fix: negative surface completion now requires unchanged, complete, untruncated reads of every declared file, including REJECTED-linked surfaces. Findings remain model judgments, and complete reads are not semantic correctness. Feedback identifies the next bounded missing range. Prompt explicitly prohibits extrapolating sampled versions into universal ranges.208isolatedLinux tests passed in17.70s.

Freeze14 explicitly enumerates the original nine module areas, retaining static-serving/upload path scope. Budget250calls/120iterations is an openly changed condition. First result must be reviewed before the three controls/repeats. This is not a whole-repository or independent blind assessment. Raw archives stay private; hash-linked public results in evaluation/evidence-remediation-12 and13.
