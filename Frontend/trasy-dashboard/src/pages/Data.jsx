import axios from "axios";
import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts/highstock";
import boost from "highcharts/modules/boost";
import React, { useEffect, useMemo, useState } from "react";
import "./Data.scss"; // Assuming you will create this CSS file for styling

// Initialize the boost module
boost(Highcharts);

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
      const response = await axios.post(`http://localhost:1011/sqlQuery`, {
        query: "SELECT SYMBOL FROM HistoricalData",
      });
      const fetchedSymbols = response.data.map((item) => item.SYMBOL);
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
        |> range(start: -3y)
        |> filter(fn: (r) => r["_measurement"] == "futures_data")
        |> filter(fn: (r) => r["FileSymbol"] == "${symbol}")
        |> filter(fn: (r) => r["_field"] == "Open" or r["_field"] == "High" or r["_field"] == "Low" or r["_field"] == "Close" or r["_field"] == "Volume")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> sort(columns: ["_time"], desc: true)`;

      const response = await axios.post("http://localhost:1010/fluxQuery", {
        fluxQuery: query,
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
        open: parseFloat(item.Open),
        high: parseFloat(item.High),
        low: parseFloat(item.Low),
        close: parseFloat(item.Close),
        volume: parseFloat(item.Volume),
      }))
      .sort((a, b) => a.time - b.time); // Sort by time in ascending order

    const candlesticks = processedData.map((item) => [
      item.time,
      item.open,
      item.high,
      item.low,
      item.close,
    ]);

    console.log("Processed chart data:", processedData);

    const volume = processedData.map((item) => [item.time, item.volume]);

    return { candlesticks, volume };
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

  const chartOptions = useMemo(
    () => ({
      boost: {
        useGPUTranslations: true,
        seriesThreshold: 1, // Boost if more than one series
      },
      title: {
        text: `Stock Price for ${selectedSymbol}`,
      },
      rangeSelector: {
        selected: 1,
      },
      yAxis: [
        {
          labels: {
            align: "right",
            x: -3,
          },
          title: {
            text: "Price",
          },
          height: "60%",
          lineWidth: 2,
          resize: {
            enabled: true,
          },
        },
        {
          labels: {
            align: "right",
            x: -3,
          },
          title: {
            text: "Volume",
          },
          top: "80%",
          height: "20%",
          offset: 0,
          lineWidth: 2,
        },
      ],
      tooltip: {
        split: true,
      },
      series: [
        {
          type: "candlestick",
          name: selectedSymbol,
          data: processChartData(data).candlesticks,
        },
        {
          type: "column",
          name: "Volume",
          data: processChartData(data).volume,
          yAxis: 1,
        },
      ],
    }),
    [data, selectedSymbol]
  );

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
