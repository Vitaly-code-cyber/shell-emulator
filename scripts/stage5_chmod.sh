#!/usr/bin/env bash
# Этап 5: все режимы команды chmod и подтверждение того, что
# изменения выполняются только в оперативной памяти.
set -uo pipefail

source "$(dirname "$0")/common.sh"

IMAGE="$BUILD_DIR/deep.zip"
LOG_FILE="$BUILD_DIR/stage5.xml"

step "Сборка образа VFS"
python3 "$ROOT/tools/build_vfs.py" deep

step "Контрольная сумма образа до запуска эмулятора"
shasum "$IMAGE"

step "Все режимы команды chmod"
run_emulator --vfs "$IMAGE" --log "$LOG_FILE" \
    --script "$ROOT/startup/stage5_chmod.vsh"

step "Контрольная сумма образа после изменения прав"
shasum "$IMAGE"

step "Повторный запуск: права восстановлены, изменений на диске нет"
run_emulator_script stage5_reload --vfs "$IMAGE" <<'COMMANDS'
ls -l /home/user
COMMANDS

step "Ошибка: путь не существует"
run_emulator_script stage5_missing --vfs "$IMAGE" <<'COMMANDS'
chmod 755 /home/nobody
COMMANDS

step "Ошибка: не задан путь"
run_emulator_script stage5_no_path --vfs "$IMAGE" <<'COMMANDS'
chmod 755
COMMANDS

step "Ошибка: неверная символьная запись режима"
run_emulator_script stage5_bad_mode --vfs "$IMAGE" <<'COMMANDS'
chmod u+q /home/user/profile.conf
COMMANDS

step "Журнал событий этапа"
cat "$LOG_FILE"
