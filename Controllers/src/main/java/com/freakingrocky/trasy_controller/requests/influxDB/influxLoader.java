package com.freakingrocky.trasy_controller.requests.influxDB;

import java.util.Map;

import reactor.core.publisher.Flux;

public interface InfluxLoader {
    Flux<String> queryData(String query);
    Flux<Map<String, Object>> queryCandleData(String query);
    Flux<Map<String, Object>> queryDataJSON(String query);
}
