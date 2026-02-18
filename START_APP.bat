@echo off
REM ADO Audit Log Analyzer - Quick Launch Script
echo Starting ADO Audit Log Analyzer...

"%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run audit_log_analyzer.py

pause
