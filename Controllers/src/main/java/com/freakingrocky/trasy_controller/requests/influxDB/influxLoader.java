package com.freakingrocky.trasy_controller.requests.influxDB;

import org.reactivestreams.Publisher;

public interface influxLoader {
    Publisher<String> queryData(String query);
    void setInfluxBucket(String bucket);
}
