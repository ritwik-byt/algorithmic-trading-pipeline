import os
import pandas as pd
import glob

def clean_stock_data():
    raw_folder = 'data/raw'
    processed_folder = 'data/processed'
    os.makedirs(processed_folder, exist_ok=True)
    
    csv_files = glob.glob(os.path.join(raw_folder, '*_raw.csv'))
    all_cleaned_data = []

    for file_path in csv_files:
        ticker_name = os.path.basename(file_path).split('_')[0]
        print(f"Cleaning data for: {ticker_name}")
        
        df = pd.read_csv(file_path)
        
        # Ensure the first column is named Date
        if 'Date' not in df.columns:
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            
        # Standardize column naming conventions
        df.columns = [str(col).replace(' ', '').replace('_', '').lower() for col in df.columns]
        
        rename_map = {}
        for col in df.columns:
            if 'date' in col: rename_map[col] = 'Date'
            elif 'open' in col: rename_map[col] = 'Open'
            elif 'high' in col: rename_map[col] = 'High'
            elif 'low' in col: rename_map[col] = 'Low'
            elif 'close' in col and 'adj' not in col: rename_map[col] = 'Close'
            elif 'adj' in col: rename_map[col] = 'AdjClose'
            elif 'vol' in col: rename_map[col] = 'Volume'

        df.rename(columns=rename_map, inplace=True)
        df['Ticker'] = ticker_name
        
        if 'AdjClose' not in df.columns:
            df['AdjClose'] = df['Close']
            
        required_cols = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'AdjClose', 'Volume']
        
        # Drop rows where the Date value is non-numeric or missing headers
        df = df[df['Date'].str.contains('Ticker|Price|date', case=False, na=False) == False]
        df = df[required_cols].dropna(subset=['Date', 'Close'])
        
        # Parse datetimes safely
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        df.dropna(subset=['Date'], inplace=True)
        
        all_cleaned_data.append(df)

    master_df = pd.concat(all_cleaned_data, ignore_index=True)
    master_df.drop_duplicates(subset=['Date', 'Ticker'], inplace=True)
    master_df.sort_values(by=['Ticker', 'Date'], inplace=True)
    
    output_path = os.path.join(processed_folder, 'master_stock_prices.csv')
    master_df.to_csv(output_path, index=False)
    print(f"\nSuccess! Cleaned master file generated with {len(master_df)} rows.")

if __name__ == '__main__':
    clean_stock_data()