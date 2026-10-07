# Persistent operator business policy

Observed defect: consolidated_acceptance appends the business policy as a third message, while Engine.compact_context retains only the first two initial messages plus recent tool rounds. Long audits can lose the policy that defines authorization correctness.

Selected design: Engine accepts bounded optional business_policy and includes it in its initial operator message. Preserve it through existing compaction without promoting policy to source or deployment evidence. Store operator_context.json for replay. CLI --policy-file reads UTF-8 policy before model construction; evaluator passes only policy, never target labels. Empty policy retains existing behavior. Limit 8000 characters to bound context; reject oversized/invalid input rather than truncating semantics.

Alternatives: retaining every user message would also retain obsolete operational prompts and repository content; separate retrieval of operator policy would allow the same omission to recur. A fixed initial policy is simpler and preserves provenance.

Verification: regression after two compactions, malformed/oversized input before any model call, evaluator policy passage with target non-leakage. Existing frozen12 runs use unchanged implementation; preserve their identity. Run full isolated Linux tests for the new candidate, then a fresh frozen smoke test of policy flow. Historical44 is not relabeled as a test of changed code.

## Additional observed gate feedback defect
Frozen12 first audit exhausted48 iterations, with15 decision attempts. Gate requires exact list membership but gave no exact corrective value; Engine returned a success-shaped next action for a failed gate. Keep exact membership rule, return JSON-quoted original claim and specific correction instructions. Replay the original proposal to show rejection remains, exact model-authored correction succeeds, and no status auto-promotion occurs.52targeted tests pass. Freeze12 has3 unexecuted jobs, not retries.
