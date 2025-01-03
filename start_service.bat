@echo off
echo Starting Xero Automation Service...
call venv\Scripts\activate
python run_service.py --interval 300
pause