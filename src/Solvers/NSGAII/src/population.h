#ifndef POPULATION_H
#define POPULATION_H

#include "solution.h"
#include <functional>
#include <random>
#include <vector>

using namespace std;

namespace NSGAII {
    extern bool random_bool();
    extern int random_int();

    class Population {
    private:
        int variable_num = 0;
        int objective_num = 0;
        int constraint_num = 0;
        vector<Solution> population;

    public:
        Population();
        Population(int size, int variable_num, int objective_num);
        Population(int size, int variable_num, int objective_num, int constraint_num);
        Solution& at(int index);
        int size() const;
        const vector<Solution>& list() const;
        void add(const Solution& s);
        const Solution& get(int index) const;
        void set(const vector<Solution>& solutions);
        void set(int index, const Solution& s);
        int get_variable_num() const;
        int get_objective_num() const;
        int get_constraint_num() const;
        void combine(const Population& P);
        void clear();

        static Solution random_solution(int variable_num, int objective_num, int constraint_num);
        static vector<vector<SolutionRecord>> fast_non_dominated_sort(const Population& P);
        static void crowding_distance_assignment(vector<SolutionRecord>& L, const vector<double>& obj_range);
        static bool crowded_comparison(const SolutionRecord&, const SolutionRecord&);
        vector<Solution> random_select(int number) const;
        static pair<Solution, Solution> best_two(vector<Solution>& solutions);
    };
}


#endif //POPULATION_H