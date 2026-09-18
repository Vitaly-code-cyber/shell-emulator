#!/usr/bin/env bash
# Запуск эмулятора командной оболочки.
# Все аргументы передаются приложению без изменений.
set -euo pipefail

cd "$(dirname "$0")"
exec python3 -m src.main "$@"
