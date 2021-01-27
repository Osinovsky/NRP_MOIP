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

public class ConstrainedMONRP extends AbstractBinaryProblem {
    private static final long serialVersionUID = 1L;
    private List<Integer> bitsPerVariable;
    private int varNum;
    private List<Integer> pre = new ArrayList<Integer>();
    private List<Integer> suf = new ArrayList<Integer>();
    // members
    private List<List<Double>> objectives;
    private List<Map<Integer, Double>> inequations;

    private double timeLimit;
    private double repair;
    private IloCplex cplex;
    private IloIntVar[] vars;
    private double[] firstVals;
    private double[] secondVals;

    public ConstrainedMONRP(
        double repair,
        double timeLimit,
        List<List<Double>> objectives,
        List<Map<Integer, Double>> inequations
    ) {
        this.objectives = objectives;
        this.inequations = inequations;
        this.repair = repair;
        this.timeLimit = timeLimit;

        this.varNum = this.objectives.get(0).size();
        setNumberOfVariables(this.varNum);
        setNumberOfConstraints(this.inequations.size());
        setNumberOfObjectives(this.objectives.size());
        setName("Constrained MONRP");
        // set bits for each variables
        bitsPerVariable = new ArrayList<>(this.varNum);
        for (int var = 0; var < this.varNum; var ++) {
            bitsPerVariable.add(1);
        }
        constructRequestList();

        try {
            this.cplex = new IloCplex();
            this.cplex.setOut(null);
			// cplex.setParam(IloCplex.Param.MIP.Tolerances.AbsMIPGap, 0.0);
			// cplex.setParam(IloCplex.Param.MIP.Tolerances.MIPGap, 0.0);
			this.cplex.setParam(IloCplex.Param.Threads, 1);
			// cplex.setParam(IloCplex.Param.Parallel, 0);
            this.cplex.setParam(IloCplex.Param.TimeLimit, this.timeLimit);
            
            IloIntVar[] x = this.cplex.boolVarArray(this.varNum);
            this.vars = x;

            for (int i = 0; i < this.inequations.size(); ++ i) {
                IloIntExpr cst = this.cplex.sum(x[this.suf.get(i)], this.cplex.prod(-1, x[this.pre.get(i)]));
                this.cplex.addLe(cst, 0.0);
            }

            this.firstVals = new double[x.length];
            for (int i = 0; i < x.length; ++ i) this.firstVals[i] = this.objectives.get(0).get(i);
            this.cplex.addMinimize(this.cplex.scalProd(x, firstVals));

            this.secondVals = new double[x.length];
            for (int i = 0; i < x.length; ++ i) this.secondVals[i] = this.objectives.get(1).get(i);
        } catch (IloException e) {
            System.err.println("Cplex initialize: " + e);
            this.repair = 0.0;
        }
    }

    @Override
    public List<Integer> getListOfBitsPerVariable() {
      return bitsPerVariable;
    }

    public boolean around(double num, int mid) {
        return num <= mid + 1e-6 && num >= mid - 1e-6;
    }

    public void constructRequestList() {
        for (int i = 0; i < this.inequations.size(); ++ i) {
            Map<Integer, Double> ineq = this.inequations.get(i);
            if (ineq.size() == 3) {
                int pre = -1;
                int suf = -1;
                for (int key : ineq.keySet()) {
                    double val = ineq.get(key);
                    if (around(val, 0)) {
                        if (key != this.varNum) {
                            assert false;
                        }
                    } else if (around(val, -1)) {
                        pre = key;
                    } else if (around(val, 1)) {
                        suf = key;
                    } else {
                        assert false;
                    }
                }
                assert pre != -1 && suf != -1;
                this.pre.add(pre);
                this.suf.add(suf);
            }
        }
    }


    @Override
    public CBinarySolution createSolution() {
        CBinarySolution solution = new CBinarySolution(getListOfBitsPerVariable(), getNumberOfObjectives(), getNumberOfConstraints());
        return solution;
    }

    // repair
    public void repair(BinarySolution solution) {
        List<BinarySet> vars = solution.getVariables();
        for (int i = 0; i < this.suf.size(); ++ i) {
            int suf = this.suf.get(i);
            int pre = this.pre.get(i);
            if (vars.get(suf).get(0) && !vars.get(pre).get(0)) {
                solution.getVariable(suf).set(0, false);
            }
        }
    }
    
    public void fixSolution(BinarySolution solution) {
        try {
            // see second obj as optimal
            IloRange cst = cplex.addLe(cplex.scalProd(this.vars, this.secondVals), solution.getObjective(1));
            if (this.cplex.solve()) {
                if (this.cplex.getStatus().toString().toLowerCase().contains("optimal")) {
                    // have solution
                    double[] vals = cplex.getValues(this.vars);
                    for (int i = 0; i < this.varNum; ++ i) {
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

    private void subEvaluate(BinarySolution solution) {
        // get all variables
        List<BinarySet> variables = solution.getVariables();
        // evaluate objectives
        for (int objIndex = 0; objIndex < this.objectives.size(); ++ objIndex) {
            // prepare the objective
            double obj = 0.0;
            List<Double> objective = this.objectives.get(objIndex);
            // for each variable
            for (int index = 0; index < variables.size(); ++ index) {
                if (variables.get(index).get(0)) {
                    obj += objective.get(index);
                }
            }
            // set the objective
            solution.setObjective(objIndex, obj);
        }
        // evaluate constraints
        for (int cstIndex = 0; cstIndex < this.inequations.size(); ++ cstIndex) {
            // prepare the constraint
            double cst = 0.0;
            Map<Integer, Double> constraint = this.inequations.get(cstIndex);
            // for each variable
            for (int index = 0; index < variables.size(); ++ index) {
                if (constraint.containsKey(index) && variables.get(index).get(0)) {
                    cst -= constraint.get(index);
                }
            }
            // for the constant
            if (constraint.containsKey(variables.size())) {
                cst += constraint.get(variables.size());
            }
            // set the constraint
            solution.setConstraint(cstIndex, cst);
        }
    }

    // evaluate
    public void evaluate(BinarySolution solution) {
        subEvaluate(solution);
        if (Math.random() < this.repair) {
            fixSolution(solution);
        }
    }
}
