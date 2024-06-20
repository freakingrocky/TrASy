package com.freakingrocky.trasy_controller.requests.influxDB.Impl;

import com.freakingrocky.trasy_controller.requests.influxDB.influxLoader;
import com.freakingrocky.trasy_controller.util.ConfigLoader;
import com.influxdb.client.InfluxDBClient;
import com.influxdb.client.InfluxDBClientFactory;
import com.influxdb.client.QueryApi;
import com.influxdb.query.FluxTable;
import com.influxdb.query.FluxRecord;
import org.reactivestreams.Publisher;
import org.reactivestreams.Subscriber;
import org.reactivestreams.Subscription;

import java.util.List;
import java.util.concurrent.Flow;
import java.util.concurrent.SubmissionPublisher;

public class influxLoaderImpl implements influxLoader {

    private String token;
    private String org;
    private String bucket;
    private InfluxDBClient client;

    public influxLoaderImpl() {
        // Load configuration
        ConfigLoader configLoader = new ConfigLoader("config.properties");
        String url = configLoader.getProperty("influxdb.url");
        this.token = configLoader.getProperty("influxdb.token");
        this.org = configLoader.getProperty("influxdb.org");
        this.client = InfluxDBClientFactory.create(url, token.toCharArray());
    }

    @Override
    public void setInfluxBucket(String bucket) {
        this.bucket = bucket;
    }

    @Override
    public Publisher<String> queryData(String query) {
        SubmissionPublisher<String> publisher = new SubmissionPublisher<>();
        QueryApi queryApi = client.getQueryApi();

        queryApi.query(query, org,
            (cancellable, record) -> {
                String recordData = record.getTime() + ": " + record.getValueByKey("_value");
                publisher.submit(recordData);
            },
            throwable -> {
                publisher.closeExceptionally(throwable);
            },
            () -> {
                publisher.close();
            }
        );

        return subscriber -> publisher.subscribe(new Flow.Subscriber<>() {
            @Override
            public void onSubscribe(Flow.Subscription subscription) {
                subscriber.onSubscribe(new Subscription() {
                    @Override
                    public void request(long n) {
                        subscription.request(n);
                    }

                    @Override
                    public void cancel() {
                        subscription.cancel();
                    }
                });
            }

            @Override
            public void onNext(String item) {
                subscriber.onNext(item);
            }

            @Override
            public void onError(Throwable throwable) {
                subscriber.onError(throwable);
            }

            @Override
            public void onComplete() {
                subscriber.onComplete();
            }
        });
    }

    public void close() {
        if (client != null) {
            client.close();
        }
    }
}
