import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Algorithmic Trading Dashboard", layout="wide")

def get_data():
    # 1. Try connecting to the local MySQL database first
    try:
        db_user = 'root'
        db_password = 'Trading123'
        db_host = '127.0.0.1'
        db_port = '3306'
        db_name = 'trading_platform'
        
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
        query = "SELECT * FROM TradingSignals ORDER BY Date ASC;"
        df = pd.read_sql(query, con=engine)
        if not df.empty:
            return df
    except Exception:
        pass  
        
    # 2. Fallback: Check the file directly inside the dashboard folder
    local_backup = os.path.join(os.path.dirname(__file__), 'trading_signals_backup.csv')
    if os.path.exists(local_backup):
        df = pd.read_csv(local_backup)
        df['Date'] = df['Date'].astype(str)
        return df

    # 3. Last Resort Fallback
    fallback_csv = 'data/processed/master_stock_prices.csv'
    if os.path.exists(fallback_csv):
        df = pd.read_csv(fallback_csv)
        df['Date'] = df['Date'].astype(str)
        return df

    raise FileNotFoundError("Could not connect to MySQL or find any fallback data files.")

try:
    df = get_data()
except Exception as e:
    st.error(f"Data loading engine failed! Error: {e}")
    st.stop()

# --- Dashboard Layout Structure ---
st.title("📈 Quantitative Trading Analytics Dashboard")
st.markdown("This dashboard pulls live analytics directly from our structured MySQL trading database.")
st.markdown("---")

# MOVED TO MAIN PAGE: Dropdown menu sits cleanly below the title headers
ticker_list = sorted(df['Ticker'].dropna().unique())
selected_ticker = st.selectbox("🎯 Select Stock Ticker to Analyze:", ticker_list)

filtered_df = df[df['Ticker'] == selected_ticker].copy()
latest_data = filtered_df.iloc[-1]

# Display Real-Time Analytical KPI Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label=f"Current {selected_ticker} Price", value=f"${latest_data['Close']:.2f}")
with col2:
    st.metric(label="Daily Return", value=f"{latest_data['DailyReturn']*100:.2f}%")
with col3:
    st.metric(label="30-Day Volatility", value=f"{latest_data['Volatility30']:.2f}")
with col4:
    signal_key = 'SignalFlag' if 'SignalFlag' in latest_data else ('Signal' if 'Signal' in latest_data else None)
    signal = latest_data[signal_key] if signal_key else "N/A"
    st.metric(label="Engine Signal", value=str(signal).upper())

st.markdown("---")
st.subheader(f"{selected_ticker} Price Trend & Moving Averages")

# Construct Interactive Time-Series Charts via Plotly Engine
fig = go.Figure()
fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['Close'], name='Closing Price', line=dict(color='#1f77b4', width=2)))

if 'MA20' in filtered_df.columns:
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['MA20'], name='20-Day SMA', line=dict(color='#ff7f0e', width=1.5, dash='dash')))
if 'MA50' in filtered_df.columns:
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['MA50'], name='50-Day SMA', line=dict(color='#2ca02c', width=1.5, dash='dot')))

fig.update_layout(template="plotly_dark", xaxis_title="Timeline", yaxis_title="Price (USD)", margin=dict(l=20, r=20, t=20, b=20), height=500, hovermode="x unified")

# Fixed structural width parameter warning
st.plotly_chart(fig, width='stretch')