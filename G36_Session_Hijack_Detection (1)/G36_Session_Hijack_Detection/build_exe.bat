@echo off
REM Builds a standalone Windows executable: dist\G36_Detection.exe
pip install -r requirements.txt pyinstaller
pyinstaller --onefile --name G36_Detection --paths src ^
  --exclude-module tkinter --exclude-module IPython --exclude-module lxml ^
  --exclude-module PyQt5 --exclude-module PyQt6 src\evaluate.py
echo.
echo Done. Run dist\G36_Detection.exe  (copy it into the exe\ folder for submission)
pause
