import os
import polars as pl
from tqdm import tqdm
from PyTrasy import DataContainer
import asyncio

def csv_loading_func(args):
    file_path, symbol_name = args
    df = pl.read_csv(file_path)
    df = df.with_columns(
        pl.col('datetime').str.strptime(pl.Datetime, '%Y-%m-%d %H:%M:%S')
    )

    nifty_50_list = [
        "NIFTY 50", "EICHERMOT", "ADANIPORTS", "M&M", "SHRIRAMFIN", "TITAN", "ADANIENT", 
        "CIPLA", "SBILIFE", "BAJAJ-AUTO", "BPCL", "HDFCBANK", "RELIANCE", "ULTRACEMCO", 
        "HINDUNILVR", "BAJFINANCE", "TATAMOTORS", "HDFCLIFE", "AXISBANK", "GRASIM", 
        "JSWSTEEL", "ASIANPAINT", "SUNPHARMA", "BHARTIARTL", "ITC", "BRITANNIA", 
        "HINDALCO", "TATASTEEL", "POWERGRID", "COALINDIA", "MARUTI", "TATACONSUM", 
        "DRREDDY", "DIVISLAB", "BAJAJFINSV", "ICICIBANK", "KOTAKBANK", "ONGC", 
        "INFY", "NTPC", "APOLLOHOSP", "LTIM", "HEROMOTOCO", "NESTLEIND", "SBIN", 
        "INDUSINDBK", "LT", "HCLTECH", "WIPRO", "TCS", "TECHM"]

    # Ensure consistent field types
    df = df.with_columns(pl.col("volume").cast(pl.Int64))  # Cast volume to integer type

    records = []
    for row in df.iter_rows(named=True):
        record = {
            "measurement": "futures_data",
            "tags": {
                "FileSymbol": symbol_name,
                "BaseSymbol": 'NIFTY50' if row['symbol'].upper() in nifty_50_list else 'NIFTY200'
            },
            "fields": {
                "Open": row['open'],
                "High": row['high'],
                "Low": row['low'],
                "Close": row['close'],
                "Volume": row['volume'],
                "Expiry": None,
                "Strike": None,
                "OptionType": None,
                "OI": None
            },
            "time": row['datetime']
        }
        records.append(record)
    return records

def process_csv_file(data_container, file_path, symbol_name):
    records = csv_loading_func((file_path, symbol_name))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait_for(data_container.load_with_func(lambda _: records), timeout=7200))

def main():
    base_dir = r'C:\Users\freakingrocky\CS Stuff\Tracys\DATA\DATA\NF_200\NF_200_1min\big_data'
    data_container = DataContainer(name='Historical Data')

    # List all CSV files
    csv_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                symbol_name = os.path.splitext(file)[0]  # Extract symbol name from file name
                csv_files.append((file_path, symbol_name))


    csv_files.sort()
    index = 0
    while index < len(csv_files):
        if 'TCS' in csv_files[index]:
            break
        index += 1

    csv_files = csv_files[index:] + csv_files[:2]
    # Process each CSV file with a progress bar
    for file_path, symbol_name in tqdm(csv_files, desc="Processing CSV files"):
        process_csv_file(data_container, file_path, symbol_name)

if __name__ == '__main__':
    main()
