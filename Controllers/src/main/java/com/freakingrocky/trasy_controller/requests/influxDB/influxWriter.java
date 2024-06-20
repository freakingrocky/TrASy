package com.freakingrocky.trasy_controller.requests.influxDB;

public interface influxWriter {
    void writeData(String measurement, String fieldKey, double fieldValue, String tagKey, String tagValue) throws Exception;
    void setInfluxBucket(String bucket);
    void close();
}
