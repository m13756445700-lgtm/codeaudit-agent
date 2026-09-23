FROM ghcr.io/chaitin/agent-compose-guest@sha256:a99584629d9fe8c677683cdb6be88578b556a6e04e50abc5f1039424fdbefe73
ARG CODEAUDIT_MCP_TOOL_PREFIX=code-audit-service__code-audit-local__
COPY harden-runtime.py /tmp/harden-runtime.py
RUN python3 /tmp/harden-runtime.py /usr/lib/node_modules/@chaitin-ai/agent-compose-runtime/dist/runners/codex.js "$CODEAUDIT_MCP_TOOL_PREFIX" \
 && rm /tmp/harden-runtime.py
