PYTHON ?= python3
ARGS ?=

.PHONY: help run vfs test lint clean

help:
	@echo "make run   ARGS='...'  - запустить эмулятор"
	@echo "make vfs               - собрать ZIP-образы VFS в build"
	@echo "make test              - запустить модульные тесты"
	@echo "make lint              - проверить оформление кода"
	@echo "make clean             - удалить временные файлы"

run:
	$(PYTHON) -m src.main $(ARGS)

vfs:
	$(PYTHON) tools/build_vfs.py

test:
	$(PYTHON) -m unittest discover -s tests -t . -v

lint:
	$(PYTHON) tools/check_style.py

clean:
	rm -rf build
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
