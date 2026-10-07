# Persistent operator business policy

Observed defect: consolidated_acceptance appends the business policy as a third message, while Engine.compact_context retains only the first two initial messages plus recent tool rounds. Long audits can lose the policy that defines authorization correctness.

Selected design: Engine accepts bounded optional business_policy and includes it in its initial operator message. Preserve it through existing compaction without promoting policy to source or deployment evidence. Store operator_context.json for replay. CLI --policy-file reads UTF-8 policy before model construction; evaluator passes only policy, never target labels. Empty policy retains existing behavior. Limit 8000 characters to bound context; reject oversized/invalid input rather than truncating semantics.

Alternatives: retaining every user message would also retain obsolete operational prompts and repository content; separate retrieval of operator policy would allow the same omission to recur. A fixed initial policy is simpler and preserves provenance.

Verification: regression after two compactions, malformed/oversized input before any model call, evaluator policy passage with target non-leakage. Existing frozen12 runs use unchanged implementation; preserve their identity. Run full isolated Linux tests for the new candidate, then a fresh frozen smoke test of policy flow. Historical44 is not relabeled as a test of changed code.

## Additional observed gate feedback defect
Frozen12 first audit exhausted48 iterations, with15 decision attempts. Gate requires exact list membership but gave no exact corrective value; Engine returned a success-shaped next action for a failed gate. Keep exact membership rule, return JSON-quoted original claim and specific correction instructions. Replay the original proposal to show rejection remains, exact model-authored correction succeeds, and no status auto-promotion occurs.52targeted tests pass. Freeze12 has3 unexecuted jobs, not retries.

## Frozen13 semantic review and negative coverage follow-up
First run COMPLETE with5 decisions, but serving.py/test.py/response.py sampled snippets were used to claim whole-module absence via REJECTED decisions, bypassing the full-read rule for feature_absent. Do not accept that as scope closure. Add a conservative negative-surface rule: any surface linked to REJECTED requires all declared file bytes/lines read unchanged and untruncated. Individual hypothesis judgments remain possible from targeted evidence; broad negative completion costs more reads or is honestly deferred. Return bounded next-read coordinates. This is a coverage constraint, not proof of semantic safety. Original model still overgeneralizes runtime versions; that remains a review concern, not fixed by this coverage guard.

## Frozen14 context failure and candidate16
First14audit b3363530d9c3457aa99ae3fc4ef2d030 stopped after114calls with context limit,1LIKELY7REJECTED. Remaining3jobs not attempted. Compactor now evicts complete old assistant/tool rounds when serialized envelope exceeds85000; it never truncates tool argument JSON or leaves orphan replies. Policy and state retained, full trace stays on disk. Notes/hypothesis/settlement memory may shrink to explicit navigation summaries when necessary.71targetedPASS;209isolatedLinuxPASS17.72s. Freeze16 retains14scope/budget and uses new fingerprint;15knowledge plan unexecuted/superseded. This prevents one engineering failure mode, not a semantic correctness claim.

## Freeze17 feedback loss and candidate18
Provider restored;17 endedINCOMPLETE with repeated segment-boundary failure after141search calls and102compactions,2865503tokens. Old round-eviction order erased latest search feedback before reducing stale excerpts. Candidate18 keeps newest complete round, reduces old read/notes memory first, evicts latest only if intrinsically oversized. No orphan tool replies or altered verdicts.72targetedPASS/210LinuxPASS18.51s. Same9module scope/250calls120iterations in new18, first only before expansion.
