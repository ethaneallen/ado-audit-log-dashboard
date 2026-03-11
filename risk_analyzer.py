"""
Risk analysis and detection utilities
"""

import pandas as pd
import json
from config import RISKY_ACTIONS, RISKY_EVENT_KEYWORDS


def analyze_risks(df):
    """Add risk indicators to the dataframe"""
    df['IsRisky'] = df.apply(is_risky_action, axis=1)
    return df


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
                        perm_name = event.get('PermissionNames', 'Unknown permission')
                        change_type = event.get('Change', 'Modified')
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
                        allow_val = perm.get('Allow', perm.get('BaseEntry', {}).get('Allow', 0))
                        deny_val = perm.get('Deny', perm.get('BaseEntry', {}).get('Deny', 0))
                        if allow_val > 0 or deny_val > 0:
                            changes.append(f"  Allow: {allow_val}, Deny: {deny_val}")
        
        return changes if changes else None
    except Exception as e:
        return [f"Error parsing: {str(e)}"]


def calculate_user_risk_scores(df):
    """Calculate risk scores for each user"""
    if 'Actor Name' not in df.columns or 'IsRisky' not in df.columns:
        return pd.DataFrame()
    
    risk_data = []
    for user in df['Actor Name'].dropna().unique():
        if str(user).strip() == '':
            continue
            
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
    
    # Return empty DataFrame if no data
    if not risk_data:
        return pd.DataFrame()
    
    risk_df = pd.DataFrame(risk_data).sort_values('Risk Score (%)', ascending=False)
    return risk_df


def detect_critical_alerts(df):
    """Detect and return critical alerts for high-risk patterns"""
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
    
    # Check for unusual after-hours activity
    if 'DateTime' in df.columns and not df['DateTime'].isna().all():
        after_hours = df[df['DateTime'].dt.hour.isin([22, 23, 0, 1, 2, 3, 4, 5])]
        if len(after_hours) > 20:
            alerts.append({
                'Type': '🌙 After-Hours Activity',
                'Description': f"{len(after_hours)} actions performed outside business hours",
                'Severity': '🟡 Medium',
                'Count': len(after_hours),
                'Alert_Type': 'after_hours',
                'Data': after_hours
            })
    
    # Check for multiple users from same IP
    if 'IP Address' in df.columns and 'Actor Name' in df.columns:
        ip_users = df.groupby('IP Address')['Actor Name'].nunique()
        suspicious_ips = ip_users[ip_users > 5]
        if len(suspicious_ips) > 0:
            for ip, user_count in suspicious_ips.items():
                alerts.append({
                    'Type': '🌐 Shared IP Activity',
                    'Description': f"{user_count} different users from IP {ip}",
                    'Severity': '🟡 Medium',
                    'Count': user_count,
                    'Alert_Type': 'shared_ip',
                    'Data': df[df['IP Address'] == ip]
                })
    
    return alerts


def get_risk_badge(is_risky):
    """Return HTML badge for risk level"""
    if is_risky:
        return '<span class="risky-action">⚠️ RISKY</span>'
    return '<span class="normal-action">✓ Normal</span>'
