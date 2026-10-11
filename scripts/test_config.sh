#!/bin/sh
# Проверка параметров командной строки эмулятора
cd "$(dirname "$0")/.." || exit 1

echo "=== Без параметров ==="
echo exit | python3 src/main.py

echo "=== Только --vfs ==="
echo exit | python3 src/main.py --vfs vfs/minimal.csv

echo "=== Только --script ==="
python3 src/main.py --script examples/demo.txt

echo "=== Оба параметра ==="
python3 src/main.py --vfs vfs/minimal.csv --script examples/demo.txt