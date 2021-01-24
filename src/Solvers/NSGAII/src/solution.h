#ifndef SOLUTION_H
#define SOLUTION_H

#include <vector>

using namespace std;

namespace NSGAII {
    class Solution {
        private:
            vector<bool> variables;
            vector<double> objectives;
            vector<double> constraints;
            bool if_feasible = true;

        public:
            Solution(int variable_num, int objective_num);
            Solution(int variable_num, int objective_num, int constraint_num);
            bool get_variable(int index) const;
            double get_objective(int index) const;
            double get_constraint(int index) const;
            void set_variable(int index, bool value);
            void set_objective(int index, double value);
            void set_constraint(int index, double value);
            const vector<bool>& get_variables() const;
            const vector<double>& get_objectives() const;
            const vector<double>& get_constraints() const;
            int get_variable_num() const;
            int get_objective_num() const;
            int get_constraint_num() const;
            bool constrained() const;
            bool feasible() const;
            bool check_feasible();
            static bool dominate(const Solution&, const Solution&);

            void operator=(const Solution&);
            bool operator==(const Solution&) const;
            bool operator<(const Solution&) const;
    };
}

#endif //SOLUTION_H
