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
        'ny_df': pd.read_csv('data/output/ny_df.csv'),
        'ny_pepsico_df': pd.read_csv('data/output/ny_pepsico_df.csv'),
        'pepsico_df': pd.read_csv('data/output/pepsico_df.csv'),
        'ny_pepsico_item_weekly_df': pd.read_csv('data/output/ny_pepsico_item_weekly_df.csv'),
        'vendor_revenue': pd.read_csv('data/output/vendor_revenue.csv'),
    }
    return dataframes

data = load_data()
ny_df = data['ny_df']
ny_pepsico_df = data['ny_pepsico_df']
pepsico_df = data['pepsico_df']
ny_pepsico_item_weekly_df = data['ny_pepsico_item_weekly_df']
vendor_revenue = data['vendor_revenue']
st.table(pepsico_df)

# Defining multiselection in Streamlit for fashion news
# Convert your date columns to datetime format
pepsico_df['Calendar week starting on'] = pd.to_datetime(pepsico_df['Calendar week starting on'])
pepsico_df['Calendar week ending on'] = pd.to_datetime(pepsico_df['Calendar week ending on'])

# Extract all unique years from both columns
start_years = pepsico_df['Calendar week starting on'].dt.year.unique().tolist()
end_years = pepsico_df['Calendar week ending on'].dt.year.unique().tolist()

# Combine and deduplicate the year lists
all_years = list(set(start_years + end_years))

# Use the years as options for the multiselect widget
selected_years = st.sidebar.multiselect(
    label="YEAR",
    options=all_years,
    default=all_years,
    key="filter_years"
)

# Filter the DataFrame to include only selected_years data
selected_years_df = pepsico_df[
    pepsico_df['Calendar week starting on'].dt.year.isin(selected_years) |
    pepsico_df['Calendar week ending on'].dt.year.isin(selected_years)
]

# Filter the DataFrame to include only selected_years data
selected_years_df = pepsico_df[
    pepsico_df['Calendar week starting on'].dt.year.isin(selected_years) |
    pepsico_df['Calendar week ending on'].dt.year.isin(selected_years)
]

# Calculate total volume and revenue for selected years
total_volume = round(selected_years_df['UNITS'].sum(), 0)
total_revenue = round(selected_years_df['DOLLARS'].sum(), 0)

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

# Find the top 3 regions by revenue and round the values
top_3_regions_df = selected_years_df.groupby('Market_Name')['DOLLARS'].sum().nlargest(3).round(0)

# Create a bar chart for the top 3 markets in Streamlit using Altair
chart_data = pd.DataFrame(top_3_regions_df).reset_index()
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
tab1, tab2, tab3 = st.tabs(["Revenue", "Marketing", "Resources"])

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
