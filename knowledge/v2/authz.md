# Authentication and authorization
Distinguish identity verification from permission to each object/action. Trace route middleware, principal construction, tenant ownership checks and actual query/update. An object ID alone is not proof of IDOR; inspect global middleware/service policy before confirming missing authorization. A login check alone is not object authorization. Require reachability and attacker identity/role assumptions; unavailable middleware source means insufficient evidence. Cite checks when rejecting, rather than assuming framework defaults.

## Practice card CA-K03 — finite mapping and actual boundary (revision 2026-09-29)
Provenance: local four-file `benchmark/false-positive`, audit `173bb238ebd149da9d8c86bb1ea84a29`, snapshot `d2900109e7ab021b8a78113702de2e5be466c2000a23fbf6e8c917cbbe66222d`; observed one rejected and one insufficient-evidence decision. This small fixture is training/regression material, not independent validation.
Procedure: trace the externally supplied identifier through the lookup and verify all selected values are immutable server-owned entries before interpreting the downstream dangerous API. Cite the mapping and rejection branch as counter-evidence. Do not treat input selection as control over the mapped command/path. Counterexample: a mutable mapping populated from user records invalidates this rejection; read every write or mark the assumption unresolved.
Authorization remains separate: a finite mapping does not prove the current user is entitled to every selectable operation. Require identity, ownership/tenant scope and the protected action; missing business policy requires manual review, not an invented IDOR verdict.

## Review procedure CA-K05 — tenant policy across layers
Source: project-authored review procedure and `evaluation/business-ground-truth.json` synthetic counterexamples. This is not customer incident experience or an independently measured gain. Business policy must come from the audited application or explicitly supplied scope, not from this card.

Invariant: for a tenant-private resource, each read, write, batch item and cache hit must be constrained to the authenticated principal's permitted tenant. Trace trusted principal construction separately from client-supplied tenant IDs. A role such as editor normally describes allowed actions, not authority over every tenant. Do not assume tenant-private policy if it is absent: record the uncertainty.

1. Read route registration and middleware, identity construction, service guard, repository operation and the response/mutation. A scoped helper's existence is not evidence that this path calls it.
2. Batch authorization is per selected object unless code proves a shared authorized scope. Checking only the first item leaves later IDs unproven. For writes, inspect whether partial mutation happens before a later authorization failure.
3. Cache lookup must preserve the authorization boundary before returning a hit. A scoped database query on misses does not protect unscoped hits. Check cache key, key collisions, scope of sharing and invalidation after permission changes.
4. Reject an IDOR candidate when an actual path binds a trusted tenant and enforces it for every operation. Quote the guard and the call site. A globally unique UUID or unpredictable identifier is not an ownership check.
5. Counterexamples: intentionally public records, verified cross-tenant administrator grants, immutable allowlisted records, isolated per-tenant cache instances. Read supporting policy/code before applying these exceptions; unavailable dependencies or deployment isolation require explicit uncertainty.

Stopping rule: report a bounded judgment with the exact action and assumptions. Do not claim all authorization sound after one guarded endpoint; leave untouched surfaces deferred. Knowledge-off and generic-control evaluation must use identical snapshots and external policy context.
