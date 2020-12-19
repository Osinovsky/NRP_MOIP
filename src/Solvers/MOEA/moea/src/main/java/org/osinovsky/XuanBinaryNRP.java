package org.osinovsky;


import org.uma.jmetal.problem.binaryproblem.impl.AbstractBinaryProblem;
import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.util.binarySet.BinarySet;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;

public class XuanBinaryNRP extends AbstractBinaryProblem {
    private static final long serialVersionUID = 1L;

    private List<Integer> bitsPerVariable;
    // members
    private Map<Integer, Integer> cost;
    private Map<Integer, Integer> profit;
    private Map<Integer, ArrayList<Integer>> requests;
    private Map<Integer, Integer> reqDict;
    private Map<Integer, Integer> rvReqDict;
    // private List<Boolean> seed;

    // constructor
    public XuanBinaryNRP(Map<Integer, Integer> cost,
                   Map<Integer, Integer> profit,
                   Map<Integer, ArrayList<Integer>> requests,
                   Map<Integer, Integer> reqDict,
                   Map<Integer, Integer> rvReqDict
                   ) {
        // assign to members
        this.cost = cost;
        this.profit = profit;
        this.requests = requests;
        this.reqDict = reqDict;
        this.rvReqDict = rvReqDict;
        // this.seed = seed;
        // if (seed != null) assert this.cost.size() == this.seed.size();
        // get length of each arguments
        // set some attributes
        setNumberOfVariables(this.cost.size());
        setNumberOfObjectives(2);
        setNumberOfConstraints(0);
        setName("XuanBinaryNRP");
        // set bits for each variables
        bitsPerVariable = new ArrayList<>(this.cost.size());
        for (int var = 0; var < this.cost.size(); var++) {
            bitsPerVariable.add(1);
        }
    }

    @Override
    public List<Integer> getListOfBitsPerVariable() {
      return bitsPerVariable;
    }

    // @Override
    // public BinarySolution createSolution() {
    //     BinarySolution solution = new DefaultBinarySolution(getListOfBitsPerVariable(), getNumberOfObjectives(), getNumberOfConstraints());
    //     if (seed != null) {
    //         int variablesNum = getNumberOfVariables();
    //         BinarySet bits = new BinarySet(1);
    //         for (int i = 0; i < variablesNum; ++ i) {
    //             solution.getVariable(i).set(0, this.seed.get(i));
    //         }
    //     }
    //     return solution;
    // }

    // evaluate
    @Override
    public void evaluate(BinarySolution solution) {
        // get all variables
        List<BinarySet> variables = solution.getVariables();
        // prepare profitSum and costSum
        int profitSum = 0;
        int costSum = 0;
        // calculate cost
        for (int i = 0; i < variables.size(); ++ i) {
            if (variables.get(i).get(0)) {
                costSum += this.cost.get(this.reqDict.get(i));
            }
        }
        // calculate profit
        for (int customer : this.requests.keySet()) {
            int satisfied = 0;
            List<Integer> reqList = this.requests.get(customer);
            for (int req : this.requests.get(customer)) {
                if (variables.get(this.rvReqDict.get(req)).get(0)) {
                    satisfied += 1;
                } else {
                    break;
                }
            }
            if (satisfied == reqList.size()) {
                profitSum -= this.profit.get(customer);
            }
        }
        // update objectives
        solution.setObjective(0, profitSum);
        solution.setObjective(1, costSum);
    }
}

