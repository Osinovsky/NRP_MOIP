package org.osinovsky;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.Arrays;

public class XuanProblemLoader {
    // members
    private Map<Integer, Integer> cost = new HashMap<>();
    private Map<Integer, Integer> profit = new HashMap<>();
    private Map<Integer, Integer> urgency = new HashMap<>();
    private Map<Integer, ArrayList<Integer>> requests = new HashMap<Integer, ArrayList<Integer>>();
    // reqDict map index to requirement id
    private Map<Integer, Integer> reqDict = new HashMap<>(); // index -> req id
    private Map<Integer, Integer> rvReqDict = new HashMap<>(); // req id -> index

    // get cost
    public Map<Integer, Integer> getCost() {
        return this.cost;
    }
    // get profit
    public Map<Integer, Integer> getProfit() {
        return this.profit;
    }
    // get urgency
    public Map<Integer, Integer> getUrgency() {
        return this.urgency;
    }
    // get requests
    public Map<Integer, ArrayList<Integer>> getRequests() {
        return this.requests;
    }
    // get reqDict
    public Map<Integer, Integer> getReqDict() {
        return this.reqDict;
    }
    // get reversed reqDict
    public Map<Integer, Integer> getRvReqDict() {
        return this.rvReqDict;
    }

    // evaluate
    public int evaluate(ArrayList<Boolean> variables) {
        int sumProfit = 0;
        for (int cust : this.requests.keySet()) {
            int counter = 0;
            for (int i = 0; i < variables.size(); ++ i) {
                if (variables.get(i)) {
                    if (this.requests.get(cust).contains(this.reqDict.get(i))) {
                        counter ++;
                    }
                }
            }
            if (this.requests.get(cust).size() == counter){
                sumProfit += this.profit.get(cust);
            }
        }
        return sumProfit;
    }
 

    // load from problem file
    @SuppressWarnings("unchecked")
    public XuanProblemLoader(String fileName){
        ObjectMapper mapper = new ObjectMapper();
        HashMap<String, Object> value = new HashMap<String, Object>();
        try {
            value = mapper.readValue(new File(fileName),  HashMap.class);
        } catch (Exception e) {

        }
        // cost
        Map<String, Integer> costMap = (Map<String, Integer>)value.get("cost");
        for (String keyStr : costMap.keySet()) {
            int key = Integer.parseInt(keyStr);
            this.cost.put(key, costMap.get(keyStr));
        }
        // construct reqDict from cost
        ArrayList<Integer> reqList = new ArrayList<Integer>();
        for (String keyStr : costMap.keySet()) {
            reqList.add(Integer.parseInt(keyStr));
        }
        Integer[] reqArray = new Integer[reqList.size()];
        for (int i = 0; i < reqArray.length; ++ i){
            reqArray[i] = reqList.get(i);
        }
        Arrays.sort(reqArray);
        int counter = 0;
        for (int key : reqArray) {
            reqDict.put(counter, key);
            rvReqDict.put(key, counter);
            counter += 1;
        }

        // profit
        Map<String, Integer> profitMap = (Map<String, Integer>)value.get("profit");
        for (String keyStr : profitMap.keySet()) {
            int key = Integer.parseInt(keyStr);
            this.profit.put(key, profitMap.get(keyStr));
        }

        // requests
        Map<String, ArrayList<Integer>> requestMap = (Map<String, ArrayList<Integer>>)value.get("request");
        for (String keyStr : requestMap.keySet()) {
            int key = Integer.parseInt(keyStr);
            ArrayList<Integer> requestList  = requestMap.get(keyStr);
            ArrayList<Integer> yaRequestList = new ArrayList<>();
            for (int req : requestList) {
                yaRequestList.add(req);
            }
            this.requests.put(key, yaRequestList);
        }

        // urgency
        Map<String, Integer> urgencyMap = (Map<String, Integer>)value.get("urgency");
        for (String keyStr : urgencyMap.keySet()) {
            int key = Integer.parseInt(keyStr);
            this.urgency.put(key, urgencyMap.get(keyStr));
        }
    }
}
