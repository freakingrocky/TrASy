package com.freakingrocky.trasy_controller.requests.influxDB.Impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.freakingrocky.trasy_controller.requests.influxDB.InfluxLoader;
import com.freakingrocky.trasy_controller.util.ConfigLoader;
import com.influxdb.client.InfluxDBClient;
import com.influxdb.client.InfluxDBClientFactory;
import com.influxdb.client.QueryApi;

import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Flux;

@Slf4j
@Service
public class InfluxLoaderImpl implements InfluxLoader {

    private final InfluxDBClient client;

    @Autowired
    public InfluxLoaderImpl(ConfigLoader configLoader) {
        String url = configLoader.getProperty("influxdb.url");
        String token = configLoader.getProperty("influxdb.token");
        String org = configLoader.getProperty("influxdb.org");
        this.client = InfluxDBClientFactory.create(url, token.toCharArray(), org);
    }

    @Override
    public Flux<String> queryData(String query, String bucket) {
        QueryApi queryApi = client.getQueryApi();

        return Flux.create(sink -> {
            queryApi.query(query, (cancellable, record) -> {
                log.debug("Received record: {}", record);
                String value = String.valueOf(record.getValue());
                String time = String.valueOf(record.getTime());

                if (value != null) {
                    String result = time + ": " + value;
                    sink.next(result);
                }
            }, throwable -> {
                sink.error(throwable);
            }, sink::complete);
        });
    }

    public void close() {
        if (client != null) {
            client.close();
        }
    }
}
