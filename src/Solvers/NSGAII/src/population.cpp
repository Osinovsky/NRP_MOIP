#include "population.h"
#include <iostream>
#include <vector>
#include <limits>
#include <algorithm>
#include <ctime>

using namespace std;

namespace NSGAII {
    bool random_bool() {
        static auto gen = bind(uniform_int_distribution<>(0, 1), mt19937((unsigned int)time(NULL)));
        return gen();
    }

    int random_int() {
        static auto int_gen = bind(uniform_int_distribution<int>(1, 99), mt19937((unsigned int)time(NULL)));
        return int_gen();
    }

    int random_big_int() {
        static auto bint_gen = bind(uniform_int_distribution<int>(1, 99999), mt19937((unsigned int)time(NULL)));
        return bint_gen();
    }

    Population::Population() {}
    Population::Population(int size, int variable_num, int objective_num) {
        Population(size, variable_num, objective_num, 0);
    }
    Population::Population(int size, int variable_num, int objective_num, int constraint_num) {
        this->variable_num = variable_num;
        this->objective_num = objective_num;
        this->constraint_num = constraint_num;
        for (int i = 0; i < size; ++ i) {
            this->population.push_back(random_solution(variable_num, objective_num, constraint_num));
        }
    }

    Solution& Population::at(int index) { return this->population.at(index); }
    int Population::size() const { return this->population.size(); }
    const vector<Solution>& Population::list() const { return this->population; }
    void Population::add(const Solution& s) { this->population.push_back(s); }
    const Solution& Population::get(int index) const { return this->population.at(index); }
    int Population::get_variable_num() const { return this->variable_num; }
    int Population::get_objective_num() const { return this->objective_num; }
    int Population::get_constraint_num() const { return this->constraint_num; }
    void Population::set(const vector<Solution>& solutions) { this->population = solutions; }
    void Population::set(int index, const Solution& s) {
        if (s.get_variable_num() == this->variable_num &&
            s.get_objective_num() == this->objective_num &&
            s.get_constraint_num() == this->constraint_num){
            this->population.at(index) = s;
        } else {
            cout << "solution not match with population" << endl;
        }
        
    }

    void Population::combine(const Population& P) {
        const auto& plist = P.list();
        this->population.insert(this->population.end(), plist.begin(), plist.end());
    }

    void Population::clear() {
        this->population.clear();
    }

    Solution Population::random_solution(int variable_num, int objective_num, int constraint_num) {
        Solution s(variable_num, objective_num, constraint_num);
        for (int i = 0; i < variable_num; ++ i) {
            s.set_variable(i, random_bool());
        }
        return s;
    }

    vector<vector<SolutionRecord>> Population::fast_non_dominated_sort(const Population& P) {
        int population_size = P.size();
        // prepare F
        vector<vector<SolutionRecord>> F;
        F.push_back(vector<SolutionRecord>());
        // prepare sp
        vector<vector<int>> S;
        vector<int> n(population_size, 0);
        for (int pi = 0; pi < population_size; ++ pi) {
            const Solution& p = P.get(pi);
            vector<int> Sp;
            for (int qi = 0; qi < population_size; ++ qi) {
                const Solution& q = P.get(qi);
                if (p < q) {
                    Sp.push_back(qi);
                }else if (q < p) {
                    n.at(pi) += 1;
                }
            }
            if (n.at(pi) == 0) {
                auto r = SolutionRecord(pi, p);
                r.rank = 0;
                F.at(0).push_back(r);
            }
            S.push_back(Sp);
        }
        int i = 0;
        do {
            vector<SolutionRecord> Q;
            for (const auto& pi : F.at(i)) {
                for (int qi : S.at(pi.id)) {
                    n.at(qi) -= 1;
                    if (n.at(qi) == 0) {
                        auto r = SolutionRecord(qi, P.get(qi));
                        r.rank = i + 1;
                        Q.push_back(r);
                    }
                }
            }
            i += 1;
            if (!Q.empty()) F.push_back(Q);
            else break;
        } while(true);
        return F;
    }

    void Population::crowding_distance_assignment(vector<SolutionRecord>& L, const vector<double>& obj_range) {
        int l = L.size();
        if (l == 0) return;
        for (auto& sr : L) { sr.distance = 0.0; }
        int obj_num = L.at(0).objectives.size();
        for (int m = 0; m < obj_num; ++ m) {
            sort(L.begin(), L.end(), [m](const SolutionRecord& r1, const SolutionRecord& r2){
                return r1.objectives.at(m) < r2.objectives.at(m);
            });
            L.at(0).distance = numeric_limits<double>::infinity();
            L.at(l-1).distance = numeric_limits<double>::infinity();
            for (int i = 1; i < l-1; ++ i) {
                double delta = L.at(i+1).objectives.at(m) - L.at(i-1).objectives.at(m);
                L.at(i).distance += (delta / (obj_range.at(m)));
            }
        }
    }

    bool Population::crowded_comparison(const SolutionRecord& r1, const SolutionRecord& r2) {
        return (r1.rank < r2.rank || ((r1.rank == r2.rank) && (r1.distance > r2.distance)));
    }

    vector<Solution> Population::random_select(int number) const {
        if (number <= 0 || number >= this->population.size()) cout << "tournament size cannot be " << number << endl;
        int size = this->population.size();
        vector<Solution> solutions;
        vector<int> record;
        for (int i = 0; i < number; ++ i) {
            int chosen = random_big_int() % size;
            while (find(record.begin(), record.end(), chosen) != record.end()) {
                chosen = random_big_int() % size;
            }
            record.push_back(chosen);
            solutions.push_back(this->population.at(chosen));
        }
        return solutions;
    }

    pair<Solution, Solution> Population::best_two(vector<Solution>& solutions) {
        sort(solutions.begin(), solutions.end(), Solution::constrained_dominate);
        return pair<Solution, Solution>(solutions.at(0), solutions.at(1));
    }
}
