# Path traversal — boundary proof

Trace input decoding, normalization, joins and file operations separately. Normalization is not root confinement. Check component-aware containment, absolute-path override, URL decoding order, alternate separators and symlinks. A string-prefix check confuses root with root-evil. The same validated path must reach the sink; state filesystem permissions and attacker control. Unknown implementation semantics stay unresolved. Fixed filename mapping can limit traversal but does not establish authorization.

## CA-K04: platform-dependent containment — current evidence, 2026-10-06

Use exact evidence below, not a blanket Python version range. Tagged source observations:

| CPython tag | isabs('//server/share') | isabs('//server/share/file') |
|---|---|---|
| 3.10.0 | False | True |
| 3.11.0 | False | True |
| 3.11.1 | False | True |
| 3.11.2 | True | True |
| 3.11.9 | True | True |

The adjacent 3.11.1/3.11.2 tags establish the observed change on the 3.11 branch only. Do not extrapolate to every older/newer release or an entire other release branch. These observations concern string-helper semantics, not a Windows deployment or filesystem test.

Auditable sources:
- https://raw.githubusercontent.com/python/cpython/v3.11.1/Lib/ntpath.py — SHA256 `ee9655fc0b3dd63aa8e583bb8cdcdd692e8d1cdcb347e1483475718f9a95ca3d`
- https://raw.githubusercontent.com/python/cpython/v3.11.2/Lib/ntpath.py — SHA256 `6dcebd56222c03c4c897938d0a153b3f164bbd2edf7474aaebf0fff7aee7d504`

The reviewed 3.11.1 isabs implementation obtains the tail using `s = splitdrive(s)[1]` and checks its first character for a separator. For bare `//server/share`, splitdrive yields (`//server/share`, empty string); for `//server/share/file`, it yields (`//server/share`, `/file`). This explains the distinct outcomes. The pinned 3.11.2 implementation treats both as absolute. The offline replay script in this project's scripts/replay_runtime_evidence.py verifies whole-file hashes before compiling three reviewed string helpers. It does not execute target repository code. Knowledge supplies these external facts; it is not a read receipt for the audited repository.

## Applying the evidence

Read the target normalization, every guard and final join. Compare path flavors: POSIX normalization/joining may coexist with platform-native isabs. An independent leading-slash rejection defeats this specific forward-slash UNC route; verify it in the target snapshot rather than assuming a fix exists. An alternate-separator check may independently reject backslashes, so an isabs counterexample with backslashes alone proves no bypass.

For a variadic helper, check each component before the final join. A bare UNC component followed by a separate relative filename is distinct from one UNC string containing a filename. Do not assume downstream callers supply multiple components. State a concrete input, each guard result, and the returned value under an exact supported runtime precondition.

Separate claims: (1) a helper violates its promised returned-path root confinement, (2) a caller can access an external file, (3) a deployment exposes that caller. Proving the first does not prove the others. Conversely, a missing deployment fact does not refute an already demonstrated conditional helper-contract violation. Match confidence to the claim actually assessed. No required verdict: preserve LIKELY or INSUFFICIENT_EVIDENCE if decisive facts for that claim remain missing.

For a single-component caller, a bare-share return alone does not establish isfile=True or a successful open. Trace those requirements separately. Rejecting an independent caller defect does not erase inherited helper risk; do not summarize a caller as universally safe. Repository version, test-client code and the audit host OS do not prove deployment conditions.

## Provenance and advisory discrepancy

This card was developed after this project's failed known Werkzeug regression, not from private customer experience or blind evaluation. The maintainer advisory https://github.com/pallets/werkzeug/security/advisories/GHSA-f9vj-2wh5-fj8j describes a Windows UNC issue in Werkzeug 3.0.5 and earlier, using a broad Python version summary. Early 3.11 tagged-source observations above differ from that summary; use the exact pinned facts for runtime reasoning. Werkzeug 3.0.6 adds an explicit leading-slash check; still read the audited version to verify its guards. Results on these known versions do not demonstrate independent generalization or unique knowledge gain. Earlier card revisions and failed findings remain in Git/evaluation history; their broad summaries are not current evidence.

## Pinned normalization and join semantics

CPython3.11.1 posixpath source: https://raw.githubusercontent.com/python/cpython/v3.11.1/Lib/posixpath.py , SHA256 `115bb3d2051318ee3d951cdb13c60f118f15cea837cb69fb52cf543c12fe25c3`. The reviewed pure-Python normpath fallback preserves exactly two leading slashes. The join function replaces accumulated components when a later component starts with slash. Hash-checked offline string-helper replay yields: normpath('//server/share') == '//server/share'; join('trusted-root', '//server/share') == '//server/share'; joining the separate components '//server/share' and 'file' yields '//server/share/file'. A single '//server/share/file' also normalizes unchanged, but the separate isabs guard differs as shown above. These are dependency string semantics, not execution of target guards, Windows filesystem behavior, or a deployment observation. Verify all target guards before claiming a contract violation. The replay selects the Python fallback, not the native POSIX accelerator.
