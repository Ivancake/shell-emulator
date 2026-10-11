@echo off
rem Проверка параметров командной строки эмулятора
cd /d "%~dp0.."

echo === Без параметров ===
echo exit | python src\main.py

echo === Только --vfs ===
echo exit | python src\main.py --vfs vfs\minimal.csv

echo === Только --script ===
python src\main.py --script examples\demo.txt

echo === Оба параметра ===
python src\main.py --vfs vfs\minimal.csv --script examples\demo.txt