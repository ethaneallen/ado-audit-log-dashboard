# ADO Audit Log Analyzer - PowerShell Installation Script
# This script will check for Python and install it if needed

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ADO Audit Log Analyzer - Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if Python is installed
function Test-PythonInstalled {
    try {
        $version = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python found: $version" -ForegroundColor Green
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Function to install Python using winget
function Install-Python {
    Write-Host ""
    Write-Host "Python is not installed. Attempting to install..." -ForegroundColor Yellow
    Write-Host ""
    
    # Check if winget is available
    try {
        $null = Get-Command winget -ErrorAction Stop
        Write-Host "Installing Python 3.12 via winget..." -ForegroundColor Cyan
        
        winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✓ Python installed successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "IMPORTANT: Please do the following:" -ForegroundColor Yellow
            Write-Host "1. Close this PowerShell window" -ForegroundColor Yellow
            Write-Host "2. Open a NEW PowerShell window" -ForegroundColor Yellow
            Write-Host "3. Run the installation script again" -ForegroundColor Yellow
            Write-Host ""
            Read-Host "Press Enter to exit"
            exit 0
        } else {
            throw "Installation failed"
        }
    } catch {
        Write-Host ""
        Write-Host "✗ Automatic installation failed." -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install Python manually:" -ForegroundColor Yellow
        Write-Host "1. Go to: https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "2. Download Python 3.12 or later" -ForegroundColor White
        Write-Host "3. Run the installer" -ForegroundColor White
        Write-Host "4. ✓ CHECK 'Add Python to PATH' during installation" -ForegroundColor Green
        Write-Host "5. Restart your computer" -ForegroundColor White
        Write-Host "6. Run this script again" -ForegroundColor White
        Write-Host ""
        
        $openBrowser = Read-Host "Open Python download page in browser? (Y/N)"
        if ($openBrowser -eq 'Y' -or $openBrowser -eq 'y') {
            Start-Process "https://www.python.org/downloads/"
        }
        
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check for Python
if (-not (Test-PythonInstalled)) {
    Install-Python
}

# If we got here, Python is installed
Write-Host ""
Write-Host "Installing required Python packages..." -ForegroundColor Cyan
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Gray
python -m pip install --upgrade pip --quiet

# Install requirements
Write-Host "Installing streamlit, pandas, plotly..." -ForegroundColor Gray
python -m pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ Installation complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "To run the application:" -ForegroundColor Cyan
    Write-Host "  Option 1: Double-click run_app.bat" -ForegroundColor White
    Write-Host "  Option 2: Run: python -m streamlit run audit_log_analyzer.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✗ Package installation failed." -ForegroundColor Red
    Write-Host "Trying alternative method..." -ForegroundColor Yellow
    
    python -m ensurepip --default-pip
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Installation successful!" -ForegroundColor Green
    } else {
        Write-Host "✗ Installation failed. Please check your internet connection." -ForegroundColor Red
    }
}

Write-Host ""
Read-Host "Press Enter to exit"
