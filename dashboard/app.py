import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Algorithmic Trading Dashboard", layout="wide")

def get_data():
    # Try connecting to the local MySQL database first
    try:
        db_user = 'root'
        db_password = 'Trading123'
        db_host = '127.0.0.1'
        db_port = '3306'
        db_name = 'trading_platform'
        
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
        query = "SELECT * FROM TradingSignals ORDER BY Date ASC;"
        return pd.read_sql(query, con=engine)
    except Exception as db_error:
        # Fallback: If database isn't reachable, look for a generated signals backup CSV
        st.sidebar.warning("Running in Cloud/Offline Mode (Using static CSV data engine)")
        
        # We check if a fallback file exists, or generate one from our master file
        processed_csv = 'data/processed/master_stock_prices.csv'
        if os.path.exists(processed_csv):
            # This loads the base dataset safely if MySQL is sleeping
            df = pd.read_csv(processed_csv)
            # Add simple fallback columns to match the database structure for the UI
            df['DailyReturn'] = df.groupby('Ticker')['Close'].pct_change()
            df['MA20'] = df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(20).mean())
            df['MA50'] = df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(50).mean())
            df['Volatility30'] = df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(30).std())
            df['SignalFlag'] = ['BUY' if m20 > m50 else 'SELL' for m20, m50 in zip(df['MA20'], df['MA50'])]
            return df
        else:
            raise db_error

try:
    df = get_data()
except Exception as e:
    st.error(f"Data loading failed! Error: {e}")
    st.stop()

# --- The rest of the code stays exactly the same ---
st.title("📈 Quantitative Trading Analytics Dashboard")
st.markdown("This dashboard pulls live analytics directly from our structured MySQL trading database.")
st.markdown("---")

ticker_list = df['Ticker'].unique()
selected_ticker = st.sidebar.selectbox("Select Stock Ticker:", ticker_list)

filtered_df = df[df['Ticker'] == selected_ticker]
latest_data = filtered_df.iloc[-1]

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
st.subheader(f"{selected_ticker} Price Trend & Moving Averages")

fig = go.Figure()
fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['Close'], name='Closing Price', line=dict(color='#1f77b4', width=2)))
fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['MA20'], name='20-Day SMA', line=dict(color='#ff7f0e', width=1.5, dash='dash')))
fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['MA50'], name='50-Day SMA', line=dict(color='#2ca02c', width=1.5, dash='dot')))

fig.update_layout(template="plotly_dark", xaxis_title="Timeline", yaxis_title="Price (USD)", margin=dict(l=20, r=20, t=20, b=20), height=500, hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)