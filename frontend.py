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

# Get the unique UPCs present in the DataFrame
unique_upc = sorted(list(ny_pepsico_df['UPC'].unique()))

# Use the UPCs as options for the selectbox widget
selected_upc = st.sidebar.selectbox(
    label="UPC",
    options=unique_upc,
    index=0,  # Optional: this sets the default selected index
    key="filter_upc"
)

# Filter the DataFrame by the selected UPC
filter_ny_pepsico_upc_df = ny_pepsico_df[ny_pepsico_df['UPC'] == selected_upc]

# Get the unique retailers for the selected UPC
unique_retailers = sorted(list(filter_ny_pepsico_upc_df['MskdName'].unique()))

# Use the retailers as options for the selectbox widget
selected_retailer = st.sidebar.selectbox(
    label="RETAILER",
    options=unique_retailers,
    index=0,  # Optional: this sets the default selected index
    key="filter_retailer"
)

# Add a slider to select the number of top products to display
selected_product_number = st.sidebar.slider("Number of top products to display", 1, 20, 10)

# Filter the DataFrame based on the selected years
filter_ny_pepsico_df = ny_pepsico_df[ny_pepsico_df['YEAR'].isin(selected_years)]
filter_market_share_df = market_share_df[market_share_df['YEAR'].isin(selected_years)]
filter_top_regions_df = top_regions_df[top_regions_df['YEAR'].isin(selected_years)]
filter_ny_top_products_df = ny_top_products_df[ny_top_products_df['YEAR'].isin(selected_years)]

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

# Group by 'Market_Name' and sum 'Total_Revenue'
grouped_data = filter_top_regions_df.groupby('Market_Name')['Total_Revenue'].sum().reset_index()

# Rename the columns
grouped_data.columns = ['Market Name', 'Total Revenue']

# Sort the data in descending order and take the top 10
grouped_data = grouped_data.sort_values('Total Revenue', ascending=False).head(10)

