# Getting Started with ADO Audit Log Analyzer

## Welcome! 👋

This guide will help you get up and running with the ADO Audit Log Analyzer in just a few minutes.

## Step 1: Install Python (if needed)

Check if Python is installed:
```powershell
python --version
```

If not installed, download Python 3.8+ from [python.org](https://www.python.org/downloads/)

## Step 2: Install Dependencies

Open PowerShell or Command Prompt in the project folder and run:
```powershell
pip install -r requirements.txt
```

This installs:
- streamlit (web framework)
- pandas (data processing)
- plotly (charts)
- openpyxl (Excel support)

## Step 3: Launch the App

### Option A: Use the Batch File (Easiest)
Double-click `START_APP.bat`

### Option B: Use Command Line
```powershell
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Step 4: Upload Your Audit Log

1. Export audit logs from Azure DevOps as CSV
2. In the app, click "Browse files" or drag-and-drop your CSV
3. Wait for the file to load (you'll see a success message)

## Step 5: Start Analyzing!

### Quick Start Workflows

#### Find What Broke
1. Click **"Last 7 Days"** quick filter
2. Click **"Risky Actions"** quick filter  
3. Look at the timeline for spikes
4. Click on the spike date to see details

#### Track Permission Changes
1. Click **"Permission Changes"** quick filter
2. Go to **Permissions** tab
3. Review the "Who Did What To Whom" matrix
4. Export the report if needed

#### Investigate a User
1. Go to **Users** tab
2. Select the user from dropdown
3. Review their activity timeline
4. Check their risk score

#### Compare Time Periods
1. Go to **Compare Periods** tab
2. Select "before incident" date range
3. Select "after incident" date range
4. Review the differences

## Understanding the Interface

### Top Metrics Bar
Shows at-a-glance stats:
- Total Entries
- Unique Users
- Permission Changes
- Risky Actions
- Unique IPs

### Quick Filters (One-Click)
- **All Deletions**: Show delete/remove operations
- **Permission Changes**: Show permission mods
- **Risky Actions**: Show high-risk actions
- **Access Changes**: Show access grants/revokes
- **Today**: Show today's activity
- **Last 7 Days**: Show last week

### Sidebar Filters (Detailed)
- Date range picker
- User filter
- Action type filter
- Event type filter
- Risk level filter

### Tabs
- **Search & Filter**: Main search interface
- **Permissions**: Permission analysis
- **Users**: User activity
- **Dashboard**: Overview charts
- **Analytics**: Deep analysis
- **Risk Analysis**: Risky actions focus
- **Timeline**: Activity over time
- **Alerts**: Critical alerts
- **Compare Periods**: Time comparison
- **Reference**: Column help

## Common Tasks

### Export Data
1. Apply your filters
2. Click "📥 Export CSV" button
3. Save the file

### Search for Something
1. Type in the search box
2. Searches: names, events, descriptions, IPs
3. Combine with filters for precision

### Reset Everything
Click "🔄 Reset All Filters" in the sidebar

### Copy Data
1. Filter to what you need
2. Click "📋 Copy Data" button
3. Select and copy the displayed text

## Tips for Success

### 🎯 Start Broad, Then Narrow
1. Start with quick filters
2. Add date range
3. Add specific search terms
4. Export results

### 📊 Use Visualizations
- Timeline shows activity spikes
- Charts show patterns
- Metrics show trends

### 🔍 Investigate Systematically
1. When did it happen? (Timeline)
2. Who did it? (Users tab)
3. What changed? (Search & Filter)
4. Why is it risky? (Risk Analysis)

### 💾 Export Early, Export Often
- Export full dataset first
- Then export filtered views
- Keep for documentation

## Customization (Optional)

Want to customize? Edit `config.py`:

```python
# Add your own risk keywords
RISKY_ACTIONS = {
    'delete', 'remove', 'your_keyword'
}

# Add your own quick filters
QUICK_FILTERS = {
    'My Custom Filter': {
        'description': 'What it does',
        'filter_type': 'description_contains',
        'values': ['keyword1', 'keyword2']
    }
}
```

## Troubleshooting

### App Won't Start
```powershell
# Update streamlit
pip install --upgrade streamlit

# Try with python -m
python -m streamlit run app.py
```

### CSV Won't Load
- Make sure it's a CSV from ADO audit logs
- Check the file isn't corrupted
- Try re-exporting from ADO

### Slow Performance
- Use quick filters to reduce data
- Narrow date range
- Pagination kicks in automatically at 1000+ rows

### Can't Find Something
- Check your filters aren't too restrictive
- Try "Reset All Filters"
- Use broader search terms

## Next Steps

1. ✅ Load your first audit log
2. ✅ Try the quick filters
3. ✅ Explore different tabs
4. ✅ Export a report
5. ✅ Customize config.py (optional)

## Need More Help?

- **Quick tips**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Full documentation**: See [README.md](README.md)
- **What's new**: See [CHANGELOG.md](CHANGELOG.md)
- **Upgrading**: See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

## You're Ready! 🚀

You now know enough to start analyzing your ADO audit logs effectively. The more you use it, the more efficient you'll become at finding issues quickly.

Happy analyzing! 🔍
