@echo off
REM Builds a standalone Windows executable (dist\G36_Detection.exe)
pip install -r requirements.txt pyinstaller
pyinstaller --onefile --name G36_Detection --paths src src\evaluate.py
echo.
echo Done. Run dist\G36_Detection.exe
pause
