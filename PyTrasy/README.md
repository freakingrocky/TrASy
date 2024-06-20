# PyTracy
PyTracy is the Pythonic Component of Tracy. It is used for:
- API Calls *(reccomended for backtesting only)*
- Data Loading *(reccomended for backtesting only)*
- Strategy Building *(reccomended for prototyping only)*
- Visualizations 

## Data Loading
In order to load data, InfluxDB has several allowed Data Formats it can process. For simplicity, PyTraSy only supports dictionaries. Thus, your loading_pipeline must end up providing dictionary in the end of the loading pipeline in the following format, but it is easily editable in the Data.py file as needed:


```py
records = [
    {
 "measurement": "cpu",
    	 "tags": {"core": "0"},
    	 "fields": {"temp": 25.3},
    	 "time": 1657729063
    },
    {
    	 "measurement": "cpu",
    	 "tags": {"core": "0"},
    	 "fields": {"temp": 25.4},
    	 "time": 1657729078
    },
    {
 "measurement": "cpu",
    	 "tags": {"core": "0"},
    	 "fields": {"temp": 25.2},
    	 "time": 1657729093
    },
]
```

*measurement is required by InfluxDB and must be provided, it can be simply the name of the stock/option/whatever as needed*

Always ensure that the function is called with asyncio as such:
```py
import asyncio

async def main():
    data_container = DataContainer(name="example_bucket")

    # Add some example process to the pipeline
    def example_process(data):
        # Example processing logic
        return data

    data_container.add_process(example_process)

    # Example data source
    example_data = {"measurement": "test", "tags": {"tag1": "value1"}, "fields": {"field1": 1.0}}

    # Call load_source asynchronously
    await data_container.load_source(data_source=example_data)

# Run the async main function
asyncio.run(main())

```

This ensures that TraSy does not freeze when loading data.

## Using C Process
The process must be named func in your C code and must only have one function in the entire file.