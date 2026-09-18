#!/usr/bin/env bash
# Этап 2: совместное использование всех параметров командной строки
# и проверка содержимого созданного XML-журнала.
set -uo pipefail

source "$(dirname "$0")/common.sh"

LOG_FILE="$BUILD_DIR/stage2_full.xml"

step "Все три параметра сразу: --vfs, --log, --script"
run_emulator \
    --vfs "$BUILD_DIR/minimal.zip" \
    --log "$LOG_FILE" \
    --script "$ROOT/startup/stage2_basic.vsh"

step "Содержимое XML-журнала $LOG_FILE"
cat "$LOG_FILE"
