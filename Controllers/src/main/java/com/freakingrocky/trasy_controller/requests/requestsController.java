package com.freakingrocky.trasy_controller.requests;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class requestsController {

    // Example of a GET request
    @GetMapping("/data")
    public String getData() {
        // TODO: Implement the service call and return data
        return "Data fetched successfully";
    }

    // Example of a POST request, expecting a JSON payload
    @PostMapping("/submit")
    public String submitData(@RequestBody String requestData) {
        // TODO: Deserialize requestData to a DTO, validate, and process
        // For now, just echo back the requestData
        return "Received: " + requestData;
    }

    // Add more endpoints as required
}
