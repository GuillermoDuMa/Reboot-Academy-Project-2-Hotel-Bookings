import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Hotel Bookings Analysis",
    page_icon="🏨",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('hotel_bookings_clean.csv')
    # Convert arrival_date to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(df['arrival_date']):
        df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    # Add day of week column
    df['day_of_week'] = df['arrival_date'].dt.day_name()
    return df

df = load_data()

# Title
st.title("🏨 Hotel Bookings Analysis Dashboard")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Cancellation Rates", "Lead Time vs Cancellations", "ADR Analysis"])

# Tab 1: Cancellation Rates
with tab1:
    st.header("Cancellation Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graph 1: Cancellation vs Total Bookings
        st.subheader("Cancellation vs Total Bookings")
        total_bookings = len(df)
        canceled_bookings = df['is_canceled'].sum()
        not_canceled = total_bookings - canceled_bookings
        
        fig = px.pie(
            values=[canceled_bookings, not_canceled],
            names=['Canceled', 'Not Canceled'],
            color_discrete_sequence=['#FF5252', '#4CAF50']
        )
        fig.update_traces(
            textinfo='percent+label',
            marker=dict(line=dict(color='#000000', width=2)),
            name="Booking Status"
        )
        fig.update_layout(
            legend=dict(font=dict(color='black', size=12)),
            template="none",
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display metrics
        st.metric("Total Bookings", total_bookings)
        st.metric("Cancelation Rate", f"{(canceled_bookings/total_bookings)*100:.1f}%")
    
    with col2:
        # Graph 2: Cancellations per Market Segment
        st.subheader("Cancellations per Market Segment")
        market_cancel = df.groupby('market_segment')['is_canceled'].agg(['count', 'sum']).reset_index()
        market_cancel['cancelation_rate'] = (market_cancel['sum'] / market_cancel['count']) * 100
        
        fig = px.bar(
            market_cancel,
            x='market_segment',
            y='cancelation_rate',
            color='market_segment',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            xaxis_title="Market Segment",
            yaxis_title="Cancellation Rate (%)",
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(font=dict(color='black', size=12)),
            template="none",
            showlegend=True
        )
        fig.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)

# Tab 2: Lead Time vs Cancellations
with tab2:
    st.header("Lead Time Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graph 1: Cancellation rates by lead time groups
        st.subheader("Cancellation Rates by Lead Time Groups")
        
        # Create lead time groups
        bins = [0, 7, 30, 60, 90, float('inf')]
        labels = ['0-7 days', '8-30 days', '31-60 days', '61-90 days', '90+ days']
        df['lead_time_group'] = pd.cut(df['lead_time'], bins=bins, labels=labels)
        
        # Calculate cancellation rates
        lead_time_cancel = df.groupby('lead_time_group')['is_canceled'].agg(['count', 'sum']).reset_index()
        lead_time_cancel['cancelation_rate'] = (lead_time_cancel['sum'] / lead_time_cancel['count']) * 100
        
        fig = px.bar(
            lead_time_cancel,
            x='lead_time_group',
            y='cancelation_rate',
            color='lead_time_group',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            xaxis_title="Lead Time Group",
            yaxis_title="Cancellation Rate (%)",
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(font=dict(color='black', size=12)),
            template="none",
            showlegend=True
        )
        fig.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graph 2: Relation between lead time and cancellations (trend line only, rounded x-ticks, y as %)
        st.subheader("Lead Time vs Cancellation Rate")

        # Create scatter plot with trend line, but hide markers
        fig = px.scatter(
            df,
            x='lead_time',
            y='is_canceled',
            trendline="lowess",
            color_discrete_sequence=['#2196F3'],
            opacity=0  # Hide the scatter points
        )
        # Remove scatter points, keep only the trend line
        fig.data = [trace for trace in fig.data if trace.mode == 'lines']

        # Multiply y values by 100 to get percentages and CLIP to [0, 100]
        if fig.data:
            y_vals = fig.data[0].y * 100
            y_vals = np.clip(y_vals, 0, 100)
            fig.data[0].y = y_vals

        # Set rounded x-ticks
        max_lead = int(np.ceil(df['lead_time'].max() / 100.0)) * 100
        fig.update_layout(
            xaxis=dict(
                title="Lead Time (days)",
                tickmode='array',
                tickvals=list(range(0, max_lead+1, 100)),
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            yaxis=dict(
                title="Cancellation Rate (%)",
                tickmode='array',
                tickvals=[0, 20, 40, 60, 80, 100],
                ticktext=['0%', '20%', '40%', '60%', '80%', '100%'],
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(font=dict(color='black', size=12)),
            template="none",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

# Tab 3: ADR Analysis
with tab3:
    st.header("Average Daily Rate (ADR) Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graph 1: Average ADR by market segment (sorted)
        st.subheader("Average ADR by Market Segment")
        adr_market = df.groupby('market_segment')['adr'].mean().round(2).reset_index()
        adr_market = adr_market.sort_values('adr', ascending=False)  # Sort descending
        
        fig = px.bar(
            adr_market,
            x='market_segment',
            y='adr',
            color='market_segment',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            xaxis_title="Market Segment",
            yaxis_title="Average ADR ($)",
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(font=dict(color='black', size=12)),
            template="none",
            showlegend=False  # Hide legend, as color is not needed
        )
        fig.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graph 2: Most Profitable Customer Types by ADR (horizontal bar, labels on bars, no axis titles)
        st.subheader("Most Profitable Customer Types by ADR")
        
        # Calculate average ADR by customer type
        profitable_customers = df.groupby('customer_type')['adr'].mean().round(2).sort_values(ascending=True)
        
        # Create horizontal bar chart with text labels
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=profitable_customers.values,
            y=profitable_customers.index,
            orientation='h',
            marker=dict(
                color=profitable_customers.values,
                colorscale='Viridis',
                line=dict(color='black', width=1)
            ),
            text=profitable_customers.index,
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(color='white', size=12),
            hovertemplate='%{y}: %{x}<extra></extra>',
            showlegend=False
        ))
        
        fig.update_layout(
            title=dict(
                text="Most Profitable Customer Types by ADR",
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=False,
                showticklabels=True,
                title=None  # Remove x-axis title
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,  # Hide y-axis tick labels
                title=None  # Remove y-axis title
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            template="none"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Graph 3: Average ADR by day of week with booking count
    st.subheader("Average ADR and Number of Bookings by Day of Week")
    adr_dow = df.groupby('day_of_week').agg(
        adr=('adr', 'mean'),
        count=('adr', 'count')
    ).round(2).reset_index()
    
    # Order days of week
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    adr_dow['day_of_week'] = pd.Categorical(adr_dow['day_of_week'], categories=days_order, ordered=True)
    adr_dow = adr_dow.sort_values('day_of_week')
    
    # Create a figure with secondary y-axis
    fig = go.Figure()
    # Bar for count
    fig.add_trace(go.Bar(
        x=adr_dow['day_of_week'],
        y=adr_dow['count'],
        name='Number of Bookings',
        marker_color='#B0BEC5',
        yaxis='y2',
        opacity=0.5
    ))
    # Line for ADR
    fig.add_trace(go.Scatter(
        x=adr_dow['day_of_week'],
        y=adr_dow['adr'],
        name='Average ADR',
        mode='lines+markers',
        line=dict(color='#2196F3', width=3),
        marker=dict(size=10, line=dict(width=2, color='black'))
    ))
    fig.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Average ADR ($)",
        yaxis2=dict(
            title="Number of Bookings",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(font=dict(color='black', size=12)),
        template="none",
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)
