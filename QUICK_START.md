# 🚀 QUICK START GUIDE

## First Time Setup

### **ONE-CLICK INSTALLATION** (Recommended)

Just double-click `install.bat` - it will:
1. ✓ Check if Python is installed
2. ✓ Install Python automatically if needed (via winget)
3. ✓ Install all required packages
4. ✓ Let you know when ready!

**Alternative:** Right-click `install.ps1` → "Run with PowerShell"

### **Manual Installation** (if automatic fails)

**Step 1: Install Python**
1. Go to: https://www.python.org/downloads/
2. Download Python 3.12 or later
3. **CRITICAL**: ✓ Check "Add Python to PATH" during installation
4. Restart your computer
5. Run `install.bat` again

**Step 2: Install Packages**
```powershell
python -m pip install -r requirements.txt
```

## Running the App

### Easy Method (Windows):
- Double-click `run_app.bat`
- Your browser will automatically open the app

### Manual Method:
```powershell
py -m streamlit run audit_log_analyzer.py
```

Or:
```powershell
streamlit run audit_log_analyzer.py
```

## Using the App

1. **Upload Your Audit Log**
   - Click "Browse files" button
   - Select your ADO audit log CSV file
   - Example: `Audit Log 2026-02-13.csv`

2. **Start Investigating!**
   - Use filters in the sidebar
   - Search for users or keywords
   - Check the "Risky Actions" tab first
   - Export results as needed

## Quick Troubleshooting

### "Python is not recognized"
- Python is not installed or not in PATH
- Download from: https://www.python.org/downloads/
- Make sure to check "Add to PATH" during installation

### "streamlit is not recognized"
- Run `install.bat` first
- Or manually: `py -m pip install streamlit`

### App won't open in browser
- Manually go to: http://localhost:8501

### CSV won't load
- Make sure it's exported from ADO audit logs
- Check that the file has the correct columns

## Example Investigation

**Scenario**: Something broke on Feb 13 at 2pm

1. Upload your audit log CSV
2. Go to "Search & Filter" tab
3. Set date to Feb 13, 2026
4. Select "Risky Only" filter
5. Look for events around 2pm
6. Export the results

## Need Help?

Check the full README.md for detailed documentation.

---

**Pro Tip**: Bookmark http://localhost:8501 for quick access while the app is running!
