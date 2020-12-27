package org.osinovsky;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;

public class NRPProblemLoader {
    // members
    private List<List<Double>> objectives;
    private List<Map<Integer, Double>> inequations;

    public List<List<Double>> getObjectives() {
        return this.objectives;
    }

    public List<Map<Integer, Double>> getInequations() {
        return this.inequations;
    }

    @SuppressWarnings("unchecked")
    public NRPProblemLoader(String fileName) {
        ObjectMapper mapper = new ObjectMapper();
        HashMap<String, Object> value = new HashMap<String, Object>();
        try {
            value = mapper.readValue(new File(fileName),  HashMap.class);
        } catch (Exception e) {

        }
        this.objectives = (List<List<Double>>)value.get("objectives");
        this.inequations = new ArrayList<Map<Integer, Double>>();
        List<Map<String, Double>> tmp_csts = (List<Map<String, Double>>)value.get("inequations");
        for (Map<String, Double> tmp_cst : tmp_csts) {
            Map<Integer, Double> cst = new HashMap<Integer, Double>();
            for (Map.Entry<String, Double> entry : tmp_cst.entrySet()) {
                cst.put(Integer.parseInt(entry.getKey()), entry.getValue());
            }
            this.inequations.add(cst);
        }
    }
}
