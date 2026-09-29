FROM ghcr.io/chaitin/octobus@sha256:377409360a3d54f8e058340a7fb4874a994f18d11d35ba8f7cae0bec23a724a6 AS octobus
FROM ghcr.io/chaitin/agent-compose-guest@sha256:a99584629d9fe8c677683cdb6be88578b556a6e04e50abc5f1039424fdbefe73
USER root
COPY --from=octobus /usr/local/bin/octobus /usr/local/bin/octobus
RUN sed -i 's|http://mirrors.tuna.tsinghua.edu.cn/debian|https://deb.debian.org/debian|g' /etc/apt/sources.list.d/debian.sources && apt-get update && apt-get install -y --no-install-recommends python3.11-venv && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/codeaudit-venv
COPY pyproject.toml /opt/codeaudit/pyproject.toml
ARG CODEAUDIT_PIP_INDEX_URL=https://pypi.org/simple
RUN PIP_CONFIG_FILE=/dev/null PIP_INDEX_URL=${CODEAUDIT_PIP_INDEX_URL} PIP_EXTRA_INDEX_URL= /opt/codeaudit-venv/bin/pip install --no-cache-dir setuptools==75.8.0 wheel==0.45.1 jsonschema==4.23.0 PyYAML==6.0.2 javalang==0.13.0 defusedxml==0.7.1 semgrep==1.99.0 opentelemetry-instrumentation-requests==0.46b0
COPY agent /opt/codeaudit/agent
COPY schemas /opt/codeaudit/schemas
COPY knowledge /opt/codeaudit/knowledge
COPY rules /opt/codeaudit/rules
RUN /opt/codeaudit-venv/bin/pip install --no-deps --no-build-isolation /opt/codeaudit
ENV PATH=/opt/codeaudit-venv/bin:$PATH
COPY benchmark /opt/codeaudit/benchmark
COPY octobus/repo-tools /opt/codeaudit/octobus/repo-tools
COPY scripts /opt/codeaudit/scripts
ENV PYTHONPATH=/opt/codeaudit PYTHONDONTWRITEBYTECODE=1
WORKDIR /opt/codeaudit
ENTRYPOINT []
CMD ["codeaudit", "--help"]
