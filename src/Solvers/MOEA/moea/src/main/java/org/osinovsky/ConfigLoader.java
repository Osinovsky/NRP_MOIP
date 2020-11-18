package org.osinovsky;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

public class ConfigLoader {
    // members
    Map<String, Object> config;

    // get the config
    public Map<String, Object> getConfig() {
        return this.config;
    }

    @SuppressWarnings("unchecked")
    public ConfigLoader(String fileName) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            this.config = mapper.readValue(new File(fileName),  HashMap.class);
        } catch (Exception e) {

        }
    }
}

