# 🔍 ADO Audit Log Analyzer

A powerful, interactive web application built with Streamlit to help you quickly analyze Azure DevOps (ADO) audit logs. When something breaks in your ADO environment, this tool makes it easy to identify **who made what changes and when**.

## ✨ Features

### 🔍 **Search & Filter**
- **Advanced Search**: Search across all log fields (names, events, descriptions, IPs)
- **Date Range Filtering**: Narrow down to specific time periods when issues occurred
- **Multi-Select Filters**: Filter by users, action types, and event types
- **Risk Level Filtering**: Show only risky actions or normal operations
- **Smart Column Selection**: Choose which columns to display
- **CSV Export**: Export filtered results for further analysis or reporting

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

### ⚠️ **Risky Actions Detection**
Automatically identifies potentially problematic actions:
- **Deletions & Removals**: Track destructive operations
- **Access Modifications**: Monitor permission changes
- **Updates & Patches**: Highlight configuration changes
- **Recent Risky Actions**: See the latest concerning events
- **Risky User Rankings**: Identify users performing risky operations
- **Risky Actions Timeline**: Visualize when problems occurred
- **Dedicated Export**: Download risky actions report

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
   streamlit run audit_log_analyzer.py
   ```

3. **Open in Browser**
   - The app will automatically open in your default browser
   - Or manually navigate to: `http://localhost:8501`

### Usage

1. **Upload Your Audit Log**
   - Click "Browse files" or drag-and-drop your CSV file
   - The CSV should be exported directly from Azure DevOps audit logs

2. **Explore the Tabs**
   - **Search & Filter**: Find specific events or users
   - **Dashboard**: Get an overview of activity
   - **Analytics**: Dive deep into patterns and trends
   - **Risky Actions**: Focus on potentially problematic changes

3. **Investigate Issues**
   - Use date filters to isolate when the problem occurred
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

1. **Quick Investigation**: Use the "Risky Only" filter + date range to immediately find problematic changes

2. **Export Before Filtering**: Export the full dataset first, then apply filters for targeted exports

3. **Search is Powerful**: The search box searches ALL fields, not just visible ones

4. **Timeline is Your Friend**: Look for spikes in the timeline chart to spot when issues occurred

5. **IP Tracking**: Unusual IP addresses can indicate unauthorized access

6. **Automation Detection**: Users with no email (like "RM_Automation") are typically automated processes

## 🛠️ Troubleshooting

### App Won't Start
```powershell
# Ensure streamlit is installed
pip install --upgrade streamlit

# Try running with full path
python -m streamlit run audit_log_analyzer.py
```

### CSV Won't Load
- Verify the CSV is from ADO audit logs
- Check that dates are in the expected format
- Ensure the file is not corrupted or empty

### Performance Issues
- For very large files (>100k rows), filtering may take a moment
- Close other browser tabs using the app
- Restart the Streamlit server

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
