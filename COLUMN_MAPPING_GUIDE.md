# Column Mapping Guide

## Understanding the Warnings

### "Duplicate columns after mapping"
This means your CSV has multiple columns that the app is trying to map to the same standard name. The app will keep only the first occurrence.

**Common causes:**
- CSV has both "ActorDisplayName" and "ActorName" (both map to "Actor Name")
- Multiple columns with similar names
- Export included duplicate data

### "Column 'Actor Name' not found in CSV - using empty values"
This means the app couldn't find a column containing user names in your CSV.

**Impact:**
- User-related features will be limited
- User activity analysis won't work
- Risk scores by user won't be available

## Quick Diagnosis

Run the diagnostic tool to see what's in your CSV:

```powershell
python diagnose_csv.py your_audit_log.csv
```

This will show you:
- All columns in your CSV
- What mappings were found
- What's missing
- Suggestions for fixing issues

## Solution Options

### Option 1: Check Your CSV Export (Recommended)

1. Go back to Azure DevOps
2. Re-export the audit log
3. Make sure to include all columns
4. Check the export settings

**Typical ADO audit log columns:**
- ActorDisplayName or ActorName
- ActorUPN or ActorEmail  
- Timestamp or Date
- CategoryDisplayName or Event
- ActionId or Action
- Details or Description
- IpAddress

### Option 2: Add Custom Column Mappings

If your CSV has different column names, add them to `config.py`:

1. Open `config.py` in a text editor
2. Find the `COLUMN_MAPPINGS` section
3. Add your column names to the appropriate list

**Example:**

```python
COLUMN_MAPPINGS = {
    'Actor Name': [
        'actordisplayname', 
        'actorname', 
        'username', 
        'user',
        'your_column_name_here'  # Add your column name
    ],
    'Actor Email': [
        'actorupn', 
        'actoremail', 
        'useremail', 
        'email', 
        'upn',
        'your_email_column'  # Add your column name
    ],
    # ... rest of mappings
}
```

**Important:** Use lowercase, no spaces or underscores in the mapping list.

### Option 3: Rename Columns in Your CSV

1. Open your CSV in Excel or a text editor
2. Rename the columns to match expected names:
   - User column → "Actor Name"
   - Email column → "Actor Email"
   - Date column → "Date"
   - Event column → "Event"
   - Action column → "Action"
   - Description column → "Description"
   - IP column → "IP Address"
3. Save as CSV (UTF-8)
4. Upload to the app

## Expected Column Names

The app looks for these standard columns:

| Standard Name | Alternative Names Recognized |
|---------------|------------------------------|
| Actor Name | ActorDisplayName, ActorName, UserName, User |
| Actor Email | ActorUPN, ActorEmail, UserEmail, Email, UPN |
| Actor UUID | ActorUserId, UserId, ActorId |
| Date | Date, Timestamp, DateTime |
| Event | CategoryDisplayName, Category, Event, EventType |
| Action | ActionId, Action, ActionType |
| Description | Details, Description, Summary |
| IP Address | IpAddress, IP, ClientIP |
| ScopeDisplayName | ScopeDisplayName, Scope, Organization |
| ProjectName | ProjectName, Project |
| Data | Data, Details, AdditionalData |

## Troubleshooting Specific Issues

### Issue: "Actor Name" not found

**Check if your CSV has:**
- A column with user names
- A column with display names
- A column with email addresses (can be used as fallback)

**Solutions:**
1. Add your user column name to config.py:
   ```python
   'Actor Name': ['actordisplayname', 'actorname', 'username', 'user', 'YourColumnName'],
   ```

2. Or rename the column in your CSV to "Actor Name"

### Issue: Duplicate columns after mapping

**This happens when:**
- Multiple columns map to the same standard name
- Example: Both "Details" and "Description" map to "Description"

**Solutions:**
1. Check which columns are duplicates using the diagnostic tool
2. Remove one of the duplicate columns from your CSV
3. Or adjust the mapping in config.py to be more specific

### Issue: Most columns missing

**This usually means:**
- Wrong CSV file (not from ADO audit logs)
- Export was incomplete
- CSV is corrupted

**Solutions:**
1. Verify you're using an ADO audit log export
2. Re-export from ADO with all columns
3. Check the CSV isn't corrupted (open in Excel)

## Testing Your Mappings

After making changes to config.py:

1. Save the file
2. Restart the app: `streamlit run app.py`
3. Upload your CSV
4. Check the "View CSV Columns" expander
5. Look for the "Column Mappings Applied" expander
6. Verify the mappings look correct

## Example: Adding Custom Mappings

Let's say your CSV has these columns:
- "Modified By" (should be Actor Name)
- "User Email" (should be Actor Email)
- "When" (should be Date)
- "What Happened" (should be Description)

Edit config.py:

```python
COLUMN_MAPPINGS = {
    'Actor Name': [
        'actordisplayname', 'actorname', 'username', 'user',
        'modifiedby'  # Add this
    ],
    'Actor Email': [
        'actorupn', 'actoremail', 'useremail', 'email', 'upn'
        # 'useremail' already covers this
    ],
    'Date': [
        'date', 'timestamp', 'datetime',
        'when'  # Add this
    ],
    'Description': [
        'details', 'description', 'summary',
        'whathappened'  # Add this
    ],
    # ... rest unchanged
}
```

## Getting Help

If you're still having issues:

1. Run the diagnostic tool: `python diagnose_csv.py your_file.csv`
2. Check the output for suggestions
3. Review the "View CSV Columns" expander in the app
4. Check the "Column Mappings Applied" expander
5. Verify your CSV is from ADO audit logs

## Best Practices

1. **Always check the diagnostic output first**
2. **Keep a backup of your original CSV**
3. **Test with a small CSV first**
4. **Document any custom mappings you add**
5. **Re-export from ADO if possible** (easiest solution)

## Summary

The warnings are normal if:
- Your CSV has non-standard column names
- You're using a custom export format
- Your ADO instance uses different column names

The app will still work, but some features may be limited if key columns like "Actor Name" are missing.

**Recommended action:** Run the diagnostic tool to see exactly what's in your CSV and get specific recommendations.
