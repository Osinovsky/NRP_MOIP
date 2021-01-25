#include "../src/dumper.h"
#include "../src/solution.h"
#include "../src/population.h"
#include <iostream>

using namespace std;
using namespace NSGAII;

Solution random_solution(int v, int o, int c) {
    auto s = Population::random_solution(v, o, c);
    for (int i = 0; i < o; ++ i) {
        s.set_objective(i, NSGAII::random_int());
    }
    return s;
}

vector<Solution> random_solutions(int s, int v, int o, int c) {
    vector<Solution> solutions;
    for (int i = 0; i < s; ++ i) {
        auto s = random_solution(v, o, c);
        solutions.push_back(s);
    }
    return solutions;
}

void case_tests() {
    Dumper::dump_info(0.02, 100, "i_test.json");

    auto solutions = random_solutions(1000, 100, 3, 20);
    Dumper::dump_solutions(solutions, "v_test.txt", "s_test.txt");
}

void unit_tests() {

}

int main() {
    cout << "case tests..." << endl;
    case_tests();

    cout << "unit tests..." << endl;
    unit_tests();

    cout << "done!" << endl;

    return 0;
}
