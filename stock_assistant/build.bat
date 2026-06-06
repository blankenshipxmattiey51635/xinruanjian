@echo off
setlocal
cd /d %~dp0
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
pyinstaller --noconfirm --windowed --name StockAssistant --add-data "config;config" --add-data "data;data" main.py
echo.
echo 打包完成后请查看 dist\StockAssistant\StockAssistant.exe
pause
