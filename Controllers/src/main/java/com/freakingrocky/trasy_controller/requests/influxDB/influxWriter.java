package com.freakingrocky.trasy_controller.requests.influxDB;

public interface InfluxWriter {
    void writeData(String measurement, String fieldKey, double fieldValue, String tagKey, String tagValue, String bucket) throws Exception;
    void close();
}
