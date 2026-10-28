@echo off
cd /d "%~dp0.."
echo --- no package
python src\main.py --repo https://example.com/alpine
echo --- bad package name
python src\main.py --package "bad name" --repo https://example.com/alpine
echo --- bad url
python src\main.py --package nginx --repo ftp://example.com/alpine
echo --- test file is missing
python src\main.py --package A --repo missing.txt --test-mode
echo --- bad filter
python src\main.py --package nginx --repo https://example.com/alpine --filter "a b"
echo --- unknown option
python src\main.py --package nginx --repo https://example.com/alpine --color