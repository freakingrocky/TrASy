#include "influxdb.h"
#include <iostream>
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/beast/version.hpp>
#include <boost/asio/connect.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <boost/asio/strand.hpp>
#include <jsoncpp/json/json.h>

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
        query["org"] = INFLUXDB_ORG; // Include the organization name

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