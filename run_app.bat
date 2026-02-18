@echo off
echo ========================================
echo Starting ADO Audit Log Analyzer...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    REM Try common Python installation paths
    set "PYTHON_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
    if not exist "%PYTHON_PATH%" set "PYTHON_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
    if not exist "%PYTHON_PATH%" set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    if not exist "%PYTHON_PATH%" set "PYTHON_PATH=C:\Program Files\Python312\python.exe"
    
    if not exist "%PYTHON_PATH%" (
        echo [ERROR] Python is not installed!
        echo.
        echo Please run install.bat first to install Python and dependencies.
        echo.
        pause
        exit /b 1
    )
) else (
    set "PYTHON_PATH=python"
)

REM Check if streamlit is installed
"%PYTHON_PATH%" -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Streamlit is not installed!
    echo.
    echo Please run install.bat first to install dependencies.
    echo.
    pause
    exit /b 1
)

echo The app will open in your default browser.
echo Press Ctrl+C in this window to stop the app.
echo.

"%PYTHON_PATH%" -m streamlit run audit_log_analyzer.py

pause
