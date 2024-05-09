# Tracy
Trading System for Retail Users, built with Python, kdb+/polars, C++, Java

## Highlights
- Tracy uses Python for the end-user, resulting in a low barrier for entry into automating strategies
- Tracy is extensible using Python/C++/Java and can be connected to virtually broker
- Tracy uses influxdb for data processing, great for time series data *(unless you have 100,000$ a year for kdb+)*
- Tracy uses a mix of C++ and Java for forward testing and live trades, resulting in low processing latency
- Tracy uses Django and Python for backtesting, resulting in an easy coding and prototyping experience with nice visualizations

## Current Status

## Installation

## How to use
**Setting up InfluxDB**
1. Follow the steps listed here: https://docs.influxdata.com/influxdb/v2/install/?t=Windows
2. Follow the steps here and get the InfluxDB API Token and paste it into the SECRETS.py file: https://docs.influxdata.com/influxdb/v2/get-started/setup/

*If you follow these steps as listed, your first bucket is ready and the InfluxDB connection is ready.*

Now run the ``test_influxDB.py`` file to check if the connection is working as expected.

## Limitations

## Developing Guidelines