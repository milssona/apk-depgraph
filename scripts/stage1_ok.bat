@echo off
cd /d "%~dp0.."
python src\main.py --package nginx --repo https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64 --ascii-tree --filter lib
python src\main.py --package A --repo testdata\test_repo.txt --test-mode