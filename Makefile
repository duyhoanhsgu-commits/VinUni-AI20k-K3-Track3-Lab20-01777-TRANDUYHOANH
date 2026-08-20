PYTHON ?= .venv/bin/python3

.PHONY: install test lint format typecheck run-baseline run-multi clean

install:
	$(PYTHON) -m pip install -e ".[dev,llm]"

test:
	PYTHONPATH=src $(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests

format:
	$(PYTHON) -m ruff format src tests

typecheck:
	$(PYTHON) -m mypy src

run-baseline:
	PYTHONPATH=src $(PYTHON) -m multi_agent_research_lab.cli baseline --query "Research GraphRAG state-of-the-art"

run-multi:
	PYTHONPATH=src $(PYTHON) -m multi_agent_research_lab.cli multi-agent --query "Research GraphRAG state-of-the-art"

run-benchmark:
	PYTHONPATH=src $(PYTHON) -m multi_agent_research_lab.cli benchmark

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache dist build *.egg-info
