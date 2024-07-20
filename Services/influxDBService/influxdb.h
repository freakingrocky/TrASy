#ifndef INFLUXDB_H
#define INFLUXDB_H

#include <string>

std::string executeFluxQuery(const std::string& body);

#endif // INFLUXDB_H
