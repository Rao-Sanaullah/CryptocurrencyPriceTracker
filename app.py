import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import ta 


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
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error {response.status_code}: Unable to fetch data for {coin_id}.")
            return None
    except Exception as e:
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
        st.error(f"An error occurred while fetching historical data: {e}")
        return None

# Function to add technical indicators like RSI, SMA
def add_technical_indicators(historical_data):
    historical_data['RSI'] = ta.RSI(historical_data['Price'], timeperiod=14)  # RSI
    historical_data['SMA_50'] = ta.SMA(historical_data['Price'], timeperiod=50)  # 50-Day Simple Moving Average
    historical_data['SMA_200'] = ta.SMA(historical_data['Price'], timeperiod=200)  # 200-Day Simple Moving Average
    return historical_data

# User input for selecting cryptocurrencies for comparison
coin_1 = st.selectbox("Select the first cryptocurrency", ["bitcoin", "ethereum", "ripple", "litecoin", "dogecoin"])
coin_2 = st.selectbox("Select the second cryptocurrency", ["bitcoin", "ethereum", "ripple", "litecoin", "dogecoin"])

# Fetch real-time data for both coins
real_time_data_1 = fetch_real_time_data(coin_1)
real_time_data_2 = fetch_real_time_data(coin_2)

if real_time_data_1 and real_time_data_2:
    st.subheader(f"💰 {real_time_data_1['name']} ({real_time_data_1['symbol'].upper()}) vs {real_time_data_2['name']} ({real_time_data_2['symbol'].upper()})")

    # Extract the current price and format it for EUR
    current_price_1_eur = real_time_data_1['market_data']['current_price']['eur']
    current_price_2_eur = real_time_data_2['market_data']['current_price']['eur']
    
    # Calculate the percentage change today
    price_change_24h_1 = real_time_data_1['market_data']['price_change_percentage_24h']
    price_change_24h_2 = real_time_data_2['market_data']['price_change_percentage_24h']
    
    # Display the price summary in a similar Google-style format
    st.write(f"### Market Summary")
    st.write(f"**{real_time_data_1['name']}**")
    st.write(f"**{current_price_1_eur:,.2f} EUR**")
    st.write(f"**{price_change_24h_1:+.2f}%** today")

    st.write(f"**{real_time_data_2['name']}**")
    st.write(f"**{current_price_2_eur:,.2f} EUR**")
    st.write(f"**{price_change_24h_2:+.2f}%** today")

    # Fetch Historical Data (Last 30 days) for both coins
    historical_data_1 = fetch_historical_data(coin_1)
    historical_data_2 = fetch_historical_data(coin_2)

    if historical_data_1 is not None and historical_data_2 is not None:
        historical_data_1 = add_technical_indicators(historical_data_1)
        historical_data_2 = add_technical_indicators(historical_data_2)

        # Plot Historical Price Data with Plotly
        fig = go.Figure()

        # Adding Trace for Cryptocurrency 1 Price
        fig.add_trace(go.Scatter(
            x=historical_data_1['Date'],
            y=historical_data_1['Price'],
            mode='lines',
            name=f"{real_time_data_1['name']} Price",
            line=dict(color='green', width=3)
        ))

        # Adding Trace for Cryptocurrency 2 Price
        fig.add_trace(go.Scatter(
            x=historical_data_2['Date'],
            y=historical_data_2['Price'],
            mode='lines',
            name=f"{real_time_data_2['name']} Price",
            line=dict(color='blue', width=3)
        ))

        # Add SMA (50 and 200)
        fig.add_trace(go.Scatter(
            x=historical_data_1['Date'],
            y=historical_data_1['SMA_50'],
            mode='lines',
            name=f"{real_time_data_1['name']} SMA 50",
            line=dict(color='orange', width=2, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=historical_data_1['Date'],
            y=historical_data_1['SMA_200'],
            mode='lines',
            name=f"{real_time_data_1['name']} SMA 200",
            line=dict(color='red', width=2, dash='dash')
        ))

        fig.add_trace(go.Scatter(
            x=historical_data_2['Date'],
            y=historical_data_2['SMA_50'],
            mode='lines',
            name=f"{real_time_data_2['name']} SMA 50",
            line=dict(color='yellow', width=2, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=historical_data_2['Date'],
            y=historical_data_2['SMA_200'],
            mode='lines',
            name=f"{real_time_data_2['name']} SMA 200",
            line=dict(color='purple', width=2, dash='dash')
        ))

        # Add Title and Layout for the Graph
        fig.update_layout(
            title=f"{real_time_data_1['name']} vs {real_time_data_2['name']} Price History (Last 30 Days)",
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

    # User input for portfolio tracking for both cryptocurrencies
    portfolio_quantity_1 = st.number_input(f"Enter the number of {real_time_data_1['name']} you own:", min_value=0.0, step=0.1, format="%.2f")
    portfolio_quantity_2 = st.number_input(f"Enter the number of {real_time_data_2['name']} you own:", min_value=0.0, step=0.1, format="%.2f")

    if portfolio_quantity_1 > 0:
        # Calculate the current portfolio value in EUR and USD for Coin 1
        portfolio_value_1_eur = portfolio_quantity_1 * current_price_1_eur
        portfolio_value_1_usd = portfolio_quantity_1 * real_time_data_1['market_data']['current_price']['usd']

        # Display portfolio value for Coin 1
        st.write(f"**Your Portfolio Value for {real_time_data_1['name']}**")
        st.write(f"**{portfolio_quantity_1} {real_time_data_1['name']}** is worth: {portfolio_value_1_eur:,.2f} EUR")

    if portfolio_quantity_2 > 0:
        # Calculate the current portfolio value in EUR and USD for Coin 2
        portfolio_value_2_eur = portfolio_quantity_2 * current_price_2_eur
        portfolio_value_2_usd = portfolio_quantity_2 * real_time_data_2['market_data']['current_price']['usd']

        # Display portfolio value for Coin 2
        st.write(f"**Your Portfolio Value for {real_time_data_2['name']}**")
        st.write(f"**{portfolio_quantity_2} {real_time_data_2['name']}** is worth: {portfolio_value_2_eur:,.2f} EUR")

else:
    st.error("Error: Unable to fetch cryptocurrency data. Please try again later.")
