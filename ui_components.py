"""
UI Components and Tab Views
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from data_loader import safe_column_access, safe_unique_values
from risk_analyzer import (
    parse_json_field, extract_permission_changes,
    calculate_user_risk_scores, detect_critical_alerts
)
from visualizations import *
from config import (
    DEFAULT_DISPLAY_COLUMNS, SEARCHABLE_COLUMNS, QUICK_FILTERS,
    ROWS_PER_PAGE, MAX_ROWS_BEFORE_PAGINATION
)
from saved_filters import (
    show_saved_filters_ui, save_filter_dialog, get_filter_config
)


def show_welcome_screen():
    """Display welcome screen when no file is uploaded"""
    st.info("👆 Please upload an audit log CSV file to get started")
    
    st.markdown("### 📋 Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔍 Search & Filter**
        - Quick filter presets
        - Search by user name
        - Filter by date range
        - Filter by action type
        - Export filtered results
        - Pagination for large datasets
        """)
    
    with col2:
        st.markdown("""
        **📊 Dashboard**
        - Activity timeline
        - Top users by activity
        - Action type distribution
        - IP address tracking
        - Compare time periods
        """)
    
    with col3:
        st.markdown("""
        **⚠️ Risk Detection**
        - Identify risky actions
        - Track deletions/modifications
        - Access changes monitoring
        - Quick incident investigation
        - After-hours activity alerts
        """)


def apply_quick_filter(df, filter_name):
    """Apply a quick filter preset to the dataframe"""
    if filter_name not in QUICK_FILTERS:
        return df
    
    filter_config = QUICK_FILTERS[filter_name]
    filter_type = filter_config['filter_type']
    values = filter_config['values']
    
    if filter_type == 'description_contains':
        mask = pd.Series([False] * len(df), index=df.index)
        if 'Description' in df.columns:
            for val in values:
                mask |= df['Description'].astype(str).str.contains(val, case=False, na=False)
        return df[mask]
    
    elif filter_type == 'action_contains':
        mask = pd.Series([False] * len(df), index=df.index)
        if 'Action' in df.columns:
            for val in values:
                mask |= df['Action'].astype(str).str.contains(val, case=False, na=False)
        if 'Event' in df.columns:
            for val in values:
                mask |= df['Event'].astype(str).str.contains(val, case=False, na=False)
        return df[mask]
    
    elif filter_type == 'risky_only':
        if 'IsRisky' in df.columns:
            return df[df['IsRisky'] == True]
        return df
    
    elif filter_type == 'date_range':
        if 'DateTime' not in df.columns or df['DateTime'].isna().all():
            return df
        
        max_date = df['DateTime'].max().date()
        
        if 'today' in values:
            return df[df['DateTime'].dt.date == max_date]
        elif 'last_7_days' in values:
            start_date = max_date - timedelta(days=7)
            return df[df['DateTime'].dt.date >= start_date]
    
    return df


