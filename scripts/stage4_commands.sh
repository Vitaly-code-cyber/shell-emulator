#!/usr/bin/env bash
# Этап 4: все режимы команд ls, cd, history и echo.
set -uo pipefail

source "$(dirname "$0")/common.sh"

IMAGE="$BUILD_DIR/deep.zip"
LOG_FILE="$BUILD_DIR/stage4.xml"

step "Сборка образа VFS"
python3 "$ROOT/tools/build_vfs.py" deep

step "Все режимы команд на образе с глубокой вложенностью"
run_emulator --vfs "$IMAGE" --log "$LOG_FILE" \
    --script "$ROOT/startup/stage4_commands.vsh"

step "Ошибка: неизвестный ключ команды ls"
run_emulator_script stage4_bad_option --vfs "$IMAGE" <<'COMMANDS'
ls -z
COMMANDS

step "Ошибка: переход в файл вместо каталога"
run_emulator_script stage4_cd_file --vfs "$IMAGE" <<'COMMANDS'
cd /etc/app/config.ini
COMMANDS

step "Ошибка: несуществующий путь в команде cd"
run_emulator_script stage4_cd_missing --vfs "$IMAGE" <<'COMMANDS'
cd /home/nobody
COMMANDS

step "Ошибка: неверный аргумент команды history"
run_emulator_script stage4_history --vfs "$IMAGE" <<'COMMANDS'
echo первая команда
history много
COMMANDS

step "Ошибка: команды VFS без параметра --vfs"
run_emulator_script stage4_no_vfs <<'COMMANDS'
echo VFS не загружена, echo работает
ls
COMMANDS

step "Журнал событий этапа"
cat "$LOG_FILE"
