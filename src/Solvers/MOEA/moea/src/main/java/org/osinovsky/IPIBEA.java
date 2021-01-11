package org.osinovsky;

import org.uma.jmetal.algorithm.multiobjective.ibea.IBEA;
import org.uma.jmetal.operator.crossover.CrossoverOperator;
import org.uma.jmetal.operator.mutation.MutationOperator;
import org.uma.jmetal.problem.Problem;
import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.util.binarySet.BinarySet;
import org.uma.jmetal.operator.selection.impl.NaryTournamentSelection;
import org.uma.jmetal.util.comparator.RankingAndCrowdingDistanceComparator;
import java.util.ArrayList;
import java.util.List;
import java.util.HashSet;

public class IPIBEA extends IBEA<BinarySolution>{
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
    public IPIBEA(
        Problem<BinarySolution> problem, int patient,
        int populationSize, int archiveSize, int maxEvaluations,
        int tournamentSize,
        CrossoverOperator<BinarySolution> crossoverOperator,
        MutationOperator<BinarySolution> mutationOperator,
        ArrayList<Boolean> seed
    ) {
        super(problem, populationSize, archiveSize, maxEvaluations,
            new NaryTournamentSelection<>(tournamentSize, new RankingAndCrowdingDistanceComparator<BinarySolution>()),
            crossoverOperator, mutationOperator);
        this.maxEva = maxEvaluations;
        this.patient = patient;
        this.seed = seed;
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

    protected List<BinarySolution> createInitialPopulation() {
        List<BinarySolution> population = new ArrayList<>(this.populationSize);
        BinarySolution first = problem.createSolution();
        // if seed is not empty, it would be used
        if (this.seed.size() > 0) {
            System.out.println("seed used, from IPIBEA");
            for (int index = 0; index < this.seed.size(); ++ index) {
                BinarySet bset = new BinarySet(1);
                bset.set(0, this.seed.get(index));
                first.setVariable(index, bset);
                problem.evaluate(first); // TODO: is it necessary? but whatever
                population.add(first);
            }
        }
        
        for (int i = 1; i < this.populationSize; i++) {
            BinarySolution newIndividual = this.problem.createSolution();
            population.add(newIndividual);
        }
        return population;
    }
    
    protected boolean isStoppingConditionReached(List<BinarySolution> population, int evaluations) {
        if (this.patient == 0){
            return evaluations >= this.maxEva;
        } else {
            if (this.updateLast(population)) {
                if (this.sameOld >= this.patient) {
                    System.out.println("lose patient at: " + Integer.toString(evaluations));
                }
                return (evaluations >= this.maxEva
                ||  this.sameOld >= this.patient);
            }else{
                return false;
            }
        }
    }

    @Override public void run() {
        int evaluations;
        List<BinarySolution> solutionSet, offSpringSolutionSet;
    
        //Initialize the variables
        solutionSet = new ArrayList<>(populationSize);
        archive = new ArrayList<>(archiveSize);
        evaluations = 0;
    
        //-> Create the initial solutionSet
        solutionSet = this.createInitialPopulation();
    
        while (!this.isStoppingConditionReached(solutionSet, evaluations)) {
          List<BinarySolution> union = new ArrayList<>();
          union.addAll(solutionSet);
          union.addAll(archive);
          calculateFitness(union);
          archive = union;
    
          while (archive.size() > populationSize) {
            removeWorst(archive);
          }
          // Create a new offspringPopulation
          offSpringSolutionSet = new ArrayList<>(populationSize);
          BinarySolution parent1;
          BinarySolution parent2;
          while (offSpringSolutionSet.size() < populationSize) {
            int j = 0;
            do {
            j++;
            parent1 = selectionOperator.execute(archive);
            } while (j < IBEA.TOURNAMENTS_ROUNDS);
            int k = 0;
            do {
            k++;
            parent2 = selectionOperator.execute(archive);
            } while (k < IBEA.TOURNAMENTS_ROUNDS);
    
            List<BinarySolution> parents = new ArrayList<>(2);
            parents.add(parent1);
            parents.add(parent2);
    
            //make the crossover
            List<BinarySolution> offspring = crossoverOperator.execute(parents);
            mutationOperator.execute(offspring.get(0));
            problem.evaluate(offspring.get(0));
            //problem.evaluateConstraints(offSpring[0]);
            offSpringSolutionSet.add(offspring.get(0));
            evaluations++;
          }
          solutionSet = offSpringSolutionSet;
        }
    }
}
