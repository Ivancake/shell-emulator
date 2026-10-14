#!/bin/sh
# Проверка работы эмулятора с различными вариантами VFS
cd "$(dirname "$0")/.." || exit 1

echo "=== Без VFS (пустой корень) ==="
python3 src/main.py --script examples/vfs_demo.txt

echo "=== Минимальная VFS ==="
python3 src/main.py --vfs vfs/minimal.csv --script examples/vfs_demo.txt

echo "=== Несколько файлов ==="
python3 src/main.py --vfs vfs/several_files.csv --script examples/vfs_demo.txt

echo "=== Три и более уровня вложенности ==="
python3 src/main.py --vfs vfs/deep.csv --script examples/vfs_demo.txt

echo "=== Несуществующий файл VFS ==="
python3 src/main.py --vfs vfs/missing.csv
echo "Код возврата: $?"

echo "=== Некорректный base64 ==="
python3 src/main.py --vfs vfs/bad_base64.csv
echo "Код возврата: $?"

echo "=== Нет родительского каталога ==="
python3 src/main.py --vfs vfs/bad_parent.csv
echo "Код возврата: $?"