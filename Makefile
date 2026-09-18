PYTHON ?= python3
ARGS ?=

.PHONY: help run vfs test clean

help:
	@echo "make run   ARGS='...'  - запустить эмулятор"
	@echo "make vfs               - собрать ZIP-образы VFS в build"
	@echo "make test              - запустить модульные тесты"
	@echo "make clean             - удалить временные файлы"

run:
	$(PYTHON) -m src.main $(ARGS)

vfs:
	$(PYTHON) tools/build_vfs.py

test:
	$(PYTHON) -m unittest discover -s tests -t . -v

clean:
	rm -rf build
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
