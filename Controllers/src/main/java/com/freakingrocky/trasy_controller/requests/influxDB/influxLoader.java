package com.freakingrocky.trasy_controller.requests.influxDB;

import org.reactivestreams.Publisher;

public interface InfluxLoader {
    Publisher<String> queryData(String query, String bucket);
}
