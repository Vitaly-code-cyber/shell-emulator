#!/usr/bin/env bash
# Этап 2: запуск эмулятора без параметров и с каждым параметром
# командной строки по отдельности.
set -uo pipefail

source "$(dirname "$0")/common.sh"

step "Запуск без параметров (все значения по умолчанию)"
run_emulator

step "Только --vfs: имя VFS попадает в приглашение к вводу"
run_emulator --vfs "$BUILD_DIR/minimal.zip"

step "Только --log: журнал событий в формате XML"
run_emulator --log "$BUILD_DIR/stage2_defaults.xml"

step "Только --script: выполнение стартового скрипта"
run_emulator --script "$ROOT/startup/stage2_basic.vsh"

step "Справка по параметрам командной строки"
run_emulator --help
