#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_map>

// Function to trim whitespace from the start and end of a string
std::string trim(const std::string& str) {
    size_t first = str.find_first_not_of(" \t\n\r");
    size_t last = str.find_last_not_of(" \t\n\r");
    if (first == std::string::npos || last == std::string::npos) {
        return "";
    }
    return str.substr(first, last - first + 1);
}

// Function to read the .env file and return a map of key-value pairs
std::unordered_map<std::string, std::string> readEnvFile(const std::string& filename) {
    std::unordered_map<std::string, std::string> envMap;
    std::ifstream envFile(filename);

    if (!envFile) {
        std::cerr << "Could not open the file: " << filename << std::endl;
        return envMap;
    }

    std::string line;
    while (std::getline(envFile, line)) {
        std::istringstream iss(line);
        std::string key, value;

        if (std::getline(iss, key, '=') && std::getline(iss, value)) {
            key = trim(key);
            value = trim(value);
            envMap[key] = value;
        }
    }

    envFile.close();
    return envMap;
}

// Function to print the key-value pairs
void printEnvValues(const std::unordered_map<std::string, std::string>& envMap) {
    std::cout << envMap.at("INFLUXDB_ORG") << std::endl;
}

int main() {
    const std::string filename = ".env";
    std::unordered_map<std::string, std::string> envValues = readEnvFile(filename);

    std::cout << "Environment Variables:" << std::endl;
    printEnvValues(envValues);

    return 0;
}
