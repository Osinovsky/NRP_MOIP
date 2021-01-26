#include "../src/problem.h"
#include <iostream>
#include <string>


using namespace std;
using namespace NSGAII;

template <typename t>
void print_vector(const vector<t>& vl) {
    for (auto e : vl) {
        cout << e << ", ";
    }
    cout << endl;
}

template <typename t1, typename t2>
void print_map(const map<t1, t2>& mp) {
    for (const auto& p : mp) {
        cout << "(" << p.first << ", " << p.second << "), ";
    }
    cout << endl;
}

void case_tests() {
    string config_file = "./test/config-realistic_m1-binary.json";
    Config config(config_file);
    cout << "itrs " << config.iteration << endl;
    cout << "popl " << config.population << endl;
    cout << "max_eva " << config.max_evaluations << endl;
    cout << "tour " << config.tournament << endl;
    cout << "mut " << config.mutation << endl;
    cout << "crs " << config.crossover << endl;
    cout << "rpr " << config.repair << endl;
    cout << "problem " << config.problem_name << endl;
    cout << "dump " << config.dump_path << endl;
    cout << "res " << config.result_path << endl; 

    string NRP_file = "./test/MSWord-binary.json";
    NRP nrp(NRP_file);
    for (const auto& cst : nrp.objectives) {
        print_vector(cst);
    }
    for (const auto& ineq : nrp.inequations) {
        print_map(ineq);
    }


    string Xuan_file = "./test/classic_1-binary.json";
    XuanNRP xuan(Xuan_file);
    print_vector(xuan.cost);
    print_vector(xuan.profit);
    print_vector(xuan.urgency);
    for (const auto& rl : xuan.requests) {
        print_vector(rl);
    }
}

int main() {
    cout << "case tests..." << endl;
    case_tests();

    cout << "done!" << endl;

    return 0;
}
