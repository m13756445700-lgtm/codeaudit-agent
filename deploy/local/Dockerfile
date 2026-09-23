FROM ghcr.io/chaitin/octobus@sha256:377409360a3d54f8e058340a7fb4874a994f18d11d35ba8f7cae0bec23a724a6 AS octobus
FROM ghcr.io/chaitin/agent-compose-guest@sha256:a99584629d9fe8c677683cdb6be88578b556a6e04e50abc5f1039424fdbefe73
USER root
COPY --from=octobus /usr/local/bin/octobus /usr/local/bin/octobus
RUN apt-get update && apt-get install -y --no-install-recommends python3.11-venv && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/codeaudit-venv
COPY pyproject.toml /opt/codeaudit/pyproject.toml
COPY agent /opt/codeaudit/agent
COPY schemas /opt/codeaudit/schemas
COPY knowledge /opt/codeaudit/knowledge
COPY rules /opt/codeaudit/rules
RUN /opt/codeaudit-venv/bin/pip install --no-cache-dir /opt/codeaudit semgrep==1.99.0 opentelemetry-instrumentation-requests==0.46b0
ENV PATH=/opt/codeaudit-venv/bin:$PATH
RUN groupadd --system octobus && useradd --system --gid octobus --home-dir /var/lib/octobus --create-home octobus
ENV OCTOBUS_ADDR=0.0.0.0:9000 OCTOBUS_DATA_DIR=/var/lib/octobus
USER octobus
WORKDIR /var/lib/octobus
ENTRYPOINT ["octobus"]
CMD ["serve"]
