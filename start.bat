@echo off

if not exist "venv\" (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt

if not exist ".env" (
    echo .env file not found! create it with your API_KEY
    pause
    exit
)

python run.py

echo.
echo backend on port:1000 running
pause
