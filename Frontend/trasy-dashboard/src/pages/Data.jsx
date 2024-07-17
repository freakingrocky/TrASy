import axios from "axios";
import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts/highstock";
import React, { useEffect, useState } from "react";
import "./Data.scss"; // Assuming you will create this CSS file for styling

// TODO: Fix the Symbols Loading System (too slow and inefficient)
// TODO: Use a reactive query for JAVA fetching
const Data = () => {
  const [data, setData] = useState([]);
  const [symbols, setSymbols] = useState([]);
  const [filteredSymbols, setFilteredSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);

  useEffect(() => {
    fetchSymbols();
  }, []);

  useEffect(() => {
    if (selectedSymbol) {
      setData([]);
      setPage(0);
      setHasMore(true);
      fetchData(0, selectedSymbol);
    }
  }, [selectedSymbol]);

  useEffect(() => {
    if (page > 0 && selectedSymbol) {
      fetchData(page, selectedSymbol);
    }
  }, [page, selectedSymbol]);

  const fetchSymbols = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8080/sql/symbols`
      );
      const fetchedSymbols = response.data.map((item) => item.symbol);
      setSymbols(fetchedSymbols);
      setFilteredSymbols(fetchedSymbols);
      console.log("Fetched symbols:", fetchedSymbols);
    } catch (error) {
      console.error("Error fetching symbols:", error);
    }
  };

  const fetchData = async (page, symbol) => {
    try {
      const query = `from(bucket: "Historical Data")
        |> range(start: -2y)
        |> filter(fn: (r) => r["_measurement"] == "futures_data")
        |> filter(fn: (r) => r["FileSymbol"] == "${symbol}")
        |> filter(fn: (r) => r["_field"] == "Open" or r["_field"] == "High" or r["_field"] == "Low" or r["_field"] == "Close" or r["_field"] == "Volume")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> sort(columns: ["_time"], desc: true)`;

      const response = await axios.post("http://localhost:8080/influx/query", {
        query: query,
        timeout: 60000, // Set timeout to 60 seconds
      });

      const result = response.data;
      console.log("Fetched data:", result); // Log fetched data

      if (result.length < 365) {
        setHasMore(false);
      }
      setData((prevData) => [...prevData, ...result]); // Append new data
    } catch (error) {
      console.error("Error fetching data:", error);
      setHasMore(false);
    }
  };

  const processChartData = (data) => {
    const processedData = data
      .map((item) => ({
        time: new Date(item._time).getTime(),
        open: item.Open,
        high: item.High,
        low: item.Low,
        close: item.Close,
        volume: item.Volume,
      }))
      .sort((a, b) => a.time - b.time); // Sort by time in ascending order

    const candlesticks = processedData.map((item) => [
      item.time,
      item.open,
      item.high,
      item.low,
      item.close,
    ]);

    const volume = processedData.map((item) => [item.time, item.volume]);

    const { upperBand, lowerBand } = calculateBollingerBands(processedData);

    console.log("Processed chart data:", {
      candlesticks,
      volume,
      upperBand,
      lowerBand,
    });

    return { candlesticks, volume, upperBand, lowerBand };
  };

  const calculateBollingerBands = (data) => {
    const period = 20;
    const multiplier = 2;
    const movingAverage = (values) => values.reduce((sum, value) => sum + value, 0) / values.length;
    const standardDeviation = (values, mean) => Math.sqrt(values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / values.length);

    const upperBand = [];
    const lowerBand = [];

    for (let i = 0; i < data.length; i++) {
      if (i >= period - 1) {
        const slice = data.slice(i - period + 1, i + 1);
        const closes = slice.map((item) => item.close);
        const mean = movingAverage(closes);
        const sd = standardDeviation(closes, mean);

        upperBand.push([data[i].time, mean + multiplier * sd]);
        lowerBand.push([data[i].time, mean - multiplier * sd]);
      }
    }

    return { upperBand, lowerBand };
  };

  const handleSearch = (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    if (term.length >= 3) {
      const filtered = symbols.filter((symbol) =>
        symbol.includes(term.toUpperCase())
      );
      setFilteredSymbols(filtered);
    } else {
      setFilteredSymbols(symbols);
    }
  };

  const handleSelectSymbol = (symbol) => {
    setSelectedSymbol(symbol);
  };

  const chartOptions = {
    title: {
      text: `Stock Price for ${selectedSymbol}`,
    },
    rangeSelector: {
      selected: 1,
    },
    yAxis: [
      {
        labels: {
          align: 'right',
          x: -3,
        },
        title: {
          text: 'Price',
        },
        height: '60%',
        lineWidth: 2,
        resize: {
          enabled: true,
        },
      },
      {
        labels: {
          align: 'right',
          x: -3,
        },
        title: {
          text: 'Volume',
        },
        top: '80%',
        height: '20%',
        offset: 0,
        lineWidth: 2,
      },
    ],
    tooltip: {
      split: true,
    },
    series: [
      {
        type: 'candlestick',
        name: selectedSymbol,
        data: processChartData(data).candlesticks,
      },
      {
        type: 'column',
        name: 'Volume',
        data: processChartData(data).volume,
        yAxis: 1,
      },
      {
        type: 'line',
        name: 'Upper Bollinger Band',
        data: processChartData(data).upperBand,
        color: 'rgba(255, 99, 132, 0.5)',
        lineWidth: 1,
        tooltip: {
          valueDecimals: 2,
        },
      },
      {
        type: 'line',
        name: 'Lower Bollinger Band',
        data: processChartData(data).lowerBand,
        color: 'rgba(255, 99, 132, 0.5)',
        lineWidth: 1,
        tooltip: {
          valueDecimals: 2,
        },
      },
    ],
  };

  return (
    <div className="container">
      <input
        type="text"
        placeholder="Search symbols"
        value={searchTerm}
        onChange={handleSearch}
        className="search-bar"
      />
      <ul className="symbol-list">
        {filteredSymbols.map((symbol) => (
          <li key={symbol} onClick={() => handleSelectSymbol(symbol)}>
            {symbol}
          </li>
        ))}
      </ul>
      {selectedSymbol && (
        <div className="chart-container">
          <HighchartsReact
            highcharts={Highcharts}
            constructorType={"stockChart"}
            options={chartOptions}
            containerProps={{ style: { height: "80vh" } }}
          />
        </div>
      )}
    </div>
  );
};

export default Data;
