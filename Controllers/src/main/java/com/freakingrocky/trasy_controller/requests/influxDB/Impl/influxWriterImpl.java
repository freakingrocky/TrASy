package com.freakingrocky.trasy_controller.requests.influxDB.Impl;

import java.time.Instant;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.freakingrocky.trasy_controller.requests.influxDB.InfluxWriter;
import com.freakingrocky.trasy_controller.util.ConfigLoader;
import com.influxdb.client.InfluxDBClient;
import com.influxdb.client.InfluxDBClientFactory;
import com.influxdb.client.WriteApiBlocking;
import com.influxdb.client.domain.WritePrecision;
import com.influxdb.client.write.Point;

@Service
public class InfluxWriterImpl implements InfluxWriter {

    private final InfluxDBClient client;
    private final String org;
    private String bucket;

    @Autowired
    public InfluxWriterImpl(ConfigLoader configLoader) {
        String url = configLoader.getProperty("influxdb.url");
        String token = configLoader.getProperty("influxdb.token");
        this.org = configLoader.getProperty("influxdb.org");
        this.client = InfluxDBClientFactory.create(url, token.toCharArray());
    }



    public void setInfluxBucket(String bucket) {
        this.bucket = bucket;
    }

    @Override
    public void writeData(String measurement, String fieldKey, double fieldValue, String tagKey, String tagValue, String bucket) throws Exception {
        this.setInfluxBucket(bucket);
        WriteApiBlocking writeApi = client.getWriteApiBlocking();

        Point point = Point.measurement(measurement)
                           .addTag(tagKey, tagValue)
                           .addField(fieldKey, fieldValue)
                           .time(Instant.now(), WritePrecision.NS);

        try {
            writeApi.writePoint(this.bucket, this.org, point);
        } catch (Exception e) {
            throw new Exception("Failed to write data to InfluxDB", e);
        }
    }

    @Override
    public void writeData(Point point, String bucket) throws Exception {
        this.setInfluxBucket(bucket);

        WriteApiBlocking writeApi = client.getWriteApiBlocking();
        try {
            writeApi.writePoint(this.bucket, this.org, point);
        } catch (Exception e) {
            throw new Exception("Failed to write data to InfluxDB", e);
        }
    }

    @Override
    public void close() {
        if (client != null) {
            client.close();
        }
    }
}
