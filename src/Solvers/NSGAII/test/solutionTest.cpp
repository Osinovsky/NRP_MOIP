#include "../src/solution.h"
#include <iostream>
#include <assert.h>
#include <cstdlib>
#include <random>

using namespace std;
using namespace NSGAII;

Solution random_solution(int vn, int on, int cn) {
    random_device rd;
    mt19937 mt(rd());
    uniform_real_distribution<double> double_dist(-100.0, 100.0);
    uniform_int_distribution<int> int_dist(1, 100);
    Solution s(vn, on, cn);

    for (int k = 0; k < vn; ++ k) {
        bool value = int_dist(mt) > 50;
        s.set_variable(k, value);
    }
    for (int k = 0; k < on; ++ k) {
        double value = double_dist(mt);
        s.set_objective(k, value);
    }
    if (cn != 0) {
        for (int k = 0; k < cn; ++ k) {
            double value = double_dist(mt);
            s.set_constraint(k, value);
        }
    }
    return s;
}

Solution random_solution() {
    random_device rd;
    mt19937 mt(rd());
    uniform_int_distribution<int> int_dist(1, 100);

    int vn = int_dist(mt);
    int on = int_dist(mt);
    int cn = 0;
    if (int_dist(mt) > 50) cn = int_dist(mt);
    return random_solution(vn, on, cn);
}

void unit_tests(){
    random_device rd;
    mt19937 mt(rd());
    uniform_real_distribution<double> double_dist(-100.0, 100.0);
    uniform_int_distribution<int> int_dist(1, 100);

    for (int i = 0; i < 100; ++ i) {
        // create solution
        size_t vn = int_dist(mt);
        size_t on = int_dist(mt);
        size_t cn = 0;
        if (int_dist(mt) > 50) cn = int_dist(mt);
        Solution s(vn, on, cn);
        assert(s.get_variable_num() == vn);
        assert(s.get_objective_num() == on);
        assert(s.get_constraint_num() == cn);
        assert(s.constrained() == (cn > 0));
        assert(s.feasible());
        // set solution
        uniform_int_distribution<int> vi(0, vn-1);
        uniform_int_distribution<int> oi(0, on-1);
        uniform_int_distribution<int> ci(0, cn<1?0:cn-1);
        int round = int_dist(mt);
        for (int k = 0; k < round; ++ k) {
            int index = vi(mt);
            bool value = int_dist(mt) > 50;
            s.set_variable(index, value);
            assert(s.get_variable(index) == value);
        }
        round = int_dist(mt);
        for (int k = 0; k < round; ++ k) {
            int index = oi(mt);
            double value = double_dist(mt);
            s.set_objective(index, value);
            assert(s.get_objective(index) == value);
        }
        if (cn != 0) {
            round = int_dist(mt);
            for (int k = 0; k < round; ++ k) {
                int index = ci(mt);
                double value = double_dist(mt);
                s.set_constraint(index, value);
                assert(s.get_constraint(index) == value);
            }
        }
        bool f = true;
        for (int k = 0; k < s.get_constraint_num(); ++ k) {
            if (s.get_constraint(k) < -1e-6) {
                f = false;
                break;
            }
        }
        s.check_feasible();
        assert(f == s.feasible());
    }

    // copy
    for (int i = 0; i < 100; ++ i) {
        auto s = random_solution();
        auto s2 = random_solution();
        s2 = s;
        assert(s.get_variable_num() == s2.get_variable_num());
        assert(s.get_objective_num() == s2.get_objective_num());
        assert(s.get_constraint_num() == s2.get_constraint_num());
        assert(s.feasible() == s2.feasible());
        assert(s.constrained() == s2.constrained());
        assert(s.get_variables() == s2.get_variables());
        assert(s.get_objectives() == s2.get_objectives());
        assert(s.get_constraints() == s2.get_constraints());
        assert(s == s2);
        assert(s2 == s);
    }

    // dominate
    for (int i = 0; i < 100; ++ i) {
        random_device rd;
        mt19937 mt(rd());
        uniform_int_distribution<int> int_dist(1, 100);

        int vn = int_dist(mt);
        int on = int_dist(mt);
        int cn = 0;
        if (int_dist(mt) > 50) cn = int_dist(mt);

        auto s1 = random_solution(vn, on, cn);
        auto s2 = random_solution(vn, on, cn);
        assert((
            (s1.feasible() && !s2.feasible()) ||
            (
                (s1.feasible() == s2.feasible()) &&
                (Solution::dominate(s1, s2))
            )
        ) == (s1 < s2)
        );
        assert(!((s1 < s2) && (s2 < s1)));
        assert(!(s1 < s1) && !(s2 < s2));
    }

    // flip
    for (int i = 0; i < 100; ++ i ){
        random_device rd;
        mt19937 mt(rd());
        uniform_int_distribution<int> int_dist(1, 100);

        int vn = int_dist(mt);
        int on = int_dist(mt);
        int cn = 0;
        if (int_dist(mt) > 50) cn = int_dist(mt);
        auto s = random_solution(vn, on, cn);
        int round = int_dist(mt) % 30;

        uniform_int_distribution<int> pos(0, vn-1);

        for (int j = 0; j < round; ++ j) {
            int position = pos(mt);
            bool last = s.get_variable(position);
            s.flip(position);
            assert(last != s.get_variable(position));
        }
    }

    // cuts
    for (int i = 0; i < 100; ++ i) {
        random_device rd;
        mt19937 mt(rd());
        uniform_int_distribution<int> int_dist(1, 100);

        int vn = int_dist(mt) + 3;
        int on = int_dist(mt);
        int cn = 0;
        if (int_dist(mt) > 50) cn = int_dist(mt);
        auto s1 = random_solution(vn, on, cn);
        auto s2 = random_solution(vn, on, cn);

        uniform_int_distribution<int> pos(1, vn-2);
        int mid = pos(mt);
        auto s1ht = s1.cut(mid);
        auto s2ht = s2.cut(mid);
        assert(s1ht.first == s1.cut_head(mid));
        assert(s1ht.second == s1.cut_tail(mid));
        assert(s2ht.first == s2.cut_head(mid));
        assert(s2ht.second == s2.cut_tail(mid));

        auto s1cp = s1;
        auto s2cp = s2;

        s1.update_tail(mid, s2.cut_tail(mid));
        s2.update_head(mid, s1.cut_head(mid));
        assert(s1.get_variable_num() == vn);
        assert(s2.get_variable_num() == vn);
    
        for (int k = 0; k < vn; ++ k) {
            if (k < mid) {
                assert(s1.get_variable(k) == s1cp.get_variable(k));
                assert(s2.get_variable(k) == s1cp.get_variable(k));
            } else {
                assert(s1.get_variable(k) == s2cp.get_variable(k));
                assert(s2.get_variable(k) == s2cp.get_variable(k));
            }
        }
    }
}

