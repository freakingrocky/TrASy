import polars as pol
from SECRETS import INFLUXDB_TOKEN, INFLUX_ORG, INFLUX_URL
from CONSTANTS import CFUNC, JAVAFUNC
from influxdb_client import InfluxDBClient
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from copy import copy
import asyncio
import ctypes
import os
import platform
import subprocess

from typing import Callable


class DataContainer:

    def __init__(self, name: str, retention_rules: list = []) -> None:
        """
        Initialize a new instance of DataContainer class.

        This method creates a new InfluxDB bucket with the given name. If a bucket with the same name already exists,
        it retrieves the bucket ID. If no bucket exists, it creates a new bucket with the provided retention rules.

        Parameters:
            - name (str): The name of the InfluxDB bucket.
            - retention_rules (list, optional): A list of retention rules for the bucket. Defaults to an empty list.

        Returns:
            - None

        Raises:
            - AssertionError: If the name parameter is not a string.
        """
        assert isinstance(name, str), "name must be a string"

        self.load_pipeline = []
        self.influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUXDB_TOKEN, org=INFLUX_ORG)
        self.influx_buckets_api = self.influx_client.buckets_api()

        # Check if the bucket with the given name exists
        existing_buckets = self.influx_buckets_api.find_buckets().buckets
        existing_bucket = next((b for b in existing_buckets if b.name == name), None)

        if existing_bucket:
            self.bucket_id = existing_bucket.id
        else:
            # Create a new bucket
            created_bucket = self.influx_buckets_api.create_bucket(bucket_name=name, retention_rules=retention_rules, org_id=INFLUX_ORG)
            self.bucket_id = created_bucket.id  # Retrieve bucket ID

        assert self.bucket_id, "Error with InfluxDB API, Try Running the test_influxDB.py script to debug"

    async def load_with_func(self, loading_func: Callable, *args) -> None:
        """
        Load data into the InfluxDB bucket using a provided function.

        Warning: This method is mainly intended for backtesting purposes.

        Parameters:
            - loading_func (Callable): A function that processes the data source and returns a record that can be written to InfluxDB.
            - *args: Variable length argument list to be passed to the loading_func.

        Returns:
            - None

        Raises:
            - AssertionError: If the loading_func is not a callable object.
        """
        assert isinstance(loading_func, Callable), "loading_pipeline must be a function"

        async with InfluxDBClientAsync(
            url=INFLUX_URL, token=INFLUXDB_TOKEN, org=INFLUX_ORG
        ) as client:
            await client.write_api().write(bucket=self.bucket_id, record=loading_func(*args))

    async def load_source(self, data_source, loading_pipeline: Callable|None = None, preserve_load_pipeline: bool = False, unique_load_pipeline: bool = False) -> None:
        """
        Load data into the InfluxDB bucket using a loading pipeline.

        Parameters:
            - data_source (Any): The data source to be loaded into the InfluxDB bucket.
            - loading_pipeline (Callable, optional): A function or callable object that processes the data source. Defaults to None.
            - preserve_load_pipeline (bool, optional): If True, the loading pipeline will be preserved for future data loading. Defaults to False.
            - unique_load_pipeline (bool, optional): If True, only the provided loading pipeline will be used for data loading. Defaults to False.

        Returns:
            - None

        Raises:
            - AssertionError: If no loading pipeline is provided.
            - AssertionError: If both preserve_load_pipeline and unique_load_pipeline are True.
            - Exception: If an invalid process type is encountered.
        """
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
                result = subprocess.run(["java", f"{process[0]}" + data_source], capture_output=True, text=True)
                data_source = result.stdout
            else:
                raise Exception(f"Invalid process type: {process[2]}")

        async with InfluxDBClientAsync(
            url=INFLUX_URL, token=INFLUXDB_TOKEN, org=INFLUX_ORG
        ) as client:
            await client.write_api().write(bucket=self.bucket_id, record=data_source)


    async def get_polars(self, query: str) -> pol.DataFrame:
        """
        Warning: Mainly meant for Backtesting only.

        This method retrieves data from InfluxDB using a provided Flux query and converts it into a Polars DataFrame.

        Parameters:
            - query (str): A valid Flux query string.

        Returns:
            - pol.DataFrame: A Polars DataFrame containing the retrieved data.

        Raises:
            - AssertionError: If the provided query is not a string.

        Note:
            - This method is asynchronous and should be used with the `await` keyword when calling it.
        """
        assert isinstance(query, str), "Query must be a string containing valid flux code."

        async with InfluxDBClientAsync(
            url=INFLUX_URL, token=INFLUXDB_TOKEN, org=INFLUX_ORG
        ) as client:
            query_api = client.query_api()
            result = await query_api.query_data_frame(org=INFLUX_ORG, query=query)
            polars_data = pol.from_pandas(result)

        return polars_data


    def add_process(self, func: Callable) -> None:
        """
        Add a function to the data loading pipeline.

        This method appends a function to the load_pipeline list. The function will be executed during data loading.

        Parameters:
            - func (Callable): The function to be added to the load_pipeline. The function should take one argument (data_source) and return processed data.

        Returns:
            - None

        Raises:
            - AssertionError: If the provided func is not a callable object.

        Note:
            - The function will be executed with the data_source as its argument.
            - The order of execution in the load_pipeline is the same as the order of addition.
        """
        assert isinstance(func, Callable), "func must be a function"
        self.load_pipeline.append((func, 0))

    def add_c_process(self, c_func: str, c_types: list, comp_options: str = None) -> None:
        """
        Add a C function to the data loading pipeline.

        This method compiles a C function into a shared library, loads it using ctypes, and appends it to the load_pipeline list.
        The C function will be executed during data loading.

        Parameters:
            - c_func (str): The path to the C file to be compiled.
            - c_types (list): A list containing the types of the arguments and return of the C function.
            - comp_options (str, optional): Additional compiler options. Defaults to None.

        Returns:
            - None

        Raises:
            - AssertionError: If the provided c_types is not a list.
            - AssertionError: If the provided c_func is not a string.

        Note:
            - The C function should be compiled with the -shared option to create a shared library.
            - The C function should be placed in the 'c_funcs' directory within the current working directory.
        """
        assert isinstance(c_types, list), "c_types must be a list containing the types of the arguments and return of the C function"
        assert isinstance(c_func, str), "c_func must be a string containing the path to the C file uncompiled"

        os.execute(f"gcc -shared -o {os.path.join(os.cwd(), 'c_funcs', os.path.basename(c_func))}{' ' + comp_options + ' ' if comp_options else ''}{' -fPIC' if platform.system.lower() != 'windows' else ''} {c_func}")
        c_func = ctypes.CDLL('./c_funcs/' + os.path.basename(c_func))
        c_func.func.argtypes = c_types[:-1]
        c_func.func.restype = c_types[-1]
        self.load_pipeline.append((c_func, CFUNC))

    def add_java_process(self, j_func):
        """
        Add a Java function to the data loading pipeline.

        This method compiles a Java function into a bytecode file, compiles it, and appends it to the load_pipeline list.
        The Java function will be executed during data loading.

        Parameters:
            - j_func (str): The name of the Java file to be compiled. The file should be located in the current working directory.

        Returns:
            - None

        Raises:
            - FileNotFoundError: If the Java file does not exist in the current working directory.
            - subprocess.CalledProcessError: If the 'javac' command fails to compile the Java file.

        Note:
            - The Java function should be placed in the same directory as the Python script.
            - The Java file should have a '.java' extension.
            - The Java function should be compiled with the 'javac' command before being added to the load_pipeline.
        """
        subprocess.run(["javac", f"{j_func}.java"])
        self.load_pipeline.append((j_func, JAVAFUNC))

    def destroy(self) -> None:
        self.influx_buckets_api.delete_bucket(self.bucket_id)

    def visualize(self, indicators: list):
        pol_df = asyncio.run(self.get_polars(indicators)) # TODO
        pass

    def process_exist_data(self):
        # TODO: Process whatever is already loaded
        pass
