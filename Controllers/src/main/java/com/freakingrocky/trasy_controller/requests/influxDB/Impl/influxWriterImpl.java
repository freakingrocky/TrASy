package com.freakingrocky.trasy_controller.requests.influxDB.Impl;

import com.influxdb.client.InfluxDBClient;
import com.influxdb.client.InfluxDBClientFactory;
import com.influxdb.client.WriteApiBlocking;
import com.influxdb.client.domain.WritePrecision;
import com.influxdb.client.write.Point;
import com.freakingrocky.trasy_controller.util.ConfigLoader;

import com.freakingrocky.trasy_controller.requests.influxDB.influxWriter;

import java.time.Instant;

public class influxWriterImpl implements influxWriter {

    ConfigLoader configLoader = new ConfigLoader("config.properties");
    private InfluxDBClient client;
    private String url = configLoader.getProperty("influxdb.url");
    private String token = configLoader.getProperty("influxdb.token");
    private String org = configLoader.getProperty("influxdb.org");
    private String bucket;

    @Override
    public void setInfluxBucket(String bucket) {
        this.bucket = bucket;
    }

    public influxWriterImpl(String bucket) {
        this.client = InfluxDBClientFactory.create(this.url, this.token.toCharArray());
    }

    @Override
    public void writeData(String measurement, String fieldKey, double fieldValue, String tagKey, String tagValue) throws Exception {
        WriteApiBlocking writeApi = client.getWriteApiBlocking();

        Point point = Point.measurement(measurement)
                .addTag(tagKey, tagValue)
                .addField(fieldKey, fieldValue)
                .time(Instant.now(), WritePrecision.NS);

        try {
            writeApi.writePoint(bucket, org, point);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    public void close() {
        if (client != null) {
            client.close();
        }
    }

}
