"""
Configuration settings for ADO Audit Log Analyzer
"""

# Risk detection keywords - customize these based on your needs
RISKY_ACTIONS = {
    'delete', 'remove', 'revoke', 'destroy', 'terminate',
    'update', 'modify', 'change', 'patch', 'edit'
}

RISKY_EVENT_KEYWORDS = {
    'delete', 'remove', 'revoke', 'destroy', 'terminate',
    'update', 'modify', 'change', 'access'
}

# Date format patterns to try when parsing dates
DATE_FORMATS = [
    '%Y-%m-%d at %I:%M %p',  # 2026-02-13 at 7:28 AM
    '%Y-%m-%d %I:%M %p',     # 2026-02-13 7:28 AM
    '%Y-%m-%d %H:%M:%S',     # 2026-02-13 19:28:00
    '%m/%d/%Y %I:%M %p',     # 02/13/2026 7:28 AM
    '%d/%m/%Y %H:%M:%S',     # 13/02/2026 19:28:00
]

# Columns to search when doing text search (instead of all columns)
SEARCHABLE_COLUMNS = [
    'Actor Name', 'Actor Email', 'Description', 'Event', 
    'Action', 'IP Address', 'ScopeDisplayName', 'ProjectName'
]

# Default columns to display in search results
DEFAULT_DISPLAY_COLUMNS = [
    'Date', 'Event', 'Actor Name', 'Description', 'Action', 'IsRisky'
]

# Pagination settings
ROWS_PER_PAGE = 100
MAX_ROWS_BEFORE_PAGINATION = 1000

# Performance settings
ENABLE_MEMORY_OPTIMIZATION = True  # Convert columns to category type
ENABLE_SEARCH_OPTIMIZATION = True  # Use vectorized search
CACHE_TIMEOUT_SECONDS = 3600  # 1 hour cache
SHOW_PERFORMANCE_METRICS = True  # Show memory usage and timing

# Quick filter presets
QUICK_FILTERS = {
    'All Deletions': {
        'description': 'Show all delete/remove operations',
        'filter_type': 'description_contains',
        'values': ['delete', 'remove']
    },
    'Permission Changes': {
        'description': 'Show only permission modifications',
        'filter_type': 'action_contains',
        'values': ['permission', 'ModifyPermission']
    },
    'Risky Actions': {
        'description': 'Show only high-risk actions',
        'filter_type': 'risky_only',
        'values': []
    },
    'Access Changes': {
        'description': 'Show access modifications',
        'filter_type': 'description_contains',
        'values': ['access', 'grant', 'revoke']
    },
    'Today': {
        'description': 'Show today\'s activity',
        'filter_type': 'date_range',
        'values': ['today']
    },
    'Last 7 Days': {
        'description': 'Show last week\'s activity',
        'filter_type': 'date_range',
        'values': ['last_7_days']
    }
}

# Column name mappings for flexible CSV parsing
COLUMN_MAPPINGS = {
    'Actor Name': ['actordisplayname', 'actorname', 'username', 'displayname'],
    'Actor Email': ['actorupn', 'actoremail', 'useremail', 'email', 'upn'],
    'Actor UUID': ['actoruuid', 'actoruserid', 'actorid'],
    'Date': ['date', 'timestamp', 'datetime'],
    'Event': ['categorydisplayname', 'category', 'event', 'eventtype'],
    'Action': ['actionid', 'action', 'actiontype'],
    'Description': ['details', 'description', 'summary'],
    'IP Address': ['ipaddress', 'ip', 'clientip'],
    'Object Type': ['objecttype', 'targettype'],
    'Object UUID': ['objectuuid', 'targetid', 'objectid'],
    'ScopeDisplayName': ['scopedisplayname', 'scope', 'organization'],
    'ProjectName': ['projectname', 'project'],
    'Data': ['data', 'additionaldata']
}
