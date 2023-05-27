# Import necessary modules
import streamlit as st
import pandas as pd
from PIL import Image
import altair as alt

# Setting theme for streamlit
favicon = Image.open('data/images/favicon.png')
st.set_page_config(
    page_title="Pepsico Inc. Dashboard", 
    page_icon=favicon, 
    layout="wide", 
    initial_sidebar_state="expanded",
)

# Set the title
st.title('Pepsico Inc. Dashboard')

# Define Streamlit widgets for filters
st.sidebar.image("data/images/logo.png", output_format='PNG', use_column_width=True)

# Load the data
@st.cache_data
def load_data():
    dataframes = {
        'ny_pepsico_df_2011': pd.read_csv('data/output/ny_pepsico_df_2011.csv'),
        'ny_pepsico_df_2012': pd.read_csv('data/output/ny_pepsico_df_2012.csv'),
        'ny_pepsico_item_weekly_df': pd.read_csv('data/output/ny_pepsico_item_weekly_df.csv'),
        'ny_pepsico_top_customers_df': pd.read_csv('data/output/ny_pepsico_top_customers_df.csv'),
        'ny_pepsico_vsod_df': pd.read_csv('data/output/ny_pepsico_vsod_df.csv'),
        'ny_promo_pct_df': pd.read_csv('data/output/ny_promo_pct_df.csv'),
        'ny_top_products_df': pd.read_csv('data/output/ny_top_products_df.csv'),
        'yearly_totals_df': pd.read_csv('data/output/yearly_totals_df.csv'),
        'top_regions_df': pd.read_csv('data/output/top_regions_df.csv'),
        'market_totals_df': pd.read_csv('data/output/market_totals_df.csv'),
    }
    return dataframes

data = load_data()
ny_pepsico_df_2011 = data['ny_pepsico_df_2011']
ny_pepsico_df_2012 = data['ny_pepsico_df_2012']
ny_pepsico_df = pd.concat([ny_pepsico_df_2011, ny_pepsico_df_2012], ignore_index=True)
ny_pepsico_top_customers_df = data['ny_pepsico_top_customers_df']
ny_pepsico_item_weekly_df = data['ny_pepsico_item_weekly_df']
ny_promo_pct_df = data['ny_promo_pct_df']
ny_top_products_df = data['ny_top_products_df']
yearly_totals_df = data['yearly_totals_df']
top_regions_df = data['top_regions_df']
ny_pepsico_vsod_df = data['ny_pepsico_vsod_df']
market_totals_df = data['market_totals_df']

# Get the unique years present in the DataFrame
unique_years = sorted(list(ny_pepsico_df['YEAR'].unique()))

# Use the years as options for the multiselect widget
selected_years = st.sidebar.multiselect(
    label="YEAR",
    options=unique_years,
    default=unique_years,
    key="filter_years"
)

if not selected_years:
    st.warning('Please select at least one option.')
    selected_years = unique_years  # Default to all years if none are selected

# Group by UPC, calculate the sum of DOLLARS, sort in descending order and reset the index
sorted_upc_df = ny_pepsico_df.groupby('UPC').agg({'DOLLARS': 'sum'}).sort_values('DOLLARS', ascending=False).reset_index()

# Get the sorted unique UPCs based on revenue
unique_upc = sorted_upc_df['UPC'].tolist()

# Use the UPCs as options for the selectbox widget
selected_upc = st.sidebar.selectbox(
    label="UPC",
    options=unique_upc,
    index=min(22, len(unique_upc)-1),  # Prevents IndexError
    key="filter_upc"
)

# Filter the DataFrame by the selected UPC
filter_ny_pepsico_upc_df = ny_pepsico_df[ny_pepsico_df['UPC'] == selected_upc]

# Get the unique retailers for the selected UPC
unique_retailers = sorted(list(filter_ny_pepsico_upc_df['MskdName'].unique()))

