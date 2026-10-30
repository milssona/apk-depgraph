@echo off
cd /d "%~dp0.."
set REPO=https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64
python src\main.py --package nginx --repo %REPO% --ascii-tree --filter lib
python src\main.py --package A --repo testdata\test_repo.txt --test-mode