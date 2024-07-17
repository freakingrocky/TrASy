package com.freakingrocky.trasy_controller.requests.sql;

import java.util.Map;

import reactor.core.publisher.Flux;

public interface sqlMethods {
    Flux<Map<String, Object>> getSymbols();
}
