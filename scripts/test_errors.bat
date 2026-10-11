@echo off
rem Проверка обработки ошибок при запуске эмулятора
cd /d "%~dp0.."

echo === Ошибки в стартовом скрипте ===
python src\main.py --script examples\errors.txt
echo Код возврата: %errorlevel%

echo === Несуществующий стартовый скрипт ===
python src\main.py --script examples\missing.txt
echo Код возврата: %errorlevel%

echo === Неизвестный параметр ===
python src\main.py --unknown
echo Код возврата: %errorlevel%