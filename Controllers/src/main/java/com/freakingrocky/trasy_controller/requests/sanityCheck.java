package com.freakingrocky.trasy_controller.requests;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/sanity")
public class sanityCheck {

    @GetMapping("/greet")
    public String greet() {
        return "It works!";
    }
}
