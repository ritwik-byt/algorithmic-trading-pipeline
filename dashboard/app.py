import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go

# 1. Page Configuration (This styles our web browser tab)
st.set_page_config(page_title="Algorithmic Trading Dashboard", layout="wide")

# 2. Establish connection to our MySQL Database
def get_data():
    db_user = 'root'
    db_password = 'Trading123'  # Your updated database password
    db_host = '127.0.0.1'
    db_port = '3306'
    db_name = 'trading_platform'
    
    # Using the robust pymysql driver adapter
    engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    
    # Query the analytical table we built in SQL
    query = "SELECT * FROM TradingSignals ORDER BY Date ASC;"
    df = pd.read_sql(query, con=engine)
    return df

# Load the data into the app
try:
    df = get_data()
except Exception as e:
    st.error(f"Database connection failed! Error: {e}")
    st.stop()

# 3. Create the Header Text
st.title("📈 Quantitative Trading Analytics Dashboard")
st.markdown("This dashboard pulls live analytics directly from our structured MySQL trading database.")
st.markdown("---")

# 4. Create Sidebar Filter (Dropdown menu to choose a stock)
ticker_list = df['Ticker'].unique()
selected_ticker = st.sidebar.selectbox("Select Stock Ticker:", ticker_list)

# Filter our main table down to just the stock the user picked
filtered_df = df[df['Ticker'] == selected_ticker]

# Grab the most recent row of data to display summary cards
latest_data = filtered_df.iloc[-1]

# 5. Create Key Performance Indicator (KPI) Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label=f"Current {selected_ticker} Price", value=f"${latest_data['Close']:.2f}")
with col2:
    st.metric(label="Daily Return", value=f"{latest_data['DailyReturn']*100:.2f}%")
with col3:
    st.metric(label="30-Day Volatility", value=f"{latest_data['Volatility30']:.2f}")
with col4:
    signal = latest_data['SignalFlag']
    st.metric(label="Engine Signal", value=signal)

st.markdown("---")

# 6. Build the Interactive Chart using Plotly
st.subheader(f"{selected_ticker} Price Trend & Moving Averages")

fig = go.Figure()

# Plot the standard closing price line
fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['Close'], name='Closing Price', line=dict(color='#1f77b4', width=2)))

# Plot the short-term 20-day moving average line
fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['MA20'], name='20-Day SMA', line=dict(color='#ff7f0e', width=1.5, dash='dash')))

# Plot the long-term 50-day moving average line
fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['MA50'], name='50-Day SMA', line=dict(color='#2ca02c', width=1.5, dash='dot')))

# Format the chart spacing and theme layout
fig.update_layout(
    template="plotly_dark",
    xaxis_title="Timeline",
    yaxis_title="Price (USD)",
    margin=dict(l=20, r=20, t=20, b=20),
    height=500,
    hovermode="x unified"
)

# Display the final chart inside our Streamlit app page
st.plotly_chart(fig, use_container_width=True)