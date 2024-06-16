import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import polars as pol
import datetime as dt

# Secrets and connection parameters
from PyTrasy.SECRETS import INFLUXDB_TOKEN, INFLUX_ORG, INFLUX_URL

# Ignore Known Warnings from InfluxDB Client
import warnings
warnings.filterwarnings('ignore')


# Initialize connection
token = INFLUXDB_TOKEN
org_name = INFLUX_ORG  # Assuming this is the name of the organization
url = INFLUX_URL
bucket_name = "TraSy Test"

try:
    # Create client
    client = InfluxDBClient(url=url, token=token, org=org_name)

    # Fetch organization details to get the correct org ID
    orgs_api = client.organizations_api()
    orgs = orgs_api.find_organizations()
    org = next((o for o in orgs if o.name == org_name), None)
    if not org:
        raise ValueError(f"Organization '{org_name}' not found.")
    org_id = org.id

    # Create bucket
    influxdb_buckets_api = client.buckets_api()
    new_bucket = influxdb_client.domain.bucket.Bucket(
        name=bucket_name,
        retention_rules=[],
        org_id=org_id  # Use the correct org ID
    )
    created_bucket = influxdb_buckets_api.create_bucket(new_bucket)
    bucket_id = created_bucket.id  # Retrieve bucket ID

    # Write data to bucket
    write_api = client.write_api(write_options=SYNCHRONOUS)
    point = Point("measurement1").field("value", 10.0).time(time=dt.datetime.utcnow(), write_precision=WritePrecision.NS)
    write_api.write(bucket=bucket_name, org=org_name, record=point)

    # Query data from bucket
    query_api = client.query_api()
    query = f"""
    from(bucket: "{bucket_name}")
      |> range(start: -10m)
      |> filter(fn: (r) => r._measurement == "measurement1")
    """
    tables = query_api.query(query, org=org_name)
    data_frame = query_api.query_data_frame(query)
    polars_data = pol.from_pandas(data_frame)

    # Debug: Print the data_frame columns and first few rows
    # print(f"DataFrame Columns: {data_frame.columns}")
    # print(f"First few rows:\n{data_frame.head()}")

    # Assertion to verify connection and data
    assert not polars_data.is_empty(), "Query returned no data."
    assert "_value" in polars_data.columns, "Expected column 'value' not found."
    assert polars_data["_value"].is_not_null().all(), "Null values found in 'value' column."

    print("InfluxDB connection is verified.")

except Exception as e:
    print(f"Error verifying InfluxDB connection: {e}")

finally:
    # Clean up: delete the test bucket
    if 'bucket_id' in locals():
        influxdb_buckets_api.delete_bucket(bucket_id)

    # Close client
    client.close()
