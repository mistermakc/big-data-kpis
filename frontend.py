# Import necessary modules
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image
import numpy as np
import altair as alt

# Setting theme for streamlit
image = Image.open('data/images/logo.png')
st.set_page_config(
    page_title="Groceries Dashboard", 
    page_icon=image, 
    layout="wide", 
    initial_sidebar_state="expanded",
)

# Title
st.title('Pepsico Inc. Dashboard')

# Defining Streamlit widgets for filters
st.sidebar.image("data/images/logo.png", output_format='PNG', use_column_width=True)

# Load the data
@st.cache_data
def load_data():
    dataframes = {
        'market_share_df': pd.read_csv('data/output/market_share_df.csv'),
        'ny_pepsico_df': pd.read_csv('data/output/ny_pepsico_df.csv'),
        'ny_pepsico_item_weekly_df': pd.read_csv('data/output/ny_pepsico_item_weekly_df.csv'),
        'ny_pepsico_top_customers_df': pd.read_csv('data/output/ny_pepsico_top_customers_df.csv'),
        'ny_pepsico_vsod_df': pd.read_csv('data/output/ny_pepsico_vsod_df.csv'),
        'ny_promo_pct_df': pd.read_csv('data/output/ny_promo_pct_df.csv'),
        'ny_top_products_df': pd.read_csv('data/output/ny_top_products_df.csv'),
        'yearly_totals_df': pd.read_csv('data/output/yearly_totals_df.csv'),
        'vendor_revenue': pd.read_csv('data/output/vendor_revenue.csv'),
        'top_regions_df': pd.read_csv('data/output/top_regions_df.csv'),
    }
    return dataframes

data = load_data()
market_share_df = data['market_share_df']
ny_pepsico_df = data['ny_pepsico_df']
ny_pepsico_top_customers_df = data['ny_pepsico_top_customers_df']
ny_pepsico_item_weekly_df = data['ny_pepsico_item_weekly_df']
ny_promo_pct_df = data['ny_promo_pct_df']
ny_top_products_df = data['ny_top_products_df']
yearly_totals_df = data['yearly_totals_df']
top_regions_df = data['top_regions_df']
vendor_revenue = data['vendor_revenue']

# Get the unique years present in the DataFrame
unique_years = sorted(list(ny_pepsico_df['YEAR'].unique()))

# Use the years as options for the multiselect widget
selected_years = st.sidebar.multiselect(
    label="YEAR",
    options=unique_years,
    default=unique_years,
    key="filter_years"
)

# Filter the DataFrame based on the selected years
filter_ny_pepsico_df = ny_pepsico_df[ny_pepsico_df['YEAR'].isin(selected_years)]
filter_market_share_df = market_share_df[market_share_df['YEAR'].isin(selected_years)]
filter_top_regions_df = top_regions_df[top_regions_df['YEAR'].isin(selected_years)]

# Calculate total volume and revenue for selected years
total_volume = round(filter_ny_pepsico_df['UNITS'].sum(), 0)
total_revenue = round(filter_ny_pepsico_df['DOLLARS'].sum(), 0)

# Calculate total market share
total_market_share_pepsico = filter_market_share_df[filter_market_share_df['L3'] == 'PEPSICO INC']['DOLLARS'].sum()
total_market_share_all = filter_market_share_df['DOLLARS'].sum()
total_marketshare = (total_market_share_pepsico / total_market_share_all) * 100

# Display total volume and revenue in Streamlit
with st.container():
    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(
        label = "Total Revenue",
        value = "{:,.0f}".format(total_revenue),
        #delta = "{:,.2f}%".format(total_volume),
    )
    kpi2.metric(
        label = "Total Volume",
        value = "{:,.0f}".format(total_volume),
        #delta = "{:,.2f}%".format(total_revenue),
    )
    kpi3.metric(
        label = "Total Market Share",
        value = "{:,.2f}%".format(total_marketshare),
    )

#####

# Filter only the required columns: 'Market_Name' and 'Total_Revenue'
chart_data = filter_top_regions_df[['Market_Name', 'Total_Revenue']].copy()

# Rename the columns
chart_data.columns = ['Market Name', 'Revenue']

# Sort the data in descending order
chart_data = chart_data.sort_values('Revenue', ascending=False)

chart_top_regions = alt.Chart(chart_data).mark_bar(color='#1E4B92').encode(
    x=alt.X('Market Name:N', title='Market Name', sort='-y'),  # sort bars by 'Revenue'
    y=alt.Y('Revenue:Q', title='Revenue'),
).properties(
    title='Top 3 Markets by Revenue',
    height=368,
    width=alt.Step(100)  # make the chart responsive
).configure_axis(
    labelFontSize=12,
    titleFontSize=14,
).configure_title(
    fontSize=16,
    font='Arial',
    anchor='middle'
)



###### NEXT CHART

