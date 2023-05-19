# H&M KPI Dashboard

Welcome to the H&M KPI dashboard, a powerful solution built using Streamlit to help you explore and analyze the most desired KPIs of H&M. 

Try the dashboard: [H&M KPI Dashboard](https://mistermakc-capstone.streamlit.app)

<img width="1434" alt="Screenshot 2023-04-06 at 12 17 49" src="https://user-images.githubusercontent.com/60471340/230348609-e880032b-0541-442a-8c90-5f59cadde75c.png">

## Features

The H&M KPI dashboard provides the following features:

1. **User Authentication**: Secure access to the dashboard through a login system.
2. **Easy Navigation**: Navigate to different tabs to explore various aspects of H&M's data, such as Revenue, Marketing, and Resources.
3. **Interactive Filters**: Use multiple filters to quickly sift through data and narrow down the information you're looking for (e.g. year and month, sales channel, etc.).
4. **Visually Appealing Charts and Graphs**: Gain insights through simple and colorful visualizations that provide a comprehensive overview of each KPI.
5. **Data-Driven Decisions**: Leverage the power of data to drive success for your business and stay ahead of the competition.

## How to Use

1. **Log in** to the dashboard using your credentials.
   - Name: `Capstone`
   - Password: `Pandas2020!`
   > To change your password, use the `pass_gen.py` file to hash your password and store your username and password in the `config.yaml` file
2. Navigate through the **Revenue**, **Marketing**, **Customers**, and **Resources** tabs or have a close-up view at all the **Product Sales**.
3. On each page, use the **sidebar filters** to explore data based on your preferences.
4. View the **KPIs** and **charts** displayed on the pages to understand trends and patterns in the data.
5. Log out when you're finished.

## Page Structure:
1. **Login page:** Initial log-in page, then KPI page and log-out page
2. **Revenue:** Tab dedicated to the analysis of H&M's revenue statistics
3. **Marketing:** Tab dedicated to the analysis of H&M's marketing efforts
4. **Resources:** Tab dedicated to the analysis of H&M's customers and inventory
5. **Product Sales:** Expander dedicated to the analysis of H&M's product sales

## Required Modules

Before using the dashboard, the following Python modules must be installed:

1. Streamlit: `pip install streamlit`
2. Pandas: `pip install pandas`
3. Requests: `pip install requests`
4. Retry: `pip install retry`
5. Authenticator: `pip install authenticator`
6. Altair: `pip install altair`
7. Pillow: `pip install pillow`
8. Streamlit Authenticator: `pip install streamlit_authenticator`
9. YAML: `pip install yaml`

