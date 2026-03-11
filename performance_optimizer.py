"""
Performance optimization utilities
"""

import streamlit as st
import pandas as pd
from functools import lru_cache
import hashlib


def get_dataframe_hash(df):
    """Create a hash of the dataframe for caching"""
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()


@st.cache_data(ttl=3600)
def cache_dataframe_load(file_content, file_name):
    """Cache the loaded dataframe"""
    import io
    from data_loader_simple import load_data
    
    file_obj = io.BytesIO(file_content)
    return load_data(file_obj)


@st.cache_data(ttl=3600)
def cache_risk_analysis(df_hash, df_json):
    """Cache risk analysis results"""
    from risk_analyzer import analyze_risks
    df = pd.read_json(df_json)
    return analyze_risks(df)


@st.cache_data(ttl=3600)
def cache_user_list(df_hash, actor_name_series):
    """Cache unique user list"""
    return sorted([v for v in actor_name_series.dropna().unique() if str(v).strip() != ''])


@st.cache_data(ttl=3600)
def cache_filter_results(df_hash, filter_params):
    """Cache filtered dataframe results"""
    # This will be called with filter parameters
    pass


def optimize_dataframe(df):
    """Optimize dataframe memory usage"""
    # Convert object columns to category where appropriate
    for col in df.columns:
        if df[col].dtype == 'object':
            num_unique = df[col].nunique()
            num_total = len(df[col])
            
            # If less than 50% unique values, convert to category
            if num_unique / num_total < 0.5:
                df[col] = df[col].astype('category')
    
    return df


def create_indexes(df):
    """Create indexes for faster filtering"""
    # Sort by commonly filtered columns
    if 'DateTime' in df.columns and not df['DateTime'].isna().all():
        df = df.sort_values('DateTime')
    
    return df


def batch_process_large_dataset(df, batch_size=5000):
    """Process large datasets in batches"""
    num_batches = (len(df) - 1) // batch_size + 1
    return num_batches, batch_size
