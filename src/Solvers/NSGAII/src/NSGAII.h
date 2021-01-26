#ifndef NSGAII_H
#define NSGAII_H

#include "solution.h"
#include "population.h"
#include "problem.h"
#include <ctime>
#include <random>

using namespace std;

namespace NSGAII {
    class NSGAII {
    private:
        Population population;
        Population offspring;
        Problem* problem;
        int evaluation = 0;

        int variable_num;
        int objective_num;
        int constraint_num;
        int population_size;
        int max_evaluations;
        int tournament_num;
        double mutation_probability;
        double crossover_probability;
        double repair_probability;
        double xuan;
        vector<double> ranges;

        mt19937 mt =  mt19937((unsigned int)time(NULL));
        uniform_real_distribution<double> decimal_gen;
        uniform_int_distribution<int> mid_gen;

    private:
        void evaluate_all(Population& P);

    public:
        NSGAII(int variable_num, int objective_num, int constraint_num, Problem* problem, Config config);
        const vector<Solution>& get_population() const;
        vector<Solution> get_results() const;
        void prepare();
        void execute();

        void create_init_population();
        void make_new_population();
        pair<Solution, Solution> tournament_selection();
        void single_point_crossover(Solution& s1, Solution& s2);
        void bitwise_mutation(Solution& s);
    };
}

#endif //NSGA_H