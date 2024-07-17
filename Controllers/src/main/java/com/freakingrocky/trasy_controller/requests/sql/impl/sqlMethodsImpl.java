package com.freakingrocky.trasy_controller.requests.sql.impl;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.HashMap;
import java.util.Map;

import org.springframework.stereotype.Service;

import com.freakingrocky.trasy_controller.requests.sql.sqlMethods;

import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Flux;

@Slf4j
@Service
public class sqlMethodsImpl implements sqlMethods {

    @Override
    public Flux<Map<String, Object>> getSymbols() {
        return Flux.create(sink -> {
            String url = "jdbc:jtds:sqlserver://FREAKINGROCKY/SQLEXPRESS;databaseName=INFLUX_HISTORICAL_SYMBOLS;useNTLMv2=true;domain=freakingrocky";

            try (Connection conn = DriverManager.getConnection(url);
                 Statement stmt = conn.createStatement();
                 ResultSet rs = stmt.executeQuery("SELECT SYMBOL FROM HistoricalData")) {

                while (rs.next()) {
                    Map<String, Object> symbolMap = new HashMap<>();
                    symbolMap.put("symbol", rs.getString("SYMBOL"));
                    sink.next(symbolMap);
                }
                sink.complete();

            } catch (Exception e) {
                log.error("Error fetching symbols", e);
                sink.error(e);
            }
        });
    }
}
