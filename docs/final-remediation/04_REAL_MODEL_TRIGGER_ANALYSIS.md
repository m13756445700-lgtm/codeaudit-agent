# P0.5: why the previous run did not trigger rejection

Prior audit892583c225bd4ea6a0161ca36cbbad55, tested product commit fd175be; prior evidence remains unchanged. response-01.json explicitly says it has read1–120 of173 and cannot establish full-file absence, then calls read_range121–173. This is an observable action explanation, not access to private model reasoning.

The system prompt requires complete declared-file reads for feature_absent and forbids sampled absence. Tool descriptions constrain reads to120 lines and settlement to actual evidence. The seed user message contained actual total_lines173 and actual lines1–120, exposing an obvious unread tail. Checkpoint state reported the surface unsettled. No Gate rejection or pending_evidence existed yet. The harness's instruction to settle before further reading conflicted with the stronger system rule. The model correctly prioritized complete evidence.

Therefore prior test induction was inadequate and used an instruction this P0.5 specification now forbids. Its historical result is not altered; it demonstrates proactive supplementation, not product failure or post-rejection recovery. P0.5 removes all instructions to settle prematurely or to deliberately fail. Product prompts, tool schemas, Gate and recovery logic remain frozen.

## Acceptance design and limits

A normal scoped audit task, real seeded plan/partial reads, truthful read payloads and freely selected subsequent model actions. A: single declared180-line reference catalogue, first150 read. B: three declared modules, controller/service fully read and security configuration partly read. B includes an actual authorization guard in initially unread source, so a correct verdict may overturn an absence assumption. An optional third attempt varies the partial-read placement to an interior gap. No expected answer, unread line coordinates or ground-truth label is inserted into model prompts; returned real read metadata is preserved.

At most3 real audit attempts total. No mock/replay/model tool-call injection; a harness subclass only records actual dispatch inputs/results and state transitions. Every non-seed dispatch must match a real response's tool call. Full API message payloads (without credentials), returned responses, actual Gate feedback and pre/post coverage are retained. A post-rejection recovery PASS requires the same audit/context to receive the actual rejection, read new missing evidence, and then obtain accepted settlement or justified abstention without repeating identical failed settlement. COMPLETE without rejection is TEST_INCONCLUSIVE, never recovery PASS.

This is a controlled recovery-path experiment with Local read-only transport, not OctoBus E2E or general vulnerability accuracy validation. Only the tested provider/model is covered. On success rerun full pytest; on3 no-rejection attempts stop INCONCLUSIVE. No product changes, deployment, release or push are planned.
