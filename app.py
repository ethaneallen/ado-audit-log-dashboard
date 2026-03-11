"""
ADO Audit Log Analyzer - Main Application
A comprehensive Streamlit application for analyzing Azure DevOps audit logs
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# Import custom modules
from data_loader_simple import load_data, safe_column_access, safe_unique_values
from risk_analyzer import (
    analyze_risks, parse_json_field, extract_permission_changes,
    calculate_user_risk_scores, detect_critical_alerts, get_risk_badge
)
from visualizations import (
    create_timeline_chart, create_action_distribution_chart,
    create_event_pie_chart, create_user_activity_chart,
    create_hourly_activity_chart, create_ip_activity_chart,
    create_users_per_ip_chart, create_risky_users_chart,
    create_risky_action_types_chart, create_risky_timeline_chart,
    create_comparison_chart
)
from config import (
    DEFAULT_DISPLAY_COLUMNS, SEARCHABLE_COLUMNS, QUICK_FILTERS,
    ROWS_PER_PAGE, MAX_ROWS_BEFORE_PAGINATION
)
from ui_components import (
    show_welcome_screen, show_search_and_filter, show_permissions_tab,
    show_users_tab, show_dashboard, show_analytics, show_risky_actions,
    show_timeline_tab, show_alerts_tab, show_comparison_tab, show_column_reference
)

# Page configuration
st.set_page_config(
    page_title="ADO Audit Log Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0078D4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0078D4;
    }
    .risky-action {
        background-color: #FFE5E5;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        color: #D13438;
        font-weight: bold;
    }
    .normal-action {
        background-color: #E5F5E5;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        color: #107C10;
    }
    .quick-filter-btn {
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<div class="main-header">🔍 ADO Audit Log Analyzer</div>', unsafe_allow_html=True)
    st.markdown("**Quickly identify who did what and when in your Azure DevOps audit logs**")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your ADO Audit Log CSV file",
        type=['csv'],
        help="Upload the CSV file exported from Azure DevOps audit logs"
    )
    
    if uploaded_file is not None:
        # Cache the file content for faster reloads
        file_content = uploaded_file.read()
        uploaded_file.seek(0)
        
        # Load data with caching
        with st.spinner("Loading audit log data..."):
            df = load_data(uploaded_file)
        
        if df is not None:
            # Add risk analysis with progress
            with st.spinner("Analyzing risks..."):
                df = analyze_risks(df)
            
            # Show memory usage
            memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
            st.success(f"✅ Loaded {len(df):,} entries ({memory_usage:.1f} MB in memory)")
            
            # Create tabs for different views
            tabs = st.tabs([
                "🔍 Search & Filter",
                "🔐 Permissions",
                "👥 Users",
                "📊 Dashboard",
                "📈 Analytics",
                "⚠️ Risk Analysis",
                "📋 Timeline",
                "🚨 Alerts",
                "🔄 Compare Periods",
                "📚 Reference"
            ])
            
            with tabs[0]:
                show_search_and_filter(df)
            
            with tabs[1]:
                show_permissions_tab(df)
            
            with tabs[2]:
                show_users_tab(df)
            
            with tabs[3]:
                show_dashboard(df)
            
            with tabs[4]:
                show_analytics(df)
            
            with tabs[5]:
                show_risky_actions(df)
            
            with tabs[6]:
                show_timeline_tab(df)
            
            with tabs[7]:
                show_alerts_tab(df)
            
            with tabs[8]:
                show_comparison_tab(df)
            
            with tabs[9]:
                show_column_reference(df)
    else:
        show_welcome_screen()


if __name__ == "__main__":
    main()
