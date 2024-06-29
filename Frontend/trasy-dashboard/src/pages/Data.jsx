import axios from "axios";
import { createChart } from "lightweight-charts";
import React, { useEffect, useRef, useState } from "react";
import "./Data.scss"; // Assuming you will create this CSS file for styling

const Data = () => {
  const [data, setData] = useState([]);
  const [symbols, setSymbols] = useState([]);
  const [filteredSymbols, setFilteredSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);
  const chartContainerRef = useRef(null);
  const chart = useRef(null);
  const candlestickSeries = useRef(null);
  const volumeSeries = useRef(null);
  const upperBandSeries = useRef(null);
  const lowerBandSeries = useRef(null);

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

  useEffect(() => {
    if (
      chart.current &&
      candlestickSeries.current &&
      volumeSeries.current &&
      upperBandSeries.current &&
      lowerBandSeries.current
    ) {
      const chartData = processChartData(data);
      candlestickSeries.current.setData(chartData.candlesticks);
      volumeSeries.current.setData(chartData.volume);
      upperBandSeries.current.setData(chartData.upperBand);
      lowerBandSeries.current.setData(chartData.lowerBand);
    }
  }, [data]);

  const fetchSymbols = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8080/influx/query/symbols`
      );
      const fetchedSymbols = response.data.map((item) => item.FileSymbol);
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
        time: new Date(item._time).getTime() / 1000,
        open: item.Open,
        high: item.High,
        low: item.Low,
        close: item.Close,
        volume: item.Volume,
      }))
      .sort((a, b) => a.time - b.time); // Sort by time in ascending order

    const candlesticks = processedData.map((item) => ({
      time: item.time,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    }));

    const volume = processedData.map((item) => ({
      time: item.time,
      value: item.volume,
    }));

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
    const movingAverage = (values) =>
      values.reduce((sum, value) => sum + value, 0) / values.length;
    const standardDeviation = (values, mean) =>
      Math.sqrt(
        values.reduce((sum, value) => sum + (value - mean) ** 2, 0) /
          values.length
      );

    const upperBand = [];
    const lowerBand = [];

    for (let i = 0; i < data.length; i++) {
      if (i >= period - 1) {
        const slice = data.slice(i - period + 1, i + 1);
        const closes = slice.map((item) => item.close);
        const mean = movingAverage(closes);
        const sd = standardDeviation(closes, mean);

        upperBand.push({ time: data[i].time, value: mean + multiplier * sd });
        lowerBand.push({ time: data[i].time, value: mean - multiplier * sd });
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
    if (chart.current) {
      chart.current.remove();
      chart.current = null;
    }
    createChartInstance();
  };

  const createChartInstance = () => {
    if (chartContainerRef.current) {
      chart.current = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height: 500,
      });
      candlestickSeries.current = chart.current.addCandlestickSeries();
      volumeSeries.current = chart.current.addHistogramSeries({
        priceFormat: { type: "volume" },
        priceLineVisible: false,
        color: "#26a69a",
      });
      upperBandSeries.current = chart.current.addLineSeries({
        color: "rgba(255, 99, 132, 0.5)",
        lineWidth: 1,
      });
      lowerBandSeries.current = chart.current.addLineSeries({
        color: "rgba(255, 99, 132, 0.5)",
        lineWidth: 1,
      });
      chart.current.resize(window.innerWidth * 0.9, 500);
      const chartData = processChartData(data);
      candlestickSeries.current.setData(chartData.candlesticks);
      volumeSeries.current.setData(chartData.volume);
      upperBandSeries.current.setData(chartData.upperBand);
      lowerBandSeries.current.setData(chartData.lowerBand);

      // Add drawing tools
      const tool = chart.current.addLineSeries({
        color: "#ff0000",
        lineWidth: 2,
      });

      chart.current.subscribeClick((param) => {
        if (param.point) {
          tool.update({
            time: param.time,
            value: param.point.price,
          });
        }
      });
    }
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
        <div ref={chartContainerRef} className="chart-container" />
      )}
    </div>
  );
};

export default Data;
