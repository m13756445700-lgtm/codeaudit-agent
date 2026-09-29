ARG TEST_BASE=codeaudit-final:2.0
FROM ${TEST_BASE}
USER root
RUN PIP_CONFIG_FILE=/dev/null PIP_INDEX_URL=https://pypi.org/simple PIP_EXTRA_INDEX_URL= /opt/codeaudit-venv/bin/pip install --no-cache-dir pytest==8.3.5
COPY . /test
WORKDIR /test
ENTRYPOINT ["/opt/codeaudit-venv/bin/python", "-m", "pytest", "-p", "no:cacheprovider"]
CMD ["tests", "-q"]