# Check if there are any unique retailers
if unique_retailers:
    # Use the retailers as options for the selectbox widget
    selected_retailer = st.sidebar.selectbox(
        label="RETAILER",
        options=unique_retailers,
        index=min(3, len(unique_retailers)-1),  # Prevents IndexError
        key="filter_retailer"
    )
else:
    # If there are no unique retailers, handle the exception here.
    st.sidebar.write('No retailers available for the selected UPC.')
    selected_retailer = None

# Add a slider to select the number of top products to display
selected_product_number = st.sidebar.slider("NO. PRODUCTS", 3, 20, 10)

# Filter the DataFrame based on the selected years
filter_ny_pepsico_df = ny_pepsico_df[ny_pepsico_df['YEAR'].isin(selected_years)]
filter_top_regions_df = top_regions_df[top_regions_df['YEAR'].isin(selected_years)]
filter_ny_top_products_df = ny_top_products_df[ny_top_products_df['YEAR'].isin(selected_years)]
filter_ny_pepsico_vsod_df = ny_pepsico_vsod_df[ny_pepsico_vsod_df['YEAR'].isin(selected_years)]
filter_ny_promo_pct_df = ny_promo_pct_df[ny_promo_pct_df['YEAR'].isin(selected_years)]
filter_market_totals_df = market_totals_df[market_totals_df['YEAR'].isin(selected_years)]

# Calculate total volume, revenue and vsod for selected years
total_volume = round(filter_market_totals_df[filter_market_totals_df['L3'] == 'PEPSICO INC']['total_volume'].sum(), 0)
total_revenue = round(filter_market_totals_df[filter_market_totals_df['L3'] == 'PEPSICO INC']['total_revenue'].sum(), 0)
total_volume_sold_on_deal = (filter_ny_pepsico_vsod_df['VSoD'].sum() / filter_ny_pepsico_vsod_df['TotalVolume'].sum()) * 100

# Calculate total market share
total_market_share_pepsico = filter_market_totals_df[filter_market_totals_df['L3'] == 'PEPSICO INC']['total_revenue'].sum()
total_market_share_all = filter_market_totals_df['total_revenue'].sum()
total_marketshare = (total_market_share_pepsico / total_market_share_all) * 100

# Display key kpis
with st.container():
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

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
    kpi4.metric(
        label = "Total Volume Sold on Deal",
        value = "{:,.2f}%".format(total_volume_sold_on_deal),
    )

# CHART: TOP REGIONS

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

# CHART: TOP RETAILERS

# Group by MskdName and sum UNITS and DOLLARS columns
ny_pepsico_customers_df = filter_ny_pepsico_df.groupby('MskdName').agg({'DOLLARS': 'sum', 'UNITS': 'sum'})

# Sort by DOLLARS column in descending order
ny_pepsico_top_customers_df = ny_pepsico_customers_df.sort_values('DOLLARS', ascending=False).reset_index()
ny_pepsico_top_customers_melt_df = ny_pepsico_top_customers_df.melt('MskdName', ['DOLLARS', 'UNITS'], 'Metric', 'Value')

# Create bar chart (dollars)
chart_retailers_revenue = alt.Chart(ny_pepsico_top_customers_melt_df[ny_pepsico_top_customers_melt_df['Metric']=='DOLLARS']).mark_bar().encode(
    x=alt.X('MskdName:N', sort=alt.EncodingSortField(field='Value', order='descending')),
    y=alt.Y('Value:Q', axis=alt.Axis(title='Revenue ($)', titleColor='#1E4B92')),
    color=alt.value('#1E4B92'),
).properties(
    title='Top Retailers by Revenue',
)

# Create line chart (units)
chart_retailers_units = alt.Chart(ny_pepsico_top_customers_melt_df[ny_pepsico_top_customers_melt_df['Metric']=='UNITS']).mark_line().encode(
    x=alt.X('MskdName:N'),
    y=alt.Y('Value:Q', axis=alt.Axis(title='Units (#)',  titleColor='red')),
    color=alt.value('red'),
)

