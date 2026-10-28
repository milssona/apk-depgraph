@echo off
cd /d "%~dp0.."
echo === nginx ===
python src\main.py --package nginx --repo https://dl-cdn.alpinelinux.org/alpine/latest-stable/main/x86_64
echo === curl ===
python src\main.py --package curl --repo https://dl-cdn.alpinelinux.org/alpine/latest-stable/main/x86_64
echo === no such package ===
python src\main.py --package nosuchpkg --repo https://dl-cdn.alpinelinux.org/alpine/latest-stable/main/x86_64
echo === bad repo url ===
python src\main.py --package nginx --repo http://127.0.0.1:9/x
echo === test repo ===
python src\main.py --package A --repo testdata\test_repo.txt --test-mode