import polars as pol
import numpy as np
from SECRETS import INFLUXDB_TOKEN


class DataContainer:

    def __init__(self): # todo: use influxdb instead of polars
        assert 'symbol' in schema.keys(), 'symbol is required for a DataContainer'
        assert isinstance(schema, dict), 'schema must be a dict'

        self.pipeline = []
        self.load_pipeline = []
        self.influx_db_connection = None

    def load_source(self, data_source, loading_pipeline: function|None = None, preserve_load_pipeline: bool = False):
        assert self.load_pipeline, 'A Loading Pipeline must be provided'
        assert data_source, 'Data Source must not be empty'

        if preserve_load_pipeline:
            if self.load_pipeline:
                OVERRIDE = input('A Loading Pipeline Exists Already. Override? [Y/N]')
                while OVERRIDE not in ['Y', 'N']:
                    OVERRIDE = input('Input not recognized. Please input Y and press enter for Yes, and N for No.')

                if OVERRIDE.capitalize() == 'Y':
                    self.load_pipeline = [loading_pipeline]

        if loading_pipeline and not OVERRIDE:
            self.time_data

        pass

    def add_process(self, func: function):
        pass

    def add_c_process(self, c_func):
        pass

    def add_java_process(self, j_func):
        pass

    def visualize(self, indicator: list):
        pass
