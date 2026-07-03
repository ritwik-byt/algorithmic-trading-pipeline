import pandas as pd
from sqlalchemy import create_engine, text

def load_data_to_mysql():
    processed_file = 'data/processed/master_stock_prices.csv'
    
    # 1. Read our clean master CSV data
    print("Reading clean dataset...")
    df = pd.read_csv(processed_file)
    
    # 2. Database Connection Credentials
    # REPLACE 'your_root_password_here' WITH YOUR ACTUAL MYSQL ROOT PASSWORD
    db_user = 'root'
    db_password = 'Trading123' 
    db_host = '127.0.0.1'
    db_port = '3306'
    db_name = 'trading_platform'
    
    # Create the SQLAlchemy engine connection string
    connection_string = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)
    
    # 3. Define SQL table schema explicitly
    create_table_query = """
    CREATE TABLE IF NOT EXISTS StockPrices (
        Date DATE,
        Ticker VARCHAR(10),
        Open DOUBLE,
        High DOUBLE,
        Low DOUBLE,
        Close DOUBLE,
        AdjClose DOUBLE,
        Volume BIGINT,
        PRIMARY KEY (Ticker, Date)
    );
    """
    
    print("Connecting to MySQL and ensuring table exists...")
    with engine.connect() as conn:
        conn.execute(text(create_table_query))
        conn.commit()
        
    # 4. Insert data using Pandas to_sql engine
    print(f"Loading {len(df)} rows into MySQL table 'StockPrices'...")
    
    # 'append' ensures if we update data later, it adds seamlessly.
    # index=False tells it not to create an extra column for row index numbers.
    df.to_sql(name='StockPrices', con=engine, if_exists='append', index=False)
    
    print("Data successfully loaded into MySQL!")

if __name__ == '__main__':
    load_data_to_mysql()