import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import talib

# Streamlit App Title
st.title("🚀 Cryptocurrency Price Tracker")

# Custom CSS for Styling
st.markdown("""
    <style>
        .css-1v3fvcr {
            color: #ffffff;
            font-family: 'Roboto', sans-serif;
            font-weight: bold;
        }
        .stTextInput > div > div > input {
            background-color: #f1f1f1;
            border-radius: 10px;
        }
        .css-1bb5k9w {
            background-color: #4CAF50;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Function to fetch real-time data from CoinGecko API
def fetch_real_time_data(coin_id='bitcoin'):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    try:
        response = requests.get(url)
        # Check if the response was successful
        if response.status_code == 200:
            return response.json()
        else:
            # If the response status is not 200, display error
            st.error(f"API Error {response.status_code}: Unable to fetch data for {coin_id}.")
            return None
    except Exception as e:
        # Handle any exceptions during the request
        st.error(f"An error occurred while fetching data: {e}")
        return None

# Function to fetch historical data (last 30 days)
def fetch_historical_data(coin_id='bitcoin'):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range?vs_currency=eur&from={start_timestamp}&to={end_timestamp}"
    try:
        response = requests.get(url)
        # Check if the response was successful
        if response.status_code == 200:
            data = response.json()
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['Timestamp', 'Price'])
            df['Date'] = pd.to_datetime(df['Timestamp'], unit='ms')
            return df
        else:
            st.error(f"API Error {response.status_code}: Unable to fetch historical data for {coin_id}.")
            return None
    except Exception as e:
        # Handle any exceptions during the request
        st.error(f"An error occurred while fetching historical data: {e}")
        return None

# User input for selecting cryptocurrency
coin = st.selectbox("Select Cryptocurrency", ["bitcoin", "ethereum", "ripple", "litecoin", "dogecoin"])

# Real-time data
real_time_data = fetch_real_time_data(coin)

if real_time_data:
    st.subheader(f"💰 {real_time_data['name']} ({real_time_data['symbol'].upper()})")

    # Extract the current price and format it for EUR
    try:
        current_price_eur = real_time_data['market_data']['current_price']['eur']
        current_price_usd = real_time_data['market_data']['current_price']['usd']
        price_change_24h = real_time_data['market_data']['price_change_percentage_24h']
        market_cap = real_time_data['market_data']['market_cap']['eur']
    except KeyError as e:
        st.error(f"Missing data in response: {e}")
        st.stop()

    # Display the price summary in a similar Google-style format
    st.write(f"### Market Summary")
    st.write(f"**{real_time_data['name']}**")
    st.write(f"**{current_price_eur:,.2f} EUR**")
    st.write(f"**{price_change_24h:+.2f}%** today")
    st.write(f"**Market Cap**: {market_cap:,.0f} EUR")

    # Fetch Historical Data (Last 30 days)
    # Check if historical data is already cached in session state
    if 'historical_data' not in st.session_state or st.session_state['historical_data_timestamp'] < datetime.now() - timedelta(minutes=30):
        historical_data = fetch_historical_data(coin)
        if historical_data is not None:
            st.session_state['historical_data'] = historical_data
            st.session_state['historical_data_timestamp'] = datetime.now()
    else:
        historical_data = st.session_state['historical_data']

    if historical_data is not None:
        # Plot Historical Price Data with Plotly
        fig = go.Figure()

        # Adding Trace for Cryptocurrency Price
        fig.add_trace(go.Scatter(
            x=historical_data['Date'],
            y=historical_data['Price'],
            mode='lines',
            name=f"{real_time_data['name']} Price",
            line=dict(color='green', width=3)
        ))

        # Add Title and Layout for the Graph
        fig.update_layout(
            title=f"{real_time_data['name']} Price History (Last 30 Days)",
            xaxis_title="Date",
            yaxis_title="Price (EUR)",
            template="plotly_dark",
            title_font=dict(size=20, color="white"),
            xaxis=dict(tickformat="%b %d", title_font=dict(size=14)),
            yaxis=dict(title_font=dict(size=14)),
            plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
            showlegend=True
        )

        # Display Plotly Chart
        st.plotly_chart(fig, use_container_width=True)

    # Portfolio Tracker - Enhanced Version
    st.subheader("🧮 Portfolio Tracker")

    # User input for portfolio tracking
    portfolio_quantity = st.number_input(f"Enter the number of {real_time_data['name']} you own:", min_value=0.0, step=0.1, format="%.2f")
    
    if portfolio_quantity > 0:
        # Calculate the current portfolio value in EUR and USD
        portfolio_value_eur = portfolio_quantity * current_price_eur
        portfolio_value_usd = portfolio_quantity * current_price_usd

        # Display portfolio value
        st.write(f"**Your Portfolio Value**")
        st.write(f"**{portfolio_quantity} {real_time_data['name']}** is worth:")
        st.write(f"**{portfolio_value_eur:,.2f} EUR**")
        st.write(f"**{portfolio_value_usd:,.2f} USD**")

        # Calculate and display portfolio change
        price_change = portfolio_quantity * (price_change_24h / 100) * current_price_eur
        st.write(f"**24h Portfolio Change**: {price_change:+,.2f} EUR")

else:
    st.error("Error: Unable to fetch cryptocurrency data. Please try again later.")
