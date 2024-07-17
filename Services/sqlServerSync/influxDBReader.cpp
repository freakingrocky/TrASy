#include <influxdb.hpp>
#include <thread>
#include <vector>
#include <iostream>
#include <chrono>
#include <ctime>
#include "json.hpp"  // Include the nlohmann/json library

using json = nlohmann::json;

// Function to convert time_t to ISO 8601 format
std::string to_iso_8601(std::time_t time) {
    std::tm tm = *std::gmtime(&time);
    char buffer[30];
    std::strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &tm);
    return std::string(buffer);
}

// Function to execute a Flux query
std::vector<std::string> execute_flux_query(const std::string& query) {
    influxdb_cpp::server_info si("127.0.0.1", 8086, "your_database");
    std::string resp;

    influxdb_cpp::query(resp, query, si);

    // Process response and return data
    std::vector<std::string> result; // Process `resp` into result
    return result;
}

// Function to find the first and last date from InfluxDB
std::pair<std::string, std::string> find_first_and_last_date() {
    influxdb_cpp::server_info si("127.0.0.1", 8086, "your_database");
    std::string first_date_query = "from(bucket: \"your_bucket\") |> range(start: 0) |> first()";
    std::string last_date_query = "from(bucket: \"your_bucket\") |> range(start: 0) |> last()";
    std::string first_resp, last_resp;

    influxdb_cpp::query(first_resp, first_date_query, si);
    influxdb_cpp::query(last_resp, last_date_query, si);

    // Parse JSON responses
    json first_json = json::parse(first_resp);
    json last_json = json::parse(last_resp);

    // Extract the actual dates
    std::string first_date = first_json["results"][0]["series"][0]["values"][0][0].get<std::string>();
    std::string last_date = last_json["results"][0]["series"][0]["values"][0][0].get<std::string>();

    return {first_date, last_date};
}

// Function to parallelize Flux queries based on the number of cores
void parallel_flux_queries(const std::string& base_query, int num_cores) {
    auto [start_time, end_time] = find_first_and_last_date();

    // Convert start_time and end_time to time_t
    std::tm tm_start{}, tm_end{};
    std::istringstream ss_start(start_time), ss_end(end_time);
    ss_start >> std::get_time(&tm_start, "%Y-%m-%dT%H:%M:%SZ");
    ss_end >> std::get_time(&tm_end, "%Y-%m-%dT%H:%M:%SZ");

    std::time_t start = std::mktime(&tm_start);
    std::time_t end = std::mktime(&tm_end);
    std::time_t interval = (end - start) / num_cores;

    std::vector<std::thread> threads;
    std::vector<std::vector<std::string>> results(num_cores);

    for (int i = 0; i < num_cores; ++i) {
        std::time_t range_start = start + i * interval;
        std::time_t range_end = (i == num_cores - 1) ? end : range_start + interval;

        std::string query = base_query + " |> range(start: " + to_iso_8601(range_start) + ", stop: " + to_iso_8601(range_end) + ")";

        threads.emplace_back([&, i, query]() {
            try {
                results[i] = execute_flux_query(query);
            } catch (const std::exception& e) {
                std::cerr << "Error in thread " << i << ": " << e.what() << std::endl;
            }
        });
    }

    for (auto& t : threads) {
        t.join();
    }

    // Combine results
    std::vector<std::string> combined_results;
    for (const auto& res : results) {
        combined_results.insert(combined_results.end(), res.begin(), res.end());
    }

    // Return combined results
    for (const auto& entry : combined_results) {
        std::cout << entry << std::endl;
    }
}

int main() {
    try {
        int num_cores = std::thread::hardware_concurrency();
        parallel_flux_queries("from(bucket: \"your_bucket\")", num_cores);
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
    }

    return 0;
}
