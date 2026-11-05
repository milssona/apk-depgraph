@echo off
cd /d "%~dp0.."
set REPO=https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64
echo === diamond, PlantUML text ===
python src\main.py --package A --repo testdata\test_repo.txt --test-mode --plantuml
echo === diamond, picture from PlantUML server ===
python src\main.py --package A --repo testdata\test_repo.txt --test-mode --image diamond.png
echo === nginx, picture from PlantUML server ===
python src\main.py --package nginx --repo %REPO% --image nginx.png