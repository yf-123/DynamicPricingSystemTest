@echo off

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM Create necessary directories
if not exist models mkdir models
if not exist logs mkdir logs

echo Setup completed successfully!
pause 