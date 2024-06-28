package com.freakingrocky.trasy_controller.util;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;

@Component
public class ConfigLoader {

    private Properties properties;

    @PostConstruct
    public void init() {
        properties = new Properties();
        try (InputStream input = getClass().getClassLoader().getResourceAsStream("config.properties")) {
            if (input == null) {
                throw new IOException("Unable to find config.properties");
            }
            properties.load(input);
        } catch (IOException e) {
            e.printStackTrace();
            throw new RuntimeException("Failed to load properties file: config.properties", e);
        }
    }

    public String getProperty(String key) {
        return properties.getProperty(key);
    }
}
