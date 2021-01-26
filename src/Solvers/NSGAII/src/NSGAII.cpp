#include "NSGAII.h"
#include <iostream>
#include <vector>

using namespace std;

namespace NSGAII {
    NSGAII::NSGAII(int variable_num, int objective_num, int constraint_num, Problem* problem, Config config) {
        this->variable_num = variable_num;
        this->objective_num = objective_num;
        this->constraint_num = constraint_num;
        this->problem = problem;
        this->population_size = config.population;
        this->max_evaluations = config.max_evaluations;
        this->tournament_num = config.tournament;
        this->mutation_probability = config.mutation;
        this->crossover_probability = config.crossover;
        this->repair_probability = config.repair;
        this->xuan = config.xuan;

        this->decimal_gen = uniform_real_distribution<double>(0.0, 1.0);
        this->mid_gen = uniform_int_distribution<int>(1, variable_num-2);

        this->ranges = problem->objective_ranges(this->xuan);
    }

    const vector<Solution>& NSGAII::get_population() const { return this->population.list(); }

    vector<Solution> NSGAII::get_results() const {
        vector<Solution> results;
        for (const auto& solution : this->population.list()) {
            if (solution.feasible()) {
                results.push_back(solution);
            }
        }
        return results;
    }

    void NSGAII::evaluate_all(Population& P) {
        for (int i = 0; i < P.size(); ++ i) {
            this->problem->evaluate(P.at(i), this->xuan);
        }
        this->evaluation += this->population_size;
    }

    void NSGAII::prepare() {
        this->create_init_population();
        this->offspring = this->population;
    }

    void NSGAII::execute() {
        auto& P = this->population;
        auto& Q = this->offspring;
        
        while (this->evaluation < this->max_evaluations) {
            // R = P U Q
            Population R = P;
            R.combine(Q); 
            P.clear();
            Q.clear();
            // F = fast-non-dominated-sort(R)
            auto F = Population::fast_non_dominated_sort(R);
            int i = 0;
            vector<SolutionRecord> PR;
            while (PR.size() + F.at(i).size() <= this->population_size) {
                // crowding-distance-assignment(F[i])
                Population::crowding_distance_assignment(F.at(i), this->ranges);
                // P = P U F[i]
                PR.insert(PR.end(), F.at(i).begin(), F.at(i).end());
                i += 1;
                // cout << PR.size() << ", " << F.at(i).size() << endl;
            }
            // cout << "#" << PR.size() << endl;
            // sort(F[i])
            sort(F.at(i).begin(), F.at(i).end(), Population::crowded_comparison);
            int vacation = this->population_size - PR.size();
            // P = P U F[0..N-|P|]
            // cout << vacation << "#" << endl;
            PR.insert(PR.end(), F.at(i).begin(), F.at(i).begin() + vacation);
            P.set(SolutionRecord::restore(R.list(), PR));
            // Q = make-new-population(P)
            this->make_new_population();
        }
    }

    void NSGAII::create_init_population() {
        this->population = Population(this->population_size, this->variable_num, this->objective_num, this->constraint_num);
        evaluate_all(this->population);
    }

    void NSGAII::make_new_population() {
        auto& Q = this->offspring;
        assert(Q.size() == 0);

        while (Q.size() < this->population_size) {
            auto parents = this->tournament_selection();
            this->single_point_crossover(parents.first, parents.second);
            this->bitwise_mutation(parents.first);
            this->bitwise_mutation(parents.second);
            Q.add(parents.first); Q.add(parents.second);
        }

        assert(Q.size() == this->population_size);
        this->evaluate_all(Q);
    }

    pair<Solution, Solution> NSGAII::tournament_selection() {
        auto candid = this->population.random_select(this->tournament_num);
        return Population::best_two(candid);
    }

    void NSGAII::single_point_crossover(Solution& s1, Solution& s2) {
        if (this->decimal_gen(this->mt) <= this->crossover_probability) {
            int mid = this->mid_gen(this->mt);
            s1.update_tail(mid, s2.cut_tail(mid));
            s2.update_head(mid, s1.cut_head(mid));
        }
    }

    void NSGAII::bitwise_mutation(Solution& s) {
        for (int i = 0; i < this->variable_num; ++ i) {
            if (this->decimal_gen(this->mt) <= this->mutation_probability) {
                s.flip(i);
            }
        }
    }
}
