package org.osinovsky;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class XuanProblemLoader {
    // members
    private Map<Integer, Integer> cost = new HashMap<>();
    private Map<Integer, Integer> profit = new HashMap<>();
    private Map<Integer, Integer> urgency = new HashMap<>();
    private Map<Integer, ArrayList<Integer>> requests = new HashMap<Integer, ArrayList<Integer>>();

    private List<Integer> rcost = new ArrayList<>();
    private List<Integer> rprofit = new ArrayList<>();
    private List<Integer> rurgency = new ArrayList<>();
    private List<List<Integer>> rrequests = new ArrayList<List<Integer>>();


    // get cost
    public List<Integer> getCost() {
        return this.rcost;
    }
    // get profit
    public List<Integer> getProfit() {
        return this.rprofit;
    }
    // get urgency
    public List<Integer> getUrgency() {
        return this.rurgency;
    }
    // get requests
    public List<List<Integer>> getRequests() {
        return this.rrequests;
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
        Map<Integer, Integer> reqRename = new HashMap<Integer, Integer>();
        Map<Integer, Integer> reqRenameRev = new HashMap<Integer, Integer>();
        int counter = 0;
        for (Map.Entry<Integer, Integer> entry : this.cost.entrySet()) {
            this.rcost.add(entry.getValue());
            reqRename.put(entry.getKey(), counter);
            reqRenameRev.put(counter, entry.getKey());
            counter += 1;
        }

        // profit
        Map<String, Integer> profitMap = (Map<String, Integer>)value.get("profit");
        for (String keyStr : profitMap.keySet()) {
            int key = Integer.parseInt(keyStr);
            this.profit.put(key, profitMap.get(keyStr));
        }
        Map<Integer, Integer> cusRenameRev = new HashMap<Integer, Integer>();
        counter = 0;
        for (Map.Entry<Integer, Integer> entry : this.profit.entrySet()) {
            this.rprofit.add(entry.getValue());
            cusRenameRev.put(counter, entry.getKey());
            counter += 1;
        }

        // urgency
        Map<String, Integer> urgencyMap = (Map<String, Integer>)value.get("urgency");
        for (String keyStr : urgencyMap.keySet()) {
            int key = Integer.parseInt(keyStr);
            this.urgency.put(key, urgencyMap.get(keyStr));
        }
        for (int i = 0; i < reqRename.size(); ++ i) {
            this.rurgency.add(this.urgency.get(reqRenameRev.get(i)));
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

        for (int i = 0; i < cusRenameRev.size(); ++ i) {
            List<Integer> tmpList = new ArrayList<Integer>();
            for (int req : this.requests.get(cusRenameRev.get(i))) {
                tmpList.add(reqRename.get(req));
            }
            this.rrequests.add(tmpList);
        }
    }
}
