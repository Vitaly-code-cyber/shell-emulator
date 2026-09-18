PYTHON ?= python3
ARGS ?=

.PHONY: help run test clean

help:
	@echo "make run   ARGS='...'  - запустить эмулятор"
	@echo "make test              - запустить модульные тесты"
	@echo "make clean             - удалить временные файлы"

run:
	$(PYTHON) -m src.main $(ARGS)

test:
	$(PYTHON) -m unittest discover -s tests -t . -v

clean:
	rm -rf build
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
