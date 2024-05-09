import polars as pol
from SECRETS import INFLUXDB_TOKEN, INFLUX_ORG, INFLUX_URL
from influxdb_client import InfluxDBClient
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from copy import copy
import asyncio
import ctypes
import os
import platform


class DataContainer:

    def __init__(self, name: str) -> None:
        assert isinstance(name, str), "name must be a string"

        self.load_pipeline = []
        self.influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUXDB_TOKEN, org=INFLUX_ORG)
        self.influx_buckets_api = self.influx_client.buckets_api()

        new_bucket = self.influx_client.domain.bucket.Bucket(
            name=name,
            retention_rules=[],
            org_id=INFLUX_ORG
        )
        created_bucket = self.influx_buckets_api.create_bucket(new_bucket)
        self.bucket_id = created_bucket.id  # Retrieve bucket ID
        assert self.bucket_id, "Error with InfluxDB API, Try Running the test_influxDB.py script to debug"


    async def load_source(self, data_source, loading_pipeline: function|None = None, preserve_load_pipeline: bool = False, unique_load_pipeline: bool = False) -> None:
        assert self.load_pipeline, 'A Loading Pipeline must be provided'
        assert not (preserve_load_pipeline and unique_load_pipeline), "A unique pipeline cannot be preserved and unique at the same time"

        load_pipeline = copy(self.load_pipeline)
        if preserve_load_pipeline:
            self.load_pipeline.append((loading_pipeline, 0))

        if unique_load_pipeline:
            load_pipeline = [(loading_pipeline, 0)]

        for process in load_pipeline:
            if process[1] == 0:
                data_source = process[0](data_source)
            if process[1] == 1:
                data_source = process[0].func(data_source)
            if process[2] == 2:
                pass
            else:
                raise Exception(f"Invalid process type: {process[2]}")

        async with InfluxDBClientAsync(
            url=INFLUX_URL, token=INFLUXDB_TOKEN, org=INFLUX_ORG
        ) as client:
            await client.write_api().write(bucket=self.bucket_id, record=data_source)


    async def get_polars(self, query: str) -> pol.DataFrame:
        """Warning: Mainly meant for Backtesting only."""
        assert isinstance(query, str), "Query must be a string containing valid flux code."

        async with InfluxDBClientAsync(
            url=INFLUX_URL, token=INFLUXDB_TOKEN, org=INFLUX_ORG
        ) as client:
            query_api = client.query_api()
            result = await query_api.query_data_frame(org=INFLUX_ORG, query=query)
            polars_data = pol.from_pandas(result)

        return polars_data


    def add_process(self, func: function) -> None:
        self.load_pipeline.append((func, 0))

    def add_c_process(self, c_func: str, c_types: list, comp_options: str = None) -> None:
        assert isinstance(c_types, list), "c_types must be a list containing the types of the arguments and return of the C function"
        assert isinstance(c_func, str), "c_func must be a string containing the path to the C file uncompiled"

        os.execute(f"gcc -shared -o {os.path.join(os.cwd(), "c_funcs", os.path.basename(c_func))}{' ' + comp_options + ' ' if comp_options else ''}{' -fPIC' if platform.system.lower() != 'windows' else ''} {c_func}")
        c_func = ctypes.CDLL('./c_funcs/' + os.path.basename(c_func))
        c_func.func.argtypes = c_types[:-1]
        c_func.func.restype = c_types[-1]
        self.load_pipeline.append((c_func, 1))

    def add_java_process(self, j_func):
        self.load_pipeline.append((j_func, 2))

    def destroy(self) -> None:
        self.influx_buckets_api.delete_bucket(self.bucket_id)

    def visualize(self, indicators: list):
        asyncio.run(self.get_polars(indicators)) # TODO
        pass