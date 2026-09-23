# CodeAudit 审计报告

Finding 数量：12

## sql_injection-TC-01-src-main-resources-mapper-UserMapper.xml-5 — VERIFIED
- 类别：SQL_INJECTION
- 结论：Use parameterized binding or a finite server-side allowlist mapping.
- 证据位置：src/main/resources/mapper/UserMapper.xml:5

## sql_injection-TC-02-src-main-resources-mapper-UserMapper.xml-8 — REJECTED
- 类别：SQL_INJECTION
- 结论：Use parameterized binding or a finite server-side allowlist mapping.
- 证据位置：src/main/resources/mapper/UserMapper.xml:8

## sql_injection-TC-03-src-main-resources-mapper-UserMapper.xml-5 — REJECTED
- 类别：SQL_INJECTION
- 结论：Use parameterized binding or a finite server-side allowlist mapping.
- 证据位置：src/main/resources/mapper/UserMapper.xml:5

## sql_injection-TC-04-src-main-resources-mapper-UserMapper.xml-5 — VERIFIED
- 类别：SQL_INJECTION
- 结论：Use parameterized binding or a finite server-side allowlist mapping.
- 证据位置：src/main/resources/mapper/UserMapper.xml:5

## command_injection-TC-05-src-main-java-lab-CommandController.java-12 — VERIFIED
- 类别：COMMAND_INJECTION
- 结论：Avoid shell command text; use fixed executable and immutable finite argument mapping.
- 证据位置：src/main/java/lab/CommandController.java:12

## command_injection-TC-06-src-main-java-lab-CommandController.java-22 — REJECTED
- 类别：COMMAND_INJECTION
- 结论：Avoid shell command text; use fixed executable and immutable finite argument mapping.
- 证据位置：src/main/java/lab/CommandController.java:22

## ssrf-TC-07-src-main-java-lab-FetchController.java-13 — VERIFIED
- 类别：SSRF
- 结论：Use immutable serviceId-to-URL mapping; review DNS, redirects and egress policy separately.
- 证据位置：src/main/java/lab/FetchController.java:13

## ssrf-TC-08-src-main-java-lab-FetchController.java-18 — REJECTED
- 类别：SSRF
- 结论：Use immutable serviceId-to-URL mapping; review DNS, redirects and egress policy separately.
- 证据位置：src/main/java/lab/FetchController.java:18

## path_traversal-TC-09-src-main-java-lab-ReadController.java-14 — VERIFIED
- 类别：PATH_TRAVERSAL
- 结论：Resolve real target and base paths, enforce directory boundary, and prevent concurrent filesystem mutation.
- 证据位置：src/main/java/lab/ReadController.java:14

## path_traversal-TC-10-src-main-java-lab-ReadController.java-28 — REJECTED
- 类别：PATH_TRAVERSAL
- 结论：Resolve real target and base paths, enforce directory boundary, and prevent concurrent filesystem mutation.
- 证据位置：src/main/java/lab/ReadController.java:28

## sql_injection-TC-11-src-main-resources-mapper-UserMapper.xml-5 — REJECTED
- 类别：SQL_INJECTION
- 结论：Use parameterized binding or a finite server-side allowlist mapping.
- 证据位置：src/main/resources/mapper/UserMapper.xml:5

## sql_injection-TC-12-src-main-resources-mapper-UserMapper.xml-5 — REJECTED
- 类别：SQL_INJECTION
- 结论：Use parameterized binding or a finite server-side allowlist mapping.
- 证据位置：src/main/resources/mapper/UserMapper.xml:5
