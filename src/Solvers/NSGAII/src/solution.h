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
        static bool constrained_dominate(const Solution&, const Solution&);

        void operator=(const Solution&);
        bool operator==(const Solution&) const;
        bool operator<(const Solution&) const;

        pair<vector<bool>, vector<bool>> cut(int mid) const;
        vector<bool> cut_head(int mid) const;
        vector<bool> cut_tail(int mid) const;
        void update_head(int mid, const vector<bool>& head);
        void update_tail(int mid, const vector<bool>& tail);
        void flip(int position);
    };

    class SolutionRecord {
    public:
        int id = -1;
        int rank = -1;
        double distance = 0.0;
        vector<double> objectives;

        SolutionRecord(int id, const Solution& s);
        static vector<SolutionRecord> shortcut(const vector<Solution>& l);
        static vector<Solution> restore(const vector<Solution>& R, const vector<SolutionRecord>& F);
    };
}

#endif //SOLUTION_H