void case_tests() {
    Solution s1(0, 3, 1);

    assert(s1.feasible());
    s1.set_constraint(0, -1.0);
    s1.check_feasible();
    assert(!s1.feasible());
    s1.set_constraint(0, .0);
    s1.check_feasible();
    assert(s1.feasible());

    Solution s2(0, 3, 1);

    s1.set_objective(0, 0.0);
    s1.set_objective(1, 0.0);
    s1.set_objective(2, 0.0);

    s2.set_objective(0, 0.0);
    s2.set_objective(1, 0.0);
    s2.set_objective(2, 0.0);

    assert(s1 == s2);

    s2.set_objective(1, 2.0);

    assert(s1 < s2);

    s1.set_objective(0, 2.0);

    assert(!(s1 < s2) && !(s2 < s1));

    s1 = random_solution(10, 3, 0);

    auto ht = s1.cut(3);
    assert(ht.first.size() == 3);
    assert(ht.second.size() == 7);

    s2 = random_solution(10, 3, 0);
    auto s1_copy = s1;
    auto s2_copy = s2;

    int mid = 4;
    auto s1ht = s1.cut(mid);
    auto s2ht = s2.cut(mid);
    assert(s1ht.first == s1.cut_head(mid));
    assert(s1ht.second == s1.cut_tail(mid));
    assert(s2ht.first == s2.cut_head(mid));
    assert(s2ht.second == s2.cut_tail(mid));
    s1.update_head(mid, s2ht.first);
    s2.update_tail(mid, s1ht.second);
    for (int i = 0; i < 10; ++ i) {
        if (i < mid) {
            assert(s1.get_variable(i) == s2_copy.get_variable(i));
            assert(s2.get_variable(i) == s2_copy.get_variable(i));
        } else {
            assert(s1.get_variable(i) == s1_copy.get_variable(i));
            assert(s2.get_variable(i) == s1_copy.get_variable(i));
        }
    }

    auto s3 = s1;
    s3.flip(7);
    assert(s3.get_variable(7) != s1.get_variable(7));
    s3.flip(7);
    assert(s3 == s1);
}

int main() {
    cout << "case tests..." << endl;
    case_tests();

    cout << "unit tests..." << endl;
    unit_tests();

    cout << "done!" << endl;

    return 0;
}
