#include <memory>
#include <iostream>
#include <vector>
#include <assert.h>
#include <random>
#include <limits>
#include <functional>
#include <algorithm>
#include <ctime>

using namespace std;

int random_int() {
    static auto int_gen = bind(uniform_int_distribution<int>(1, 99), mt19937((unsigned int)time(NULL)));
    return int_gen();
}


int main(){
    for (int i = 0; i < 10; ++ i) {
        cout << random_int() << ", ";
    }
    cout << endl;
    return 0;
}