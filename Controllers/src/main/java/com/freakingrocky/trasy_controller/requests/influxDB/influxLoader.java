package com.freakingrocky.trasy_controller.requests.influxDB;

import reactor.core.publisher.Flux;

public interface InfluxLoader {
    Flux<String> queryData(String query, String bucket);
}
