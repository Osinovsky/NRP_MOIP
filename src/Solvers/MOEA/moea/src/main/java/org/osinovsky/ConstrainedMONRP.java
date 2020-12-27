package org.osinovsky;

import org.uma.jmetal.problem.binaryproblem.impl.AbstractBinaryProblem;
import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.util.binarySet.BinarySet;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;

public class ConstrainedMONRP extends AbstractBinaryProblem {
    private static final long serialVersionUID = 1L;
    private List<Integer> bitsPerVariable;
    private int varNum;
    // members
    private List<List<Double>> objectives;
    private List<Map<Integer, Double>> inequations;

    public ConstrainedMONRP(
        List<List<Double>> objectives,
        List<Map<Integer, Double>> inequations
    ) {
        this.objectives = objectives;
        this.inequations = inequations;

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
    }

    @Override
    public List<Integer> getListOfBitsPerVariable() {
      return bitsPerVariable;
    }


    @Override
    public CBinarySolution createSolution() {
        CBinarySolution solution = new CBinarySolution(getListOfBitsPerVariable(), getNumberOfObjectives(), getNumberOfConstraints());
        return solution;
    }

    // evaluate
    public void evaluate(BinarySolution solution) {
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
}
