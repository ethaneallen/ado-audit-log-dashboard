# Answer: Are These Warnings Normal?

## Your Question
> Is this message normal?
> ⚠️ Duplicate columns after mapping. Keeping first occurrence only...
> ⚠️ Column 'Actor Name' not found in CSV - using empty values

## Short Answer

**These warnings are NOT normal for a standard ADO audit log export**, but they're not critical errors. The app will still work, but with limited functionality.

## What This Means

### Warning 1: "Duplicate columns after mapping"
Your CSV has multiple columns that the app is trying to map to the same standard name. The app automatically handles this by keeping only the first one.

**Impact:** Minor - the app works fine, just using the first column

### Warning 2: "Actor Name not found"
The app couldn't find a column containing user names in your CSV.

**Impact:** Major - User-related features won't work:
- ❌ User activity analysis
- ❌ Risk scores by user  
- ❌ "Who did what" reports
- ❌ User filtering

## Why This Happens

1. **Your CSV has non-standard column names**
   - ADO exports can vary by version/configuration
   - Custom exports may use different names

2. **Your CSV is missing columns**
   - Incomplete export
   - Wrong export type
   - Permissions limited what was exported

3. **Your CSV has duplicate columns**
   - Export included redundant data
   - Multiple similar columns

## What To Do

### Step 1: Diagnose Your CSV

Run this command to see what's actually in your CSV:

```powershell
python diagnose_csv.py your_audit_log.csv
```

This will show you:
- ✅ All columns in your file
- ✅ What mappings were found
- ✅ What's missing
- ✅ Specific recommendations

### Step 2: Choose a Fix

**Option A: Re-export from ADO (Easiest)**
1. Go back to Azure DevOps
2. Export audit logs again
3. Make sure to include all columns
4. Upload the new file

**Option B: Add Custom Mappings**
1. Run the diagnostic tool (Step 1)
2. See what columns you have
3. Edit `config.py` and add your column names
4. Restart the app

**Option C: Rename Columns**
1. Open CSV in Excel
2. Rename columns to match expected names
3. Save as CSV (UTF-8)
4. Upload to app

## Expected Columns

A standard ADO audit log should have columns like:
- ActorDisplayName or ActorName (user who did the action)
- ActorUPN or ActorEmail (user's email)
- Timestamp or Date (when it happened)
- CategoryDisplayName or Event (what type of event)
- ActionId or Action (specific action taken)
- Details or Description (description of what happened)
- IpAddress (IP address)

## Can I Still Use The App?

**Yes, but with limitations:**

✅ **Will work:**
- Basic data viewing
- Date filtering
- Search functionality
- Export data
- Timeline view (if dates are present)

❌ **Won't work well:**
- User analysis (no user names)
- Risk scores by user
- User activity timelines
- "Who did what" reports
- User filtering

## Recommended Action

1. **Run the diagnostic tool:**
   ```powershell
   python diagnose_csv.py your_audit_log.csv
   ```

2. **Review the output** - it will tell you exactly what's wrong

3. **Follow the recommendations** - usually re-exporting is easiest

4. **If you need help** - see [COLUMN_MAPPING_GUIDE.md](COLUMN_MAPPING_GUIDE.md)

## Quick Test

To see if your CSV is usable:
1. Look at the "View CSV Columns" expander in the app
2. Check if you see columns with user names, dates, and actions
3. If yes, you can add custom mappings
4. If no, you need to re-export from ADO

## Bottom Line

**These warnings mean your CSV doesn't match the expected format.** The app will work, but user-related features will be limited. Run the diagnostic tool to see exactly what's wrong and get specific fix recommendations.

**Most common solution:** Re-export the audit log from Azure DevOps with all columns included.
