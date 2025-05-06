import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from scipy.optimize import curve_fit


# Set page config
st.set_page_config(
    page_title="Sunrise Hospitality Hotels Analysis",
    page_icon="🏨",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('hotel_bookings_clean.csv', parse_dates=['arrival_date'])
    
    # Add day of week column
    df['day_of_week'] = df['arrival_date'].dt.day_name()
    return df

df = load_data()

# Title
st.title("Sunrise Hospitality Hotels Analysis")

# Defining monthly
month_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
df['arrival_date_month'] = pd.Categorical(df['arrival_date_month'], categories=month_order, ordered=True)

monthly =   (
            df.groupby('arrival_date_month', 
            observed=False).agg(cancellation_rate=('is_canceled','mean'), 
            total_reservations=('is_canceled',
            'size')).reset_index()
            )

monthly['cancellation_rate_pct'] = monthly['cancellation_rate'] * 100

# Create tabs
tab1, tab2, tab3 = st.tabs(["Cancellation Rates", "Lead Time Analysis", "ADR Analysis"])

# Tab 1: Cancellation Rates
with tab1:
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Graph 1: Cancelled Bookings %
        st.markdown("<h3 style='text-align: center;'>Cancelled Bookings vs Non-cancelled Bookings</h3>", unsafe_allow_html=True)
        total_bookings = len(df)
        canceled_bookings = df['is_canceled'].sum()
        not_canceled = total_bookings - canceled_bookings
        
        fig = px.pie(
            values=[canceled_bookings, not_canceled],
            names=['Canceled', 'Not Canceled'],
            color_discrete_sequence=['#FDDC6D', '#F34A05'],
            height=500
        )
        fig.update_traces(
            textinfo='percent+label',
            marker=dict(line=dict(color='#FFFFFF', width=2)),
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
        st.markdown("<h3 style='text-align: center;'>Cancellations per Market Segment</h3>", unsafe_allow_html=True)
        market_cancel = (
            df.groupby('market_segment')['is_canceled']
              .agg(total='size', canceled='sum')
              .reset_index()
        )
        market_cancel['cancelation_rate'] = (market_cancel['canceled'] / market_cancel['total']) * 100

        # Sort by cancellation rate for consistent color assignment
        market_cancel = market_cancel.sort_values('cancelation_rate', ascending=False)

        fig = px.bar(
            market_cancel,
            x='market_segment',
            y='cancelation_rate',
            color='market_segment',
            text=market_cancel['cancelation_rate'].round(1),
            color_discrete_sequence=['#cf4003', '#F34A05', '#FA6225', '#FDA400', '#FDB32F', '#FDDC6D', '#FDF4A3'],
            width=700,
            height=500
        )
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside',
            marker_line_color='white',
            marker_line_width=1
        )
        fig.update_layout(
            xaxis_title="Market Segment",
            yaxis_title="Cancellation Rate (%)",
            template="none",
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=60, r=20, t=30, b=40),
            font=dict(family="Arial", size=13, color="#333333"),
            legend=dict(
                title_text = "",
                orientation="h",
                x=0.5, xanchor="center",
                y=-0.15, yanchor="top",
                font=dict(size=12)
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        st.markdown("<h3 style='text-align: center;'>Monthly Cancellations vs Total Bookings</h3>", unsafe_allow_html=True)

        # Rename columns for the legend
        monthly_plot = monthly.rename(columns={
            'cancellation_rate_pct': 'Cancellation rate (%)',
            'total_reservations':  'Total bookings'
        })

        from plotly.subplots import make_subplots
        import plotly.graph_objects as go

        # Create figure with secondary axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Line 1: Cancellation (%), left axis
        fig.add_trace(
            go.Scatter(
                x=monthly_plot['arrival_date_month'],
                y=monthly_plot['Cancellation rate (%)'],
                mode='lines+markers+text',
                name='Cancellation rate (%)',
                text=[f"{v:.1f}%" for v in monthly_plot['Cancellation rate (%)']],
                textposition='top center',
                line=dict(color='#F34A05', width=3),
                marker=dict(size=10, line=dict(width=2, color='black'))
            ),
            secondary_y=False
        )

        # Line 2: Total Bookings, right axis
        fig.add_trace(
            go.Scatter(
                x=monthly_plot['arrival_date_month'],
                y=monthly_plot['Total bookings'],
                mode='lines+markers+text',
                name='Total bookings',
                text=monthly_plot['Total bookings'].astype(str),
                textposition='bottom center',
                line=dict(color='#FDDC6D', width=3),
                marker=dict(size=10, line=dict(width=2, color='black'))
            ),
            secondary_y=True
        )

        # Common layout
        fig.update_layout(
            width=700,
            height=500,
            template='none',
            font=dict(family='Arial', size=13, color='#333333'),
            margin=dict(l=80, r=20, t=50, b=100),
            legend=dict(
                orientation='h',
                x=0.5,
                xanchor='center',
                y=-0.3,
                yanchor='top',
                font=dict(size=12)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        # Axes
        fig.update_xaxes(title_text='Month', tickangle=-45)
        fig.update_yaxes(
            title_text='Cancellation rate (%)',
            secondary_y=False,
            range=[0, monthly_plot['Cancellation rate (%)'].max() * 1.2]
        )
        fig.update_yaxes(
            title_text='Total bookings',
            secondary_y=True
        )

        st.plotly_chart(fig, use_container_width=True)

# color_discrete_sequence=['#cf4003', '#F34A05', '#FA6225', '#FDA400', '#FDB32F', '#FDDC6D', '#FDF4A3']
        
###########################################################################################################################3

# Tab 2: Lead Time vs Cancellations
with tab2:
    # First row with two columns
    col1, col2 = st.columns(2)
    
    with col1:
        # New Graph: Lead Time Distribution
        st.markdown("<h3 style='text-align: center;'>Lead Time Distribution</h3>", unsafe_allow_html=True)
        
        fig = px.histogram(
            df,
            x='lead_time',
            nbins=50,
            color_discrete_sequence=['#F34A05']
        )
        
        fig.update_layout(
            xaxis_title="Lead Time (days)",
            yaxis_title="Number of Bookings",
            plot_bgcolor='white',
            paper_bgcolor='white',
            template="none",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Moved Graph: Cancellation rates by lead time groups
        st.markdown("<h3 style='text-align: center;'>Cancellation rates by lead time groups</h3>", unsafe_allow_html=True)
        
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
            color_discrete_sequence=['#FFCC33', '#FFA832', '#FE8330', '#FE5F2F', '#FD3A2D']
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
        fig.update_traces(marker_line_color='white', marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
    
    # Second row: Full width graph
    st.markdown("<h3 style='text-align: center;'>Cancellation Rate Trend by Lead Time</h3>", unsafe_allow_html=True)
    
    # Create scatter plot with trend line, but hide markers
    fig = px.scatter(
        df,
        x='lead_time',
        y='is_canceled',
        trendline="lowess",
        color_discrete_sequence=['#FE8330'],
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graph 1: Average ADR by market segment (sorted)
       
        st.markdown("<h3 style='text-align: center;'>Average ADR by Market Segment</h3>", unsafe_allow_html=True)

        adr_market = df.groupby('market_segment')['adr'].mean().round(2).reset_index()
        adr_market = adr_market.sort_values('adr', ascending=False)  # Sort descending
        
        fig = px.bar(
            adr_market,
            x='market_segment',
            y='adr',
            color='market_segment',
            color_discrete_sequence=['#cf4003', '#F34A05', '#FA6225', '#FDA400', '#FDB32F', '#FDDC6D', '#FDF4A3'], # Paleta de colores
            height=500  # Match the height of the adjacent graph
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
        fig.update_traces(marker_line_color='white', marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graph 2: Most Profitable Customer Types by ADR (horizontal bar, labels on bars, no axis titles)
        st.markdown("<h3 style='text-align: center;'>Most Profitable Customer Types by ADR </h3>", unsafe_allow_html=True)
        
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
                colorscale=['#F34A05', '#cd853f', '#FA6225', '#FDDC6D'],
                line=dict(color='white', width=1)
            ),
            text=profitable_customers.index,
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(color='black', size=12),
            hovertemplate='%{y}: %{x}<extra></extra>',
            showlegend=False
        ))
        
        fig.update_layout(
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
            height=500,  # Match the height of the adjacent graph
            margin=dict(l=20, r=20, t=40, b=20),
            template="none"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Graph 3: Average ADR and Number of Bookings by Day of Week
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
        marker_color='#FDDC6D',
        yaxis='y2',
        opacity=0.5
    ))
    # Line for ADR
    fig.add_trace(go.Scatter(
        x=adr_dow['day_of_week'],
        y=adr_dow['adr'],
        name='Average ADR',
        mode='lines+markers',
        line=dict(color='#F34A05', width=3),
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

    # NEW GRAPH: Average Length of Stay by Country and Customer Type
    st.subheader("Average Length of Stay by Country and Customer Type")
    
    # Calculate total length of stay
    df['total_stay'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    
    # Get top 10 countries by booking volume
    top_countries = df['country_name'].value_counts().head(10).index.tolist()
    country_data = df[df['country_name'].isin(top_countries)]
    
    # Create a dictionary for country codes (using ISO-3 style abbreviations)
    country_codes = {
        'Portugal': 'PRT',
        'United Kingdom': 'GBR',
        'France': 'FRA',
        'Spain': 'ESP',
        'Germany': 'DEU',
        'Italy': 'ITA',
        'Ireland': 'IRL',
        'Belgium': 'BEL',
        'Brazil': 'BRA',
        'Netherlands': 'NLD',
        'United States of America': 'USA',
        'Switzerland': 'CHE',
        'China': 'CHN',
        'Austria': 'AUT',
        'Sweden': 'SWE',
        'Norway': 'NOR',
        'Poland': 'POL',
        'Denmark': 'DNK',
        'Russia': 'RUS',
        'Australia': 'AUS'
    }
    
    # Create pivot table
    los_pivot = pd.pivot_table(
        country_data,
        values='total_stay',
        index='country_name',
        columns='customer_type',
        aggfunc='mean'
    ).round(1)
    
    # Create a version with country codes for display
    los_pivot_display = los_pivot.copy()
    los_pivot_display.index = [country_codes.get(country, country[:3].upper()) for country in los_pivot.index]
    
    # Create heatmap
    hover_text = []
    for country in los_pivot.index:
        row = []
        for customer_type in los_pivot.columns:
            value = los_pivot.loc[country, customer_type]
            row.append(f"Country: {country}<br>Customer Type: {customer_type}<br>Avg. Length of Stay: {value:.1f} nights")
        hover_text.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=los_pivot.values,
        x=los_pivot.columns,
        y=los_pivot_display.index,  # Use the abbreviated codes for display
        colorscale=['#F7E0E0', '#F34A05'],
        text=los_pivot.values.round(1),
        texttemplate="%{text}",
        textfont={"size":12},
        hovertext=hover_text,
        hoverinfo="text"
    ))
    
    fig.update_layout(
        title={
            'text': 'Average Length of Stay (Nights)',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Customer Type",
        yaxis_title="Country",
        xaxis={'side': 'bottom'},
        yaxis={
            'tickangle': 0,  # Keep labels horizontal
            'automargin': True,  # Automatically adjust margin to fit labels
            'tickfont': {'size': 11}  # Slightly smaller font
        },
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        margin=dict(l=120, r=40, t=60, b=40),  # Increase left margin for country names
        template="none"
    )
    
    # Add annotations with better visibility
    for i in range(len(los_pivot.index)):
        for j in range(len(los_pivot.columns)):
            fig.add_annotation(
                x=j,
                y=i,
                text=str(los_pivot.values[i, j]),
                showarrow=False,
                font=dict(
                    color="black" if los_pivot.values[i, j] < los_pivot.values.max()*0.7 else "white",
                    size=12
                )
            )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add interpretive text
    st.markdown("""
    <small>Note: Country names are displayed using ISO 3-letter codes. Hover over the heatmap cells for full country names.</small>
    """, unsafe_allow_html=True)