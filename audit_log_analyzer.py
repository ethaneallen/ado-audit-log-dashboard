"""
ADO Audit Log Analyzer
A comprehensive Streamlit application for analyzing Azure DevOps audit logs
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

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
</style>
""", unsafe_allow_html=True)

# Define risky actions that might cause issues
RISKY_ACTIONS = {
    'delete', 'remove', 'revoke', 'destroy', 'terminate',
    'update', 'modify', 'change', 'patch', 'edit'
}

RISKY_EVENT_KEYWORDS = {
    'delete', 'remove', 'revoke', 'destroy', 'terminate',
    'update', 'modify', 'change', 'access'
}

def load_data(uploaded_file):
    """Load and parse the CSV audit log file"""
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
                    st.info(f"✅ Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
                break
            except Exception as e:
                last_error = e
                continue
        else:
            # All strategies failed
            raise last_error
        
        # Display the columns found (for debugging)
        st.info(f"✅ Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        
        # Show columns in an expander for debugging
        with st.expander("📋 View CSV Columns"):
            st.write("**Columns found in your CSV file:**")
            for i, col in enumerate(df.columns, 1):
                st.write(f"{i}. `{col}`")
            
            st.markdown("---")
            st.write("**First 3 rows preview:**")
            st.dataframe(df.head(3), use_container_width=True)
        
        # Normalize column names - strip whitespace and handle common variations
        df.columns = df.columns.str.strip()
        
        # Create a column mapping for flexible column name matching
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower().replace(' ', '').replace('_', '')
            if 'actorname' in col_lower or 'username' in col_lower:
                column_mapping['Actor Name'] = col
            elif 'actoremail' in col_lower or 'useremail' in col_lower or 'email' in col_lower:
                column_mapping['Actor Email'] = col
            elif 'actoruuid' in col_lower or 'userid' in col_lower:
                column_mapping['Actor UUID'] = col
            elif col_lower == 'date' or col_lower == 'timestamp':
                column_mapping['Date'] = col
            elif col_lower == 'event' or col_lower == 'eventtype':
                column_mapping['Event'] = col
            elif col_lower == 'action' or col_lower == 'actiontype':
                column_mapping['Action'] = col
            elif 'description' in col_lower:
                column_mapping['Description'] = col
            elif 'ipaddress' in col_lower or col_lower == 'ip':
                column_mapping['IP Address'] = col
            elif 'objecttype' in col_lower:
                column_mapping['Object Type'] = col
            elif 'objectuuid' in col_lower:
                column_mapping['Object UUID'] = col
        
        # Rename columns if mappings found
        if column_mapping:
            df.rename(columns={v: k for k, v in column_mapping.items()}, inplace=True)
        
        # Ensure required columns exist - add them if missing
        required_cols = ['Actor Name', 'Event', 'Action', 'Date', 'Description', 'IP Address']
        for col in required_cols:
            if col not in df.columns:
                # Add missing column with empty values
                df[col] = ''
                st.warning(f"Column '{col}' not found in CSV - using empty values")
            else:
                # Replace any NaN values with empty strings for string columns
                if col != 'Date':  # Don't replace Date NaNs yet
                    df[col] = df[col].fillna('')
        
        # Parse the date column
        if 'Date' in df.columns:
            # Handle the format "2026-02-13 at 7:28 AM" or other common formats
            df['DateTime'] = pd.to_datetime(df['Date'], format='%Y-%m-%d at %I:%M %p', errors='coerce')
            # Try alternative formats if the above didn't work
            if df['DateTime'].isna().all():
                df['DateTime'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Add risk indicator
        df['IsRisky'] = df.apply(is_risky_action, axis=1)
        
        return df
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
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
                # Read just the header
                import csv
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
        
        return None

def is_risky_action(row):
    """Determine if an action is potentially risky"""
    action = str(row.get('Action', '')).lower()
    event = str(row.get('Event', '')).lower()
    description = str(row.get('Description', '')).lower()
    
    # Check if action or event contains risky keywords
    if any(keyword in action for keyword in RISKY_ACTIONS):
        return True
    if any(keyword in event for keyword in RISKY_EVENT_KEYWORDS):
        return True
    if 'delete' in description or 'remove' in description:
        return True
    
    return False

def safe_column_access(df, col_name, default=''):
    """Safely access a column that might not exist"""
    if col_name in df.columns:
        return df[col_name]
    return pd.Series([default] * len(df), index=df.index)

def safe_unique_values(df, col_name):
    """Safely get unique values from a column"""
    if col_name in df.columns:
        # Get unique values, drop NaN, and exclude empty strings
        values = df[col_name].dropna().unique()
        # Filter out empty strings and sort
        values = sorted([v for v in values if str(v).strip() != ''])
        return values
    return []

def get_risk_badge(is_risky):
    """Return HTML badge for risk level"""
    if is_risky:
        return '<span class="risky-action">⚠️ RISKY</span>'
    return '<span class="normal-action">✓ Normal</span>'

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
        # Load data
        with st.spinner("Loading audit log data..."):
            df = load_data(uploaded_file)
        
        if df is not None:
            st.success(f"✅ Loaded {len(df):,} audit log entries")
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs([
                "🔍 Search & Filter",
                "📊 Dashboard",
                "📈 Analytics",
                "⚠️ Risky Actions"
            ])
            
            # TAB 1: Search & Filter
            with tab1:
                show_search_and_filter(df)
            
            # TAB 2: Dashboard
            with tab2:
                show_dashboard(df)
            
            # TAB 3: Analytics
            with tab3:
                show_analytics(df)
            
            # TAB 4: Risky Actions
            with tab4:
                show_risky_actions(df)
    else:
        # Show welcome screen
        st.info("👆 Please upload an audit log CSV file to get started")
        
        st.markdown("### 📋 Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🔍 Search & Filter**
            - Search by user name
            - Filter by date range
            - Filter by action type
            - Export filtered results
            """)
        
        with col2:
            st.markdown("""
            **📊 Dashboard**
            - Activity timeline
            - Top users by activity
            - Action type distribution
            - IP address tracking
            """)
        
        with col3:
            st.markdown("""
            **⚠️ Risk Detection**
            - Identify risky actions
            - Track deletions/modifications
            - Access changes monitoring
            - Quick incident investigation
            """)

def show_search_and_filter(df):
    """Search and filter interface"""
    st.subheader("🔍 Search and Filter Audit Logs")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Reset button
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        
        # Date range filter
        st.subheader("📅 Date Range")
        if 'DateTime' in df.columns and not df['DateTime'].isna().all():
            min_date = df['DateTime'].min().date()
            max_date = df['DateTime'].max().date()
            
            date_range = st.date_input(
                "Select date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        else:
            date_range = None
        
        # Actor name filter
        st.subheader("👤 User")
        all_actors = safe_unique_values(df, 'Actor Name')
        selected_actors = st.multiselect(
            "Filter by user",
            options=['All'] + all_actors,
            default=['All']
        )
        
        # Action filter
        st.subheader("⚡ Action Type")
        all_actions = safe_unique_values(df, 'Action')
        selected_actions = st.multiselect(
            "Filter by action",
            options=['All'] + all_actions,
            default=['All']
        )
        
        # Event filter
        st.subheader("📝 Event Type")
        all_events = safe_unique_values(df, 'Event')
        selected_events = st.multiselect(
            "Filter by event",
            options=['All'] + all_events,
            default=['All']
        )
        
        # Risk filter
        st.subheader("⚠️ Risk Level")
        risk_filter = st.radio(
            "Show",
            options=['All Actions', 'Risky Only', 'Normal Only']
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    # Date filter
    if date_range and len(date_range) == 2 and 'DateTime' in df.columns and not df['DateTime'].isna().all():
        start_date, end_date = date_range
        # Ensure we're comparing dates properly
        mask = (filtered_df['DateTime'].dt.date >= start_date) & (filtered_df['DateTime'].dt.date <= end_date)
        filtered_df = filtered_df[mask]
    
    # Actor filter
    if 'All' not in selected_actors and selected_actors and 'Actor Name' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Actor Name'].isin(selected_actors)]
    
    # Action filter
    if 'All' not in selected_actions and selected_actions and 'Action' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Action'].isin(selected_actions)]
    
    # Event filter
    if 'All' not in selected_events and selected_events and 'Event' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Event'].isin(selected_events)]
    
    # Risk filter
    if risk_filter == 'Risky Only':
        filtered_df = filtered_df[filtered_df['IsRisky'] == True]
    elif risk_filter == 'Normal Only':
        filtered_df = filtered_df[filtered_df['IsRisky'] == False]
    
    # Search box
    search_query = st.text_input(
        "🔎 Search across all fields",
        placeholder="Enter keywords to search...",
        help="Search in all columns including description, user names, events, etc."
    )
    
    if search_query:
        mask = filtered_df.astype(str).apply(
            lambda row: row.str.contains(search_query, case=False, na=False).any(),
            axis=1
        )
        filtered_df = filtered_df[mask]
    
    # Display results
    st.markdown(f"### 📋 Results: {len(filtered_df):,} entries")
    
    # Debug info in expander
    with st.expander("🔧 Filter Debug Info"):
        st.write(f"**Original data:** {len(df):,} rows")
        st.write(f"**After filters:** {len(filtered_df):,} rows")
        st.write(f"**Date range active:** {date_range is not None and len(date_range) == 2}")
        st.write(f"**DateTime column exists:** {'DateTime' in df.columns}")
        if 'DateTime' in df.columns:
            st.write(f"**DateTime has values:** {not df['DateTime'].isna().all()}")
            st.write(f"**DateTime min:** {df['DateTime'].min()}")
            st.write(f"**DateTime max:** {df['DateTime'].max()}")
        st.write(f"**Actor filter active:** {'All' not in selected_actors and len(selected_actors) > 0}")
        st.write(f"**Action filter active:** {'All' not in selected_actions and len(selected_actions) > 0}")
        st.write(f"**Event filter active:** {'All' not in selected_events and len(selected_events) > 0}")
        st.write(f"**Risk filter:** {risk_filter}")
        if search_query:
            st.write(f"**Search query:** '{search_query}'")
    
    # Export button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"filtered_audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Show/hide columns selector
        if st.checkbox("Select Columns"):
            # Only include columns that exist in the dataframe
            default_cols = [col for col in ['Date', 'Event', 'Actor Name', 'Description', 'Action', 'IsRisky'] if col in filtered_df.columns]
            selected_cols = st.multiselect(
                "Choose columns to display",
                options=list(filtered_df.columns),
                default=default_cols
            )
            if selected_cols:
                filtered_df = filtered_df[selected_cols]
    
    # Display dataframe with risk highlighting
    if not filtered_df.empty:
        # Create a copy for display
        display_df = filtered_df.copy()
        
        # Format the risk column
        if 'IsRisky' in display_df.columns:
            display_df['Risk'] = display_df['IsRisky'].apply(lambda x: '⚠️ RISKY' if x else '✓ Normal')
            display_df = display_df.drop('IsRisky', axis=1)
        
        # Show dataframe
        st.dataframe(
            display_df,
            use_container_width=True,
            height=600
        )
    else:
        st.warning("No results found matching your filters")

def show_dashboard(df):
    """Dashboard with key metrics and visualizations"""
    st.subheader("📊 Audit Log Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events = len(df)
        st.metric("Total Events", f"{total_events:,}")
    
    with col2:
        unique_users = safe_column_access(df, 'Actor Name').nunique()
        st.metric("Unique Users", f"{unique_users:,}")
    
    with col3:
        risky_count = df['IsRisky'].sum()
        risky_pct = (risky_count / len(df) * 100) if len(df) > 0 else 0
        st.metric("Risky Actions", f"{risky_count:,}", f"{risky_pct:.1f}%")
    
    with col4:
        unique_ips = safe_column_access(df, 'IP Address').nunique()
        st.metric("Unique IPs", f"{unique_ips:,}")
    
    st.markdown("---")
    
    # Timeline chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📅 Activity Timeline")
        if 'DateTime' in df.columns and not df['DateTime'].isna().all():
            timeline_df = df.groupby(df['DateTime'].dt.date).size().reset_index()
            timeline_df.columns = ['Date', 'Count']
            
            fig = px.line(
                timeline_df,
                x='Date',
                y='Count',
                title='Daily Activity',
                markers=True
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Events",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("DateTime information not available")
    
    with col2:
        st.markdown("#### ⚡ Action Distribution")
        action_counts = df['Action'].value_counts().head(10)
        
        fig = px.bar(
            x=action_counts.values,
            y=action_counts.index,
            orientation='h',
            title='Top 10 Actions',
            labels={'x': 'Count', 'y': 'Action Type'}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Event types and Top users
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📝 Event Types")
        event_counts = df['Event'].value_counts().head(10)
        
        fig = px.pie(
            values=event_counts.values,
            names=event_counts.index,
            title='Top 10 Event Types'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 👥 Most Active Users")
        if 'Actor Name' in df.columns:
            user_counts = df['Actor Name'].value_counts().head(10)
            
            fig = px.bar(
                x=user_counts.values,
                y=user_counts.index,
                orientation='h',
                title='Top 10 Users by Activity',
                labels={'x': 'Number of Actions', 'y': 'User'}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("User information not available in this dataset")

def show_analytics(df):
    """Detailed analytics and insights"""
    st.subheader("📈 Advanced Analytics")
    
    # User activity analysis
    st.markdown("### 👤 User Activity Analysis")
    
    if 'Actor Name' in df.columns:
        user_activity = df.groupby('Actor Name').agg({
            'Event': 'count',
            'IsRisky': 'sum',
            'Action': lambda x: x.value_counts().index[0] if len(x) > 0 else 'N/A'
        }).reset_index()
        user_activity.columns = ['User', 'Total Actions', 'Risky Actions', 'Most Common Action']
        user_activity['Risk %'] = (user_activity['Risky Actions'] / user_activity['Total Actions'] * 100).round(1)
        user_activity = user_activity.sort_values('Total Actions', ascending=False)
        
        st.dataframe(
            user_activity.head(20),
            use_container_width=True,
            height=400
        )
    else:
        st.info("User activity information not available in this dataset")
    
    # Hourly activity pattern
    st.markdown("### ⏰ Activity Patterns by Hour")
    if 'DateTime' in df.columns and not df['DateTime'].isna().all():
        hourly_activity = df.groupby(df['DateTime'].dt.hour).size().reset_index()
        hourly_activity.columns = ['Hour', 'Count']
        
        fig = px.bar(
            hourly_activity,
            x='Hour',
            y='Count',
            title='Activity by Hour of Day',
            labels={'Hour': 'Hour of Day (24h)', 'Count': 'Number of Events'}
        )
        fig.update_xaxes(tickmode='linear', tick0=0, dtick=1)
        st.plotly_chart(fig, use_container_width=True)
    
    # IP Address analysis
    st.markdown("### 🌐 IP Address Analysis")
    col1, col2 = st.columns(2)
    
    if 'IP Address' in df.columns:
        with col1:
            ip_counts = df['IP Address'].value_counts().head(15)
            st.markdown("#### Top 15 IP Addresses")
            
            fig = px.bar(
                x=ip_counts.values,
                y=ip_counts.index,
                orientation='h',
                labels={'x': 'Number of Actions', 'y': 'IP Address'}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Actor Name' in df.columns:
                users_per_ip = df.groupby('IP Address')['Actor Name'].nunique().sort_values(ascending=False).head(15)
                st.markdown("#### IPs with Most Users")
                
                fig = px.bar(
                    x=users_per_ip.values,
                    y=users_per_ip.index,
                    orientation='h',
                    labels={'x': 'Number of Unique Users', 'y': 'IP Address'}
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("User information not available")
    else:
        st.info("IP Address information not available in this dataset")

def show_risky_actions(df):
    """Focus on risky/suspicious actions"""
    st.subheader("⚠️ Risky Actions Analysis")
    
    risky_df = df[df['IsRisky'] == True].copy()
    
    if risky_df.empty:
        st.success("✅ No risky actions detected in this audit log!")
        return
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Risky Actions",
            f"{len(risky_df):,}",
            f"{len(risky_df)/len(df)*100:.1f}% of all actions"
        )
    
    with col2:
        if 'Actor Name' in risky_df.columns:
            risky_users = risky_df['Actor Name'].nunique()
            st.metric("Users with Risky Actions", f"{risky_users:,}")
        else:
            st.metric("Users with Risky Actions", "N/A")
    
    with col3:
        if 'DateTime' in risky_df.columns and not risky_df['DateTime'].isna().all():
            latest_risky = risky_df['DateTime'].max()
            st.metric("Latest Risky Action", latest_risky.strftime("%Y-%m-%d %H:%M"))
    
    st.markdown("---")
    
    # Recent risky actions
    st.markdown("### 🚨 Most Recent Risky Actions")
    
    # Select only columns that exist
    available_cols = [col for col in ['Date', 'Event', 'Description', 'Actor Name', 'Action', 'IP Address'] if col in risky_df.columns]
    
    if 'DateTime' in risky_df.columns and not risky_df['DateTime'].isna().all():
        recent_risky = risky_df.nlargest(20, 'DateTime')[available_cols]
    else:
        recent_risky = risky_df.head(20)[available_cols]
    
    if not recent_risky.empty:
        st.dataframe(recent_risky, use_container_width=True, height=400)
    else:
        st.info("No risky actions to display")
    
    # Risky users ranking
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Users with Most Risky Actions")
        if 'Actor Name' in risky_df.columns:
            risky_user_counts = risky_df['Actor Name'].value_counts().head(15)
            
            fig = px.bar(
                x=risky_user_counts.values,
                y=risky_user_counts.index,
                orientation='h',
                labels={'x': 'Number of Risky Actions', 'y': 'User'},
                color=risky_user_counts.values,
                color_continuous_scale='Reds'
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("User information not available")
    
    with col2:
        st.markdown("### ⚡ Risky Action Types")
        if 'Action' in risky_df.columns:
            risky_action_counts = risky_df['Action'].value_counts().head(10)
            
            fig = px.pie(
                values=risky_action_counts.values,
                names=risky_action_counts.index,
                color_discrete_sequence=px.colors.sequential.Reds_r
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Action information not available")
    
    # Timeline of risky actions
    if 'DateTime' in risky_df.columns and not risky_df['DateTime'].isna().all():
        st.markdown("### 📊 Risky Actions Timeline")
        risky_timeline = risky_df.groupby(risky_df['DateTime'].dt.date).size().reset_index()
        risky_timeline.columns = ['Date', 'Count']
        
        fig = px.area(
            risky_timeline,
            x='Date',
            y='Count',
            title='Daily Risky Actions',
            color_discrete_sequence=['#D13438']
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Risky Actions",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Export risky actions
    st.markdown("### 📥 Export Risky Actions")
    csv = risky_df.to_csv(index=False)
    st.download_button(
        label="Download Risky Actions Report (CSV)",
        data=csv,
        file_name=f"risky_actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
