import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def download_stock_data():
    tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL', 'AMZN']
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')
    
    print(f"Starting data download from {start_date} to {end_date}...")
    os.makedirs('data/raw', exist_ok=True)
    
    for ticker in tickers:
        print(f"Downloading {ticker}...")
        
        # Download data
        stock_df = yf.download(ticker, start=start_date, end=end_date)
        
        if not stock_df.empty:
            # FIX: If yfinance returns multi-index columns, flatten them out completely
            if isinstance(stock_df.columns, pd.MultiIndex):
                stock_df.columns = stock_df.columns.get_level_values(0)
                
            stock_df['Ticker'] = ticker
            
            # Save cleanly with a single header row
            file_path = f'data/raw/{ticker}_raw.csv'
            stock_df.to_csv(file_path)
            print(f"Successfully saved clean {ticker} raw CSV.")
        else:
            print(f"Warning: No data found for {ticker}")

    print("\nAll downloads finished successfully!")

if __name__ == '__main__':
    download_stock_data()