#include <influxdb.hpp>
#include <iostream>

void write_to_influxdb(const std::string& measurement, const std::string& value) {
    influxdb_cpp::server_info si("127.0.0.1", 8086, "your_database");

    std::string resp;
    influxdb_cpp::builder()
        .meas(measurement)
        .field("value", value)
        .post_http(si, &resp);

    std::cout << "Response: " << resp << std::endl;
}

int main() {
    write_to_influxdb("test_measurement", "test_value");
    return 0;
}
