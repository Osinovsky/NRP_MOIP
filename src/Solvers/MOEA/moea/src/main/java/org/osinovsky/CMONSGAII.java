package org.osinovsky;

import org.uma.jmetal.algorithm.Algorithm;
// import org.uma.jmetal.util.AbstractAlgorithmRunner;
import org.uma.jmetal.example.AlgorithmRunner;
import org.uma.jmetal.operator.crossover.CrossoverOperator;
import org.uma.jmetal.operator.mutation.MutationOperator;
import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.operator.mutation.impl.BitFlipMutation;
import org.uma.jmetal.operator.crossover.impl.SinglePointCrossover;

// import org.uma.jmetal.util.comparator.DominanceComparator;
// import org.uma.jmetal.util.evaluator.SolutionListEvaluator;
// import org.uma.jmetal.operator.selection.impl.BinaryTournamentSelection;
// import org.uma.jmetal.util.comparator.RankingAndCrowdingDistanceComparator;
// import org.uma.jmetal.util.evaluator.impl.SequentialSolutionListEvaluator;
// import org.uma.jmetal.algorithm.multiobjective.nsgaii.NSGAIIBuilder;
// import org.uma.jmetal.algorithm.multiobjective.nsgaii.NSGAII;

import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class CMONSGAII {
    public static void main(String[] args){
        // handle the arugments
        assert args.length == 1;
        // first arg is the config file
        String configFile = args[0];
        // load the config file
        ConfigLoader configLoader = new ConfigLoader(configFile);
        Map<String, Object> config = configLoader.getConfig();

        // load each config entry
        int iterationTimes = (int)config.get("iteration");
        String resultPath = (String)config.get("result_path");
        int populationSize = (int)config.get("population");
        int maxEvaluations = (int)config.get("max_evaluations");
        int patient = (int)config.get("patient");
        int tournamentSize = (int)config.get("tournament");
        double crossoverProbability = (double)config.get("crossover");
        double mutationProbability = (double)config.get("mutation");
        double repairProbability = (double)config.get("repair");
        double timeLimit = (double)config.get("time_limit");
        ArrayList<ArrayList<Boolean>> seeds = new ArrayList<ArrayList<Boolean>>();
        boolean useSeed = false;
        if (config.containsKey("seeds")) {
            // load seeds
            String seedFile = (String)config.get("seeds");
            SeedsLoader seedsLoader = new SeedsLoader(seedFile);
            System.out.println("This experiment will use seeds");
            useSeed = true;
            seeds = seedsLoader.sample(iterationTimes);
            seedsLoader = null;
        }

        // load problem
        String problemFile = Paths.get((String)config.get("dump_path"),
                                        (String)config.get("problem_name")+".json").toString();
        NRPProblemLoader problemLoader = new NRPProblemLoader(problemFile);
        ConstrainedMONRP problem = new ConstrainedMONRP(repairProbability, timeLimit,
                                                        problemLoader.getObjectives(), problemLoader.getInequations());

        // print iteration times
        System.out.println("iterations: " + Integer.toString(iterationTimes));
        // print configs
        System.out.println("population: " + Integer.toString(populationSize));
        System.out.println("max_evaluations: " + Integer.toString(maxEvaluations));
        System.out.println("patient: " + Integer.toString(patient));
        System.out.println("tournament: " + Integer.toString(tournamentSize));
        System.out.println("crossover: " + Double.toString(crossoverProbability));
        System.out.println("mutation: " + Double.toString(mutationProbability));
        System.out.println("repair: " + Double.toString(repairProbability));
        System.out.println("repair time limit: " + Double.toString(timeLimit));

        // operators
        CrossoverOperator<BinarySolution> crossover = new SinglePointCrossover(crossoverProbability);
        MutationOperator<BinarySolution> mutation = new BitFlipMutation(mutationProbability);

        for (int itr = 0; itr < iterationTimes; ++ itr) {
            // record time
            long startTime = System.nanoTime();
            // seed
            ArrayList<Boolean> seed = new ArrayList<Boolean>();
            if (useSeed) {
                seed = seeds.get(itr);
            }

            // the algorithm
            Algorithm<List<BinarySolution>> algorithm = new IPNSGAII(
                problem, maxEvaluations, patient,
                populationSize, populationSize, populationSize,
                tournamentSize,
                crossover, mutation, seed
            );

            // Algorithm<List<BinarySolution>> algorithm = new NSGAII<>(
            // problem, maxEvaluations, populationSize, populationSize, populationSize,
            // crossover, mutation,
            // new BinaryTournamentSelection<BinarySolution>(new RankingAndCrowdingDistanceComparator<BinarySolution>()),
            // new DominanceComparator<BinarySolution>(),
            // new SequentialSolutionListEvaluator<BinarySolution>());

            // run the algorithm
            new AlgorithmRunner.Executor(algorithm).execute();

            // record time
            long endTime = System.nanoTime();

            // get the result
            List<BinarySolution> population = algorithm.getResult();
            List<BinarySolution> pureSolutions = new ArrayList<BinarySolution>();
            for (BinarySolution solution : population) {
                boolean flag = true;
                for (double cst : solution.getConstraints()) {
                    if (cst < 0.0) {
                        flag = false;
                        break;
                    }
                }
                if (flag) {
                    pureSolutions.add(solution);
                }
            }
            // long computingTime = algorithmRunner.getComputingTime();
            long computingTime = (long)((endTime - startTime)/1000_000);
            // print infomation
            System.out.println("round: " + Integer.toString(itr));
            System.out.println("execution time: " + computingTime + "ms");
            System.out.println("solutions found: " + pureSolutions.size());

            // dump result
            new Dumper(resultPath, itr, pureSolutions, computingTime);
        }
    }
}
