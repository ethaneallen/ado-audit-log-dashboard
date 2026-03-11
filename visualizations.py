"""
Chart and visualization utilities
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_timeline_chart(df, title="Daily Activity"):
    """Create activity timeline chart"""
    if 'DateTime' not in df.columns or df['DateTime'].isna().all():
        return None
    
    timeline_df = df.groupby(df['DateTime'].dt.date).size().reset_index()
    timeline_df.columns = ['Date', 'Count']
    
    fig = px.line(
        timeline_df,
        x='Date',
        y='Count',
        title=title,
        markers=True
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Events",
        hovermode='x unified'
    )
    return fig


def create_action_distribution_chart(df, top_n=10):
    """Create action distribution bar chart"""
    if 'Action' not in df.columns:
        return None
    
    action_counts = df['Action'].value_counts().head(top_n)
    
    fig = px.bar(
        x=action_counts.values,
        y=action_counts.index,
        orientation='h',
        title=f'Top {top_n} Actions',
        labels={'x': 'Count', 'y': 'Action Type'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


def create_event_pie_chart(df, top_n=10):
    """Create event type pie chart"""
    if 'Event' not in df.columns:
        return None
    
    event_counts = df['Event'].value_counts().head(top_n)
    
    fig = px.pie(
        values=event_counts.values,
        names=event_counts.index,
        title=f'Top {top_n} Event Types'
    )
    return fig


def create_user_activity_chart(df, top_n=10):
    """Create most active users chart"""
    if 'Actor Name' not in df.columns:
        return None
    
    user_counts = df['Actor Name'].value_counts().head(top_n)
    
    fig = px.bar(
        x=user_counts.values,
        y=user_counts.index,
        orientation='h',
        title=f'Top {top_n} Users by Activity',
        labels={'x': 'Number of Actions', 'y': 'User'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


def create_hourly_activity_chart(df):
    """Create hourly activity pattern chart"""
    if 'DateTime' not in df.columns or df['DateTime'].isna().all():
        return None
    
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
    return fig


def create_ip_activity_chart(df, top_n=15):
    """Create IP address activity chart"""
    if 'IP Address' not in df.columns:
        return None
    
    ip_counts = df['IP Address'].value_counts().head(top_n)
    
    fig = px.bar(
        x=ip_counts.values,
        y=ip_counts.index,
        orientation='h',
        title=f'Top {top_n} IP Addresses',
        labels={'x': 'Number of Actions', 'y': 'IP Address'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


def create_users_per_ip_chart(df, top_n=15):
    """Create users per IP chart"""
    if 'IP Address' not in df.columns or 'Actor Name' not in df.columns:
        return None
    
    users_per_ip = df.groupby('IP Address')['Actor Name'].nunique().sort_values(ascending=False).head(top_n)
    
    fig = px.bar(
        x=users_per_ip.values,
        y=users_per_ip.index,
        orientation='h',
        title=f'Top {top_n} IPs with Most Users',
        labels={'x': 'Number of Unique Users', 'y': 'IP Address'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


def create_risky_users_chart(risky_df, top_n=15):
    """Create risky users ranking chart"""
    if 'Actor Name' not in risky_df.columns:
        return None
    
    risky_user_counts = risky_df['Actor Name'].value_counts().head(top_n)
    
    fig = px.bar(
        x=risky_user_counts.values,
        y=risky_user_counts.index,
        orientation='h',
        title=f'Top {top_n} Users with Most Risky Actions',
        labels={'x': 'Number of Risky Actions', 'y': 'User'},
        color=risky_user_counts.values,
        color_continuous_scale='Reds'
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    return fig


def create_risky_action_types_chart(risky_df, top_n=10):
    """Create risky action types pie chart"""
    if 'Action' not in risky_df.columns:
        return None
    
    risky_action_counts = risky_df['Action'].value_counts().head(top_n)
    
    fig = px.pie(
        values=risky_action_counts.values,
        names=risky_action_counts.index,
        title=f'Top {top_n} Risky Action Types',
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    return fig


def create_risky_timeline_chart(risky_df):
    """Create risky actions timeline chart"""
    if 'DateTime' not in risky_df.columns or risky_df['DateTime'].isna().all():
        return None
    
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
    return fig


def create_comparison_chart(df, date_range_1, date_range_2, label_1="Period 1", label_2="Period 2"):
    """Create comparison chart between two time periods"""
    if 'DateTime' not in df.columns or df['DateTime'].isna().all():
        return None
    
    # Filter data for each period
    df1 = df[(df['DateTime'].dt.date >= date_range_1[0]) & (df['DateTime'].dt.date <= date_range_1[1])]
    df2 = df[(df['DateTime'].dt.date >= date_range_2[0]) & (df['DateTime'].dt.date <= date_range_2[1])]
    
    # Calculate metrics
    metrics = {
        'Metric': ['Total Actions', 'Unique Users', 'Risky Actions', 'Unique IPs'],
        label_1: [
            len(df1),
            df1['Actor Name'].nunique() if 'Actor Name' in df1.columns else 0,
            df1['IsRisky'].sum() if 'IsRisky' in df1.columns else 0,
            df1['IP Address'].nunique() if 'IP Address' in df1.columns else 0
        ],
        label_2: [
            len(df2),
            df2['Actor Name'].nunique() if 'Actor Name' in df2.columns else 0,
            df2['IsRisky'].sum() if 'IsRisky' in df2.columns else 0,
            df2['IP Address'].nunique() if 'IP Address' in df2.columns else 0
        ]
    }
    
    comparison_df = pd.DataFrame(metrics)
    
    fig = go.Figure(data=[
        go.Bar(name=label_1, x=comparison_df['Metric'], y=comparison_df[label_1]),
        go.Bar(name=label_2, x=comparison_df['Metric'], y=comparison_df[label_2])
    ])
    
    fig.update_layout(
        title='Period Comparison',
        barmode='group',
        xaxis_title='Metric',
        yaxis_title='Count'
    )
    
    return fig
