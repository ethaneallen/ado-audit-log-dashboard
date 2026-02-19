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
import json

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
            if 'actordisplayname' in col_lower or 'actorname' in col_lower or 'username' in col_lower:
                column_mapping['Actor Name'] = col
            elif 'actorupn' in col_lower or 'actoremail' in col_lower or 'useremail' in col_lower or 'email' in col_lower:
                column_mapping['Actor Email'] = col
            elif 'actoruuid' in col_lower or 'actoruserid' in col_lower or 'userid' in col_lower:
                column_mapping['Actor UUID'] = col
            elif col_lower == 'date' or col_lower == 'timestamp':
                column_mapping['Date'] = col
            elif 'categorydisplayname' in col_lower or col_lower == 'category' or col_lower == 'event' or col_lower == 'eventtype':
                column_mapping['Event'] = col
            elif 'actionid' in col_lower or col_lower == 'action' or col_lower == 'actiontype':
                column_mapping['Action'] = col
            elif 'details' in col_lower or 'description' in col_lower:
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

def parse_json_field(json_str):
    """Parse JSON data field and return as dict, or None if invalid"""
    if not json_str or str(json_str).strip() == '' or str(json_str).strip() == '{}':
        return None
    try:
        # If it's already a dict, return it
        if isinstance(json_str, dict):
            return json_str
        
        # Try to parse as JSON string
        json_str = str(json_str).strip()
        if json_str.startswith('['):
            # It's a list, wrap in a dict for processing
            data = json.loads(json_str)
            return {'data': data} if isinstance(data, list) else data
        else:
            return json.loads(json_str)
    except (json.JSONDecodeError, ValueError, TypeError):
        return None

def extract_permission_changes(data_dict):
    """Extract meaningful permission change information from Data field"""
    if not data_dict:
        return None
    
    try:
        changes = []
        
        # Extract SubjectDisplayName (who was affected)
        subject = data_dict.get('SubjectDisplayName', '')
        if subject:
            changes.append(f"👤 Subject: {subject}")
        
        # Extract NamespaceName (where permissions were changed)
        namespace = data_dict.get('NamespaceName', '')
        if namespace:
            changes.append(f"📁 Namespace: {namespace}")
        
        # Check for EventSummary which contains permission change details
        if 'EventSummary' in data_dict:
            event_summary = data_dict.get('EventSummary', [])
            if isinstance(event_summary, list) and len(event_summary) > 0:
                changes.append("📝 Permission Changes:")
                for i, event in enumerate(event_summary, 1):
                    if isinstance(event, dict):
                        # The EventSummary has: PermissionNames, Change, SubjectDescriptor, SubjectDisplayName
                        perm_name = event.get('PermissionNames', 'Unknown permission')
                        change_type = event.get('Change', 'Modified')  # Usually "allow" or "deny"
                        
                        changes.append(f"  {i}. {perm_name} → {change_type.upper()}")
                    elif isinstance(event, str):
                        changes.append(f"  {event}")
        
        # Check for Permissions array as additional context
        if 'Permissions' in data_dict:
            perms = data_dict.get('Permissions', [])
            if isinstance(perms, list) and len(perms) > 0:
                changes.append("🔐 Current Permission Summary:")
                for perm in perms:
                    if isinstance(perm, dict):
                        # Extract Allow/Deny bits
                        allow_val = perm.get('Allow', perm.get('BaseEntry', {}).get('Allow', 0))
                        deny_val = perm.get('Deny', perm.get('BaseEntry', {}).get('Deny', 0))
                        if allow_val > 0 or deny_val > 0:
                            changes.append(f"  Allow: {allow_val}, Deny: {deny_val}")
        
        return changes if changes else None
    except Exception as e:
        return [f"Error parsing: {str(e)}"]

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
                perms_changed = "; ".join([f"{p.get('PermissionNames', '')} ({p.get('Change', '')})" for p in perms if isinstance(p, dict)])
        
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
        user_df = df[df['Actor Name'] == selected_user].sort_values('DateTime', ascending=False) if 'DateTime' in df.columns else df[df['Actor Name'] == selected_user]
        
        st.write(f"**{selected_user}** - {len(user_df)} actions")
        
        # Display as timeline
        for _, row in user_df.iterrows():
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
    
    if 'Actor Name' not in df.columns or 'IsRisky' not in df.columns:
        st.info("Required columns not available")
        return
    
    # Calculate risk scores
    risk_data = []
    for user in safe_unique_values(df, 'Actor Name'):
        user_df = df[df['Actor Name'] == user]
        total_actions = len(user_df)
        risky_actions = user_df['IsRisky'].sum()
        risk_score = (risky_actions / total_actions * 100) if total_actions > 0 else 0
        
        risk_data.append({
            'User': user,
            'Total Actions': total_actions,
            'Risky Actions': risky_actions,
            'Risk Score (%)': round(risk_score, 1),
            'Risk Level': '🔴 High' if risk_score > 50 else '🟡 Medium' if risk_score > 20 else '🟢 Low'
        })
    
    risk_df = pd.DataFrame(risk_data).sort_values('Risk Score (%)', ascending=False)
    st.dataframe(risk_df, use_container_width=True)

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
        scope_df = df[df['ScopeDisplayName'] == selected_scope].sort_values('DateTime', ascending=False) if 'DateTime' in df.columns else df[df['ScopeDisplayName'] == selected_scope]
        
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
        display_cols = [col for col in ['Date', 'Actor Name', 'Event', 'Action', 'Description'] if col in scope_df.columns]
        st.dataframe(scope_df[display_cols].head(20), use_container_width=True)

