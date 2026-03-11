# 🔍 ADO Audit Log Analyzer

A powerful, interactive web application built with Streamlit to help you quickly analyze Azure DevOps (ADO) audit logs. When something breaks in your ADO environment, this tool makes it easy to identify **who made what changes and when**.

> **📖 New to this tool?** Start with [GETTING_STARTED.md](GETTING_STARTED.md) or check the [INDEX.md](INDEX.md) for a complete documentation guide.

> **🆕 Upgrading from v1.0?** See [WHATS_NEW.md](WHATS_NEW.md) and [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

## ✨ Features

### 🔍 **Search & Filter**
- **Quick Filter Presets**: One-click filters for common scenarios (deletions, permissions, risky actions, date ranges)
- **Optimized Search**: Fast search across key fields only (names, events, descriptions, IPs)
- **Date Range Filtering**: Narrow down to specific time periods when issues occurred
- **Multi-Select Filters**: Filter by users, action types, and event types
- **Risk Level Filtering**: Show only risky actions or normal operations
- **Smart Column Selection**: Choose which columns to display
- **Pagination**: Automatic pagination for large datasets (>1000 rows)
- **CSV Export**: Export filtered results for further analysis or reporting
- **Copy to Clipboard**: Quick copy functionality for sharing data

### 📊 **Interactive Dashboard**
- **Key Metrics at a Glance**: Total events, unique users, risky actions, and IP addresses
- **Activity Timeline**: Visualize daily activity patterns
- **Action Distribution**: See which actions are most common
- **Event Type Breakdown**: Pie chart of event categories
- **Top Active Users**: Identify power users and their activity levels

### 📈 **Advanced Analytics**
- **User Activity Analysis**: Detailed breakdown by user with risk percentages
- **Hourly Patterns**: Discover when most activity happens
- **IP Address Analysis**: Track activity by IP and identify shared IPs
- **User-per-IP Metrics**: Spot unusual IP sharing patterns
- **Behavior Baselines**: Compare time periods to spot anomalies

### ⚠️ **Enhanced Risk Detection**
Automatically identifies potentially problematic actions:
- **Deletions & Removals**: Track destructive operations
- **Access Modifications**: Monitor permission changes
- **Updates & Patches**: Highlight configuration changes
- **After-Hours Activity**: Flag unusual timing patterns
- **Shared IP Detection**: Identify suspicious IP sharing
- **Recent Risky Actions**: See the latest concerning events
- **Risky User Rankings**: Identify users performing risky operations
- **Risky Actions Timeline**: Visualize when problems occurred
- **Dedicated Export**: Download risky actions report

### 🔄 **Compare Time Periods**
- **Side-by-Side Comparison**: Compare metrics between two date ranges
- **Change Detection**: Identify increases or decreases in activity
- **Anomaly Spotting**: Find unusual patterns by comparing to baseline periods
- **Visual Comparison Charts**: Easy-to-read comparison visualizations

### ⚙️ **Customizable Configuration**
- **Configurable Risk Keywords**: Customize what actions are flagged as risky
- **Flexible Date Formats**: Supports multiple date format variations
- **Column Mapping**: Automatically handles different CSV column names
- **Quick Filter Presets**: Customize your own quick filter shortcuts

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Install Required Packages**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Launch the Application**
   ```powershell
   streamlit run app.py
   ```
   
   Or use the provided batch file:
   ```powershell
   .\START_APP.bat
   ```

3. **Open in Browser**
   - The app will automatically open in your default browser
   - Or manually navigate to: `http://localhost:8501`

### Usage

1. **Upload Your Audit Log**
   - Click "Browse files" or drag-and-drop your CSV file
   - The CSV should be exported directly from Azure DevOps audit logs

2. **Use Quick Filters**
   - Click preset buttons like "All Deletions", "Permission Changes", or "Risky Actions"
   - Or use the sidebar for detailed filtering

3. **Explore the Tabs**
   - **Search & Filter**: Find specific events or users with quick presets
   - **Permissions**: Detailed permission change analysis
   - **Users**: User activity timelines and risk scores
   - **Dashboard**: Get an overview of activity
   - **Analytics**: Dive deep into patterns and trends
   - **Risk Analysis**: Focus on potentially problematic changes
   - **Timeline**: View activity over time
   - **Alerts**: See critical alerts and notifications
   - **Compare Periods**: Compare two time ranges to spot anomalies
   - **Reference**: Column documentation and help

4. **Investigate Issues**
   - Use quick filters or date filters to isolate when the problem occurred
   - Apply risk filters to see only concerning actions
   - Search for specific users or keywords
   - Export results for documentation

## 📋 CSV Format

The application expects a CSV file with these columns:
- `Date` - Timestamp of the event (format: "YYYY-MM-DD at HH:MM AM/PM")
- `Event` - Type of event (e.g., "Update member vault access")
- `Description` - Detailed description of what happened
- `Actor UUID` - Unique identifier for the user
- `Actor Name` - Name of the user who performed the action
- `Actor Email` - Email of the user
- `Action` - Action type (e.g., update, delete, view)
- `Object Type` - Type of object affected
- `Object UUID` - Unique identifier for the object
- `Aux Info` - Additional information
- `Aux UUID` - Auxiliary UUID
- `IP Address` - IP address of the user

## 🎯 Use Cases

### 1. **Incident Investigation**
When something breaks:
1. Set date range to when the issue started
2. Filter for risky actions only
3. Search for the affected component
4. Identify who made the change

### 2. **Security Auditing**
- Review all access modifications
- Track deletion operations
- Monitor permission changes
- Identify unusual IP addresses

### 3. **Compliance Reporting**
- Export filtered logs for audit trails
- Track user activity over time
- Generate reports on specific operations
- Document change history

### 4. **User Activity Monitoring**
- See who's most active in your ADO environment
- Track automation vs. manual changes
- Identify unusual activity patterns
- Monitor after-hours changes

## 🎨 What You'll See

### Dashboard View
- Clean, professional interface with color-coded metrics
- Interactive charts that update based on your filters
- Hover over charts for detailed information
- Responsive design that works on all screen sizes

### Risk Indicators
- 🚨 **Risky Actions**: Highlighted in red with warning badges
- ✅ **Normal Actions**: Shown in green with check marks
- 📊 **Visual Charts**: Color-coded for easy pattern recognition

## 💡 Tips & Tricks

1. **Quick Investigation**: Use quick filter buttons like "All Deletions" or "Permission Changes" for instant filtering

2. **Keyboard Shortcuts**: Use Ctrl+F to search within the displayed data

3. **Export Before Filtering**: Export the full dataset first, then apply filters for targeted exports

4. **Search is Optimized**: The search box now only searches relevant fields for better performance

5. **Timeline is Your Friend**: Look for spikes in the timeline chart to spot when issues occurred

6. **IP Tracking**: Unusual IP addresses can indicate unauthorized access

7. **Automation Detection**: Users with no email (like "RM_Automation") are typically automated processes

8. **Compare Periods**: Use the Compare Periods tab to establish baselines and spot anomalies

9. **Pagination**: Large datasets are automatically paginated for better performance

10. **Customize Risk Detection**: Edit `config.py` to customize which actions are flagged as risky

## ⚙️ Configuration

You can customize the analyzer by editing `config.py`:

- **RISKY_ACTIONS**: Keywords that flag actions as risky
- **RISKY_EVENT_KEYWORDS**: Event keywords that indicate risk
- **DATE_FORMATS**: Supported date format patterns
- **SEARCHABLE_COLUMNS**: Columns included in text search
- **QUICK_FILTERS**: Customize quick filter presets
- **ROWS_PER_PAGE**: Number of rows per page in pagination
- **MAX_ROWS_BEFORE_PAGINATION**: Threshold for enabling pagination

## 🛠️ Troubleshooting

### Column Mapping Warnings

If you see warnings like:
- "⚠️ Duplicate columns after mapping"
- "⚠️ Column 'Actor Name' not found in CSV"

**Quick fix:**
```powershell
python diagnose_csv.py your_audit_log.csv
```

This will show you what columns are in your CSV and suggest fixes.

See [COLUMN_MAPPING_GUIDE.md](COLUMN_MAPPING_GUIDE.md) for detailed help.

### App Won't Start
```powershell
# Ensure streamlit is installed
pip install --upgrade streamlit

# Try running with full path
python -m streamlit run app.py
```

### CSV Won't Load
- Verify the CSV is from ADO audit logs
- Check that dates are in a supported format (see config.py for formats)
- Ensure the file is not corrupted or empty
- The app will try multiple parsing strategies automatically

### Performance Issues
- For very large files (>100k rows), filtering may take a moment
- Pagination is automatically enabled for datasets over 1000 rows
- Close other browser tabs using the app
- Restart the Streamlit server

### Search Not Finding Results
- Make sure you're searching in the right columns (see SEARCHABLE_COLUMNS in config.py)
- Try using quick filters instead for better performance
- Check if your filters are too restrictive

## 📁 Project Structure

```
ado-audit-analyzer/
├── app.py                    # Main application entry point
├── config.py                 # Configuration and settings
├── data_loader.py            # CSV loading and parsing
├── risk_analyzer.py          # Risk detection logic
├── visualizations.py         # Chart generation
├── ui_components.py          # UI tabs and components
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── START_APP.bat            # Windows launcher
└── audit_log_analyzer.py    # Legacy single-file version (backup)
```

## 📝 Example Workflow

**Scenario**: Production broke at 2pm on Feb 13, 2026

1. Upload audit log CSV
2. Go to "Search & Filter" tab
3. Set date range to Feb 13, 2026
4. Select "Risky Only" filter
5. Look for actions between 1pm - 3pm
6. Sort by time to find the change
7. Export the filtered results for your incident report

## 🔒 Privacy & Security

- **All processing happens locally** - your audit logs never leave your machine
- **No data is stored** - files are processed in memory only
- **No external connections** - except for Streamlit's own libraries
- **Safe to use** - with sensitive audit logs

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your CSV format matches the expected structure
3. Ensure all dependencies are installed correctly

## 📄 License

Free to use for analyzing your ADO audit logs.

---

**Made with ❤️ to make your life easier when troubleshooting ADO issues**

## 📖 Additional Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Step-by-step guide for first-time users
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference card for common tasks
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and what's new
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Guide for upgrading from v1.0
- **[IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)** - Detailed list of all improvements

## 🤝 Contributing

Want to customize or extend the analyzer?
- Edit `config.py` for settings and presets
- Modules are in separate files for easy modification
- See code comments for implementation details

## 📄 License

Free to use for analyzing your ADO audit logs.
