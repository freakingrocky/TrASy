import pandas as pd
from PyTrasy.SECRETS import INFLUXDB_TOKEN, INFLUX_ORG, INFLUX_URL
from lightweight_charts import Chart
from influxdb_client import InfluxDBClient

def main():
    # Initialize the InfluxDB client
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUXDB_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()

    # InfluxDB connection details
    BUCKET_NAME = "Historical Data"

    # Define the Flux query to get data for the specific FileSymbol
    query = f'''
    from(bucket: "{BUCKET_NAME}")
      |> range(start: 2012-01-01T00:00:00Z, stop: 2024-01-01T00:00:00Z)
      |> filter(fn: (r) => r["_measurement"] == "futures_data")
      |> filter(fn: (r) => r["FileSymbol"] == "HDFCBANK")
      |> filter(fn: (r) => r["_field"] == "Open" or r["_field"] == "High" or r["_field"] == "Low" or r["_field"] == "Close" or r["_field"] == "Volume")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''

    # Execute the query and retrieve the data
    result = query_api.query_data_frame(org=INFLUX_ORG, query=query)
    print(True)

    # Ensure the DataFrame has the correct types and index
    result['_time'] = pd.to_datetime(result['_time'])
    result.set_index('_time', inplace=True)
    result = result[['Open', 'High', 'Low', 'Close', 'Volume']]

    # Prepare the data for Lightweight Charts
    data = result.reset_index()
    data['time'] = data['_time'].apply(lambda x: x.isoformat())
    data = data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
    data = data[['time', 'open', 'high', 'low', 'close', 'volume']]

    # Create the chart
    chart = Chart()

    # Set the data for the chart
    chart.set(data)

    # Show the chart
    chart.show(block=True)

if __name__ == '__main__':
    main()