def show_critical_alerts(df):
    """Display critical alerts for high-risk actions with clickable details"""
    st.subheader("🚨 Critical Alerts & Notifications")
    
    alerts = []
    
    # Check for bulk permission changes by one user
    if 'Actor Name' in df.columns and 'Action' in df.columns:
        perm_df = df[df['Action'].astype(str).str.contains('ModifyPermission|permission', case=False, na=False)]
        user_counts = perm_df['Actor Name'].value_counts()
        
        for user, count in user_counts.items():
            if count > 5:
                alerts.append({
                    'Type': '⚠️ Bulk Permission Changes',
                    'Description': f"{user} modified {count} permissions",
                    'Severity': '🔴 High',
                    'Count': count,
                    'User': user,
                    'Alert_Type': 'bulk_permissions',
                    'Data': perm_df[perm_df['Actor Name'] == user]
                })
    
    # Check for deletions
    if 'Description' in df.columns:
        delete_df = df[df['Description'].astype(str).str.contains('delete|remove', case=False, na=False)]
        if len(delete_df) > 0:
            alerts.append({
                'Type': '🗑️ Deletion Activity',
                'Description': f"{len(delete_df)} delete/remove operations detected",
                'Severity': '🔴 High',
                'Count': len(delete_df),
                'Alert_Type': 'deletions',
                'Data': delete_df
            })
    
    # Check for risky actions
    if 'IsRisky' in df.columns:
        risky_count = df['IsRisky'].sum()
        if risky_count > 10:
            alerts.append({
                'Type': '⚠️ High Risky Activity',
                'Description': f"{risky_count} risky actions detected",
                'Severity': '🟡 Medium',
                'Count': risky_count,
                'Alert_Type': 'risky_actions',
                'Data': df[df['IsRisky'] == True]
            })
    
    if alerts:
        # Show summary table first
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
        
        # Then show expandable details for each alert
        for idx, alert in enumerate(alerts):
            # Create header with user info when available
            if alert['Alert_Type'] == 'bulk_permissions':
                header = f"{alert['Type']} - {alert['User']} ({alert['Count']} changes) - {alert['Severity']}"
            else:
                header = f"{alert['Type']} - {alert['Severity']}"
            
            with st.expander(header):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Count", alert['Count'])
                with col2:
                    st.write(f"**Type:** {alert['Type']}")
                with col3:
                    st.write(f"**Severity:** {alert['Severity']}")
                
                st.markdown("---")
                
                # Show detailed changes
                if alert['Alert_Type'] == 'bulk_permissions':
                    st.write(f"### Permissions Modified by {alert['User']}")
                    perm_data = alert['Data']
                    
                    # Summary by permission
                    perm_summary = []
                    for _, row in perm_data.iterrows():
                        data_str = row.get('Data', '')
                        parsed_data = parse_json_field(data_str) if data_str else None
                        
                        if parsed_data and 'EventSummary' in parsed_data:
                            perms = parsed_data['EventSummary']
                            if isinstance(perms, list):
                                for perm in perms:
                                    if isinstance(perm, dict):
                                        perm_summary.append({
                                            'Date': row.get('Date', 'N/A'),
                                            'For User': perm.get('SubjectDisplayName', 'N/A'),
                                            'Permission': perm.get('PermissionNames', 'N/A'),
                                            'Change': perm.get('Change', 'N/A').upper(),
                                            'Scope': row.get('ScopeDisplayName', 'N/A')
                                        })
                    
                    if perm_summary:
                        summary_df = pd.DataFrame(perm_summary)
                        st.dataframe(summary_df, use_container_width=True)
                        
                        # Download option
                        csv = summary_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Export this alert details",
                            data=csv,
                            file_name=f"alert_{alert['User'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No detailed permission data available")
                
                elif alert['Alert_Type'] == 'deletions':
                    st.write("### Deletion/Remove Operations")
                    delete_data = alert['Data']
                    
                    delete_summary = []
                    for _, row in delete_data.iterrows():
                        delete_summary.append({
                            'Date': row.get('Date', 'N/A'),
                            'User': row.get('Actor Name', 'N/A'),
                            'Action': row.get('Action', 'N/A'),
                            'Description': row.get('Description', 'N/A'),
                            'IP': row.get('IP Address', 'N/A')
                        })
                    
                    if delete_summary:
                        delete_df = pd.DataFrame(delete_summary)
                        st.dataframe(delete_df, use_container_width=True)
                
                elif alert['Alert_Type'] == 'risky_actions':
                    st.write("### High-Risk Actions Detected")
                    risky_data = alert['Data']
                    
                    risky_summary = []
                    for _, row in risky_data.iterrows():
                        risky_summary.append({
                            'Date': row.get('Date', 'N/A'),
                            'User': row.get('Actor Name', 'N/A'),
                            'Event': row.get('Event', 'N/A'),
                            'Action': row.get('Action', 'N/A'),
                            'Description': row.get('Description', 'N/A')
                        })
                    
                    if risky_summary:
                        risky_df = pd.DataFrame(risky_summary).head(20)
                        st.dataframe(risky_df, use_container_width=True)
    else:
        st.success("✅ No critical alerts detected")

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
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
                "🔍 Search & Filter",
                "🔐 Permissions",
                "👥 Users",
                "📊 Dashboard",
                "📈 Analytics",
                "⚠️ Risk Analysis",
                "📋 Timeline",
                "🚨 Alerts",
                "📚 Reference"
            ])
            
            # TAB 1: Search & Filter
            with tab1:
                show_search_and_filter(df)
            
            # TAB 2: Permission Changes Reports
            with tab2:
                show_critical_alerts(df)
                st.markdown("---")
                show_permission_changes_report(df)
                st.markdown("---")
                show_who_did_what_matrix(df)
                st.markdown("---")
                show_action_history_by_scope(df)
            
            # TAB 3: Users
            with tab3:
                show_user_activity_timeline(df)
                st.markdown("---")
                show_risk_scores(df)
            
            # TAB 4: Dashboard
            with tab4:
                show_dashboard(df)
            
            # TAB 5: Analytics
            with tab5:
                show_analytics(df)
            
            # TAB 6: Risk Analysis
            with tab6:
                show_risky_actions(df)
            
            # TAB 7: Timeline (shows action history)
            with tab7:
                st.subheader("📅 Activity Timeline by Date")
                if 'DateTime' in df.columns:
                    # Group by date
                    df['Date_Only'] = df['DateTime'].dt.date
                    date_summary = df.groupby('Date_Only').agg({
                        'Id': 'count',
                        'IsRisky': 'sum' if 'IsRisky' in df.columns else lambda x: 0
                    }).rename(columns={'Id': 'Total Actions', 'IsRisky': 'Risky Actions'})
                    
                    # Reset index for plotting
                    date_summary = date_summary.reset_index()
                    date_summary.columns = ['Date', 'Total Actions', 'Risky Actions']
                    
                    fig = px.bar(date_summary, x='Date', y=['Total Actions', 'Risky Actions'],
                                title='Actions per Day', barmode='stack')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(date_summary, use_container_width=True)
                else:
                    st.info("DateTime column not available")
            
            # TAB 8: Alerts
            with tab8:
                st.subheader("🚨 Critical Alerts & Notifications")
                show_critical_alerts(df)
            
            # TAB 9: Column Reference
            with tab9:
                show_column_reference(df)
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
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Reset button
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        
        # Date range filter with presets
        st.subheader("📅 Date Range")
        if 'DateTime' in df.columns and not df['DateTime'].isna().all():
            min_date = df['DateTime'].min().date()
            max_date = df['DateTime'].max().date()
            
            # Quick presets
            preset_cols = st.columns(3)
            preset_date_range = None
            with preset_cols[0]:
                if st.button("📅 Last 24h"):
                    from datetime import timedelta
                    preset_date_range = (max_date - timedelta(days=1), max_date)
            with preset_cols[1]:
                if st.button("📆 Last 7d"):
                    from datetime import timedelta
                    preset_date_range = (max_date - timedelta(days=7), max_date)
            with preset_cols[2]:
                if st.button("📊 All Time"):
                    preset_date_range = (min_date, max_date)
            
            # Manual date picker
            date_range = st.date_input(
                "Or select custom range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            # Use preset if clicked, otherwise use manual selection
            if preset_date_range:
                date_range = preset_date_range
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
    
    # Display active filters summary (sticky at top)
    st.markdown("### 📋 Results: {0:,} entries".format(len(filtered_df)))
    
    # Show active filters as badges
    active_filters = []
    if 'All' not in selected_actors and selected_actors:
        active_filters.append(f"👤 Users: {', '.join(selected_actors)}")
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
        # Show/hide columns selector in expander
        with st.expander("📊 Select Columns"):
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
        
        # Add detailed view for permission changes
        st.markdown("---")
        st.subheader("🔐 Permission Changes Details")
        
        # Check if there are permission-related entries
        # Look for entries where Description contains "permission" or Action contains "Permission"
        perm_mask = False
        
        # Check Description column
        if 'Description' in filtered_df.columns:
            perm_mask = filtered_df['Description'].astype(str).str.contains('permission', case=False, na=False)
        
        # Also check Action column
        if 'Action' in filtered_df.columns:
            perm_mask = perm_mask | filtered_df['Action'].astype(str).str.contains('permission', case=False, na=False)
        
        # Also check Event column
        if 'Event' in filtered_df.columns:
            perm_mask = perm_mask | filtered_df['Event'].astype(str).str.contains('permission', case=False, na=False)
            
        if perm_mask.any():
            st.info(f"Found {perm_mask.sum()} permission-related entries")
            
            # Display each permission change with full details
            perm_entries = filtered_df[perm_mask]
            
            for idx, (_, row) in enumerate(perm_entries.iterrows(), 1):
                with st.expander(f"📋 Entry {idx}: {row.get('Actor Name', 'Unknown')} - {row.get('Description', 'Permission Change')[:70]}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**General Info**")
                        st.write(f"👤 User: {row.get('Actor Name', 'N/A')}")
                        st.write(f"✉️ Email/UPN: {row.get('Actor Email', 'N/A')}")
                        st.write(f"📅 Date: {row.get('Date', 'N/A')}")
                        st.write(f"🌐 IP Address: {row.get('IP Address', 'N/A')}")
                    
                    with col2:
                        st.write("**Event Details**")
                        st.write(f"Event: {row.get('Event', 'N/A')}")
                        st.write(f"Action: {row.get('Action', 'N/A')}")
                    
                    with col3:
                        st.write("**Scope/Project**")
                        
                        # Try multiple potential column names for these fields
                        org_val = (row.get('ScopeDisplayName') or row.get('Organization') or 
                                   row.get('Scope') or 'N/A')
                        proj_val = (row.get('ProjectName') or row.get('Project') or 
                                    row.get('ProjectId') or 'N/A')
                        scope_val = (row.get('ScopeType') or row.get('Scope Type') or 'N/A')
                        
                        st.write(f"Organization: {org_val}")
                        st.write(f"Project: {proj_val}")
                        st.write(f"Scope Type: {scope_val}")
                    
                    # Try to parse and display JSON data from Data column
                    data_str = row.get('Data', '') or row.get('Details', '')
                    
                    if data_str and str(data_str).strip() != '':
                        parsed_data = parse_json_field(data_str)
                        
                        if parsed_data:
                            st.divider()
                            st.subheader("✅ Extracted Permission Changes")
                            
                            # Extract permission changes
                            changes = extract_permission_changes(parsed_data)
                            if changes:
                                for change in changes:
                                    if change.startswith('  '):
                                        # Indented items - show as bullet points
                                        st.write(change)
                                    elif '→' in change:
                                        # Permission change with arrow
                                        st.success(change)
                                    elif ':' in change:
                                        # Header lines
                                        st.write(f"**{change}**")
                                    else:
                                        st.write(change)
                            
                            # Show full JSON for reference
                            with st.expander("View Full JSON Data"):
                                st.json(parsed_data)
                        else:
                            st.write("**Raw Data**")
                            st.code(str(data_str)[:500], language="json")
                    else:
                        st.write("**Description**")
                        description = row.get('Description', 'N/A')
                        st.info(description)
                    
                    # Debug: Show all available columns and their values for this row
                    with st.expander("🔧 Debug: All Available Data"):
                        st.write(f"**Total columns available: {len(row)}**")
                        debug_cols = []
                        for col_name in sorted(row.index):
                            val = row.get(col_name, '')
                            if val and str(val).strip() != '':
                                debug_cols.append(f"**{col_name}**: {str(val)[:100]}")
                        if debug_cols:
                            for col_info in debug_cols:
                                st.write(col_info)
                        else:
                            st.write("(All columns are empty or N/A)")
        else:
            st.info("No permission change entries found in filtered results. Use the search box to search for 'permission' or filter by relevant events.")
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

def show_column_reference(df):
    """Display reference guide for all audit log columns"""
    st.subheader("📚 ADO Audit Log Column Reference")
    
    # Column descriptions
    column_descriptions = {
        "Id": "Unique identifier for this audit log entry",
        "CorrelationId": "Links related audit events together (useful for tracking a single operation across multiple log entries)",
        "ActivityId": "Unique ID for the specific activity/action that occurred",
        "ActorCUID": "Correlation User ID - internal identifier for the user who performed the action",
        "ActorUserId": "Azure AD User ID of the person who performed the action",
        "ActorClientId": "Client application ID (usually empty or 00000000... for user-initiated actions)",
        "ActorUPN": "User Principal Name - the email/account of the person who performed the action",
        "ActorDisplayName": "Human-readable name of the person who performed the action",
        "Actor Name": "Same as ActorDisplayName (user who made the change)",
        "Actor Email": "Same as ActorUPN (email address of the user)",
        "Actor UUID": "Same as ActorUserId (Azure AD identifier)",
        "AuthenticationMechanism": "How the user authenticated (AAD, PAT, etc.)",
        "Timestamp": "When the action occurred",
        "Date": "Same as Timestamp (human-readable date/time)",
        "DateTime": "Parsed date/time for filtering and analysis",
        "ScopeType": "Level where the action occurred (Organization, Project, etc.)",
        "ScopeDisplayName": "Human-readable name of the scope (e.g., 'wksmallfirms (Organization)')",
        "ScopeId": "Unique ID of the scope/organization",
        "ProjectId": "Azure DevOps Project ID (empty if change was at org level)",
        "ProjectName": "Name of the project affected (empty/nan if change was at org level)",
        "IpAddress": "IP address from which the action was performed",
        "UserAgent": "Browser/client information used to perform the action",
        "ActionId": "Unique identifier for the type of action performed",
        "Area": "Broad category (e.g., 'Permissions', 'Pipelines', 'Library')",
        "Category": "Specific category (e.g., 'Modify', 'Execute', 'Access')",
        "CategoryDisplayName": "Human-readable category name",
        "Event": "What category of event occurred",
        "Action": "What specific action was taken (e.g., 'Security.ModifyPermission')",
        "Description": "Human-readable summary of what happened",
        "Data": "JSON data with detailed information about the change (permissions, affected objects, etc.)",
        "Details": "Same as Data column"
    }
    
    st.write("""
    This reference explains what each column in the audit log represents. Use these column names 
    when filtering, searching, and analyzing the data.
    """)
    
    # Create a searchable view
    col1, col2 = st.columns([1, 3])
    
    with col1:
        search_term = st.text_input("🔍 Search columns:", placeholder="e.g., 'actor', 'time'")
    
    # Filter columns based on search
    filtered_descriptions = {}
    if search_term:
        search_lower = search_term.lower()
        for col, desc in column_descriptions.items():
            if search_lower in col.lower() or search_lower in desc.lower():
                filtered_descriptions[col] = desc
    else:
        filtered_descriptions = column_descriptions
    
    # Display columns as cards
    st.write(f"**Found {len(filtered_descriptions)} column(s)**")
    st.markdown("---")
    
    for col_name in sorted(filtered_descriptions.keys()):
        with st.expander(f"**{col_name}**"):
            st.write(filtered_descriptions[col_name])
            
            # Show sample values for this column if available
            if col_name in df.columns:
                sample_values = df[col_name].dropna().unique()[:3]
                if len(sample_values) > 0:
                    st.write("**Sample values:**")
                    for val in sample_values:
                        val_str = str(val)
                        if len(val_str) > 100:
                            val_str = val_str[:100] + "..."
                        st.code(val_str, language="text")

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