# Combine charts
chart_top_retailers = alt.layer(chart_retailers_revenue, chart_retailers_units).resolve_scale(
    y='independent' 
).configure_title(
    anchor='middle'
)

# CHART: TOP PRODUCTS

# Group by UPC, and sum DOLLARS and UNITS
ny_top_products_df = filter_ny_top_products_df.groupby('UPC').agg({'DOLLARS': 'sum', 'UNITS': 'sum'}).reset_index()

# Sort by DOLLARS column in descending order and select the top N products
ny_top_products_df = ny_top_products_df.sort_values('DOLLARS', ascending=False).head(selected_product_number)

# Create Altair bar chart
chart_top_products = alt.Chart(ny_top_products_df).mark_bar().encode(
    x=alt.X('UPC:N', title='UPC', sort='-y'),
    y=alt.Y('DOLLARS:Q', title='Revenue ($)'),
    color=alt.value('#1E4B92'),
).properties(
    title='Top Selling Products by Revenue'
).configure_title(
    anchor='middle'
)

# CHART: PROMOTION PER UPC

# Calculate weighted average of PR using UNITS as weights
ny_promo_pct_df['WEIGHTED_PR'] = ny_promo_pct_df['PR'] * ny_promo_pct_df['UNITS']
ny_promo_pct_df = ny_promo_pct_df.groupby('UPC').agg({'WEIGHTED_PR': 'sum', 'UNITS': 'sum', 'DOLLARS': 'sum'}).reset_index()
ny_promo_pct_df['WEIGHTED_AVG_PR'] = ny_promo_pct_df['WEIGHTED_PR'] / ny_promo_pct_df['UNITS']

# Sort by DOLLARS column in descending order and select the top N products
ny_promo_pct_df = ny_promo_pct_df.sort_values('DOLLARS', ascending=False).head(selected_product_number)

# Create Altair bar chart with filtered products
chart_promo_pct = alt.Chart(ny_promo_pct_df).mark_bar().encode(
    x=alt.X('UPC:N', title='UPC', sort=alt.EncodingSortField(field='DOLLARS', order='descending')),
    y=alt.Y('WEIGHTED_AVG_PR:Q', title='Average PR (%)'),
    color=alt.value('#1E4B92'),
).properties(
    title='Average Promotional Activity for Top Products'
).configure_title(
    anchor='middle'
)

# CHARTS: REVENUE, UNITS, AVERAGE PR AND MARKETING, AND AVERAGE PRICE

# Filter the dataframe by item and New York area
ny_pepsico_item_df = filter_ny_pepsico_df[(filter_ny_pepsico_df['MskdName'] == selected_retailer) & (filter_ny_pepsico_df['UPC'] == selected_upc)].copy()

# Convert 'Calendar week starting on' to datetime
ny_pepsico_item_df['Calendar week starting on'] = pd.to_datetime(ny_pepsico_item_df['Calendar week starting on'])

# Set 'Calendar week starting on' as the index
ny_pepsico_item_df.set_index('Calendar week starting on', inplace=True)

# Group the data by week and calculate the metrics
ny_pepsico_item_weekly_df = ny_pepsico_item_df.resample('W').agg(
    {'DOLLARS': 'sum', 'UNITS': 'sum', 'PR': 'mean', 'D': 'mean'}
)
ny_pepsico_item_weekly_df.columns = ['Revenue', 'Units Sold', 'Avg PR', 'Avg Marketing']

# Calculate the average price
ny_pepsico_item_weekly_df['Avg Price'] = ny_pepsico_item_weekly_df['Revenue'] / ny_pepsico_item_weekly_df['Units Sold']

# Reset the index for Altair plotting
ny_pepsico_item_weekly_df = ny_pepsico_item_weekly_df.reset_index()

# Base layer
base = alt.Chart(ny_pepsico_item_weekly_df).encode(
    alt.X('Calendar week starting on:T', title='Week')
)

