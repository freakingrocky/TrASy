package com.freakingrocky.trasy_controller.requests;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.AutoConfigureOrder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import jakarta.validation.Valid;

import org.reactivestreams.Publisher;

import com.freakingrocky.trasy_controller.requests.influxDB.InfluxLoader;

@RestController
@RequestMapping("/influx")
public class requestsController {

    @Autowired
    InfluxLoader influxLoader;

    @GetMapping("/exec_query")
    public Publisher<String> getData(@RequestBody @Valid Map<?, ?> queryRequest) throws Exception {
        // TODO: Deserialize queryRequest to a DTO, validate, and process
        
        String query = (String) queryRequest.get("query");
        String bucket = (String) queryRequest.get("bucket");

        return influxLoader.queryData(query, bucket);
    }

    // Example of a POST request, expecting a JSON payload
    @PostMapping("/write_data")
    public String submitData(@RequestBody String requestData) {
        // TODO: Deserialize requestData to a DTO, validate, and process
        // For now, just echo back the requestData
        return "Received: " + requestData;
    }

    // Add more endpoints as required
}
