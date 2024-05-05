import pandas as pd
import numpy as np


class DataContainer:

    def __init__(self, cols):
        self.pipeline = []
        self.load_pipeline = []

    def load_source(self, data_source, loading_pipeline):
        pass

    def add_process(self, func):
        pass

    def add_c_process(self, c_func):
        pass

    def add_java_process(self, j_func):
        pass

    def visualize(self):
        pass
