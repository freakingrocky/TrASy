#include <iostream>
#include <map>
#include <string>
#include <thread>
#include <boost/asio.hpp>
#include "sql.h"

using namespace std;
using boost::asio::ip::tcp;

struct Endpoint {
    string req_type;
    function<string(const string&)> handler;
};

map<string, Endpoint> endpoints;

void registerEndpoint(const string& name, const string& req_type, const function<string(const string&)>& handler) {
    endpoints[name] = {req_type, handler};
}

string handleRequest(const string& method, const string& endpoint, const string& body) {
    cout << "Handling request for endpoint: " << endpoint << " with method: " << method << endl;
    auto it = endpoints.find(endpoint);
    if (it != endpoints.end() && it->second.req_type == method) {
        return it->second.handler(body);
    }
    return "That endpoint either does not exist or is under development.";
}

void session(tcp::socket socket) {
    try {
        boost::asio::streambuf buffer;
        boost::asio::read_until(socket, buffer, "\r\n\r\n");
        istream request_stream(&buffer);
        string method;
        string uri;
        string version;
        request_stream >> method >> uri >> version;

        cout << "Method: " << method << endl;
        cout << "URI: " << uri << endl;

        // Skip the rest of the first line
        request_stream.ignore(numeric_limits<streamsize>::max(), '\n');

        // Read headers
        string header;
        size_t content_length = 0;
        while (getline(request_stream, header) && header != "\r") {
            cout << "Header: " << header << endl;
            if (header.find("Content-Length:") != string::npos) {
                content_length = stoi(header.substr(header.find(":") + 1));
            }
        }

        cout << "Content-Length: " << content_length << endl;

        // Read the JSON body
        string body;
        if (method == "POST" && content_length > 0) {
            // Read until the full content length is received
            while (buffer.size() < content_length) {
                boost::asio::read(socket, buffer, boost::asio::transfer_at_least(1));
            }

            body.resize(content_length);
            buffer.sgetn(&body[0], content_length);
            cout << "Body: " << body << endl;
        }

        string response;
        if (method == "POST") {
            string endpoint = uri.substr(1); // Remove leading '/'
            response = handleRequest(method, endpoint, body);
        } else if (method == "GET") {
            string endpoint = uri.substr(1); // Remove leading '/'
            response = handleRequest(method, endpoint, "");
        } else {
            response = "Method not allowed.";
        }

        // Add CORS headers (temporary)
        string http_response = "HTTP/1.1 200 OK\r\n"
                               "Access-Control-Allow-Origin: *\r\n"
                               "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
                               "Access-Control-Allow-Headers: Content-Type\r\n"
                               "Content-Length: " + to_string(response.length()) + "\r\n\r\n" + response;
        boost::asio::write(socket, boost::asio::buffer(http_response));
    } catch (exception& e) {
        cerr << "Exception: " << e.what() << "\n";
    }
}

int main() {
    registerEndpoint("sqlQuery", "POST", executeSQLQuery);

    try {
        boost::asio::io_service io_service;
        tcp::acceptor acceptor(io_service, tcp::endpoint(tcp::v4(), 1011));

        for (;;) {
            tcp::socket socket(io_service);
            acceptor.accept(socket);
            thread(session, move(socket)).detach();
        }
    } catch (exception& e) {
        cerr << "Exception: " << e.what() << "\n";
    }

    return 0;
}
