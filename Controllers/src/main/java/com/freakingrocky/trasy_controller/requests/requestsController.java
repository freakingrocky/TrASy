package com.freakingrocky.trasy_controller.requests;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.freakingrocky.trasy_controller.requests.influxDB.InfluxLoader;
import com.freakingrocky.trasy_controller.requests.influxDB.InfluxWriter;

import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Flux;

@RestController
@Slf4j
@RequestMapping("/influx")
public class requestsController {

    @Autowired
    private InfluxLoader influxLoader;

    @Autowired
    private InfluxWriter influxWriter;

    @GetMapping("/exec_query")
    public Flux<String> getData(@RequestBody @Valid Map<String, Object> queryRequest) throws Exception {
        String query = (String) queryRequest.get("query");
        String bucket = (String) queryRequest.get("bucket");

        return influxLoader.queryData(query, bucket)
            .doOnNext(data -> log.info("Received data: {}", data))
            .doOnError(error -> log.error("Error occurred: {}", error.getMessage()))
            .doOnComplete(() -> log.info("Query completed"));
    }

    @PostMapping(value = "/write_data", consumes = MediaType.APPLICATION_JSON_VALUE)
    public String submitData(@RequestBody @Valid Map<String, Object> requestData) throws Exception {
        // TODO: Deserialize requestData to a DTO, and validate

        String measurement = (String) requestData.get("measurement");
        String fieldKey = (String) requestData.get("fieldKey");
        double fieldValue = (double) requestData.get("fieldValue");
        String tagKey = (String) requestData.get("tagKey");
        String tagValue = (String) requestData.get("tagValue");
        String bucket = (String) requestData.get("bucket");

        influxWriter.writeData(measurement, fieldKey, fieldValue, tagKey, tagValue, bucket);

        return "Received: " + requestData;
    }
}
