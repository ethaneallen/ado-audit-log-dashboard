@echo off
echo ========================================
echo ADO Audit Log Analyzer - Installation
echo ========================================
echo.

REM Check if Python is installed
echo Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    REM Try common Python installation paths
    set "PYTHON_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
    if exist "%PYTHON_PATH%" (
        echo.
        echo Found Python at: %PYTHON_PATH%
        goto :install_packages
    )
    
    set "PYTHON_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
    if exist "%PYTHON_PATH%" (
        echo.
        echo Found Python at: %PYTHON_PATH%
        goto :install_packages
    )
    
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    if exist "%PYTHON_PATH%" (
        echo.
        echo Found Python at: %PYTHON_PATH%
        goto :install_packages
    )
    
    set "PYTHON_PATH=C:\Program Files\Python312\python.exe"
    if exist "%PYTHON_PATH%" (
        echo.
        echo Found Python at: %PYTHON_PATH%
        goto :install_packages
    )
    
    echo.
    echo [WARNING] Python is not installed!
    echo.
    echo Attempting to install Python via winget...
    echo.
    
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    
    REM Check if winget command succeeded (it returns various codes, so we check the output)
    echo.
    echo Checking installation result...
    
    REM Even if winget succeeded, Python won't be in PATH until terminal restarts
    echo.
    echo ========================================
    echo Python Installation Attempted
    echo ========================================
    echo.
    echo If you saw "Successfully installed" above:
    echo.
    echo 1. CLOSE this window completely
    echo 2. Open a NEW PowerShell or Command Prompt
    echo 3. Navigate back to: %CD%
    echo 4. Run: install.bat
    echo.
    echo If installation failed:
    echo 1. Go to: https://www.python.org/downloads/
    echo 2. Download Python 3.12 or later
    echo 3. CHECK "Add Python to PATH" during install
    echo 4. Restart computer
    echo 5. Run install.bat again
    echo.
    pause
    exit /b 0
)

:install_packages
REM If we get here, either python is in PATH or PYTHON_PATH is set

if defined PYTHON_PATH (
    echo.
    echo Using: %PYTHON_PATH%
    "%PYTHON_PATH%" --version
    echo.
    echo Installing required packages...
    echo.
    "%PYTHON_PATH%" -m pip install --upgrade pip
    "%PYTHON_PATH%" -m pip install -r requirements.txt
) else (
    echo Python found: 
    python --version
    if defined PYTHON_PATH (
        "%PYTHON_PATH%" -m ensurepip --default-pip
        "%PYTHON_PATH%" -m pip install --upgrade pip
        "%PYTHON_PATH%" -m pip install -r requirements.txt
    ) else (
        python -m ensurepip --default-pip
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
    )
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Package installation failed.
    echo.
    echo Trying alternative installation method...
    python -m ensurepip --default-pip
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo To run the application, use: run_app.bat
echo.
pause
