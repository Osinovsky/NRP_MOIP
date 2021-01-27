package org.osinovsky;

import org.uma.jmetal.algorithm.multiobjective.nsgaii.NSGAII;
import org.uma.jmetal.operator.crossover.CrossoverOperator;
import org.uma.jmetal.operator.mutation.MutationOperator;
import org.uma.jmetal.problem.Problem;
// import org.uma.jmetal.solution.Solution;
import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.util.binarySet.BinarySet;
import org.uma.jmetal.util.comparator.DominanceComparator;
import org.uma.jmetal.operator.selection.impl.NaryTournamentSelection;
import org.uma.jmetal.util.comparator.RankingAndCrowdingDistanceComparator;
import org.uma.jmetal.util.evaluator.impl.SequentialSolutionListEvaluator;

import java.util.ArrayList;
import java.util.List;
import java.util.HashSet;

public class IPNSGAII extends NSGAII<BinarySolution>{
    private static final long serialVersionUID = 1L;

    // record the last populations
    HashSet<BinarySolution> elders = new HashSet<>();
    // count how many rounds that no new solutions
    int sameOld;
    // wait round
    int patient;
    // max evaluations
    int maxEva;
    // seeds
    ArrayList<Boolean> seed = new ArrayList<Boolean>();

    // constructor
    public IPNSGAII(
        Problem<BinarySolution> problem, int maxEvaluations, int patient,
        int populationSize, int matingPoolSize, int offspringPopulationSize,
        int tournamentSize,
        CrossoverOperator<BinarySolution> crossoverOperator,
        MutationOperator<BinarySolution> mutationOperator,
        ArrayList<Boolean> seed
    ) {
        // SelectionOperator<List<S>, S> selectionOperator = new BinaryTournamentSelection<S>(new RankingAndCrowdingDistanceComparator<S>());
        // SolutionListEvaluator<S> evaluator = new SequentialSolutionListEvaluator<S>();
        // Comparator<S> comparator = new DominanceComparator<S>();
        
        super(problem, maxEvaluations, populationSize, matingPoolSize, offspringPopulationSize,
        crossoverOperator, mutationOperator,
        new NaryTournamentSelection<>(tournamentSize, new RankingAndCrowdingDistanceComparator<BinarySolution>()),
        // new BinaryTournamentSelection<BinarySolution>(new RankingAndCrowdingDistanceComparator<BinarySolution>()),
        new DominanceComparator<BinarySolution>(),
        new SequentialSolutionListEvaluator<BinarySolution>());

        this.maxEva = maxEvaluations;
        this.patient = patient;
        this.seed = seed;
    }

    @Override protected List<BinarySolution> createInitialPopulation() {
        List<BinarySolution> population = new ArrayList<>(getMaxPopulationSize());
        BinarySolution first = problem.createSolution();
        // if seed is not empty, it would be used
        if (this.seed.size() > 0) {
            System.out.println("seed used, from IPNSGAII");
            for (int index = 0; index < this.seed.size(); ++ index) {
                BinarySet bset = new BinarySet(1);
                bset.set(0, this.seed.get(index));
                first.setVariable(index, bset);
                problem.evaluate(first); // TODO: is it necessary? but whatever
                population.add(first);
            }
        }
        
        for (int i = 1; i < getMaxPopulationSize(); i++) {
            BinarySolution newIndividual = getProblem().createSolution();
            population.add(newIndividual);
        }
        return population;
    }

    private List<BinarySolution> pureSolutions(List<BinarySolution> solutions) {
        List<BinarySolution> pure = new ArrayList<>();
        for (BinarySolution solution : solutions) {
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

    private boolean updateLast(List<BinarySolution> current) {
        // get solutions that satisfy the constraints
        List<BinarySolution> pure = this.pureSolutions(current);

        // String pSize = Integer.toString(pure.size());
        // String cSize = Integer.toString(current.size());
        // System.out.println(pSize + "/" + cSize);
        if (pure.size() == 0) {
            return false;
        }
        boolean flag = false;
        for (BinarySolution solution : pure) {
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
        if (this.patient == 0){
            // System.out.println(this.evaluations);
            return this.evaluations >= this.maxEva;
        } else {
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
}
