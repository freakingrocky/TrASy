# TrASy - Trading Automation System
Trading Autiomation System for Retail Users, built with Python, InfluxDB, C++, Java

## Highlights
- TraSy uses Python for the end-user, resulting in a low barrier for entry into automating strategies
- TraSy is extensible using Python/C++/Java and can be connected to brokers such as Zerodha to automatically trade 
- TraSy uses influxdb for data processing, great for time series data *(unless you have 100,000$ a year for kdb+)*
- TraSy uses a mix of C++ and Java for forward testing and live trades, resulting in low processing latency
- TraSy uses Python for backtesting, resulting in an easy coding and prototyping experience
- TraSy features a react based front end for easy visualization and results

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
