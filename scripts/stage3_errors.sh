#!/usr/bin/env bash
# Этап 3: обработка ошибок загрузки виртуальной файловой системы.
set -uo pipefail

source "$(dirname "$0")/common.sh"

BROKEN_IMAGE="$BUILD_DIR/broken.zip"
LOG_FILE="$BUILD_DIR/stage3_errors.xml"

step "Образ VFS не найден"
run_emulator --vfs "$BUILD_DIR/no_such_image.zip" --log "$LOG_FILE"

step "Образ VFS имеет неверный формат"
echo "это не ZIP-архив" > "$BROKEN_IMAGE"
run_emulator --vfs "$BROKEN_IMAGE" --log "$LOG_FILE"

step "Сообщения об ошибках сохранены в журнале"
cat "$LOG_FILE"
