import influxdb_client
import pandas as pd
import pyodbc
from influxdb_client.client.write_api import SYNCHRONOUS

from PyTrasy.SECRETS import INFLUX_ORG, INFLUX_URL, INFLUXDB_TOKEN

# Define InfluxDB connection details
influx_url = INFLUX_URL
influx_token = INFLUXDB_TOKEN
influx_org = INFLUX_ORG
influx_bucket = "Historical Data"

# Connect to InfluxDB
client = influxdb_client.InfluxDBClient(url=influx_url, token=influx_token, org=influx_org, timeout=300_000)
query_api = client.query_api()

# Query to get distinct FileSymbols
query = """
from(bucket: "Historical Data")
|> range(start: 0)
|> keep(columns: ["FileSymbol"])
|> distinct(column: "FileSymbol")
|> group()
|> sort()
"""
result = query_api.query(org=influx_org, query=query)

# Convert result to DataFrame
file_symbols = [record['FileSymbol'] for table in result for record in table.records]
df_symbols = pd.DataFrame(file_symbols, columns=['SYMBOL'])

# Function to get the first and last timestamp for each symbol
def get_first_last_timestamps(symbol):
    query = f"""
    from(bucket: "{influx_bucket}")
    |> range(start: 0)
    |> filter(fn: (r) => r["FileSymbol"] == "{symbol}")
    |> keep(columns: ["_time"])
    |> sort(columns: ["_time"])
    """
    result = query_api.query(org=influx_org, query=query)
    timestamps = [record['_time'] for table in result for record in table.records]
    if timestamps:
        return timestamps[0], timestamps[-1]
    return None, None

# Connect to SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=FREAKINGROCKY\\SQLEXPRESS;'
    'DATABASE=INFLUX_HISTORICAL_SYMBOLS;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# Insert data into HistoricalData table
for symbol in df_symbols['SYMBOL']:
    begin, end = get_first_last_timestamps(symbol)
    if begin and end:
        available_deltas = '1 Minute'
        available_indicators = 'none'
        cursor.execute("""
            INSERT INTO HistoricalData (SYMBOL, [BEGIN], [END], AVAILABLE_DELTAS, AVAILABLE_INDICATORS)
            VALUES (?, ?, ?, ?, ?)
        """, symbol, begin, end, available_deltas, available_indicators)
        conn.commit()

# Close the connection
cursor.close()
conn.close()
client.close()
