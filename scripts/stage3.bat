@echo off
cd /d "%~dp0.."
echo === diamond ===
python src\main.py --package A --repo testdata\test_repo.txt --test-mode
echo === cycle ===
python src\main.py --package A --repo testdata\cycle.txt --test-mode
echo === deep ===
python src\main.py --package A --repo testdata\deep.txt --test-mode
echo === deep, filter D ===
python src\main.py --package A --repo testdata\deep.txt --test-mode --filter D
echo === self loop ===
python src\main.py --package X --repo testdata\deep.txt --test-mode
echo === root filtered ===
python src\main.py --package A --repo testdata\deep.txt --test-mode --filter A
echo === nginx ===
python src\main.py --package nginx --repo https://dl-cdn.alpinelinux.org/alpine/latest-stable/main/x86_64
echo === nginx, filter ssl ===
python src\main.py --package nginx --repo https://dl-cdn.alpinelinux.org/alpine/latest-stable/main/x86_64 --filter ssl