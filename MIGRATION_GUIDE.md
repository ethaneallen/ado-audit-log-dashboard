# Migration Guide

## Upgrading from v1.0 to v2.0

The new version has been completely refactored for better performance and maintainability. Here's what you need to know:

### What Changed

#### File Structure
- **Old**: Single `audit_log_analyzer.py` file
- **New**: Modular structure with multiple files
  - `app.py` - Main entry point
  - `config.py` - Configuration
  - `data_loader.py` - Data loading
  - `risk_analyzer.py` - Risk analysis
  - `visualizations.py` - Charts
  - `ui_components.py` - UI components

#### Running the App
- **Old**: `streamlit run audit_log_analyzer.py`
- **New**: `streamlit run app.py` or use `START_APP.bat`

### Backward Compatibility

The old `audit_log_analyzer.py` file is kept as a backup. You can still use it if needed:
```powershell
streamlit run audit_log_analyzer.py
```

However, we recommend migrating to the new version for:
- Better performance
- More features
- Easier customization
- Better maintainability

### New Features You'll Love

1. **Quick Filter Presets**: Click buttons for instant filtering
2. **Compare Periods**: New tab to compare time ranges
3. **Pagination**: Better handling of large datasets
4. **Optimized Search**: Faster search across key fields
5. **Customizable Config**: Easy customization via config.py

### Customization

If you customized the old version, here's how to migrate your changes:

#### Custom Risk Keywords
**Old**: Edit `RISKY_ACTIONS` in `audit_log_analyzer.py`
**New**: Edit `RISKY_ACTIONS` in `config.py`

#### Custom Date Formats
**Old**: Edit date parsing logic in `load_data()` function
**New**: Add formats to `DATE_FORMATS` list in `config.py`

#### Custom Columns
**Old**: Edit column mapping in `load_data()` function
**New**: Edit `COLUMN_MAPPINGS` dictionary in `config.py`

### No Data Migration Needed

Your CSV files work exactly the same way. No changes needed to your data or export process.

### Getting Help

If you encounter issues:
1. Check the [README.md](README.md) for updated documentation
2. Review [CHANGELOG.md](CHANGELOG.md) for all changes
3. Check the troubleshooting section in README
4. The old version is still available as a fallback

### Recommended Steps

1. **Backup**: Keep your old `audit_log_analyzer.py` (already done)
2. **Test**: Try the new version with a sample CSV
3. **Customize**: Edit `config.py` if needed
4. **Deploy**: Update your shortcuts/scripts to use `app.py`

### Performance Improvements

You should notice:
- Faster search (especially on large datasets)
- Better responsiveness with pagination
- Quicker filter application
- Smoother UI interactions

### Questions?

The new modular structure makes it easier to:
- Understand the code
- Make customizations
- Add new features
- Debug issues

Each module has clear responsibilities and is well-documented.
