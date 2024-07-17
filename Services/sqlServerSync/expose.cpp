#include <iostream>
#include <boost/asio.hpp>
#include <boost/beast.hpp>

namespace beast = boost::beast;         // from <boost/beast.hpp>
namespace http = beast::http;           // from <boost/beast/http.hpp>
namespace net = boost::asio;            // from <boost/asio.hpp>
using tcp = net::ip::tcp;               // from <boost/asio/ip/tcp.hpp>

void handle_symbols_request(http::request<http::string_body>& req, http::response<http::string_body>& res) {
    if (req.method() == http::verb::get && req.target() == "/get/symbols") {
        res.result(http::status::ok);
        res.body() = "Symbols data here"; // Replace with actual data
        res.prepare_payload();
    } else {
        res.result(http::status::bad_request);
        res.body() = "Unsupported HTTP method or target";
        res.prepare_payload();
    }
}

void do_session(tcp::socket socket) {
    try {
        beast::flat_buffer buffer;

        http::request<http::string_body> req;
        http::read(socket, buffer, req);

        http::response<http::string_body> res;
        handle_symbols_request(req, res);

        http::write(socket, res);
    }
    catch (std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

int main() {
    try {
        net::io_context ioc;

        tcp::acceptor acceptor{ioc, tcp::endpoint{tcp::v4(), 9111}};
        for (;;) {
            tcp::socket socket{ioc};
            acceptor.accept(socket);
            std::thread{std::bind(&do_session, std::move(socket))}.detach();
        }
    }
    catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
    }

    return 0;
}
