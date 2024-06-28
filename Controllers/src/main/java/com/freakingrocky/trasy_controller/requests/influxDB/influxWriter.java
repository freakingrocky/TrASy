package com.freakingrocky.trasy_controller.requests.influxDB;

import com.influxdb.client.write.Point;

public interface InfluxWriter {
    void writeData(String measurement, String fieldKey, double fieldValue, String tagKey, String tagValue, String bucket) throws Exception;
    void writeData(Point point, String bucket) throws Exception;
    void close();
}
