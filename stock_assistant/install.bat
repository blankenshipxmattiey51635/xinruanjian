@echo off
setlocal
cd /d %~dp0
py -3.11 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo 安装完成。运行 start.bat 启动软件。
pause