def show_search_and_filter(df):
    """Enhanced search and filter interface with quick filters, pagination, and saved filters"""
    st.subheader("🔍 Search and Filter Audit Logs")
    
    # Quick stats at the top
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Entries", f"{len(df):,}")
    with col2:
        unique_users = df['Actor Name'].nunique() if 'Actor Name' in df.columns else 0
        st.metric("Unique Users", f"{unique_users}")
    with col3:
        perm_changes = (df['Action'].astype(str).str.contains('ModifyPermission|permission', case=False, na=False).sum() 
                       if 'Action' in df.columns else 0)
        st.metric("Permission Changes", f"{perm_changes}")
    with col4:
        risky_count = df['IsRisky'].sum() if 'IsRisky' in df.columns else 0
        st.metric("Risky Actions", f"{risky_count}")
    with col5:
        unique_ips = df['IP Address'].nunique() if 'IP Address' in df.columns else 0
        st.metric("Unique IPs", f"{unique_ips}")
    
    st.markdown("---")
    
    # Saved Filters Section
    st.markdown("### 📂 My Saved Filters")
    
    # Initialize session state for loaded filter
    if 'loaded_filter' not in st.session_state:
        st.session_state.loaded_filter = None
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_saved_filter = show_saved_filters_ui()
        if selected_saved_filter:
            st.session_state.loaded_filter = get_filter_config(selected_saved_filter)
            st.success(f"✅ Loaded filter: {selected_saved_filter}")
            st.rerun()
    
    st.markdown("---")
    
    # Quick Filters Section
    st.markdown("### ⚡ Quick Filters")
    st.caption("Click a preset to quickly filter the data")
    
    quick_filter_cols = st.columns(len(QUICK_FILTERS))
    selected_quick_filter = None
    
    for idx, (filter_name, filter_config) in enumerate(QUICK_FILTERS.items()):
        with quick_filter_cols[idx]:
            if st.button(filter_name, help=filter_config['description'], use_container_width=True):
                selected_quick_filter = filter_name
    
    st.markdown("---")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Reset button
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.session_state.loaded_filter = None
            st.rerun()
        
        st.markdown("---")
        
        # Load saved filter values if available
        loaded_filter = st.session_state.loaded_filter if 'loaded_filter' in st.session_state else None
        
        # Date range filter with presets
        st.subheader("📅 Date Range")
        date_range = None
        if 'DateTime' in df.columns and not df['DateTime'].isna().all():
            min_date = df['DateTime'].min().date()
            max_date = df['DateTime'].max().date()
            
            # Use loaded filter date range if available
            default_range = (min_date, max_date)
            if loaded_filter and loaded_filter.get('date_range'):
                try:
                    saved_range = loaded_filter['date_range']
                    if isinstance(saved_range, list) and len(saved_range) == 2:
                        default_range = tuple(saved_range)
                except:
                    pass
            
            # Manual date picker
            date_range = st.date_input(
                "Select date range",
                value=default_range,
                min_value=min_date,
                max_value=max_date
            )
        
        # Actor name filter
        st.subheader("👤 User")
        all_actors = safe_unique_values(df, 'Actor Name')
        
        # Use loaded filter actors if available
        default_actors = ['All']
        if loaded_filter and loaded_filter.get('actors'):
            default_actors = loaded_filter['actors']
        
        selected_actors = st.multiselect(
            "Filter by user",
            options=['All'] + all_actors,
            default=default_actors
        )
        
        # Action filter
        st.subheader("⚡ Action Type")
        all_actions = safe_unique_values(df, 'Action')
        
        default_actions = ['All']
        if loaded_filter and loaded_filter.get('actions'):
            default_actions = loaded_filter['actions']
        
        selected_actions = st.multiselect(
            "Filter by action",
            options=['All'] + all_actions,
            default=default_actions
        )
        
        # Event filter
        st.subheader("📝 Event Type")
        all_events = safe_unique_values(df, 'Event')
        
        default_events = ['All']
        if loaded_filter and loaded_filter.get('events'):
            default_events = loaded_filter['events']
        
        selected_events = st.multiselect(
            "Filter by event",
            options=['All'] + all_events,
            default=default_events
        )
        
        # Risk filter
        st.subheader("⚠️ Risk Level")
        
        default_risk = 'All Actions'
        if loaded_filter and loaded_filter.get('risk_filter'):
            default_risk = loaded_filter['risk_filter']
        
        risk_filter = st.radio(
            "Show",
            options=['All Actions', 'Risky Only', 'Normal Only'],
            index=['All Actions', 'Risky Only', 'Normal Only'].index(default_risk)
        )
    
    # Apply quick filter first if selected
    if selected_quick_filter:
        filtered_df = apply_quick_filter(df, selected_quick_filter)
        st.info(f"✨ Applied quick filter: {selected_quick_filter}")
    else:
        filtered_df = df.copy()
    
    # Apply manual filters
    # Date filter
    if date_range and len(date_range) == 2 and 'DateTime' in df.columns and not df['DateTime'].isna().all():
        start_date, end_date = date_range
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
    
    # Search box - optimized to search only relevant columns
    search_query = st.text_input(
        "🔎 Search across key fields",
        placeholder="Enter keywords to search...",
        help="Searches in: " + ", ".join(SEARCHABLE_COLUMNS),
        key="search_input"
    )
    
    if search_query:
        # Only search in columns that exist and are in SEARCHABLE_COLUMNS
        search_cols = [col for col in SEARCHABLE_COLUMNS if col in filtered_df.columns]
        if search_cols:
            # Use vectorized string operations for speed
            search_lower = search_query.lower()
            mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
            
            for col in search_cols:
                # Convert to string and search (faster than apply)
                mask |= filtered_df[col].astype(str).str.lower().str.contains(search_lower, na=False, regex=False)
            
            filtered_df = filtered_df[mask]
    
    # Display results count
    st.markdown(f"### 📋 Results: {len(filtered_df):,} entries")
    
    # Show active filters
    active_filters = []
    if selected_quick_filter:
        active_filters.append(f"⚡ Quick: {selected_quick_filter}")
    if 'All' not in selected_actors and selected_actors:
        active_filters.append(f"👤 Users: {len(selected_actors)}")
    if 'All' not in selected_actions and selected_actions:
        active_filters.append(f"⚡ Actions: {len(selected_actions)}")
    if 'All' not in selected_events and selected_events:
        active_filters.append(f"📝 Events: {len(selected_events)}")
    if risk_filter != 'All Actions':
        active_filters.append(f"⚠️ Risk: {risk_filter}")
    if search_query:
        active_filters.append(f"🔎 Search: '{search_query}'")
    
    if active_filters:
        st.info("Active filters: " + " | ".join(active_filters))
        
        # Save current filters button
        current_filter_config = {
            'date_range': [str(date_range[0]), str(date_range[1])] if date_range and len(date_range) == 2 else None,
            'actors': selected_actors,
            'actions': selected_actions,
            'events': selected_events,
            'risk_filter': risk_filter,
            'search_query': search_query if search_query else None
        }
        
        save_filter_dialog(current_filter_config)
    
    # Export and column selection
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Export CSV",
            data=csv,
            file_name=f"filtered_audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Copy to clipboard button (using st.code workaround)
        if st.button("📋 Copy Data"):
            st.code(filtered_df.to_csv(index=False), language=None)
            st.caption("↑ Select and copy the data above")
    
    with col3:
        # Column selector
        with st.expander("📊 Columns"):
            default_cols = [col for col in DEFAULT_DISPLAY_COLUMNS if col in filtered_df.columns]
            selected_cols = st.multiselect(
                "Choose columns",
                options=list(filtered_df.columns),
                default=default_cols
            )
    
    # Pagination for large datasets
    if len(filtered_df) > MAX_ROWS_BEFORE_PAGINATION:
        st.warning(f"⚠️ Large dataset ({len(filtered_df):,} rows). Showing paginated results.")
        
        # Calculate pages
        total_pages = (len(filtered_df) - 1) // ROWS_PER_PAGE + 1
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input(
                f"Page (1-{total_pages})",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1
            )
        
        # Get page data
        start_idx = (page - 1) * ROWS_PER_PAGE
        end_idx = start_idx + ROWS_PER_PAGE
        display_df = filtered_df.iloc[start_idx:end_idx]
        
        st.caption(f"Showing rows {start_idx + 1} to {min(end_idx, len(filtered_df))} of {len(filtered_df):,}")
    else:
        display_df = filtered_df
    
    # Display dataframe
    if not display_df.empty:
        # Apply column selection if any
        if 'selected_cols' in locals() and selected_cols:
            display_df = display_df[selected_cols]
        
        # Format risk column
        display_df_formatted = display_df.copy()
        if 'IsRisky' in display_df_formatted.columns:
            display_df_formatted['Risk'] = display_df_formatted['IsRisky'].apply(
                lambda x: '⚠️ RISKY' if x else '✓ Normal'
            )
            display_df_formatted = display_df_formatted.drop('IsRisky', axis=1)
        
        st.dataframe(
            display_df_formatted,
            use_container_width=True,
            height=600
        )
    else:
        st.warning("No results found matching your filters")


