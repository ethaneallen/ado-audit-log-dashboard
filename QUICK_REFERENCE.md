# Quick Reference Card

## 🚀 Getting Started

```powershell
# Start the app
streamlit run app.py
# or
.\START_APP.bat
```

## ⚡ Quick Filters (One-Click)

| Filter | What It Does |
|--------|-------------|
| **All Deletions** | Shows delete/remove operations |
| **Permission Changes** | Shows permission modifications |
| **Risky Actions** | Shows high-risk actions only |
| **Access Changes** | Shows access grants/revokes |
| **Today** | Shows today's activity |
| **Last 7 Days** | Shows last week's activity |

## 🔍 Search Tips

- Search box looks in: Actor Name, Email, Description, Event, Action, IP, Scope, Project
- Use quotes for exact phrases: `"delete pipeline"`
- Combine with filters for precise results
- Case-insensitive by default

## 📊 Tabs Overview

| Tab | Purpose |
|-----|---------|
| 🔍 **Search & Filter** | Find specific events with quick filters |
| 🔐 **Permissions** | Analyze permission changes |
| 👥 **Users** | User activity and risk scores |
| 📊 **Dashboard** | Overview metrics and charts |
| 📈 **Analytics** | Deep dive into patterns |
| ⚠️ **Risk Analysis** | Focus on risky actions |
| 📋 **Timeline** | Activity over time |
| 🚨 **Alerts** | Critical alerts and warnings |
| 🔄 **Compare Periods** | Compare two time ranges |
| 📚 **Reference** | Column documentation |

## 🎯 Common Workflows

### Investigate an Incident
1. Click **"Last 7 Days"** quick filter
2. Click **"Risky Actions"** quick filter
3. Use date picker to narrow to incident time
4. Search for affected component
5. Export results

### Find Who Changed Permissions
1. Click **"Permission Changes"** quick filter
2. Go to **Permissions** tab
3. Review "Who Did What To Whom" matrix
4. Export report

### Compare Before/After
1. Go to **Compare Periods** tab
2. Select "before" date range
3. Select "after" date range
4. Review metrics and changes

### Track User Activity
1. Go to **Users** tab
2. Select user from dropdown
3. Review timeline
4. Check risk score

## 📥 Export Options

- **CSV Export**: Full data export
- **Filtered Export**: Export current filtered view
- **Report Export**: Export specific analysis
- **Copy to Clipboard**: Quick copy for sharing

## ⚙️ Customization

Edit `config.py` to customize:
- Risk detection keywords
- Quick filter presets
- Date format support
- Search columns
- Pagination settings

## 🔑 Keyboard Shortcuts

- `Ctrl + F`: Search in browser
- `Ctrl + Click`: Open link in new tab
- `Esc`: Close dialogs/expanders
- `Tab`: Navigate between fields

## 💡 Pro Tips

1. **Use Quick Filters First**: Faster than manual filtering
2. **Export Before Filtering**: Keep full dataset backup
3. **Check Timeline**: Spot activity spikes visually
4. **Compare Periods**: Establish baselines
5. **Bookmark Filters**: Save common filter combinations
6. **Check Alerts Tab**: Auto-detected issues
7. **Use Pagination**: Better performance on large datasets
8. **Review Reference Tab**: Understand column meanings

## 🚨 Risk Indicators

| Indicator | Meaning |
|-----------|---------|
| 🔴 High | Deletions, bulk changes, after-hours |
| 🟡 Medium | Updates, modifications, shared IPs |
| 🟢 Low | Normal operations |
| ⚠️ RISKY | Flagged action |
| ✓ Normal | Safe action |

## 📊 Metrics Explained

- **Total Events**: All audit log entries
- **Unique Users**: Different users in logs
- **Permission Changes**: Permission modifications
- **Risky Actions**: Flagged high-risk actions
- **Unique IPs**: Different IP addresses
- **Risk %**: Percentage of risky actions

## 🔧 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| CSV won't load | Check file format, try re-export |
| Slow performance | Use pagination, reduce date range |
| No results | Check filters, try "Reset All Filters" |
| Missing columns | App auto-fills missing columns |
| Date parsing fails | Check DATE_FORMATS in config.py |

## 📞 Need Help?

1. Check **Reference** tab for column info
2. Review **README.md** for detailed docs
3. Check **CHANGELOG.md** for recent changes
4. Review **MIGRATION_GUIDE.md** if upgrading

## 🎨 Visual Indicators

- **Red background**: Risky actions
- **Green background**: Normal actions
- **Blue border**: Metric cards
- **Orange badge**: Warnings
- **Red badge**: Critical alerts