# Select the boundaries
def get_min_max_values(df):
    if df.empty:
        min_revenue = ""
        max_revenue = ""
        min_units_sold = ""
        max_units_sold = ""
    else:
        min_revenue = df['Revenue'].min()
        max_revenue = df['Revenue'].max()
        min_units_sold = df['Units Sold'].min()
        max_units_sold = df['Units Sold'].max()

    return min_revenue, max_revenue, min_units_sold, max_units_sold

min_revenue, max_revenue, min_units_sold, max_units_sold = get_min_max_values(ny_pepsico_item_weekly_df)

# Define the charts
chart_revenue = base.mark_line().encode(
    alt.Y('Revenue:Q', axis=alt.Axis(title='Revenue ($)', titleColor='#1E4B92'), scale=alt.Scale(zero=False)),
    color=alt.value('#1E4B92'),
    tooltip=['Revenue', 'Calendar week starting on']
)

chart_units = base.mark_line().encode(
    alt.Y('Units Sold:Q', axis=alt.Axis(title='Units Sold (#)', titleColor='green'), scale=alt.Scale(domain=(min_units_sold, max_revenue))),
    color=alt.value('green'),
    tooltip=['Units Sold', 'Calendar week starting on']
)

# Combine chart_revenue and chart_units with independent Y scales
chart_financials = alt.layer(chart_revenue, chart_units).resolve_scale(y='independent').properties(
    title={"text": f"Revenue & Units Sold for Item {selected_upc} for {selected_retailer}", "anchor": "middle"},
    width=600,
    height=300
)

chart_average_pr = base.mark_line().encode(
    alt.Y('Avg PR:Q', axis=alt.Axis(title='Average PR (%)', titleColor='red')),
    color=alt.value('red'),
    tooltip=['Avg PR', 'Calendar week starting on']
)

chart_average_marketing = base.mark_line().encode(
    alt.Y('Avg Marketing:Q', axis=alt.Axis(title='Average Marketing (%)', titleColor='purple')),
    color=alt.value('purple'),
    tooltip=['Avg Marketing', 'Calendar week starting on']
)

# Combine chart_average_pr and chart_average_marketing with independent Y scales
chart_advertising = alt.layer(chart_average_pr, chart_average_marketing).resolve_scale(y='independent').properties(
    title={"text": f"Avg. PR & Marketing for Item {selected_upc} for {selected_retailer}", "anchor": "middle"},
    width=600,
    height=300
)

chart_average_price = base.mark_line().encode(
    alt.Y('Avg Price:Q', axis=alt.Axis(title='Average Price ($)', titleColor='orange'),scale=alt.Scale(zero=False)),
    color=alt.value('orange'),
    tooltip=['Avg Price', 'Calendar week starting on']
).properties(title={"text": f"Avg. Price for Item {selected_upc} for {selected_retailer}", "anchor": "middle"})


# Create tabs to display different KPIs
tab1, tab2, tab3 = st.tabs(["Total Market", "New York", "Pepsico (New York)"])

with tab1:
    # Display the chart for top regions
    st.altair_chart(chart_top_regions, use_container_width=True)

with tab2:
    # Display the chart for top retailers
    st.altair_chart(chart_top_retailers, use_container_width=True)

    # Display the two charts side by side
    col1, col2 = st.columns(2, gap="small")
    with col1:
        # Display the chart for promotion per item
        st.altair_chart(chart_promo_pct, use_container_width=True)
        
    with col2:
        # Display the chart for top performing products
        st.altair_chart(chart_top_products, use_container_width=True)

with tab3:
    # Display the charts for revenue and units sold
    st.altair_chart(chart_financials, use_container_width=True)

    # Display the charts for average PR and average marketing
    st.altair_chart(chart_advertising, use_container_width=True)

    # Display the chart for average price
    st.altair_chart(chart_average_price, use_container_width=True)
