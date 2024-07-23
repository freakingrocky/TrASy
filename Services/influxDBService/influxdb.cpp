#include "influxdb.h"
#include <iostream>
#include <regex>
#include <chrono>
#include <ctime>
#include <iomanip>
#include <sstream>
#include <vector>
#include <thread>
#include <future>
#include <jsoncpp/json/json.h>
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/beast/version.hpp>
#include <boost/asio/connect.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <boost/asio/strand.hpp>

using namespace std;
namespace beast = boost::beast;
namespace http = beast::http;
namespace net = boost::asio;
using tcp = net::ip::tcp;

string csvToJson(const string& csv) {
    istringstream csvStream(csv);
    string line;
    vector<string> headers;
    Json::Value result(Json::arrayValue);

    // Parse the header line
    if (getline(csvStream, line)) {
        istringstream lineStream(line);
        string cell;
        while (getline(lineStream, cell, ',')) {
            if (cell.empty()) continue;
            headers.push_back(cell);
        }
    }

    // Parse the data lines
    while (getline(csvStream, line)) {
        istringstream lineStream(line);
        string cell;
        Json::Value jsonObject;
        for (size_t i = 0; i < headers.size(); ++i) {
            if (!getline(lineStream, cell, ',')) break;
            if (cell.empty()) continue;
            jsonObject[headers[i]] = cell;
        }
        result.append(jsonObject);
    }

    Json::StreamWriterBuilder writer;
    return Json::writeString(writer, result);
}

int getProcessorCount() {
    const int processor_count = std::thread::hardware_concurrency() * 2;  // assume every modern CPU can execute 2 threads simultaneously efficiently
    return processor_count ? processor_count : 4;  // Assume every modern CPU can execute 4 threads simultaneously efficiently
}

tm parseRelativeTime(const string& time_range) {
    int value = stoi(time_range.substr(1, time_range.size() - 2));
    char unit = time_range.back();

    auto now = chrono::system_clock::to_time_t(chrono::system_clock::now());
    tm time_info = *gmtime(&now);

    switch(unit) {
        case 'y':
            time_info.tm_year -= value;
            break;
        case 'm':
            time_info.tm_mon -= value;
            break;
        case 'w':
            time_info.tm_mday -= value * 7;
            break;
        case 'd':
            time_info.tm_mday -= value;
            break;
        case 'h':
            time_info.tm_hour -= value;
            break;
        case 's':
            time_info.tm_sec -= value;
            break;
        default:
            throw invalid_argument("Unsupported time unit");
    }
    mktime(&time_info);
    return time_info;
}

time_t tmToTimeT(tm time_info) {
    return timegm(&time_info);
}

tm timeTToTm(time_t time) {
    return *gmtime(&time);
}

vector<string> distributeQuery(const string& fluxQuery, int parts) {
    regex range_regex(R"(range\(start: (.+?)\))");
    smatch match;
    if (!regex_search(fluxQuery, match, range_regex)) {
        throw invalid_argument("No range found in query");
    }

    string time_range = match[1].str();
    time_t now = chrono::system_clock::to_time_t(chrono::system_clock::now());

    tm start_time_tm, end_time_tm;
    time_t start_time, end_time;

    if (time_range.front() == '-') {
        end_time = now;
        start_time_tm = parseRelativeTime(time_range);
        start_time = tmToTimeT(start_time_tm);
    } else {
        istringstream ss(time_range);
        ss >> get_time(&start_time_tm, "%Y-%m-%dT%H:%M:%SZ");
        start_time = tmToTimeT(start_time_tm);

        regex stop_regex(R"(stop: (.+?)\))");
        if (regex_search(fluxQuery, match, stop_regex)) {
            string stop_time_str = match[1].str();
            istringstream stop_ss(stop_time_str);
            stop_ss >> get_time(&end_time_tm, "%Y-%m-%dT%H:%M:%SZ");
            end_time = tmToTimeT(end_time_tm);
        } else {
            end_time = now;
            end_time_tm = timeTToTm(end_time);
        }
    }

    double total_duration = difftime(end_time, start_time);
    double sub_duration = total_duration / parts;

    vector<string> queries;
    for (int i = 0; i < parts; ++i) {
        time_t sub_start = start_time + sub_duration * i;
        time_t sub_end = sub_start + sub_duration;

        tm sub_start_tm = timeTToTm(sub_start);
        tm sub_end_tm = timeTToTm(sub_end);

        stringstream start_ss, end_ss;
        start_ss << put_time(&sub_start_tm, "%Y-%m-%dT%H:%M:%SZ");
        end_ss << put_time(&sub_end_tm, "%Y-%m-%dT%H:%M:%SZ");

        string new_query = regex_replace(fluxQuery, range_regex, "range(start: " + start_ss.str() + ", stop: " + end_ss.str() + ")");
        queries.push_back(new_query);
    }

    return queries;
}

string executeSingleFluxQuery(const string& fluxQuery) {
    try {
        net::io_context ioc;
        tcp::resolver resolver(ioc);
        beast::tcp_stream stream(ioc);
        auto const results = resolver.resolve(INFLUXDB_HOST, "8086");
        stream.connect(results);

        http::request<http::string_body> req{http::verb::post, "/api/v2/query?org=" + INFLUXDB_ORG, 11};
        req.set(http::field::host, INFLUXDB_HOST);
        req.set(http::field::authorization, "Token " + INFLUXDB_TOKEN);
        req.set(http::field::content_type, "application/json");

        Json::Value query;
        query["query"] = fluxQuery;
        query["type"] = "flux";
        query["org"] = INFLUXDB_ORG;

        Json::StreamWriterBuilder writer;
        string requestBody = Json::writeString(writer, query);

        req.body() = requestBody;
        req.prepare_payload();

        http::write(stream, req);

        beast::flat_buffer buffer;
        http::response<http::dynamic_body> res;
        http::read(stream, buffer, res);

        stream.socket().shutdown(tcp::socket::shutdown_both);

        string responseBody = beast::buffers_to_string(res.body().data());

        // Convert CSV to JSON
        string jsonResult = csvToJson(responseBody);
        return jsonResult;
    } catch (exception& e) {
        return string("Exception: ") + e.what();
    }
}

string executeFluxQuery(const string& body) {
    try {
        // Parse the incoming JSON body
        Json::Value root;
        Json::CharReaderBuilder reader;
        string errors;
        istringstream bodyStream(body);
        if (!Json::parseFromStream(reader, bodyStream, &root, &errors)) {
            return "Invalid JSON: " + errors;
        }

        string fluxQuery = root["fluxQuery"].asString();
        int processorCount = getProcessorCount();

        // Distribute the query
        vector<string> queries = distributeQuery(fluxQuery, processorCount);
        vector<future<string>> futures;

        for (int i = 0; i < processorCount; ++i) {
            futures.push_back(async(launch::async, [&queries, i]() {
                return executeSingleFluxQuery(queries[i]);
            }));
        }

        // Aggregate results
        Json::Value aggregatedResult(Json::arrayValue);
        for (auto& future : futures) {
            string result = future.get();
            Json::Value jsonResult;
            Json::CharReaderBuilder reader;
            string errors;
            istringstream resultStream(result);
            if (Json::parseFromStream(reader, resultStream, &jsonResult, &errors)) {
                for (const auto& entry : jsonResult) {
                    aggregatedResult.append(entry);
                }
            }
        }

        Json::StreamWriterBuilder writer;
        return Json::writeString(writer, aggregatedResult);
    } catch (exception& e) {
        return string("Exception: ") + e.what();
    }
}