def show_permissions_tab(df):
    """Permission changes analysis tab"""
    st.subheader("🔐 Permission Changes Analysis")
    
    show_permission_changes_report(df)
    st.markdown("---")
    show_who_did_what_matrix(df)
    st.markdown("---")
    show_action_history_by_scope(df)



def show_permission_changes_report(df):
    """Detailed permission changes summary report"""
    st.subheader("🔐 Permission Changes Summary Report")
    
    # Filter for permission-related entries
    perm_df = df[
        (df['Action'].astype(str).str.contains('ModifyPermission|permission', case=False, na=False)) |
        (df['Description'].astype(str).str.contains('permission', case=False, na=False))
    ].copy()
    
    if perm_df.empty:
        st.info("No permission changes found in the current filtered data")
        return
    
    st.write(f"**Found {len(perm_df)} permission change entries**")
    
    # Create summary table
    summary_data = []
    for _, row in perm_df.iterrows():
        data_str = row.get('Data', '')
        parsed_data = parse_json_field(data_str) if data_str else None
        
        perms_changed = ""
        if parsed_data and 'EventSummary' in parsed_data:
            perms = parsed_data['EventSummary']
            if isinstance(perms, list):
                perms_changed = "; ".join([
                    f"{p.get('PermissionNames', '')} ({p.get('Change', '')})" 
                    for p in perms if isinstance(p, dict)
                ])
        
        summary_data.append({
            'User': row.get('Actor Name', 'N/A'),
            'When': row.get('Date', 'N/A'),
            'Permissions Changed': perms_changed or row.get('Description', ''),
            'Scope': row.get('ScopeDisplayName', 'N/A'),
            'IP': row.get('IP Address', 'N/A')
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)
    
    # Export button
    csv = summary_df.to_csv(index=False)
    st.download_button(
        label="📥 Export Permission Changes Report",
        data=csv,
        file_name=f"permission_changes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def show_who_did_what_matrix(df):
    """Matrix showing who changed permissions for whom"""
    st.subheader("👥 Who Did What To Whom (Permission Changes Matrix)")
    
    # Filter for permission changes
    perm_df = df[
        (df['Action'].astype(str).str.contains('ModifyPermission|permission', case=False, na=False)) |
        (df['Description'].astype(str).str.contains('permission', case=False, na=False))
    ].copy()
    
    if perm_df.empty:
        st.info("No permission change data available")
        return
    
    # Extract who changed permissions for whom
    matrix_data = []
    for _, row in perm_df.iterrows():
        data_str = row.get('Data', '')
        parsed_data = parse_json_field(data_str) if data_str else None
        
        actor = row.get('Actor Name', 'Unknown')
        subject = 'Unknown'
        if parsed_data and 'SubjectDisplayName' in parsed_data:
            subject = parsed_data['SubjectDisplayName']
        
        matrix_data.append({
            'Modified By': actor,
            'For User': subject,
            'When': row.get('Date', 'N/A'),
            'What': row.get('Description', 'N/A'),
            'Scope': row.get('ScopeDisplayName', 'N/A')
        })
    
    if matrix_data:
        matrix_df = pd.DataFrame(matrix_data)
        st.dataframe(matrix_df, use_container_width=True)
    else:
        st.info("No permission change details could be extracted")


def show_action_history_by_scope(df):
    """Show action history for a selected project/scope"""
    st.subheader("📁 Action History by Project/Scope")
    
    scopes = safe_unique_values(df, 'ScopeDisplayName')
    if not scopes:
        st.info("No scope information available")
        return
    
    selected_scope = st.selectbox("Select organization/project", scopes)
    
    if selected_scope:
        scope_df = df[df['ScopeDisplayName'] == selected_scope]
        if 'DateTime' in scope_df.columns and not scope_df['DateTime'].isna().all():
            scope_df = scope_df.sort_values('DateTime', ascending=False)
        
        st.write(f"**{selected_scope}** - {len(scope_df)} actions")
        
        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Actions", len(scope_df))
        with col2:
            unique_users = scope_df['Actor Name'].nunique() if 'Actor Name' in scope_df.columns else 0
            st.metric("Users", unique_users)
        with col3:
            risky = scope_df['IsRisky'].sum() if 'IsRisky' in scope_df.columns else 0
            st.metric("Risky Actions", risky)
        
        # Action log
        st.write("**Recent Actions:**")
        display_cols = [col for col in ['Date', 'Actor Name', 'Event', 'Action', 'Description'] 
                       if col in scope_df.columns]
        st.dataframe(scope_df[display_cols].head(20), use_container_width=True)


def show_users_tab(df):
    """Users analysis tab"""
    st.subheader("👥 User Activity Analysis")
    
    show_user_activity_timeline(df)
    st.markdown("---")
    show_risk_scores(df)


def show_user_activity_timeline(df):
    """Display activity timeline for a selected user"""
    st.subheader("📋 User Activity Timeline")
    
    if 'Actor Name' not in df.columns:
        st.info("Actor Name column not available")
        return
    
    # User selector
    users = safe_unique_values(df, 'Actor Name')
    selected_user = st.selectbox("Select user to view timeline", users)
    
    if selected_user:
        user_df = df[df['Actor Name'] == selected_user]
        if 'DateTime' in user_df.columns and not user_df['DateTime'].isna().all():
            user_df = user_df.sort_values('DateTime', ascending=False)
        
        st.write(f"**{selected_user}** - {len(user_df)} actions")
        
        # Display as timeline
        for _, row in user_df.head(50).iterrows():
            col1, col2, col3 = st.columns([2, 1, 3])
            
            with col1:
                st.write(f"**{row.get('Date', 'N/A')}**")
            
            with col2:
                risk_badge = "🔴 RISKY" if row.get('IsRisky') else "✅ Normal"
                st.write(risk_badge)
            
            with col3:
                st.write(f"{row.get('Event', 'N/A')} - {row.get('Action', 'N/A')}")
                st.caption(row.get('Description', ''))


def show_risk_scores(df):
    """Display user risk scores based on activity"""
    st.subheader("⚠️ User Risk Scores")
    
    risk_df = calculate_user_risk_scores(df)
    
    if risk_df.empty:
        st.info("Unable to calculate risk scores")
        return
    
    st.dataframe(risk_df, use_container_width=True)


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
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📅 Activity Timeline")
        fig = create_timeline_chart(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("DateTime information not available")
    
    with col2:
        st.markdown("#### ⚡ Action Distribution")
        fig = create_action_distribution_chart(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Action information not available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📝 Event Types")
        fig = create_event_pie_chart(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Event information not available")
    
    with col2:
        st.markdown("#### 👥 Most Active Users")
        fig = create_user_activity_chart(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("User information not available")


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
        
        st.dataframe(user_activity.head(20), use_container_width=True, height=400)
    else:
        st.info("User activity information not available")
    
    # Hourly activity pattern
    st.markdown("### ⏰ Activity Patterns by Hour")
    fig = create_hourly_activity_chart(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("DateTime information not available")
    
    # IP Address analysis
    st.markdown("### 🌐 IP Address Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_ip_activity_chart(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("IP Address information not available")
    
    with col2:
        fig = create_users_per_ip_chart(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("User/IP information not available")


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
    
    with col3:
        if 'DateTime' in risky_df.columns and not risky_df['DateTime'].isna().all():
            latest_risky = risky_df['DateTime'].max()
            st.metric("Latest Risky Action", latest_risky.strftime("%Y-%m-%d %H:%M"))
    
    st.markdown("---")
    
    # Recent risky actions
    st.markdown("### 🚨 Most Recent Risky Actions")
    
    available_cols = [col for col in ['Date', 'Actor Name', 'Event', 'Action', 'Description'] 
                     if col in risky_df.columns]
    
    if 'DateTime' in risky_df.columns and not risky_df['DateTime'].isna().all():
        recent_risky = risky_df.nlargest(20, 'DateTime')[available_cols]
    else:
        recent_risky = risky_df.head(20)[available_cols]
    
    st.dataframe(recent_risky, use_container_width=True, height=400)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Users with Most Risky Actions")
        fig = create_risky_users_chart(risky_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⚡ Risky Action Types")
        fig = create_risky_action_types_chart(risky_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Timeline
    st.markdown("### 📊 Risky Actions Timeline")
    fig = create_risky_timeline_chart(risky_df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Export
    st.markdown("### 📥 Export Risky Actions")
    csv = risky_df.to_csv(index=False)
    st.download_button(
        label="Download Risky Actions Report (CSV)",
        data=csv,
        file_name=f"risky_actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def show_timeline_tab(df):
    """Timeline view tab"""
    st.subheader("📅 Activity Timeline by Date")
    
    if 'DateTime' not in df.columns or df['DateTime'].isna().all():
        st.info("DateTime column not available")
        return
    
    # Group by date
    df_copy = df.copy()
    df_copy['Date_Only'] = df_copy['DateTime'].dt.date
    
    date_summary = df_copy.groupby('Date_Only').agg({
        'Actor Name': 'count',
        'IsRisky': 'sum' if 'IsRisky' in df_copy.columns else lambda x: 0
    }).reset_index()
    date_summary.columns = ['Date', 'Total Actions', 'Risky Actions']
    
    # Chart
    import plotly.express as px
    fig = px.bar(
        date_summary, 
        x='Date', 
        y=['Total Actions', 'Risky Actions'],
        title='Actions per Day', 
        barmode='stack'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Table
    st.dataframe(date_summary, use_container_width=True)


def show_alerts_tab(df):
    """Alerts tab"""
    st.subheader("🚨 Critical Alerts & Notifications")
    
    alerts = detect_critical_alerts(df)
    
    if not alerts:
        st.success("✅ No critical alerts detected")
        return
    
    # Summary table
    alerts_summary = []
    for alert in alerts:
        alerts_summary.append({
            'Type': alert['Type'],
            'Description': alert['Description'],
            'Severity': alert['Severity'],
            'Count': alert['Count']
        })
    
    alerts_df = pd.DataFrame(alerts_summary)
    st.dataframe(alerts_df, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed alerts
    for idx, alert in enumerate(alerts):
        header = f"{alert['Type']} - {alert['Severity']}"
        if alert['Alert_Type'] == 'bulk_permissions':
            header = f"{alert['Type']} - {alert['User']} ({alert['Count']} changes) - {alert['Severity']}"
        
        with st.expander(header):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Count", alert['Count'])
            with col2:
                st.write(f"**Type:** {alert['Type']}")
            with col3:
                st.write(f"**Severity:** {alert['Severity']}")
            
            st.markdown("---")
            
            # Show sample data
            alert_data = alert['Data'].head(20)
            display_cols = [col for col in ['Date', 'Actor Name', 'Event', 'Action', 'Description'] 
                           if col in alert_data.columns]
            st.dataframe(alert_data[display_cols], use_container_width=True)
            
            # Export
            csv = alert['Data'].to_csv(index=False)
            st.download_button(
                label="📥 Export this alert data",
                data=csv,
                file_name=f"alert_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key=f"alert_export_{idx}"
            )


def show_comparison_tab(df):
    """Compare two time periods"""
    st.subheader("🔄 Compare Time Periods")
    
    if 'DateTime' not in df.columns or df['DateTime'].isna().all():
        st.info("DateTime information required for comparison")
        return
    
    st.markdown("""
    Compare activity between two time periods to identify changes in behavior,
    spot anomalies, or track improvements.
    """)
    
    min_date = df['DateTime'].min().date()
    max_date = df['DateTime'].max().date()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Period 1")
        period1_dates = st.date_input(
            "Select date range for Period 1",
            value=(min_date, min_date + timedelta(days=7)),
            min_value=min_date,
            max_value=max_date,
            key="period1"
        )
        period1_label = st.text_input("Label for Period 1", value="Period 1")
    
    with col2:
        st.markdown("#### Period 2")
        period2_dates = st.date_input(
            "Select date range for Period 2",
            value=(max_date - timedelta(days=7), max_date),
            min_value=min_date,
            max_value=max_date,
            key="period2"
        )
        period2_label = st.text_input("Label for Period 2", value="Period 2")
    
    if len(period1_dates) == 2 and len(period2_dates) == 2:
        # Create comparison chart
        fig = create_comparison_chart(df, period1_dates, period2_dates, period1_label, period2_label)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed comparison
        st.markdown("---")
        st.markdown("### Detailed Comparison")
        
        df1 = df[(df['DateTime'].dt.date >= period1_dates[0]) & (df['DateTime'].dt.date <= period1_dates[1])]
        df2 = df[(df['DateTime'].dt.date >= period2_dates[0]) & (df['DateTime'].dt.date <= period2_dates[1])]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**{period1_label}**")
            st.metric("Total Actions", len(df1))
            st.metric("Unique Users", df1['Actor Name'].nunique() if 'Actor Name' in df1.columns else 0)
            st.metric("Risky Actions", df1['IsRisky'].sum() if 'IsRisky' in df1.columns else 0)
        
        with col2:
            st.markdown(f"**{period2_label}**")
            st.metric("Total Actions", len(df2))
            st.metric("Unique Users", df2['Actor Name'].nunique() if 'Actor Name' in df2.columns else 0)
            st.metric("Risky Actions", df2['IsRisky'].sum() if 'IsRisky' in df2.columns else 0)
        
        with col3:
            st.markdown("**Change**")
            change_actions = len(df2) - len(df1)
            change_users = (df2['Actor Name'].nunique() if 'Actor Name' in df2.columns else 0) - \
                          (df1['Actor Name'].nunique() if 'Actor Name' in df1.columns else 0)
            change_risky = (df2['IsRisky'].sum() if 'IsRisky' in df2.columns else 0) - \
                          (df1['IsRisky'].sum() if 'IsRisky' in df1.columns else 0)
            
            st.metric("Total Actions", f"{change_actions:+d}")
            st.metric("Unique Users", f"{change_users:+d}")
            st.metric("Risky Actions", f"{change_risky:+d}")


def show_column_reference(df):
    """Display reference guide for all audit log columns"""
    st.subheader("📚 ADO Audit Log Column Reference")
    
    column_descriptions = {
        "Id": "Unique identifier for this audit log entry",
        "CorrelationId": "Links related audit events together",
        "ActivityId": "Unique ID for the specific activity/action",
        "ActorCUID": "Correlation User ID - internal identifier",
        "ActorUserId": "Azure AD User ID",
        "ActorUPN": "User Principal Name (email/account)",
        "ActorDisplayName": "Human-readable name",
        "Actor Name": "User who made the change",
        "Actor Email": "Email address of the user",
        "Actor UUID": "Azure AD identifier",
        "AuthenticationMechanism": "How the user authenticated",
        "Timestamp": "When the action occurred",
        "Date": "Human-readable date/time",
        "DateTime": "Parsed date/time for filtering",
        "ScopeType": "Level where action occurred",
        "ScopeDisplayName": "Name of the scope/organization",
        "ScopeId": "Unique ID of the scope",
        "ProjectId": "Azure DevOps Project ID",
        "ProjectName": "Name of the project affected",
        "IpAddress": "IP address from which action was performed",
        "UserAgent": "Browser/client information",
        "ActionId": "Unique identifier for action type",
        "Area": "Broad category",
        "Category": "Specific category",
        "CategoryDisplayName": "Human-readable category",
        "Event": "What category of event occurred",
        "Action": "Specific action taken",
        "Description": "Human-readable summary",
        "Data": "JSON data with detailed information",
        "IsRisky": "Risk indicator (added by analyzer)"
    }
    
    st.write("""
    This reference explains what each column represents. Use these when filtering and analyzing.
    """)
    
    # Search
    search_term = st.text_input("🔍 Search columns:", placeholder="e.g., 'actor', 'time'")
    
    # Filter
    filtered_descriptions = {}
    if search_term:
        search_lower = search_term.lower()
        for col, desc in column_descriptions.items():
            if search_lower in col.lower() or search_lower in desc.lower():
                filtered_descriptions[col] = desc
    else:
        filtered_descriptions = column_descriptions
    
    st.write(f"**Found {len(filtered_descriptions)} column(s)**")
    st.markdown("---")
    
    # Display
    for col_name in sorted(filtered_descriptions.keys()):
        with st.expander(f"**{col_name}**"):
            st.write(filtered_descriptions[col_name])
            
            # Show sample values
            if col_name in df.columns:
                sample_values = df[col_name].dropna().unique()[:3]
                if len(sample_values) > 0:
                    st.write("**Sample values:**")
                    for val in sample_values:
                        val_str = str(val)
                        if len(val_str) > 100:
                            val_str = val_str[:100] + "..."
                        st.code(val_str, language="text")
