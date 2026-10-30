@echo off
cd /d "%~dp0.."
set REPO=https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64
echo === diamond ===
python src\main.py --package A --repo testdata\test_repo.txt --test-mode --ascii-tree
echo === cycle ===
python src\main.py --package A --repo testdata\cycle.txt --test-mode --ascii-tree
echo === deep, filter D ===
python src\main.py --package A --repo testdata\deep.txt --test-mode --ascii-tree --filter D
echo === nginx ===
python src\main.py --package nginx --repo %REPO% --ascii-tree
echo === curl ===
python src\main.py --package curl --repo %REPO% --ascii-tree
echo === libpsl ===
python src\main.py --package libpsl --repo %REPO% --ascii-tree