#!/usr/bin/env bash
# Этап 3: загрузка различных вариантов VFS из ZIP-архивов.
set -uo pipefail

source "$(dirname "$0")/common.sh"

step "Сборка ZIP-образов VFS из исходных каталогов"
python3 "$ROOT/tools/build_vfs.py"

step "Минимальный образ: один файл в корне"
run_emulator --vfs "$BUILD_DIR/minimal.zip"

step "Образ из нескольких файлов в корневом каталоге"
run_emulator --vfs "$BUILD_DIR/simple.zip"

step "Образ с вложенностью не менее трёх уровней"
run_emulator --vfs "$BUILD_DIR/deep.zip"

step "Вложенный образ со стартовым скриптом и журналом"
run_emulator \
    --vfs "$BUILD_DIR/deep.zip" \
    --log "$BUILD_DIR/stage3.xml" \
    --script "$ROOT/startup/stage3_all.vsh"

step "Исходный ZIP-архив не изменён загрузкой VFS"
python3 "$ROOT/tools/build_vfs.py" deep >/dev/null
shasum "$BUILD_DIR/deep.zip"
run_emulator --vfs "$BUILD_DIR/deep.zip" >/dev/null
shasum "$BUILD_DIR/deep.zip"
