#include "problem.h"
#include "NSGAII.h"
#include "dumper.h"
#include <iostream>
#include <assert.h>
#include <string>
#include <chrono>

using namespace std;

int main(int argc, char *argv[]) {
    assert(argc == 2);
    // load config
    auto config = NSGAII::Config(string(argv[1]));
    // prepare result files
    string i_file = config.result_path + "/i_";
    string s_file = config.result_path + "/s_";
    string v_file = config.result_path + "/v_";
    // load problem
    string problem_file = config.dump_path;
    problem_file += ("/"  + config.problem_name + ".json");
    auto problem = NSGAII::XuanNRP(problem_file);
    int vars_num = problem.cost.size();
    int objs_num = 2;
    int csts_num = 0;
    if (config.xuan > 0.0) {
        csts_num = 1;
    } else if (config.xuan < -5.0) {
        objs_num = 3;
    } 

    for (int i = 0; i < config.iteration; ++ i) {
        // load NSGAII
        auto algorithm = NSGAII::NSGAII(vars_num, objs_num, csts_num, &problem, config);
        cout << "round: " << i << endl;

        chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
        algorithm.prepare();
        algorithm.execute();
        chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
        double elapsed = chrono::duration_cast<chrono::milliseconds>(end-begin).count() / 1000.0;

        auto solutions = algorithm.get_results();
        cout << "time elapsed: " << elapsed << ", solutions found:" << solutions.size() << endl;

        NSGAII::Dumper::dump_info(elapsed, solutions.size(), i_file + std::to_string(i) + ".json");
        NSGAII::Dumper::dump_solutions(solutions,
                                       v_file + std::to_string(i) + ".txt",
                                       s_file + std::to_string(i) + ".txt");
    }
    
}
