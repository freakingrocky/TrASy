package com.freakingrocky.trasy_controller.requests.influxDB.Impl;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;

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
    public Flux<String> queryData(String query) {
        QueryApi queryApi = client.getQueryApi();

        return Flux.create(sink -> {
            queryApi.query(query, (cancellable, record) -> {
                log.debug("Received record: {}", record);
                String value = String.valueOf(record.getValues());
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


    @Override
    public Flux<Map<String, Object>> queryCandleData(String query) {
        QueryApi queryApi = client.getQueryApi();

        return Flux.create(sink -> {
            queryApi.query(query, (cancellable, record) -> {
                log.debug("Received record: {}", record);

                Map<String, Object> resultMap = new HashMap<>();
                resultMap.put("time", record.getTime());
                resultMap.put("open", record.getValueByKey("Open"));
                resultMap.put("high", record.getValueByKey("High"));
                resultMap.put("low", record.getValueByKey("Low"));
                resultMap.put("close", record.getValueByKey("Close"));

                sink.next(resultMap);
            }, throwable -> {
                sink.error(throwable);
            }, sink::complete);
        });
    }

    @Override
    public Flux<Map<String, Object>> queryDataJSON(String query) {
        QueryApi queryApi = client.getQueryApi();

        return Flux.create(sink -> {
            queryApi.query(query, (cancellable, record) -> {
                log.debug("Received record: {}", record);

                Map<String, Object> resultMap = new HashMap<>();

                // Get all keys in the record dynamically
                Set<String> keys = record.getValues().keySet();
                for (String key : keys) {
                    resultMap.put(key, record.getValueByKey(key));
                }

                sink.next(resultMap);
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