# Create the chart
chart_top_regions = alt.Chart(grouped_data).mark_bar(color='#1E4B92').encode(
    x=alt.X('Market Name:N', title='Market Name', sort='-y'),  # sort bars by 'Total Revenue'
    y=alt.Y('Total Revenue:Q', title='Revenue'),
).properties(
    title='Top 10 Markets by Revenue',
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




#### NEXT CHART

# Group by MskdName and sum UNITS and DOLLARS columns
ny_pepsico_customers_df = filter_ny_pepsico_df.groupby('MskdName').agg({'DOLLARS': 'sum', 'UNITS': 'sum'})

# Sort by DOLLARS column in descending order
ny_pepsico_top_customers_df = ny_pepsico_customers_df.sort_values('DOLLARS', ascending=False).reset_index()

# Altair requires long format data
ny_pepsico_top_customers_melt_df = ny_pepsico_top_customers_df.melt('MskdName', ['DOLLARS', 'UNITS'], 'Metric', 'Value')

# Create bar chart (dollars)
dollars_chart = alt.Chart(ny_pepsico_top_customers_melt_df[ny_pepsico_top_customers_melt_df['Metric']=='DOLLARS']).mark_bar().encode(
    x=alt.X('MskdName:N'),
    y=alt.Y('Value:Q', axis=alt.Axis(title='Dollars')),
    color=alt.value('#1E4B92'),
).properties(
    title='Top Retailers by Revenue',
    width=alt.Step(30)  # controls width of bar.
)

# Create line chart (units)
units_chart = alt.Chart(ny_pepsico_top_customers_melt_df[ny_pepsico_top_customers_melt_df['Metric']=='UNITS']).mark_line().encode(
    x=alt.X('MskdName:N'),
    y=alt.Y('Value:Q', axis=alt.Axis(title='Units')),
    color=alt.value('red'),
)

# Combine charts
chart_top_retailers = alt.layer(dollars_chart, units_chart).resolve_scale(
    y='independent'  # this makes y-axis independent for each chart
).configure_title(
    anchor='middle'
)



##NEXT CHART

# Group by UPC and PRODUCT TYPE, and sum DOLLARS and UNITS
ny_top_products_df = filter_ny_top_products_df.groupby(['UPC', 'PRODUCT TYPE']).agg({'DOLLARS': 'sum', 'UNITS': 'sum'}).reset_index()

# Sort by DOLLARS column in descending order and select the top N products
ny_top_products_df = ny_top_products_df.sort_values('DOLLARS', ascending=False).head(selected_product_number)

# Add a new column to the DataFrame to combine UPC and PRODUCT TYPE, this will be used as labels on the x-axis
ny_top_products_df['UPC_PRODUCT_TYPE'] = ny_top_products_df['UPC'] + " - " + ny_top_products_df['PRODUCT TYPE']

# Create Altair bar chart
chart_top_products = alt.Chart(ny_top_products_df).mark_bar().encode(
    x=alt.X('UPC_PRODUCT_TYPE:N', title='Product Type', sort='-y'),
    y=alt.Y('DOLLARS:Q', title='Dollars'),
    color=alt.value('#1E4B92'),
).properties(
    title='Top Selling Products by Revenue'
).configure_title(
    anchor='middle'
)






### NEXT CHART

# Filter the dataframe by item and New York area
ny_pepsico_item_df = filter_ny_pepsico_df[(filter_ny_pepsico_df['MskdName'] == selected_retailer) & (filter_ny_pepsico_df['UPC'] == selected_upc)]

# Convert 'YEAR' to datetime and set as index
ny_pepsico_item_df['YEAR'] = pd.to_datetime(ny_pepsico_item_df['YEAR'], format='%Y')
ny_pepsico_item_df.set_index('YEAR', inplace=True)

# Group the data by year and calculate the metrics
ny_pepsico_item_weekly_df = ny_pepsico_item_df.groupby('YEAR').agg(
    {'DOLLARS': 'sum', 'UNITS': 'sum', 'PR': 'mean', 'D': 'mean'}
)
ny_pepsico_item_weekly_df.columns = ['Revenue', 'Units Sold', 'Avg PR', 'Avg Marketing']

# Calculate the average price
ny_pepsico_item_weekly_df['Avg Price'] = ny_pepsico_item_weekly_df['Revenue'] / ny_pepsico_item_weekly_df['Units Sold']

# Set up altair chart base
base = alt.Chart(ny_pepsico_item_weekly_df.reset_index()).encode(
    alt.X('YEAR:T')
)

# Define the charts
chart1 = base.mark_line(color='blue').encode(
    alt.Y('Revenue:Q', title='Metrics'),
).properties(title=f"Pepsico's Revenue and Units Sold for Item {selected_upc} in NY for {selected_retailer}")

chart2 = base.mark_line(color='green').encode(
    alt.Y('Units Sold:Q', title='Metrics')
)

chart3 = base.mark_line(color='red').encode(
    alt.Y('Avg PR:Q', title='Metrics')
).properties(title=f"Pepsico's Avg PR and Avg Marketing for Item {selected_upc} in NY for {selected_retailer}")

chart4 = base.mark_line(color='purple').encode(
    alt.Y('Avg Marketing:Q', title='Metrics')
)

chart5 = base.mark_line(color='orange').encode(
    alt.Y('Avg Price:Q', title='Average Price')
).properties(title=f"Pepsico's Average Price for Item {selected_upc} in NY for {selected_retailer}")


# Creating tabs to display different KPIs
tab1, tab2, tab3 = st.tabs(["Market", "New York", "Pepsico"])

with tab1:
    st.altair_chart(chart_top_regions, use_container_width=True)

with tab2:
    # Displaying the two charts side by side
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.altair_chart(chart_top_retailers, use_container_width=True)
    with col2:
        st.altair_chart(chart_top_products, use_container_width=True)

with tab3:
    # Displaying the charts for Revenue and Units Sold
    st.altair_chart(chart1 + chart2, use_container_width=True)

    # Displaying the charts for Avg PR and Avg Marketing
    st.altair_chart(chart2, use_container_width=True)

    # Displaying the chart for Avg Price
    st.altair_chart(chart3, use_container_width=True)
