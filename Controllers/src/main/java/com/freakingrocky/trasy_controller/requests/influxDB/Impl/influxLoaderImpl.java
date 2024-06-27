package com.freakingrocky.trasy_controller.requests.influxDB.Impl;

import java.util.concurrent.Flow;
import java.util.concurrent.SubmissionPublisher;

import org.reactivestreams.Publisher;
import org.reactivestreams.Subscription;

import com.freakingrocky.trasy_controller.requests.influxDB.InfluxLoader;
import com.freakingrocky.trasy_controller.util.ConfigLoader;
import com.influxdb.client.InfluxDBClient;
import com.influxdb.client.InfluxDBClientFactory;
import com.influxdb.client.QueryApi;

public class InfluxLoaderImpl implements InfluxLoader {

    private String token;
    private String org;
    private String bucket;
    private InfluxDBClient client;

    public InfluxLoaderImpl() {
        // Load configuration
        ConfigLoader configLoader = new ConfigLoader("config.properties");
        String url = configLoader.getProperty("influxdb.url");
        this.token = configLoader.getProperty("influxdb.token");
        this.org = configLoader.getProperty("influxdb.org");
        this.client = InfluxDBClientFactory.create(url, token.toCharArray());
    }

    public void setInfluxBucket(String bucket) {
        this.bucket = bucket;
    }

    @Override
    public Publisher<String> queryData(String query, String bucket) {
        this.setInfluxBucket(bucket);
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
