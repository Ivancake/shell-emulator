@echo off
chcp 65001 >nul
rem Проверка работы эмулятора с различными вариантами VFS
cd /d "%~dp0.."

echo === Без VFS (пустой корень) ===
python src\main.py --script examples\vfs_demo.txt

echo === Минимальная VFS ===
python src\main.py --vfs vfs\minimal.csv --script examples\vfs_demo.txt

echo === Несколько файлов ===
python src\main.py --vfs vfs\several_files.csv --script examples\vfs_demo.txt

echo === Три и более уровня вложенности ===
python src\main.py --vfs vfs\deep.csv --script examples\vfs_demo.txt

echo === Несуществующий файл VFS ===
python src\main.py --vfs vfs\missing.csv
echo Код возврата: %errorlevel%

echo === Некорректный base64 ===
python src\main.py --vfs vfs\bad_base64.csv
echo Код возврата: %errorlevel%

echo === Нет родительского каталога ===
python src\main.py --vfs vfs\bad_parent.csv
echo Код возврата: %errorlevel%