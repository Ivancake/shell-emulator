#!/bin/sh
# Проверка обработки ошибок при запуске эмулятора
cd "$(dirname "$0")/.." || exit 1

echo "=== Ошибки в стартовом скрипте ==="
python3 src/main.py --script examples/errors.txt
echo "Код возврата: $?"

echo "=== Несуществующий стартовый скрипт ==="
python3 src/main.py --script examples/missing.txt
echo "Код возврата: $?"

echo "=== Неизвестный параметр ==="
python3 src/main.py --unknown
echo "Код возврата: $?"