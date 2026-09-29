PYTHON ?= python3
IMAGE ?= codeaudit-final:2.0
.PHONY: test docker-test integration-test ablation-test benchmark private-git-test
test:
	$(PYTHON) -m pytest tests -q
docker-test:
	docker build --build-arg TEST_BASE=$(IMAGE) -t $(IMAGE)-test -f tests/Dockerfile .
	docker run --rm --network none --cpus 2 --memory 2g $(IMAGE)-test tests -q
integration-test:
	$(PYTHON) scripts/control.py integration
ablation-test:
	$(PYTHON) scripts/control.py ablation
benchmark:
	$(PYTHON) scripts/control.py benchmark
private-git-test:
	docker build -t codeaudit-ssh-fixture:local tests/integration/ssh_fixture
	$(PYTHON) scripts/v2_ssh_acceptance.py
