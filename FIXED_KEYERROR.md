# KeyError Fix - Risk Score (%)

## Issue
When viewing the Users tab, you encountered:
```
KeyError: 'Risk Score (%)'
```

## Root Cause
The `calculate_user_risk_scores()` function was trying to sort an empty DataFrame by the 'Risk Score (%)' column. This happened when:
1. The CSV had no valid user data (all Actor Names were empty/NaN)
2. The risk_data list was empty
3. `pd.DataFrame([])` created an empty DataFrame with no columns
4. `.sort_values('Risk Score (%)')` failed because the column didn't exist

## Fix Applied

Added a check to return early if there's no data to process:

```python
# Return empty DataFrame if no data
if not risk_data:
    return pd.DataFrame()

risk_df = pd.DataFrame(risk_data).sort_values('Risk Score (%)', ascending=False)
return risk_df
```

## Status
✅ **FIXED** - The app will now handle cases where there are no valid users gracefully.

## What Happens Now
When there are no valid users in the data:
1. The function returns an empty DataFrame immediately
2. The UI shows "Unable to calculate risk scores" message
3. No error is thrown

## How to Test
```powershell
streamlit run app.py
```

Upload your CSV file and navigate to the Users tab - it should now work without errors.

## Related Improvements
The fix also ensures that:
- Empty or whitespace-only usernames are skipped
- NaN values in Actor Name are handled properly
- The function gracefully handles edge cases

## If You Still Have Issues
1. Check if your CSV has an "Actor Name" or similar column
2. Verify the column mapping in the "View CSV Columns" expander
3. Check if the Actor Name column has any non-empty values
4. Review the data in the Search & Filter tab to see what's loaded
