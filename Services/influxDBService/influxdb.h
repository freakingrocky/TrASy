#ifndef INFLUXDB_H
#define INFLUXDB_H

#include <string>
#include <vector>
#include <mutex>

std::string executeFluxQuery(const std::string& fluxQuery);

#endif // INFLUXDB_H
