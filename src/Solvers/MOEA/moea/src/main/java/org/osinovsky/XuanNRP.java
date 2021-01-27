package org.osinovsky;


import org.uma.jmetal.problem.binaryproblem.impl.AbstractBinaryProblem;
import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.util.binarySet.BinarySet;

import ilog.concert.IloIntExpr;
import ilog.concert.IloException;
import ilog.concert.IloIntVar;
import ilog.concert.IloRange;
import ilog.cplex.IloCplex;

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
    private List<Integer> cost;
    private List<Integer> profit;
    private List<Integer> urgency;
    private List<List<Integer>> requests;
    private int mode = 0;
    
    // private List<Boolean> seed;
    private double timeLimit;
    private double repair;
    private IloCplex cplex;
    private IloIntVar[] vars;
    private double[] costVals;
    private double[] urgencyVals;
    private double[] profitVals;

    // constructor
    public XuanNRP(double bound, double repair,
                   double timeLimit,
                   List<Integer> cost,
                   List<Integer> profit,
                   List<Integer> urgency,
                   List<List<Integer>> requests
                   ) {
        // assign to members
        this.bound = bound;
        this.repair = repair;
        this.cost = cost;
        this.profit = profit;
        this.urgency = urgency;
        this.requests = requests;
        this.timeLimit = timeLimit;

        assert(cost.size() == urgency.size());
        assert(requests.size() == profit.size());

        // set some attributes
        setNumberOfVariables(this.cost.size());
        if (this.bound > 0) {
            // bincst
            this.mode = 2;
            System.out.println("Xuan Bincst NRP");
            setNumberOfObjectives(2);
            setNumberOfConstraints(1);
            this.minUrgency = 0;
            for (int urg : this.urgency) {
                this.minUrgency += urg;
            }
            double tmp = this.bound * this.minUrgency;
            this.minUrgency = (int)Math.ceil(tmp);
        } else if (this.bound < -5) {
            // triurgency
            this.mode = 3;
            System.out.println("Xuan Triurgency NRP");
            setNumberOfObjectives(3);
            setNumberOfConstraints(0);            
        } else {
            // binary
            this.mode = 1;
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

        try {
            this.cplex = new IloCplex();
            this.cplex.setOut(null);
			// cplex.setParam(IloCplex.Param.MIP.Tolerances.AbsMIPGap, 0.0);
			// cplex.setParam(IloCplex.Param.MIP.Tolerances.MIPGap, 0.0);
			this.cplex.setParam(IloCplex.Param.Threads, 1);
			// cplex.setParam(IloCplex.Param.Parallel, 0);
            this.cplex.setParam(IloCplex.Param.TimeLimit, this.timeLimit);
            
            IloIntVar[] x = this.cplex.boolVarArray(cost.size() + profit.size());
            this.vars = x;
            // add requests constraints
            int cusStart = cost.size();
            for (int i = 0; i < this.requests.size(); ++ i) {
                int cus = cusStart + i;
                for (int req : this.requests.get(i)) {
                    // cus <= req
                    IloIntExpr cst = this.cplex.sum(x[cus], this.cplex.prod(-1, x[req]));
                    this.cplex.addLe(cst, 0.0);
                }
            }

            // cost
            this.costVals = new double[x.length];
            for (int i = 0; i < cost.size(); ++ i) this.costVals[i] = cost.get(i);
            for (int i = cost.size(); i < x.length; ++ i) this.costVals[i] = 0.0;
            // urgency
            this.urgencyVals = new double[x.length];
            for (int i = 0; i < cost.size(); ++ i) urgencyVals[i] = this.urgency.get(i);
            for (int i = cost.size(); i < x.length; ++ i) this.urgencyVals[i] = 0.0;
            // profit
            this.profitVals = new double[x.length];
            for (int i = 0; i < cost.size(); ++ i) this.profitVals[i] = 0.0;
            for (int i = cost.size(); i < x.length; ++ i)  this.profitVals[i] = this.profit.get(i-cost.size());

            // TODO: maybe other objectives
            double[] profitCost = new double[x.length];
            for (int i = 0; i < x.length; ++ i) profitCost[i] = profitVals[i] - costVals[i];
            if (this.mode == 1) {
                // binary
                this.cplex.addMaximize(this.cplex.scalProd(x, profitVals));
                // this.cplex.addMaximize(this.cplex.scalProd(x, profitCost));
            } else if (this.mode == 2) {
                //bincst
                this.cplex.addGe(this.cplex.scalProd(x, urgencyVals), this.minUrgency);
                this.cplex.addMaximize(this.cplex.scalProd(x, profitCost));
            } else if (this.mode == 3) {
                // triple
                double[] profitCostUrgency = new double[x.length];
                for (int i = 0; i < x.length; ++ i) profitCostUrgency[i] = profitCost[i] + urgencyVals[i];
                this.cplex.addMaximize(this.cplex.scalProd(x, profitCostUrgency));
            } else {
                assert(false);
            }
        } catch (IloException e) {
            System.err.println("Cplex initialize: " + e);
            this.repair = 0.0;
        }

    }

    public void fixSolution(BinarySolution solution) {
        try {
            // binary & bincst, keep cost max profit
            // IloRange cst = cplex.addGe(cplex.scalProd(this.vars, this.profitVals), -solution.getObjective(0));
            IloRange cst = cplex.addLe(cplex.scalProd(this.vars, this.costVals), solution.getObjective(1));
            if (this.cplex.solve()) {
                if (this.cplex.getStatus().toString().toLowerCase().contains("optimal")) {
                    // have solution
                    double[] vals = cplex.getValues(this.vars);
                    for (int i = 0; i < this.cost.size(); ++ i) {
                        solution.getVariable(i).set(0, (Math.round(vals[i]) == 1));
                    }
                    System.out.println("fix to " + Double.toString(this.cplex.getObjValue()));
                    this.subEvaluate(solution);
                }
            }
            this.cplex.delete(cst);
        } catch (IloException e) {
            System.err.println("Cplex solution fix: " + e);
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
        // if (Math.random() < this.repair) {
        //     subEvaluate(solution);
        //     fixSolution(solution);
        // }
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
        double profitSum = 0;
        double costSum = 0;
        
        // calculate cost
        for (int i = 0; i < variables.size(); ++ i) {
            if (variables.get(i).get(0)) {
                costSum += this.cost.get(i);
            }
        }

        // calculate profit
        for (int i = 0; i < this.requests.size(); ++ i) {
            boolean sat = true;
            for (int req : this.requests.get(i)) {
                if (!variables.get(req).get(0)) {
                    sat = false;
                    break;
                }
            }
            if (sat) {
                profitSum -= this.profit.get(i);
            }
        }

        // update objectives
        solution.setObjective(0, profitSum);
        solution.setObjective(1, costSum);

        if (this.mode == 3) {
            double urgencySum = 0;
            for (int i = 0; i < variables.size(); ++ i) {
                if (variables.get(i).get(0)) {
                    urgencySum -= this.urgency.get(i);
                }
            }
            solution.setObjective(2, urgencySum);
        }
    }

    // evaluate
    @Override
    public void evaluate(BinarySolution solution) {
        subEvaluate(solution);
        if (Math.random() < this.repair) {
            fixSolution(solution);
        }
    }
}

