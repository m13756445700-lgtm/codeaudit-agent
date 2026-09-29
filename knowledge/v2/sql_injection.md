# SQL injection — code judgment checklist
Trace request/CLI/persisted input through every wrapper to actual query execution. Quote source, transformations and sink. Method names alone prove nothing.
## Binding and identifier boundaries
MyBatis ${value} substitutes SQL text; #{value} binds a value. JDBC PreparedStatement setString and DB-API execute(sql, params) bind values when placeholders are driver-supported. They do not bind table/column names. For ORDER BY interpolation inspect whether identifiers come from an immutable server-side enum/map whose default also remains fixed. Such a mapping can make a candidate REJECTED even when the scanner flags ${column}.
## Context and uncertainty
ORM APIs that accept raw SQL bypass ordinary binding. Escape functions must match database, encoding and quote context; absent implementation is insufficient evidence. Trace custom query wrappers to driver calls, not just their names. Stored procedures can construct dynamic SQL internally. Persisted user input can cause second-order injection at a later concatenation site; require both write and read evidence before confirming that path.
## Decision
CONFIRMED requires controllable SQL syntax and reachable execution without effective binding/allowlist. REJECTED requires cited binding or finite mapping on the entire path. Unknown dependency sanitizer → INSUFFICIENT_EVIDENCE. Explain impact, required endpoint access and data sensitivity; do not award arbitrary scores.
