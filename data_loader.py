"""
Simplified data loading - just use the CSV columns as-is
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import csv
from config import DATE_FORMATS


def load_data(uploaded_file):
    """Load CSV with minimal processing and optimization"""
    try:
        uploaded_file.seek(0)

        # Count total data lines in source so we can report any skipped rows.
        try:
            raw_bytes = uploaded_file.read()
            total_lines = raw_bytes.count(b'\n')
            if raw_bytes and not raw_bytes.endswith(b'\n'):
                total_lines += 1
            expected_rows = max(total_lines - 1, 0)  # minus header
        except Exception:
            expected_rows = None
        finally:
            uploaded_file.seek(0)

        # Use a callable for on_bad_lines so we can count skipped rows.
        # Returning None still skips the line (same as 'skip').
        def _count_bad(bad_line):
            _count_bad.count += 1
            return None
        _count_bad.count = 0

        df = pd.read_csv(
            uploaded_file,
            encoding='utf-8',
            engine='python',
            on_bad_lines=_count_bad,
        )

        skipped = _count_bad.count
        if skipped > 0:
            st.warning(
                f"⚠️ Skipped {skipped:,} malformed row(s) while parsing "
                "(mismatched column counts)."
            )
        elif expected_rows is not None and expected_rows - len(df) > 0:
            gap = expected_rows - len(df)
            st.warning(f"⚠️ {gap:,} row(s) in the source file were not loaded.")

        st.success(f"✅ Loaded {len(df):,} rows and {len(df.columns)} columns")
        
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        
        # Remove duplicate columns
        if df.columns.duplicated().any():
            df = df.loc[:, ~df.columns.duplicated()]
        
        # Map the actual ADO column names to what the app expects
        column_map = {
            'ActorDisplayName': 'Actor Name',
            'CategoryDisplayName': 'Event',
            'ActionId': 'Action',
            'Timestamp': 'Date',
            'Details': 'Description',
            'IpAddress': 'IP Address'
        }
        
        # Rename columns that exist
        rename_dict = {}
        for old_name, new_name in column_map.items():
            if old_name in df.columns:
                rename_dict[old_name] = new_name
        
        if rename_dict:
            df.rename(columns=rename_dict, inplace=True)
        
        # Add any still missing columns as empty
        required = ['Actor Name', 'Event', 'Action', 'Date', 'Description', 'IP Address']
        for col in required:
            if col not in df.columns:
                df[col] = ''
        
        # Parse dates
        df = parse_dates(df)
        
        # Optimize memory usage
        df = optimize_dataframe(df)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def optimize_dataframe(df):
    """Optimize dataframe for better performance"""
    # Convert object columns to category for memory efficiency
    for col in ['Actor Name', 'Event', 'Action', 'Description', 'IP Address']:
        if col in df.columns and df[col].dtype == 'object':
            # Only convert if it will save memory (less than 50% unique values)
            if df[col].nunique() / len(df) < 0.5:
                df[col] = df[col].astype('category')
    
    return df


def parse_dates(df):
    """Parse date column"""
    if 'Date' not in df.columns:
        return df
    
    df['DateTime'] = pd.to_datetime(df['Date'], errors='coerce')
    
    if not df['DateTime'].isna().all():
        valid = df['DateTime'].notna().sum()
        st.info(f"📅 Parsed {valid:,} of {len(df):,} dates")
    
    return df


def safe_column_access(df, col_name, default=''):
    """Safely access a column"""
    if col_name in df.columns:
        col_data = df[col_name]
        if isinstance(col_data, pd.DataFrame):
            return col_data.iloc[:, 0]
        return col_data
    return pd.Series([default] * len(df), index=df.index)


def safe_unique_values(df, col_name):
    """Safely get unique values"""
    if col_name in df.columns:
        try:
            col_data = df[col_name]
            if isinstance(col_data, pd.DataFrame):
                col_data = col_data.iloc[:, 0]
            values = col_data.dropna().unique()
            values = sorted([v for v in values if str(v).strip() != ''])
            return values
        except:
            return []
    return []
