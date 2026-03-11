"""
Saved Filters Management
"""

import json
import os
from datetime import datetime
import streamlit as st


FILTERS_FILE = "saved_filters.json"


def load_saved_filters():
    """Load saved filters from file"""
    if os.path.exists(FILTERS_FILE):
        try:
            with open(FILTERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_filters_to_file(filters):
    """Save filters to file"""
    try:
        with open(FILTERS_FILE, 'w') as f:
            json.dump(filters, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving filters: {e}")
        return False


def save_current_filter(name, filter_config):
    """Save current filter configuration"""
    filters = load_saved_filters()
    
    filters[name] = {
        'config': filter_config,
        'created': datetime.now().isoformat(),
        'last_used': datetime.now().isoformat()
    }
    
    if save_filters_to_file(filters):
        st.success(f"✅ Saved filter: {name}")
        return True
    return False


def delete_saved_filter(name):
    """Delete a saved filter"""
    filters = load_saved_filters()
    
    if name in filters:
        del filters[name]
        if save_filters_to_file(filters):
            st.success(f"🗑️ Deleted filter: {name}")
            return True
    return False


def update_last_used(name):
    """Update last used timestamp"""
    filters = load_saved_filters()
    
    if name in filters:
        filters[name]['last_used'] = datetime.now().isoformat()
        save_filters_to_file(filters)


def get_filter_config(name):
    """Get configuration for a saved filter"""
    filters = load_saved_filters()
    
    if name in filters:
        update_last_used(name)
        return filters[name]['config']
    return None


def show_saved_filters_ui():
    """Show UI for managing saved filters"""
    
    filters = load_saved_filters()
    
    if not filters:
        st.info("💡 No saved filters yet. Apply filters below and save them for quick access later.")
        return None
    
    # Show saved filters
    st.write(f"**{len(filters)} saved filter(s) - click to load:**")
    
    selected_filter = None
    
    for filter_name in sorted(filters.keys()):
        filter_data = filters[filter_name]
        created = datetime.fromisoformat(filter_data['created']).strftime('%Y-%m-%d %H:%M')
        last_used = datetime.fromisoformat(filter_data['last_used']).strftime('%Y-%m-%d %H:%M')
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            if st.button(f"📋 {filter_name}", key=f"load_{filter_name}", use_container_width=True):
                selected_filter = filter_name
        
        with col2:
            with st.expander("ℹ️"):
                st.caption(f"Created: {created}")
                st.caption(f"Last used: {last_used}")
                
                # Show filter details
                config = filter_data['config']
                if config.get('date_range'):
                    st.caption(f"Date: {config['date_range']}")
                if config.get('actors'):
                    st.caption(f"Users: {len(config['actors'])}")
                if config.get('risk_filter'):
                    st.caption(f"Risk: {config['risk_filter']}")
        
        with col3:
            if st.button("🗑️", key=f"del_{filter_name}"):
                delete_saved_filter(filter_name)
                st.rerun()
    
    return selected_filter


def save_filter_dialog(current_filters):
    """Show dialog to save current filters"""
    with st.expander("💾 Save Current Filters"):
        st.write("Save your current filter settings for quick access later.")
        
        filter_name = st.text_input(
            "Filter Name",
            placeholder="e.g., 'Last Week Risky Actions' or 'My Team Activity'",
            key="save_filter_name"
        )
        
        # Show what will be saved
        st.caption("**Current filters:**")
        filter_summary = []
        
        if current_filters.get('date_range'):
            filter_summary.append(f"📅 Date range: {current_filters['date_range']}")
        if current_filters.get('actors') and 'All' not in current_filters['actors']:
            filter_summary.append(f"👤 Users: {len(current_filters['actors'])} selected")
        if current_filters.get('actions') and 'All' not in current_filters['actions']:
            filter_summary.append(f"⚡ Actions: {len(current_filters['actions'])} selected")
        if current_filters.get('events') and 'All' not in current_filters['events']:
            filter_summary.append(f"📝 Events: {len(current_filters['events'])} selected")
        if current_filters.get('risk_filter') and current_filters['risk_filter'] != 'All Actions':
            filter_summary.append(f"⚠️ Risk: {current_filters['risk_filter']}")
        if current_filters.get('search_query'):
            filter_summary.append(f"🔎 Search: '{current_filters['search_query']}'")
        
        if filter_summary:
            for item in filter_summary:
                st.caption(item)
        else:
            st.caption("No filters currently applied")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Filter", use_container_width=True, disabled=not filter_name):
                if filter_name:
                    if save_current_filter(filter_name, current_filters):
                        st.balloons()
                        return True
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                return False
    
    return None
