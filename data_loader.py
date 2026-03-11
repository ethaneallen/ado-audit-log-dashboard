"""
Data loading and parsing utilities for ADO Audit Log Analyzer
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import csv
from config import DATE_FORMATS, COLUMN_MAPPINGS


def load_data(uploaded_file):
    """Load and parse the CSV audit log file with robust error handling"""
    try:
        # Try multiple parsing strategies
        parsing_attempts = [
            # Strategy 1: Standard C parser (fast)
            {
                'engine': 'c',
                'encoding': 'utf-8',
                'on_bad_lines': 'skip'
            },
            # Strategy 2: Python parser with standard quoting
            {
                'engine': 'python',
                'encoding': 'utf-8',
                'quoting': 1,
                'doublequote': True
            },
            # Strategy 3: Lenient Python parser
            {
                'engine': 'python',
                'encoding': 'utf-8',
                'on_bad_lines': 'skip',
                'quoting': 3  # QUOTE_NONE
            },
            # Strategy 4: Very lenient with error skipping
            {
                'engine': 'python',
                'encoding': 'utf-8',
                'on_bad_lines': 'skip',
                'quotechar': '"',
                'skipinitialspace': True
            }
        ]
        
        last_error = None
        for i, strategy in enumerate(parsing_attempts, 1):
            try:
                uploaded_file.seek(0)  # Reset file position
                df = pd.read_csv(uploaded_file, **strategy)
                
                # Success!
                if i > 1:
                    st.info(f"✅ Loaded CSV with parsing strategy #{i} - {len(df)} rows and {len(df.columns)} columns")
                else:
                    st.success(f"✅ Loaded CSV with {len(df):,} rows and {len(df.columns)} columns")
                break
            except Exception as e:
                last_error = e
                continue
        else:
            # All strategies failed
            raise last_error
        
        # Show columns in an expander for debugging
        with st.expander("📋 View CSV Columns"):
            st.write("**Columns found in your CSV file:**")
            for i, col in enumerate(df.columns, 1):
                st.write(f"{i}. `{col}`")
            
            st.markdown("---")
            st.write("**First 3 rows preview:**")
            st.dataframe(df.head(3), use_container_width=True)
        
        # Normalize and map columns
        df = normalize_columns(df)
        
        # Parse dates
        df = parse_dates(df)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        show_troubleshooting_tips(uploaded_file)
        return None


def normalize_columns(df):
    """Normalize column names - simplified to preserve original columns"""
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Remove duplicate columns if any (keep first)
    if df.columns.duplicated().any():
        st.warning("⚠️ Duplicate column names in CSV. Keeping first occurrence.")
        df = df.loc[:, ~df.columns.duplicated()]

    # The CSV already has "Actor Name", "Event", etc. - just use them!
    # Only add missing required columns as empty
    required_cols = ['Actor Name', 'Event', 'Action', 'Date', 'Description', 'IP Address']

    for col in required_cols:
        if col not in df.columns:
            df[col] = ''
            st.warning(f"⚠️ Column '{col}' not found - using empty values")
        else:
            # Fill NaN values
            if col != 'Date':
                df[col] = df[col].fillna('')

    return df



def parse_dates(df):
    """Parse date column with multiple format attempts"""
    if 'Date' not in df.columns:
        return df
    
    df['DateTime'] = None
    
    # Try each date format
    for date_format in DATE_FORMATS:
        try:
            parsed = pd.to_datetime(df['Date'], format=date_format, errors='coerce')
            # If we got some valid dates, use them
            if not parsed.isna().all():
                df['DateTime'] = df['DateTime'].fillna(parsed)
        except Exception:
            continue
    
    # Final fallback: let pandas infer the format
    if df['DateTime'].isna().all():
        df['DateTime'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Report parsing success
    if 'DateTime' in df.columns and not df['DateTime'].isna().all():
        valid_dates = df['DateTime'].notna().sum()
        total_dates = len(df)
        st.info(f"📅 Successfully parsed {valid_dates:,} of {total_dates:,} dates ({valid_dates/total_dates*100:.1f}%)")
    
    return df


def show_troubleshooting_tips(uploaded_file):
    """Display troubleshooting information when file loading fails"""
    st.markdown("### 💡 Troubleshooting Tips:")
    st.markdown("""
    **Common issues:**
    1. **CSV format issues** - The file may have inconsistent columns
       - Try opening in Excel and re-saving as CSV (UTF-8)
       - Check for extra commas in the data
    
    2. **Encoding issues** - Try saving with UTF-8 encoding
    
    3. **Wrong file type** - Make sure it's a CSV file from ADO audit logs
    
    4. **Corrupted file** - Try downloading the audit log again
    
    **Expected CSV format:**
    - Columns: Date, Event, Description, Actor Name, Actor Email, Action, etc.
    - Each row should have the same number of columns
    """)
    
    # Offer to try reading the first few lines
    st.markdown("---")
    if st.button("🔍 Try to Read First Few Lines Anyway"):
        try:
            uploaded_file.seek(0)
            csv_reader = csv.reader(uploaded_file.read().decode('utf-8').splitlines())
            header = next(csv_reader)
            st.write(f"**Found {len(header)} columns:**")
            st.write(header)
            
            st.write("**First few data rows:**")
            for i, row in enumerate(csv_reader):
                if i >= 5:
                    break
                st.write(f"Row {i+1}: {len(row)} fields - {row[:3]}... (truncated)")
        except Exception as debug_error:
            st.error(f"Could not read file: {debug_error}")


def safe_column_access(df, col_name, default=''):
    """Safely access a column that might not exist"""
    if col_name in df.columns:
        col_data = df[col_name]
        # If we got a DataFrame (duplicate columns), take the first column
        if isinstance(col_data, pd.DataFrame):
            return col_data.iloc[:, 0]
        return col_data
    return pd.Series([default] * len(df), index=df.index)


def safe_unique_values(df, col_name):
    """Safely get unique values from a column"""
    if col_name in df.columns:
        try:
            # Get unique values, drop NaN, and exclude empty strings
            col_data = df[col_name]
            
            # If we got a DataFrame (duplicate columns), take the first column
            if isinstance(col_data, pd.DataFrame):
                col_data = col_data.iloc[:, 0]
            
            values = col_data.dropna().unique()
            # Filter out empty strings and sort
            values = sorted([v for v in values if str(v).strip() != ''])
            return values
        except Exception as e:
            # If anything goes wrong, return empty list
            return []
    return []
