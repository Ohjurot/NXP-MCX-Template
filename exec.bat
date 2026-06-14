@echo off
REM Windows launcher for running python scripts

REM cd to repo root so all scripts see a consistent cwd; pushd/popd restores caller's directory
pushd "%~dp0"

REM Ensure the venv exists and requirements are installed
python %~dp0env\env.py
IF %ERRORLEVEL% NEQ 0 (popd & exit /b %ERRORLEVEL%)

REM Add venv Scripts folder to PATH
SET "PATH=%~dp0env\env\Scripts;%PATH%"

REM Run the script with venv python
%~dp0env\env\Scripts\python.exe %~dp0scripts\%*.py
SET MOX_EXIT=%errorlevel%
popd
exit /b %MOX_EXIT%
