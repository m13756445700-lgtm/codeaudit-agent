# SSRF — destination validation
1. Identify URL source and whether scheme, host, port, path are controllable.
2. Locate validation and exact HTTP client behavior; finding an HTTP call alone is not SSRF.
3. Inspect immutable hostname/IP mappings versus user-supplied allowlist comparisons.
4. Determine redirects and whether EACH redirected destination is checked.
5. Consider DNS rebinding and whether validation and connection use the same resolved address.
6. Check private, loopback, link-local/metadata, IPv6, IPv4-mapped IPv6, numeric decimal/hex addresses and URL parser discrepancies.
7. State network reachability as a precondition, not an observed exploit if no runtime test exists.
Unknown dependency validation, redirects or DNS behavior must not be invented. A fixed server mapping with unmodifiable complete URLs can reject raw-input SSRF; URL normalize or a textual prefix is not sufficient proof of safety.
