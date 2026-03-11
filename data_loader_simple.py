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
        # Simple loading with error skipping
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
        
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
