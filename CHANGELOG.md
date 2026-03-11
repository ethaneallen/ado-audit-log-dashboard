# Changelog

All notable changes to the ADO Audit Log Analyzer.

## [2.0.1] - Hotfix Release

### 🐛 Bug Fixes
- **Fixed Import Error**: Moved ui_components import to top of app.py (NameError fix)
- **Fixed DataFrame Error**: Added handling for duplicate column names in CSV files
- **Fixed KeyError**: Added empty data check in calculate_user_risk_scores()
- **Enhanced Error Handling**: Better handling of edge cases with missing/invalid data

### 🔧 Technical Improvements
- `safe_column_access()` now handles DataFrame returns from duplicate columns
- `safe_unique_values()` now handles DataFrame returns from duplicate columns
- `normalize_columns()` now detects and removes duplicate columns automatically
- `calculate_user_risk_scores()` now returns empty DataFrame for invalid data

### 📚 Documentation
- Added FIXED_IMPORT_ERROR.md
- Added FIXED_DATAFRAME_ERROR.md
- Added FIXED_KEYERROR.md
- Added TROUBLESHOOTING_FIXES.md

## [2.0.0] - Enhanced Version

### 🎉 Major Improvements

#### Architecture
- **Modular Design**: Split monolithic file into organized modules
  - `config.py`: Centralized configuration
  - `data_loader.py`: CSV loading and parsing
  - `risk_analyzer.py`: Risk detection logic
  - `visualizations.py`: Chart generation
  - `ui_components.py`: UI tabs and components
  - `app.py`: Main application entry point

#### Performance
- **Optimized Search**: Now searches only relevant columns instead of entire dataframe
- **Pagination**: Automatic pagination for datasets over 1000 rows
- **Faster Filtering**: Improved filter application logic
- **Better Memory Usage**: More efficient data handling

#### Features
- **Quick Filter Presets**: One-click filters for common scenarios
  - All Deletions
  - Permission Changes
  - Risky Actions
  - Access Changes
  - Today's Activity
  - Last 7 Days
- **Compare Time Periods**: New tab to compare two date ranges
- **Enhanced Risk Detection**: Additional risk patterns
  - After-hours activity detection
  - Shared IP address detection
  - Bulk operation detection
- **Copy to Clipboard**: Quick copy functionality for data sharing
- **Better Date Parsing**: Supports multiple date format variations
- **Flexible Column Mapping**: Handles different CSV column name variations

#### User Experience
- **Improved Navigation**: Better tab organization
- **Better Visual Feedback**: Enhanced metrics and indicators
- **Keyboard Shortcuts**: Better keyboard navigation support
- **Export Options**: Multiple export formats and options
- **Help Documentation**: Comprehensive column reference guide

#### Configuration
- **Customizable Risk Keywords**: Edit config.py to customize risk detection
- **Configurable Quick Filters**: Add your own quick filter presets
- **Adjustable Pagination**: Configure rows per page
- **Custom Date Formats**: Add support for your date formats

### 🐛 Bug Fixes
- Fixed date parsing issues with different locale formats
- Improved handling of missing columns
- Better error messages for CSV loading failures
- Fixed search performance issues with large datasets
- Resolved pagination edge cases

### 📚 Documentation
- Updated README with new features
- Added configuration guide
- Improved troubleshooting section
- Added project structure documentation
- Created this CHANGELOG

### 🔧 Technical Improvements
- Better code organization and maintainability
- Improved error handling throughout
- More defensive programming for missing data
- Better type handling and validation
- Cleaner separation of concerns

## [1.0.0] - Initial Release

### Features
- Basic CSV loading and parsing
- Search and filter functionality
- Dashboard with key metrics
- Risk detection for common issues
- Permission change tracking
- User activity analysis
- Export to CSV
- Multiple analysis tabs
