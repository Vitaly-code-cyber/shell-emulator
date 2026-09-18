#!/usr/bin/env bash
# Этап 2: обработка ошибок при использовании параметров командной
# строки и при выполнении стартового скрипта.
set -uo pipefail

source "$(dirname "$0")/common.sh"

LOG_FILE="$BUILD_DIR/stage2_errors.xml"

step "Ошибка внутри скрипта: выполнение останавливается на первой"
run_emulator \
    --vfs "$BUILD_DIR/minimal.zip" \
    --log "$LOG_FILE" \
    --script "$ROOT/startup/stage2_error.vsh"

step "Ошибка в журнале: сообщение сохранено вместе с именем пользователя"
cat "$LOG_FILE"

step "Несуществующий стартовый скрипт"
run_emulator --script "$ROOT/startup/no_such_script.vsh"

step "Неизвестный параметр командной строки"
run_emulator --unknown-option
