@echo off
cd /d "%~dp0.."
set REPO=https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64
echo === diamond ===
python src\main.py --package A --repo testdata\test_repo.txt --test-mode --load-order
echo === cycle ===
python src\main.py --package A --repo testdata\cycle.txt --test-mode --load-order
echo === deep ===
python src\main.py --package A --repo testdata\deep.txt --test-mode --load-order
echo === deep, filter D ===
python src\main.py --package A --repo testdata\deep.txt --test-mode --load-order --filter D
echo === nginx ===
python src\main.py --package nginx --repo %REPO% --load-order
echo === curl ===
python src\main.py --package curl --repo %REPO% --load-order