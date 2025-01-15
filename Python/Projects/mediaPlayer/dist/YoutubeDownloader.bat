@echo off
echo Checking paths...
if not exist "%~dp0Scripts\python.exe" (
    echo Python executable not found at "%~dp0Scripts\python.exe"
    pause
)
if not exist "%~dp0_req.txt" (
    echo Requirements file not found at "%~dp0_req.txt"
    pause
)
if not exist "%~dp0Main.py" (
    echo Main script not found at "%~dp0Main.py"
    pause
)
echo Paths are correct.
"%~dp0\Scripts\python.exe" -m pip install -r "%~dp0_req.txt"
"%~dp0\Scripts\python.exe" "%~dp0Main.py"
pause