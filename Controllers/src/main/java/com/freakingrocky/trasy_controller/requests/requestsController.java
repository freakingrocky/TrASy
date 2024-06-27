package com.freakingrocky.trasy_controller.requests;

import java.util.Map;

import org.reactivestreams.Publisher;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.MediaType;

import com.freakingrocky.trasy_controller.requests.influxDB.InfluxLoader;
import com.freakingrocky.trasy_controller.requests.influxDB.InfluxWriter;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/influx")
public class requestsController {

    @Autowired
    InfluxLoader influxLoader;

    @Autowired
    InfluxWriter influxWriter;

    @GetMapping("/exec_query")
    public Publisher<String> getData(@RequestBody @Valid Map<?, ?> queryRequest) throws Exception {
        // TODO: Deserialize queryRequest to a DTO, and validate
        
        String query = (String) queryRequest.get("query");
        String bucket = (String) queryRequest.get("bucket");

        return influxLoader.queryData(query, bucket);
    }

    // Example of a POST request, expecting a JSON payload
    @PostMapping(name="/write_data", consumes = MediaType.APPLICATION_JSON_VALUE)
    public String submitData(@RequestBody @Valid Map<?, ?> requestData) throws Exception {
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

    // Add more endpoints as required
}
