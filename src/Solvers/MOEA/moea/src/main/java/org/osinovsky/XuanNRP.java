package org.osinovsky;


import org.uma.jmetal.problem.binaryproblem.impl.AbstractBinaryProblem;
import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.util.binarySet.BinarySet;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.lang.Math;
import java.util.Random;

public class XuanNRP extends AbstractBinaryProblem {
    private static final long serialVersionUID = 1L;

    private List<Integer> bitsPerVariable;
    // members
    private int minUrgency;
    private double bound;
    private Map<Integer, Integer> cost;
    private Map<Integer, Integer> profit;
    private Map<Integer, Integer> urgency;
    private Map<Integer, ArrayList<Integer>> requests;
    private Map<Integer, Integer> reqDict;
    private Map<Integer, Integer> rvReqDict;
    private int lsRound;
    private double lsRatio;
    private int allCost;
    // private List<Boolean> seed;

    // constructor
    public XuanNRP(double bound,
                   Map<Integer, Integer> cost,
                   Map<Integer, Integer> profit,
                   Map<Integer, Integer> urgency,
                   Map<Integer, ArrayList<Integer>> requests,
                   Map<Integer, Integer> reqDict,
                   Map<Integer, Integer> rvReqDict,
                   int lsRound,
                   double lsRatio
                   ) {
        // assign to members
        this.bound = bound;
        this.cost = cost;
        this.profit = profit;
        this.urgency = urgency;
        this.requests = requests;
        this.reqDict = reqDict;
        this.rvReqDict = rvReqDict;
        this.lsRound = lsRound;
        this.lsRatio = lsRatio;

        this.allCost = 0;
        for (int val : this.cost.values()) {
            this.allCost += val;
        }
        // this.seed = seed;
        // if (seed != null) assert this.cost.size() == this.seed.size();
        // get length of each arguments

        // set some attributes
        setNumberOfVariables(this.cost.size());
        if (this.bound > 0) {
            // bincst
            System.out.println("Xuan Bincst NRP");
            setNumberOfObjectives(2);
            setNumberOfConstraints(1);
            this.minUrgency = 0;
            for (int urg : this.urgency.values()) {
                this.minUrgency += urg;
            }
            double tmp = this.bound * this.minUrgency;
            this.minUrgency = (int)Math.ceil(tmp);
        } else if (this.bound < -5) {
            // triurgency
            System.out.println("Xuan Triurgency NRP");
            setNumberOfObjectives(3);
            setNumberOfConstraints(0);
        } else {
            // binary
            System.out.println("Xuan Binary NRP");
            setNumberOfObjectives(2);
            setNumberOfConstraints(0);
        }
        setName("XuanNRP");
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

    @Override
    public CBinarySolution createSolution() {
        CBinarySolution solution = new CBinarySolution(getListOfBitsPerVariable(), getNumberOfObjectives(), getNumberOfConstraints());
        return solution;
    }

    public int randomItem(List<Integer> list) {
        Random randomGenerator = new Random();
        return list.get(randomGenerator.nextInt(list.size()));
    }

    public boolean dominate(BinarySolution s1, BinarySolution s2) {
        boolean equal = true;
        int length = s1.getNumberOfObjectives();
        for (int i = 0; i < length; ++ i) {
            if (s1.getObjective(i) > s2.getObjective(i)) {
                return false;
            } else if (equal && s1.getObjective(i) < s2.getObjective(i)) {
                equal = false;
            }
        }
        return !equal;
    }

    public boolean unnondominate(BinarySolution s1, BinarySolution s2) {
        int length = s1.getNumberOfObjectives();
        for (int i = 0; i < length; ++ i) {
            if (s1.getObjective(i) < s2.getObjective(i)) {
                return true;
            }
        }
        return false;
    }

    public void subEvaluate(BinarySolution solution) {
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

        if (this.bound < -5 || this.bound > 0) {
            int urgencySum = 0;
            // calculate urgency
            for (int i = 0; i < variables.size(); ++ i) {
                if (variables.get(i).get(0)) {
                    urgencySum += this.urgency.get(this.reqDict.get(i));
                }
            }
            if (this.bound < -5) {
                // triurgency
                solution.setObjective(2, urgencySum);
            } else {
                // bincst
                // evaluate constraint
                solution.setConstraint(0, urgencySum - this.minUrgency);
            }
        }
    }

    public void localSearch(BinarySolution solution) {
        List<BinarySet> variables = solution.getVariables();
        boolean changed = true;
        List<Integer> ones = new ArrayList<Integer>();
        List<Integer> zeros = new ArrayList<Integer>();
        for (int r = 0; r < this.lsRound; ++ r) {
            if (changed) {
                for (int i = 0; i < variables.size(); ++ i) {
                    if (variables.get(i).get(0)) {
                        ones.add(i);
                    } else {
                        zeros.add(i);
                    }
                }
                changed = false;
                if (ones.size() == 0 || zeros.size() == 0) {
                    return;
                }
            }
            BinarySolution newSolution = (BinarySolution)solution.copy();
            newSolution.getVariable(randomItem(ones)).set(0, false);
            newSolution.getVariable(randomItem(zeros)).set(0, true);
            subEvaluate(newSolution);
            if (dominate(newSolution, solution)) {
                solution = newSolution;
                changed = true;
            }
        }
    }

    // evaluate
    @Override
    public void evaluate(BinarySolution solution) {
        subEvaluate(solution);
        if (Math.random() < this.lsRatio) {
            localSearch(solution);
        }
    }
}

