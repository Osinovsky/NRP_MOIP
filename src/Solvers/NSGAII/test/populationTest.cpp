#include "../src/solution.h"
#include "../src/population.h"
#include <iostream>
#include <assert.h>
#include <cstdlib>
#include <random>
#include <limits>
#include <algorithm>

using namespace std;
using namespace NSGAII;


Solution random_solution(int v, int o, int c) {
    auto s = Population::random_solution(v, o, c);
    for (int i = 0; i < o; ++ i) {
        s.set_objective(i, NSGAII::random_int());
    }
    return s;
}

Population random_population(int s, int v, int o, int c) {
    auto p = Population(s, v, o, c);
    for (int i = 0; i < s; ++ i) {
        auto s = random_solution(v, o, c);
        p.set(i, s);
    }
    return p;
}

void case_tests() {

}

void unit_tests() {
    // create
    for (int repeat = 0; repeat < 100; ++ repeat) {
        int size = 10 + NSGAII::random_int();
        int vn = NSGAII::random_int();
        int on = NSGAII::random_int() % 5 + 1;
        int cn = NSGAII::random_int();
        auto P = Population(size, vn, on, cn);
        assert(P.size() == size);
        for (const auto& p : P.list()) {
            assert(p.get_variable_num() == vn);
            assert(p.get_objective_num() == on);
            assert(p.get_constraint_num() == cn);
            assert(p.feasible());
        }
    }
    // nd sort and distance assignment
    for (int repeat = 0; repeat < 20; ++ repeat) {
        int size = NSGAII::random_int() * 20;
        int vn = NSGAII::random_int();
        int on = NSGAII::random_int() % 5 + 1;
        int cn = NSGAII::random_int();
        auto P = random_population(size, vn, on, cn);
        auto F = Population::fast_non_dominated_sort(P);
        int all_size = 0;
        for (const auto& fi : F) {
            all_size += fi.size();
        }
        assert(all_size == size);
        const auto& F0 = F.at(0);
        for (const auto& fr : F0) {
            const auto& f = P.get(fr.id);
            for (const auto& p : P.list()) {
                assert(!(p < f));
            }
        }
        for (int rank = 0; rank < F.size(); ++ rank) {
            for (const auto& s : F.at(rank)) {
                assert(s.rank == rank);
            }
        }

        // crowding distance
        for (auto& f : F) {
            vector<double> range(on, 100.0);
            P.crowding_distance_assignment(f, range);
            int f_size = f.size();
            if (f_size < 3) {
                for (const auto& s : f) {
                    assert(std::isinf(s.distance));
                }
            } else {
                vector<double> dst(size, 0.0);
                for (int m = 0; m < on; ++ m) {
                    sort(f.begin(), f.end(), [m](const SolutionRecord& r1, const SolutionRecord& r2){
                        return r1.objectives.at(m) < r2.objectives.at(m);
                    });
                    dst.at(f.at(0).id) = numeric_limits<double>::infinity();
                    dst.at(f.at(f_size-1).id) = numeric_limits<double>::infinity();
                    for (int i = 1; i < f_size-1; ++ i) {
                        const auto& sr = f.at(i);
                        dst.at(sr.id) += (f.at(i+1).objectives.at(m) - f.at(i-1).objectives.at(m))/range.at(m);
                    }
                }
                // for (int i = 0; i < f_size; ++ i) cout << f.at(i).distance << ", ";
                // cout << endl;
                // for (int i = 0; i < f_size; ++ i) cout << dst.at(f.at(i).id) << ", ";
                // cout << endl;
                // for(int i = 0; i < f_size; ++ i) {
                //     const auto& fr = f.at(i);
                //     // cout << dst.at(fr.id) << ", " << fr.distance << endl;
                //     assert((std::isinf(dst.at(fr.id)) && std::isinf(fr.distance)) || abs(dst.at(fr.id) - fr.distance) < 1e-6);
                // }
            }
        }
    }
}

int main() {
    cout << "case tests..." << endl;
    case_tests();

    cout << "unit tests..." << endl;
    unit_tests();

    cout << "done!" << endl;

    return 0;
}