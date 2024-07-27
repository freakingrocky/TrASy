# Script Structure
```
// Metadata
NAME: someIndicator
SYM: si
DESC: "This indicator calculates ..."
AUTHOR: "Your Name"
CONTEXT: 5
CONTEXT[INDICATORS]: o, h, c, l, tmp1
WICK: 1m

// Execute Automatically Condition
EVENT: 2m  // default: new_data

// Performance Stuff
PARALLEL_PROCESSING: true
GPU_ACCELERATION: true

// Cache Level
CACHE: enabled // RAM
CACHE_HW: enabled // L1, L2, L3 Cache

// Import Other Stuff
PLUGIN: custom_plugin

// Multi Asset Analysis
MULTI_ASSET: true
ASSETS: [AAPL, MSFT, GOOGL]

// Example: Calculate moving averages for multiple assets
VAR[ma_aapl]: MA(AAPL.c, 10)
VAR[ma_msft]: MA(MSFT.c, 10)
VAR[ma_googl]: MA(GOOGL.c, 10)

// Example: Cross-market condition
CON[cross_market]: ma_aapl > ma_msft && ma_msft > ma_googl

// Inheritance
TEMPLATE: moving_average

// Use Different functions from programming languages
LANG[python]: IMPORT_FUNC[someFunctionDefinedInPython]

// Parameter
PARAM[period]: 14

// Variable Declarations
VAR[tmp]: o[-2] + c[-2]

// Conditional Statements
CON[c1]: tmp > 4
CON[c2]: o[-1] < c
CON[c3]: h > l

// Functions for Common Operations
FUNC[ma]: MA(c, 10)
FUNC[max]: MAX(h, 5)
FUNC[customFunc]: CUSTOM_FUNC(o, c, h, l, v)
someFunctionDefinedInPython: PIPE(o, c, h, si[-2])

// Indicator Calculation
INDICATOR(c1): o[-2] * c + h[-1] + l[-1] ^ si[-2] + tmp - si[-3]
INDICATOR(c2): ma + max
INDICATOR(!c1 AND !c2): h + l - o

// Statistical Analysis
STAT[stddev]: STDDEV(c, 10)
STAT[corr]: CORREL(c, v, 20)

// Remove Outliers
REMOVE_OUTLIERS: true

// Error Handling
ERROR: "Invalid operation on data"
ERROR[STRATEGY]: extrapolate
```

# GAMEPLAN

## Project Overview
This project aims to develop a highly parallelized and GPU-accelerated system for calculating financial indicators using CUDA and C++. The system will handle large datasets, manage dependencies, and ensure efficient memory usage and error handling. The development environment is based on C++ in WSL2, running in a Docker container on Linux.

## Hardware and Software Requirements
- **Hardware**: Any x86 CPU, any GPU compatible with CUDA.
- **Software**:
  - **Programming Language**: C++
  - **CUDA Toolkit**: Version 12.2
  - **Development Environment**: WSL2, Docker
  - **Build System**: Makefile, Dockerfile

## Parallelization Strategy
- **CUDA Utilization**: Utilize CUDA for all calculations by default. Threads will be dynamically managed and created as needed.
- **Thread Management**: CPU threads will be created and deleted dynamically. Each thread will process data as soon as dependencies are met.
- **Memory Management**:
  - **GPU**: Use VRAM for required data, leverage GPU cache as available.
  - **CPU**: Use RAM and L1/L2/L3 cache based on availability.
- **Dynamic Threading**: Use CUDA streams for concurrency, manage dependencies using CUDA events.

## Data Handling and Management
- **Data Ingestion**: Data will be ingested from InfluxDB.
- **Data Storage**: Only the required data (as per CONTEXT[INDICATORS]) will be brought into VRAM.
- **Data Caching**: Implement data caching strategies (e.g., LRU) to efficiently manage memory usage.

## Dependency Management
- **Pre-Compiled Indicators**: Pre-compiled indicators can be accessed by the script.
- **Real-Time Processing**: If the currently compiled indicator is required by another calculation, threading will be done sequentially with multiple threads distributed across cores. If not, processing will be done randomly for maximum speed.

## Performance Metrics
- **Key Metric**: Time is the primary performance metric.

## Error Handling and Logging
- **Error Logging**: Errors will be logged in individual files under `./logs/SYM_DATETIME/threads/` and compiled into `./logs/SYM_DATETIME/errors.log`.
- **Error Recovery**: Retry 5 times then log it as an error. Based on the script's ERROR[STRATEGY], either extrapolate using time series forecasting or use the previous value up to 5 times or just alert the user.

## Extensibility and Maintenance
- **Modular Code Structure**: Ensure modularity and locality of function.
- **Future Extensions**: Design the system to allow easy integration of new indicators and functionalities.

## Scalability
- **Current Focus**: Single GPU setup.
- **Future Considerations**: Multi-GPU/node setup for future scalability.

## Implementation Details

### Development Environment
- **WSL2**: Use WSL2 to provide a Linux environment for development within Windows.
- **Docker**: Create a Docker container for a consistent development and production environment.
- **Makefile**: Use a Makefile to compile the C++ code.
- **Dockerfile**: Define a Dockerfile to set up the environment, install dependencies, and build the application.

### CUDA Specifics
- **Version**: Use CUDA version 12.2.
- **Libraries**: Utilize CUDA libraries such as cuBLAS, cuFFT, and Thrust for optimized performance.

### Parallelization Strategy
- **CUDA Streams**: Use CUDA streams to manage parallel execution and concurrency.
- **Dynamic Thread Management**: Implement dynamic thread management to create and manage threads based on data readiness and dependencies.

### Data Handling
- **InfluxDB**: Retrieve data from InfluxDB.
- **Caching Strategy**: Implement a caching strategy to keep frequently accessed data in RAM or GPU cache.

### Error Handling
- **Retry Mechanism**: Implement a retry mechanism that retries failed operations up to 5 times.
- **Logging**: Log errors in a detailed manner to enable debugging and issue resolution.

### Future Considerations
- **Multi-GPU Support**: Plan for adding support for multiple GPUs in the future.
- **Distributed Computing**: Consider distributed computing frameworks for scaling across multiple nodes.
