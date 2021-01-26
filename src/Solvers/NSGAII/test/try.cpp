#include <memory>
#include <iostream>
#include <vector>
#include <assert.h>
#include <random>
#include <limits>
#include <functional>
#include <algorithm>
#include <ctime>
#include <string>
#include <fstream>
#include "../src/rapidjson/document.h"
#include "../src/rapidjson/istreamwrapper.h"
#include "../src/rapidjson/stringbuffer.h"
#include "../src/rapidjson/writer.h"

using namespace std;
using namespace rapidjson;

int random_int() {
    static auto int_gen = bind(uniform_int_distribution<int>(1, 99), mt19937((unsigned int)time(NULL)));
    return int_gen();
}

class A {
    public:
        mt19937 mt =  mt19937((unsigned int)time(NULL));
        uniform_real_distribution<double> decimal_gen;
        A() {
            decimal_gen = uniform_real_distribution<double>(0.0, 1.0);
        }

        double give() {
            return decimal_gen(mt);
        }
};

int main(int argc, char *argv[]){
    // auto file_name = "/mnt/c/Users/osino/Desktop/dev/prototype/NRP_MOIP/dump/config-classic_1-binary.json";
    auto file_name = string(argv[1]);
    ifstream file(file_name);
    IStreamWrapper isw(file);
    Document d;
    d.ParseStream(isw);

    cout << d.IsObject() << endl;

    return 0;
}