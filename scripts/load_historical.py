from PyTrasy import DataContainer
import os
import polars as pl

def csv_loading_func(args):
    file_path, symbol_name = args
    df = pl.read_csv(file_path)
    df = df.with_columns(
        (pl.col('Date') + ' ' + pl.col('Time')).str.strptime(pl.Datetime, '%Y-%m-%d %H:%M:%S').alias('datetime')
    )
    df = df.drop(['Date', 'Time'])


    # Ensure consistent field types
    df = df.with_columns(pl.col("OI").cast(pl.Int64))  # Cast OI to integer type
    df = df.with_columns(pl.col("Volume").cast(pl.Int64))  # Cast Volume to integer type

    records = []
    for row in df.iter_rows(named=True):
        record = {
            "measurement": "futures_data",
            "tags": {
                "FileSymbol": symbol_name,
                "BaseSymbol": row['Symbol'],
                "Expiry": row['Expiry'],
                "Strike": row['Strike'],
                "OptionType": row['OptionType']
            },
            "fields": {
                "Open": row['Open'],
                "High": row['High'],
                "Low": row['Low'],
                "Close": row['Close'],
                "Volume": row['Volume'],
                "OI": row['OI']
            },
            "time": row['datetime']
        }
        records.append(record)
    return records


import asyncio

async def process_csv_file(data_container, file_path, symbol_name):
    await data_container.load_with_func(csv_loading_func, file_path, symbol_name)

# Main function to process all CSV files
async def main():
    base_dir = r'C:\Users\freakingrocky\CS Stuff\Tracys\DATA\historical\NIFTY'
    data_container = DataContainer(name='Historical Data')


    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                symbol_name = os.path.splitext(file)[0]  # Extract symbol name from file name
                await process_csv_file(data_container, file_path, symbol_name)

# Run the main function
asyncio.run(main())
