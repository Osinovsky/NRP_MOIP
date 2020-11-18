package org.osinovsky;

import org.uma.jmetal.algorithm.multiobjective.nsgaii.NSGAII;
import org.uma.jmetal.operator.crossover.CrossoverOperator;
import org.uma.jmetal.operator.mutation.MutationOperator;
import org.uma.jmetal.problem.Problem;
import org.uma.jmetal.solution.Solution;
import org.uma.jmetal.util.comparator.DominanceComparator;
import org.uma.jmetal.operator.selection.impl.BinaryTournamentSelection;
import org.uma.jmetal.util.comparator.RankingAndCrowdingDistanceComparator;
import org.uma.jmetal.util.evaluator.impl.SequentialSolutionListEvaluator;

import java.util.ArrayList;
import java.util.List;
import java.util.HashSet;

public class IPNSGAII<S extends Solution<?>> extends NSGAII<S>{
    private static final long serialVersionUID = 1L;

    // record the last populations
    HashSet<S> elders = new HashSet<>();
    // count how many rounds that no new solutions
    int sameOld;
    // wait round
    int patient;
    // max evaluations
    int maxEva;

    // constructor
    public IPNSGAII(
        Problem<S> problem, int maxEvaluations, int patient,
        int populationSize, int matingPoolSize, int offspringPopulationSize,
        CrossoverOperator<S> crossoverOperator, MutationOperator<S> mutationOperator
    ) {
        // SelectionOperator<List<S>, S> selectionOperator = new BinaryTournamentSelection<S>(new RankingAndCrowdingDistanceComparator<S>());
        // SolutionListEvaluator<S> evaluator = new SequentialSolutionListEvaluator<S>();
        // Comparator<S> comparator = new DominanceComparator<S>();
        
        super(problem, maxEvaluations, populationSize, matingPoolSize, offspringPopulationSize,
        crossoverOperator, mutationOperator,
        new BinaryTournamentSelection<S>(new RankingAndCrowdingDistanceComparator<S>()),
        new DominanceComparator<S>(),
        new SequentialSolutionListEvaluator<S>());

        this.maxEva = maxEvaluations;
        this.patient = patient;
    }

    private List<S> pureSolutions(List<S> solutions) {
        List<S> pure = new ArrayList<>();
        for (S solution : solutions) {
            double[] csts = solution.getConstraints();
            boolean satisfied = true;
            for (double cst : csts) {
                if (cst < 0.0) {
                    satisfied = false;
                    break;
                }
            }
            if (satisfied) {
                pure.add(solution);
            }
        }
        return pure;
    }

    private boolean updateLast(List<S> current) {
        // get solutions that satisfy the constraints
        List<S> pure = this.pureSolutions(current);

        // String pSize = Integer.toString(pure.size());
        // String cSize = Integer.toString(current.size());
        // System.out.println(pSize + "/" + cSize);
        if (pure.size() == 0) {
            return false;
        }
        boolean flag = false;
        for (S solution : pure) {
            if (!this.elders.contains(solution)) {
                // new solution
                flag = true;
                break;
            }
        }
        if (flag) {
            // update last
            this.elders.clear();
            this.elders.addAll(pure);
            this.sameOld = 0;
        }else{
            // no new solutions
            this.sameOld += 1;
        }

        return true;
    }

    @Override protected boolean isStoppingConditionReached() {
        if (this.updateLast(this.getPopulation())) {
            if (this.sameOld >= this.patient) {
                System.out.println("lose patient at: " + Integer.toString(this.evaluations));
            }
            return (this.evaluations >= this.maxEva
            ||  this.sameOld >= this.patient);
        }else{
            return false;
        }
    }
}