# Take the top 4 vendors and the rest as "others"
top_4_vendors = vendor_revenue.iloc[:4].copy()
rest_vendors = vendor_revenue.iloc[4:].copy()

# Sum the market shares of the rest of the vendors
others_market_share = rest_vendors["market_share"].sum()

# Add a new row for "others"
others_row = pd.DataFrame({"L3": ["Others"], "DOLLARS": [0], "market_share": [others_market_share]})
top_4_vendors = top_4_vendors.append(others_row, ignore_index=True)

# Create a DataFrame suitable for Altair
chart_data = top_4_vendors[['L3', 'market_share']].copy()
chart_data['market_share'] = chart_data['market_share'] * 100  # Convert market share to percentage
chart_data.columns = ['Vendor', 'Market Share']

# Sort the data in descending order
chart_data = chart_data.sort_values('Market Share', ascending=False)

# Create a bar chart
chart_market_share = alt.Chart(chart_data).mark_bar(color='#1E4B92').encode(
    x=alt.X('Market Share:Q', title='Market Share (%)'),
    y=alt.Y('Vendor:N', title='Vendor', sort='-x'),  # Sort bars by 'Market Share'
    tooltip=[alt.Tooltip('Vendor:N', title='Vendor'), alt.Tooltip('Market Share:Q', title='Market Share', format='.2f')]
).properties(
    title='Market Share by Vendor',
    height=368,
    width=alt.Step(100)  # Make the chart responsive
).configure_axis(
    labelFontSize=12,
    titleFontSize=14,
).configure_title(
    fontSize=16,
    font='Arial',
    anchor='middle'
)

#### NEXT CHART

# Group by MskdName and sum UNITS and DOLLARS columns
ny_pepsico_customers_df = ny_pepsico_df.groupby('MskdName').agg({'DOLLARS': 'sum', 'UNITS': 'sum'})

# Sort by UNITS column in descending order
ny_pepsico_top_customers_df = ny_pepsico_customers_df.sort_values('DOLLARS', ascending=False).reset_index()

# Altair requires long format data
ny_pepsico_top_customers_melt_df = ny_pepsico_top_customers_df.melt('MskdName', ['DOLLARS', 'UNITS'], 'Metric', 'Value')

# Create bar chart (dollars)
dollars_chart = alt.Chart(ny_pepsico_top_customers_melt_df[ny_pepsico_top_customers_melt_df['Metric']=='DOLLARS']).mark_bar().encode(
    x='MskdName:N',
    y='Value:Q',
    color=alt.value('#1E4B92'),
).properties(
    width=alt.Step(30)  # controls width of bar.
)

# Create line chart (units)
units_chart = alt.Chart(ny_pepsico_top_customers_melt_df[ny_pepsico_top_customers_melt_df['Metric']=='UNITS']).mark_line().encode(
    x='MskdName:N',
    y='Value:Q',
    color=alt.value('red'),
)

# Combine charts
combined_chart = alt.layer(dollars_chart, units_chart).resolve_scale(
    y = 'independent'  # this makes y-axis independent for each chart
)

### NEXT CHART

# Create an Altair chart for Revenue and Units Sold
chart1 = alt.Chart(ny_pepsico_item_weekly_df.reset_index()).mark_line().encode(
    x='Calendar week starting on:T',
    y=alt.Y(alt.repeat("row"), type='quantitative')
).properties(
    width=600,
    height=200
).repeat(
    row=['Revenue', 'Units Sold']
)

# Create an Altair chart for Avg PR and Avg Marketing
chart2 = alt.Chart(ny_pepsico_item_weekly_df.reset_index()).mark_line().encode(
    x='Calendar week starting on:T',
    y=alt.Y(alt.repeat("row"), type='quantitative')
).properties(
    width=600,
    height=200
).repeat(
    row=['Avg PR', 'Avg Marketing']
)

# Create an Altair chart for Avg Price
chart3 = alt.Chart(ny_pepsico_item_weekly_df.reset_index()).mark_line().encode(
    x='Calendar week starting on:T',
    y='Avg Price:Q'
).properties(
    width=600,
    height=200
)


# Creating tabs to display different KPIs
tab1, tab2, tab3 = st.tabs(["Market", "New York", "Pepsico"])

with tab1:
    # Displaying the two charts side by side
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.altair_chart(chart_top_regions, use_container_width=True)
    with col2:
        st.altair_chart(chart_market_share, use_container_width=True)

with tab2:
    # Displaying the two charts side by side
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.altair_chart(combined_chart, use_container_width=True)
    with col2:
        st.altair_chart(chart_top_regions, use_container_width=True)

with tab3:
    # Displaying the charts for Revenue and Units Sold
    st.altair_chart(chart1, use_container_width=True)

    # Displaying the charts for Avg PR and Avg Marketing
    st.altair_chart(chart2, use_container_width=True)

    # Displaying the chart for Avg Price
    st.altair_chart(chart3, use_container_width=True)
