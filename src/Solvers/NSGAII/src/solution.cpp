#include "solution.h"
#include <iostream>

using namespace std;

namespace NSGAII {
    Solution::Solution(int variable_num, int objective_num) {
        Solution(variable_num, objective_num, 0);
    }
    Solution::Solution(int variable_num, int objective_num, int constraint_num) {
        this->variables = vector<bool>(variable_num);
        this->objectives = vector<double>(objective_num);
        this->constraints = vector<double>(constraint_num);
        this->if_feasible = true;
    }

    bool Solution::get_variable(int index) const { return this->variables.at(index); }
    double Solution::get_objective(int index) const { return this->objectives.at(index); }
    double Solution::get_constraint(int index) const { return this->constraints.at(index); }
    void Solution::set_variable(int index, bool value) { this->variables.at(index) = value; }
    void Solution::set_objective(int index, double value) { this->objectives.at(index) = value; }
    void Solution::set_constraint(int index, double value) {
        this->constraints.at(index) = value;
    }

    const vector<bool>& Solution::get_variables() const { return this->variables; }
    const vector<double>& Solution::get_objectives() const { return this->objectives; }
    const vector<double>& Solution::get_constraints() const { return this->constraints; }
    int Solution::get_variable_num() const { return this->variables.size(); }
    int Solution::get_objective_num() const { return this->objectives.size(); }
    int Solution::get_constraint_num() const { return this->constraints.size(); }
    
    bool Solution::constrained() const { return this->constraints.size() != 0; }
    bool Solution::feasible() const { return this->if_feasible; }
    bool Solution::check_feasible() {
        this->if_feasible = true;
        for (auto cst : this->constraints) {
            if (cst < -1e-6) {
                this->if_feasible = false;
                break;
            }
        }
        return this->if_feasible;
    }
    
    void Solution::operator=(const Solution& s) {
        this->variables = s.get_variables();
        this->objectives = s.get_objectives();
        this->constraints = s.get_constraints();
        this->if_feasible = s.feasible();
    }

    bool Solution::operator==(const Solution& s) const {
        return this->variables == s.get_variables();
    }

    bool Solution::dominate(const Solution& s1, const Solution& s2) {
        bool equal = true;
        int obj_num = s1.get_objective_num();
        for (int i = 0; i < obj_num; ++ i) {
            auto s1o = s1.get_objective(i);
            auto s2o = s2.get_objective(i);
            if (s1o > s2o) {
                return false;
            } else if(s1o < s2o) {
                equal = false;
            }
        }
        return !equal;
    }

    bool Solution::constrained_dominate(const Solution& s1, const Solution& s2) {
        if (s1.feasible()) {
            if (s2.feasible()) {
                return Solution::dominate(s1, s2);
            } else {
                return true;
            }
        } else {
            if (s2.feasible()) {
                return false;
            } else {
                return Solution::dominate(s1, s2);
            }
        }
    }

    bool Solution::operator<(const Solution& s) const {
        if (this->if_feasible) {
            if (s.feasible()) {
                return Solution::dominate(*this, s);
            } else {
                return true;
            }
        } else {
            if (s.feasible()) {
                return false;
            } else {
                return Solution::dominate(*this, s);
            }
        }
    }

    SolutionRecord::SolutionRecord(int id, const Solution& s) {
        this->id = id;
        this->objectives = s.get_objectives();
    }

    vector<SolutionRecord> SolutionRecord::shortcut(const vector<Solution>& l) {
        vector<SolutionRecord> records;
        for (int i = 0; i < l.size(); ++ i) {
            records.push_back(SolutionRecord(i, l.at(i)));
        }
        return records;
    }

    vector<Solution> SolutionRecord::restore(const vector<Solution>& R, const vector<SolutionRecord>& F) {
        vector<Solution> P;
        for (const auto& f : F) {
            P.push_back(R.at(f.id));
        }
        return P;
    }

    pair<vector<bool>, vector<bool>> Solution::cut(int mid) const {
        if (mid <= 0 || mid >= this->variables.size()-1) cout << "cut mid out of bound" << endl;
        vector<bool> head(this->variables.begin(), this->variables.begin() + mid);
        vector<bool> tail(this->variables.begin() + mid, this->variables.end());
        return make_pair(head, tail);
    }

    vector<bool> Solution::cut_head(int mid) const {
        vector<bool> head(this->variables.begin(), this->variables.begin() + mid);
        return head;
    }

    vector<bool> Solution::cut_tail(int mid) const {
        vector<bool> tail(this->variables.begin() + mid, this->variables.end());
        return tail;
    }

    void Solution::update_head(int mid, const vector<bool>& head) {
        this->variables.erase(this->variables.begin(), this->variables.begin() + mid);
        auto tmp = head;
        tmp.insert(tmp.end(), this->variables.begin(), this->variables.end());
        this->variables = tmp;
    }

    void Solution::update_tail(int mid, const vector<bool>& tail) {
        this->variables.erase(this->variables.begin() + mid, this->variables.end());
        this->variables.insert(this->variables.end(), tail.begin(), tail.end());
    }

    void Solution::flip(int position) {
        this->variables.at(position) = !this->variables.at(position);
    }
}
