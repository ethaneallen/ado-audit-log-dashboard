# Saved Filters Guide

## What Are Saved Filters?

Saved Filters let you save your favorite filter combinations and quickly apply them later. Perfect for:
- Recurring investigations
- Team-specific views
- Common analysis patterns
- Quick access to frequently used filters

## How to Use

### Saving a Filter

1. **Apply your filters** in the Search & Filter tab:
   - Select date range
   - Choose users
   - Pick actions/events
   - Set risk level
   - Enter search terms

2. **Click "💾 Save Current Filters"** expander

3. **Enter a name** for your filter:
   - "Last Week Risky Actions"
   - "My Team Activity"
   - "Permission Changes This Month"
   - "Deployment Issues"

4. **Click "💾 Save Filter"**

5. **Done!** Your filter is saved and ready to use anytime

### Loading a Saved Filter

1. Go to **Search & Filter** tab

2. Look for **💾 Saved Filters** section at the top

3. **Click the filter name** you want to load

4. **Filters are applied automatically!**

### Managing Saved Filters

**View Details:**
- Click the "ℹ️" button next to any filter
- See when it was created and last used
- View what filters are included

**Delete a Filter:**
- Click the "🗑️" button next to the filter
- Confirm deletion

## Examples

### Example 1: Weekly Security Review
**Name:** "Weekly Security Review"
**Filters:**
- Date: Last 7 days
- Risk: Risky Only
- Actions: All
- Users: All

**Use case:** Every Monday, load this filter to review last week's risky actions

### Example 2: My Team's Activity
**Name:** "DevOps Team"
**Filters:**
- Users: John, Sarah, Mike, Lisa
- Date: Last 30 days
- Risk: All Actions

**Use case:** Track what your team has been doing

### Example 3: Permission Changes
**Name:** "Permission Audits"
**Filters:**
- Quick Filter: Permission Changes
- Date: This month
- Risk: All Actions

**Use case:** Monthly permission change review

### Example 4: Deployment Tracking
**Name:** "Prod Deployments"
**Filters:**
- Search: "deploy"
- Event: Execute
- Date: Last 7 days

**Use case:** Track recent deployments

## Tips

### Naming Conventions

Good names are:
- ✅ "Last Week Risky Actions"
- ✅ "My Team - Feb 2026"
- ✅ "Permission Changes - Monthly"
- ✅ "Deployment Issues"

Avoid:
- ❌ "Filter 1"
- ❌ "Test"
- ❌ "asdf"

### Organization

Create filters for:
- **Time-based**: "This Week", "Last Month", "Q1 2026"
- **Team-based**: "DevOps Team", "Security Team", "Admins"
- **Action-based**: "Deletions", "Permission Changes", "Deployments"
- **Investigation**: "Incident Feb 13", "Outage Investigation"

### Best Practices

1. **Save frequently used combinations** - Don't save one-time searches

2. **Update regularly** - Delete old filters you don't use

3. **Use descriptive names** - You'll thank yourself later

4. **Share with team** - Tell colleagues about useful filters

5. **Create templates** - Save base filters, then adjust dates as needed

## Where Are Filters Stored?

Filters are saved in `saved_filters.json` in the app directory.

**To backup your filters:**
```powershell
copy saved_filters.json saved_filters_backup.json
```

**To share filters with team:**
1. Copy your `saved_filters.json`
2. Send to teammate
3. They place it in their app directory

## Troubleshooting

### Filter doesn't load correctly
- The data might have changed (users removed, etc.)
- Try resetting and re-saving the filter

### Can't save filter
- Check you have write permissions in the app directory
- Make sure the filter has a name

### Filter disappeared
- Check if `saved_filters.json` exists
- Restore from backup if needed

## Advanced: Editing Filters Manually

You can edit `saved_filters.json` directly:

```json
{
  "My Filter": {
    "config": {
      "date_range": ["2026-02-01", "2026-02-28"],
      "actors": ["Allen, Ethan", "Denis, Anthony"],
      "actions": ["All"],
      "events": ["All"],
      "risk_filter": "Risky Only",
      "search_query": null
    },
    "created": "2026-02-13T10:30:00",
    "last_used": "2026-02-13T14:45:00"
  }
}
```

**Warning:** Invalid JSON will break the feature. Always backup first!

## Keyboard Shortcuts

While no direct shortcuts exist, you can:
1. Save commonly used filters
2. Load them with one click
3. Much faster than manually setting filters each time!

## Future Enhancements

Potential future features:
- Export/import filter sets
- Share filters via URL
- Schedule filters to run automatically
- Filter templates library

## Questions?

**Q: How many filters can I save?**
A: Unlimited! But keep it manageable (10-20 is reasonable)

**Q: Can I edit a saved filter?**
A: Not directly - delete and re-save with same name

**Q: Do filters work across different CSV files?**
A: Yes, but user names/actions must match

**Q: Can I save quick filters?**
A: Quick filters are already saved! This is for custom combinations

## Summary

Saved Filters = **Save time** + **Consistency** + **Easy sharing**

Perfect for recurring analysis tasks!
